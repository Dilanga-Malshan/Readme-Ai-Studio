import base64, hashlib, secrets, json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import database
from app.core.config import settings
from app.core.auth import current_user, user_token, digest, cipher
from app.models.entities import User, GitHubAccount, AuthSession, OAuthState, ProfileSnapshot, ReadmeProject, ReadmeVersion, GenerationHistory, PublishHistory, UserPreference
from app.schemas.contracts import AnalyzeRequest, GenerateRequest, RewriteRequest, ProjectCreate, ProjectUpdate, RenderRequest, PublishRequest, username
from app.services.github import GitHub, analyze
from app.services.composer import TEMPLATES, fallback_content, compose, render, validate
from app.services import publishing
from app.ai import engine

router=APIRouter(prefix='/api/v1')

@router.get('/health')
async def health():
    return dict(status='ok',ai_configured=bool(settings().openai_api_key),oauth_configured=bool(settings().github_client_id and settings().github_client_secret and settings().token_encryption_key))

@router.get('/github/profile/{login}')
async def profile(login: str):
    try: username(login)
    except ValueError as e: raise HTTPException(422,str(e))
    return await GitHub(settings().github_token).profile(login)

@router.get('/github/repositories/{login}')
async def repositories(login: str):
    try: username(login)
    except ValueError as e: raise HTTPException(422,str(e))
    return await GitHub(settings().github_token).repositories(login)

@router.post('/github/analyze')
async def analysis(body: AnalyzeRequest,db: AsyncSession=Depends(database)):
    data=await analyze(body.username)
    db.add(ProfileSnapshot(username=data['profile']['login'],data=data))
    await db.commit()
    return data

async def ai_budget(request,db,operation):
    from app.models.entities import GenerationBudget
    key=digest(request.client.host if request.client else 'unknown')
    day=datetime.now(timezone.utc).date().isoformat()
    budget=await db.scalar(select(GenerationBudget).where(GenerationBudget.client_key==key,GenerationBudget.day==day))
    if budget is None:
        try:
            async with db.begin_nested():
                db.add(GenerationBudget(client_key=key,day=day,used=0))
                await db.flush()
        except IntegrityError:
            pass  # Another request initialized the same counter.
    reserved=await db.execute(update(GenerationBudget).where(GenerationBudget.client_key==key,GenerationBudget.day==day,GenerationBudget.used<settings().ai_daily_limit).values(used=GenerationBudget.used+1))
    if reserved.rowcount!=1:
        await db.rollback()
        raise HTTPException(429,'Daily AI limit reached. Use template generation or try again tomorrow (UTC reset).')
    db.add(GenerationHistory(client_key=key,operation=operation,model=settings().openai_model))
    await db.commit()

@router.post('/ai/generate')
async def generate(body: GenerateRequest,request: Request,db: AsyncSession=Depends(database)):
    data=await analyze(body.username)
    source='edited content' if body.content else 'verified template'
    content=body.content or fallback_content(data)
    if body.use_ai and not body.content:
        if not settings().openai_api_key: raise HTTPException(503,'AI is not configured. Switch off AI generation to use verified templates.')
        await ai_budget(request,db,'generate')
        content=await engine.generate(data);source='AI proposal — verify facts'
    markdown=compose(data,content,body.config)
    return dict(markdown=markdown,content=content.model_dump(),source=source,warnings=validate(markdown),analysis=data)

@router.post('/ai/rewrite')
@router.post('/ai/optimize')
@router.post('/ai/chat')
async def rewrite(body: RewriteRequest,request: Request,db: AsyncSession=Depends(database)):
    if not settings().openai_api_key: raise HTTPException(503,'AI is not configured. Set OPENAI_API_KEY on the backend.')
    await ai_budget(request,db,'rewrite')
    data=await analyze(body.username)
    proposal=await engine.rewrite(data,body.markdown,body.instruction)
    return dict(**proposal.model_dump(),warnings=validate(proposal.markdown))

@router.get('/templates')
async def templates(): return TEMPLATES
@router.get('/templates/{slug}')
async def template(slug: str):
    item=next((t for t in TEMPLATES if t['id']==slug),None)
    if not item: raise HTTPException(404,'Template not found.')
    return item

@router.post('/readmes/render')
async def anonymous_render(body: RenderRequest):
    return dict(html=render(body.markdown),warnings=validate(body.markdown))

