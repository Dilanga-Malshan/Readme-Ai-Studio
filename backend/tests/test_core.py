import base64
from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from app.schemas.contracts import AnalyzeRequest, StudioConfig, PublishRequest
from app.services.composer import compose, fallback_content, render, validate, safe_url, TEMPLATES
from app.services.github import GitHub
from app.services import publishing

@pytest.mark.parametrize('value',['a','Dilanga-Malshan','a-b','a'*39])
def test_username_valid(value): assert AnalyzeRequest(username=value).username==value
@pytest.mark.parametrize('value',['','-alice','alice-','a--b','a/b','a'*40,'<script>'])
def test_username_invalid(value):
    with pytest.raises(ValidationError): AnalyzeRequest(username=value)

def test_all_templates(evidence):
    for t in TEMPLATES:
        md=compose(evidence,fallback_content(evidence),StudioConfig(template=t['id']))
        assert 'https://github.com/alice/toolkit' in md
        assert 'Python' in md
        assert not validate(md)

def test_zero_repositories(evidence):
    evidence['ranked']=[];evidence['repositories']=[];evidence['languages']=[]
    md=compose(evidence,fallback_content(evidence),StudioConfig())
    assert 'Featured projects' not in md
    assert 'Alice' in md

def test_untrusted_metadata(evidence):
    evidence['profile']['name']='<script>alert(1)</script>'
    evidence['repositories'][0]['description']='[Click](javascript:alert(1)) <img onerror="boom">'
    result=render(compose(evidence,fallback_content(evidence),StudioConfig()))
    assert '<script>' not in result
    assert '<img onerror=' not in result
    assert 'href="javascript:' not in result

def test_safe_renderer():
    result=render('<script>alert(1)</script><img src="javascript:x" onerror="x"><iframe src="https://x"></iframe><a href="data:text/html,x">x</a>')
    assert '<script' not in result and 'onerror' not in result and '<iframe' not in result and 'href=' not in result
    assert 'src=' not in result

def test_tables_and_alt():
    result=render('| Name |\n| --- |\n| Alice |\n\n![a meaningful alt](https://example.com/a.svg)')
    assert '<table>' in result and 'alt="a meaningful alt"' in result

def test_url_validation():
    assert safe_url('javascript:alert(1)')==''
    assert safe_url('https://user:password@example.com')==''
    assert safe_url('example.com')=='https://example.com'

@pytest.mark.asyncio
async def test_github_not_found(monkeypatch):
    import httpx
    async def request(self,*args,**kwargs): return httpx.Response(404,json={},request=httpx.Request('GET','https://api.github.com/users/missing'))
    monkeypatch.setattr(httpx.AsyncClient,'request',request)
    with pytest.raises(HTTPException) as e: await GitHub().profile('missing')
    assert e.value.status_code==404

@pytest.mark.asyncio
async def test_github_rate_limit(monkeypatch):
    import httpx
    async def request(self,*args,**kwargs): return httpx.Response(403,headers={'x-ratelimit-remaining':'0'},json={})
    monkeypatch.setattr(httpx.AsyncClient,'request',request)
    with pytest.raises(HTTPException) as e: await GitHub().profile('alice')
    assert e.value.status_code==429

@pytest.mark.asyncio
async def test_pagination_and_private_filter(monkeypatch):
    gh=GitHub();calls=[]
    async def request(method,path,**kwargs):
        page=kwargs['params']['page'];calls.append(page)
        if page==1:return [dict(name=str(i),private=False) for i in range(100)]
        return [dict(name='hidden',private=True),dict(name='visible',private=False)]
    monkeypatch.setattr(gh,'request',request)
    repos=await gh.repositories('alice')
    assert calls==[1,2] and len(repos)==101 and not any(r['name']=='hidden' for r in repos)

@pytest.mark.asyncio
async def test_publish_needs_confirmation():
    with pytest.raises(HTTPException) as e: await publishing.publish('token',PublishRequest(markdown='hello',idempotency_key='x'*16))
    assert e.value.status_code==422

@pytest.mark.asyncio
async def test_publish_conflict_preserves_existing(monkeypatch):
    monkeypatch.setattr(publishing,'preview',AsyncMock(return_value=dict(sha='new-sha',branch='main')))
    with pytest.raises(HTTPException) as e: await publishing.publish('token',PublishRequest(markdown='new',confirm=True,expected_sha='old-sha',expected_branch='main',idempotency_key='x'*16))
    assert e.value.status_code==409

@pytest.mark.asyncio
async def test_publish_exact_sha(monkeypatch):
    monkeypatch.setattr(publishing,'preview',AsyncMock(return_value=dict(sha='old',branch='main',repository='alice/alice',exists=True,warnings=[])))
    calls=[]
    async def request(self,method,path,**kwargs):
        calls.append(kwargs['json']);return {'commit':{'sha':'commit'},'content':{'html_url':'https://github.com/alice/alice/blob/main/README.md'}}
    monkeypatch.setattr(GitHub,'request',request)
    result=await publishing.publish('token',PublishRequest(markdown='new',confirm=True,expected_sha='old',expected_branch='main',idempotency_key='x'*16))
    assert calls[0]['sha']=='old' and base64.b64decode(calls[0]['content']).decode()=='new'
    assert result['status']=='published'

@pytest.mark.asyncio
async def test_unsafe_publish_rejected(monkeypatch):
    monkeypatch.setattr(publishing,'preview',AsyncMock(return_value=dict(sha=None,branch='main',repository='alice/alice',exists=True,warnings=['Unsafe HTML or URL found. Remove it before publishing.'])))
    with pytest.raises(HTTPException) as e: await publishing.publish('token',PublishRequest(markdown='<script>x</script>',confirm=True,expected_branch='main',idempotency_key='x'*16))
    assert e.value.status_code==422

@pytest.mark.asyncio
async def test_missing_permission_preview(monkeypatch):
    async def request(self,method,path,**kwargs):
        if path=='/user': return {'id':1,'login':'alice'}
        return {'owner':{'id':1},'permissions':{'push':False},'private':False}
    monkeypatch.setattr(GitHub,'request',request)
    with pytest.raises(HTTPException) as e: await publishing.preview('token','new')
    assert e.value.status_code==403

def test_selected_section_preserves_other_sections():
    from app.services.sections import replace_section
    original='# Title\n\n## About me\n\nOld introduction.\n\n## Tech stack\n\nPython\n\n## Connect\n\nhttps://github.com/alice\n'
    result=replace_section(original,'About me','New introduction.')
    assert result.startswith('# Title\n\n## About me\n')
    assert result[result.index('## Tech stack'):]==original[original.index('## Tech stack'):]
    assert 'Old introduction.' not in result

def test_code_fenced_headings_do_not_split_sections():
    from app.services.sections import replace_section
    original='## About me\n\n```md\n## fake heading\n```\n\n## Tech stack\n\nPython\n'
    result=replace_section(original,'About me','New')
    assert 'fake heading' not in result and '## Tech stack\n\nPython' in result