@router.post('/readmes')
async def create_project(body: ProjectCreate,user=Depends(current_user),db: AsyncSession=Depends(database)):
    project=ReadmeProject(user_id=user.id,**body.model_dump());db.add(project);await db.flush()
    db.add(ReadmeVersion(project_id=project.id,revision=1,markdown=body.markdown))
    await db.commit();return project_data(project)

def project_data(p): return dict(id=p.id,title=p.title,markdown=p.markdown,config=p.config,revision=p.revision,updated_at=p.updated_at)
async def owned(db,user,id):
    p=await db.get(ReadmeProject,id)
    if not p or p.user_id!=user.id: raise HTTPException(404,'README not found.')
    return p

@router.get('/readmes')
async def projects(user=Depends(current_user),db: AsyncSession=Depends(database)):
    result=await db.scalars(select(ReadmeProject).where(ReadmeProject.user_id==user.id).order_by(ReadmeProject.updated_at.desc()))
    return [project_data(p) for p in result]
@router.get('/readmes/{id}')
async def project(id: str,user=Depends(current_user),db: AsyncSession=Depends(database)):
    return project_data(await owned(db,user,id))
@router.patch('/readmes/{id}')
async def save_project(id: str,body: ProjectUpdate,user=Depends(current_user),db: AsyncSession=Depends(database)):
    await owned(db,user,id)
    result=await db.execute(update(ReadmeProject).where(ReadmeProject.id==id,ReadmeProject.user_id==user.id,ReadmeProject.revision==body.revision).values(title=body.title,markdown=body.markdown,config=body.config,revision=body.revision+1,updated_at=datetime.now(timezone.utc)))
    if result.rowcount!=1:
        await db.rollback();raise HTTPException(409,'Cloud draft changed. Load the latest revision before saving.')
    db.add(ReadmeVersion(project_id=id,revision=body.revision+1,markdown=body.markdown));await db.commit()
    db.expire_all();return project_data(await owned(db,user,id))
@router.get('/readmes/{id}/versions')
async def versions(id: str,user=Depends(current_user),db: AsyncSession=Depends(database)):
    await owned(db,user,id)
    records=await db.scalars(select(ReadmeVersion).where(ReadmeVersion.project_id==id).order_by(ReadmeVersion.revision.desc()).limit(100))
    return [dict(revision=v.revision,markdown=v.markdown,created_at=v.created_at) for v in records]
@router.post('/readmes/{id}/render')
async def project_render(id: str,user=Depends(current_user),db: AsyncSession=Depends(database)):
    p=await owned(db,user,id);return dict(html=render(p.markdown),warnings=validate(p.markdown))
@router.get('/readmes/{id}/export')
async def export(id: str,user=Depends(current_user),db: AsyncSession=Depends(database)):
    p=await owned(db,user,id)
    return Response(p.markdown,media_type='text/markdown',headers={'Content-Disposition':'attachment; filename="README.md"'})

@router.get('/preferences')
async def preferences(user=Depends(current_user),db: AsyncSession=Depends(database)):
    p=await db.scalar(select(UserPreference).where(UserPreference.user_id==user.id));return p.data if p else {}
@router.put('/preferences')
async def save_preferences(body: dict,user=Depends(current_user),db: AsyncSession=Depends(database)):
    if len(json.dumps(body))>10000: raise HTTPException(422,'Preferences are too large.')
    p=await db.scalar(select(UserPreference).where(UserPreference.user_id==user.id))
    if p: p.data=body
    else: db.add(UserPreference(user_id=user.id,data=body))
    await db.commit();return body

@router.get('/auth/github/login')
async def login(db: AsyncSession=Depends(database)):
    cfg=settings()
    if not cfg.github_client_id or not cfg.github_client_secret: raise HTTPException(503,'Configure a GitHub OAuth app first. See docs/SETUP.md.')
    cipher()
    state=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(64)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    db.add(OAuthState(state_hash=digest(state),verifier=verifier,expires_at=datetime.now(timezone.utc)+timedelta(minutes=10)));await db.commit()
    url='https://github.com/login/oauth/authorize?'+urlencode(dict(client_id=cfg.github_client_id,redirect_uri=cfg.backend_url+'/api/v1/auth/github/callback',scope='read:user public_repo',state=state,code_challenge=challenge,code_challenge_method='S256'))
    response=RedirectResponse(url)
    response.set_cookie('oauth_state',state,httponly=True,secure=cfg.cookie_secure,samesite='lax',max_age=600,path='/api/v1/auth')
    return response

@router.get('/auth/github/callback')
async def callback(request: Request,code: str='',state: str='',db: AsyncSession=Depends(database)):
    cookie=request.cookies.get('oauth_state','')
    if not code or not state or not cookie or not secrets.compare_digest(state,cookie): raise HTTPException(400,'OAuth state mismatch. Sign in again.')
    # Atomic one-time state consumption; expired states are never accepted.
    stored=await db.scalar(select(OAuthState).where(OAuthState.state_hash==digest(state)))
    if not stored or stored.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc): raise HTTPException(400,'OAuth state expired.')
    verifier=stored.verifier
    result=await db.execute(delete(OAuthState).where(OAuthState.id==stored.id));await db.commit()
    if result.rowcount!=1: raise HTTPException(400,'OAuth state already used.')
    cfg=settings()
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r=await client.post('https://github.com/login/oauth/access_token',headers={'Accept':'application/json'},data=dict(client_id=cfg.github_client_id,client_secret=cfg.github_client_secret,code=code,code_verifier=verifier,redirect_uri=cfg.backend_url+'/api/v1/auth/github/callback'))
            payload=r.json()
    except (httpx.RequestError,ValueError): raise HTTPException(502,'OAuth token exchange failed.')
    token=payload.get('access_token')
    if not token: raise HTTPException(400,'GitHub authorization failed. Retry sign-in.')
    me=await GitHub(token).request('GET','/user')
    user=await db.scalar(select(User).where(User.github_id==str(me['id'])))
    if not user:
        user=User(github_id=str(me['id']),login=me['login']);db.add(user);await db.flush()
    else: user.login=me['login']
    account=await db.scalar(select(GitHubAccount).where(GitHubAccount.user_id==user.id))
    encrypted=cipher().encrypt(token.encode()).decode()
    if account: account.token_ciphertext=encrypted
    else: db.add(GitHubAccount(user_id=user.id,token_ciphertext=encrypted))
    session_token=secrets.token_urlsafe(40)
    db.add(AuthSession(user_id=user.id,token_hash=digest(session_token),csrf_token=secrets.token_hex(32),expires_at=datetime.now(timezone.utc)+timedelta(hours=cfg.session_hours)))
    await db.commit()
    response=RedirectResponse(cfg.frontend_url+'/studio')
    response.delete_cookie('oauth_state',path='/api/v1/auth')
    response.set_cookie('readme_session',session_token,httponly=True,secure=cfg.cookie_secure,samesite='lax',max_age=cfg.session_hours*3600,path='/')
    return response

@router.get('/auth/me')
async def me(request: Request,user=Depends(current_user)):
    return dict(login=user.login,csrf_token=request.state.auth_session.csrf_token)
@router.post('/auth/logout')
async def logout(request: Request,user=Depends(current_user),db: AsyncSession=Depends(database)):
    await db.delete(request.state.auth_session);await db.commit()
    response=Response(status_code=204);response.delete_cookie('readme_session',path='/');return response

@router.post('/github/publish-preview')
async def publish_preview(body: RenderRequest,user=Depends(current_user),db: AsyncSession=Depends(database)):
    return await publishing.preview(await user_token(user,db),body.markdown)
@router.post('/github/publish')
async def publish(body: PublishRequest,user=Depends(current_user),db: AsyncSession=Depends(database)):
    request_hash=digest(json.dumps(body.model_dump(exclude={'idempotency_key'}),sort_keys=True))
    previous=await db.scalar(select(PublishHistory).where(PublishHistory.user_id==user.id,PublishHistory.idempotency_key==body.idempotency_key))
    if previous:
        if previous.request_hash!=request_hash: raise HTTPException(409,'Idempotency key reused with different content.')
        if previous.status=='published': return dict(id=previous.id,**previous.result)
        raise HTTPException(409,'This publish request was already attempted. Refresh the preview before retrying with a new key.')
    record=PublishHistory(user_id=user.id,idempotency_key=body.idempotency_key,request_hash=request_hash)
    db.add(record)
    try: await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'A matching publish is already in progress.')
    try:
        result=await publishing.publish(await user_token(user,db),body)
        record.status='published';record.result=result;await db.commit();return dict(id=record.id,**result)
    except HTTPException as e:
        record.status='failed';record.result={'error':e.detail};await db.commit();raise
@router.get('/github/publish-status/{id}')
async def publish_status(id: str,user=Depends(current_user),db: AsyncSession=Depends(database)):
    p=await db.get(PublishHistory,id)
    if not p or p.user_id!=user.id: raise HTTPException(404,'Publish not found.')
    return dict(id=p.id,status=p.status,result=p.result)


@router.post('/readmes/{id}/share')
async def share(id: str,body: dict,user=Depends(current_user),db: AsyncSession=Depends(database)):
    from app.models.entities import ReadmeShare
    p=await owned(db,user,id)
    existing=await db.scalar(select(ReadmeShare).where(ReadmeShare.project_id==id))
    if body.get('enabled') is not True:
        if existing: await db.delete(existing)
        await db.commit();return dict(shared=False)
    token=secrets.token_urlsafe(32);expiry=datetime.now(timezone.utc)+timedelta(days=7)
    if existing:
        existing.token_hash=digest(token);existing.markdown=p.markdown;existing.expires_at=expiry
    else:
        db.add(ReadmeShare(project_id=id,token_hash=digest(token),markdown=p.markdown,expires_at=expiry))
    await db.commit()
    return dict(shared=True,url=settings().frontend_url+'/share/'+token,expires_at=expiry)

@router.get('/shared/{token}')
async def shared(token: str,db: AsyncSession=Depends(database)):
    from app.models.entities import ReadmeShare
    if len(token)>100: raise HTTPException(404,'Shared preview not found.')
    s=await db.scalar(select(ReadmeShare).where(ReadmeShare.token_hash==digest(token)))
    if not s or s.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc): raise HTTPException(404,'Shared preview expired or revoked.')
    return dict(markdown=s.markdown,expires_at=s.expires_at)

@router.post('/ai/variants')
async def variants(body: GenerateRequest,request: Request,db: AsyncSession=Depends(database)):
    result=await generate(body,request,db)
    from app.schemas.contracts import ProfileContent
    data=result['analysis'];content=ProfileContent(**result['content']);items=[]
    for slug in ['minimal','professional','neon']:
        t=next(t for t in TEMPLATES if t['id']==slug)
        config=body.config.model_copy(update={'template':slug,'accent':t['accent'],'typing':slug=='neon'})
        markdown=compose(data,content,config)
        items.append(dict(template=slug,name=t['name'],markdown=markdown,content=content.model_dump(),warnings=validate(markdown)))
    return dict(variants=items,source=result['source'])


@router.post('/ai/regenerate-section')
async def regenerate_section(body: RewriteRequest,request: Request,section: str='About me',db: AsyncSession=Depends(database)):
    from app.services.sections import section_bounds,replace_section
    allowed=['About me','Tech stack','What I’m working on','Featured projects','Connect','Beyond code']
    if section not in allowed: raise HTTPException(422,'Choose a supported content section.')
    section_bounds(body.markdown,section)
    if not settings().openai_api_key: raise HTTPException(503,'AI is not configured. Set OPENAI_API_KEY on the backend.')
    await ai_budget(request,db,'section')
    data=await analyze(body.username)
    proposal=await engine.structured(engine.Proposal,dict(task=f'Rewrite only the body of the {section} section. Return its Markdown body only, with no h1/h2 headings.',instruction=body.instruction,evidence=dict(profile=data['profile'],repositories=data['ranked'],languages=data['languages']),current_readme=body.markdown))
    markdown=replace_section(body.markdown,section,proposal.markdown)
    return dict(markdown=markdown,explanation=proposal.explanation,notes=proposal.notes,warnings=validate(markdown))

@router.get('/banners/svg')
async def banner(title: str='Hello, world.',subtitle: str='Your code. Your story.',accent: str='C8F77C'):
    import html,re
    if len(title)>120 or len(subtitle)>180 or not re.fullmatch(r'[a-fA-F0-9]{6}',accent): raise HTTPException(422,'Banner values are invalid.')
    # Pure SVG asset; no scripts, external resources or arbitrary markup.
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc><rect width="1200" height="320" rx="18" fill="#111318"/><path d="M900 0L1200 300M1000 0L1200 200" stroke="#{accent}" stroke-width="1" opacity=".3"/><circle cx="1040" cy="160" r="95" stroke="#{accent}" fill="none" opacity=".3"/><text x="65" y="150" font-family="sans-serif" font-size="48" fill="#{accent}">{html.escape(title)}</text><text x="68" y="205" font-family="sans-serif" font-size="22" fill="#94A3B8">{html.escape(subtitle)}</text></svg>'
    return Response(svg,media_type='image/svg+xml',headers={'Content-Disposition':'attachment; filename="banner.svg"','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; sandbox"})
