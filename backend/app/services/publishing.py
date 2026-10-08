import base64, difflib, hashlib
from fastapi import HTTPException
from app.services.github import GitHub
from app.services.composer import validate

async def preview(token,markdown):
    gh=GitHub(token); account=await gh.request('GET','/user'); login=account['login']
    repo=f'{login}/{login}'; existing=''; sha=None; branch=None; exists=True
    try:
        info=await gh.request('GET',f'/repos/{repo}')
        if info['owner']['id']!=account['id'] or not info.get('permissions',{}).get('push') or info.get('private'):
            raise HTTPException(403,'The profile repository must be public, owned by you and writable.')
        branch=info['default_branch']
    except HTTPException as e:
        if e.status_code!=404: raise
        exists=False
    if exists:
        try:
            file=await gh.request('GET',f'/repos/{repo}/contents/README.md',params={'ref':branch})
            if file.get('type')!='file': raise HTTPException(409,'README.md is not a regular file.')
            if file.get('size',0)>60000: raise HTTPException(422,'Existing README is too large for safe editing.')
            existing=base64.b64decode(file['content']).decode('utf-8');sha=file['sha']
        except HTTPException as e:
            if e.status_code!=404: raise
    return dict(repository=repo,exists=exists,sha=sha,branch=branch,existing=existing,proposed=markdown,
        diff=''.join(difflib.unified_diff(existing.splitlines(True),markdown.splitlines(True),fromfile='README.md (current)',tofile='README.md (proposed)')),
        warnings=validate(markdown))

async def publish(token,body):
    if not body.confirm: raise HTTPException(422,'Review the exact diff and explicitly confirm publishing.')
    current=await preview(token,body.markdown)
    if current['sha']!=body.expected_sha or current['branch']!=body.expected_branch:
        raise HTTPException(409,'The README or branch changed since your preview. Review a new diff.')
    unsafe=[w for w in current['warnings'] if w.startswith('Unsafe')]
    if unsafe: raise HTTPException(422,unsafe[0])
    gh=GitHub(token)
    if not current['exists']:
        if not body.create_repository: raise HTTPException(422,'Confirm creating the missing public profile repository.')
        login=current['repository'].split('/')[0]
        info=await gh.request('POST','/user/repos',json={'name':login,'private':False,'description':'My GitHub profile README','auto_init':True})
        current['branch']=info['default_branch']
    payload={'message':body.message,'content':base64.b64encode(body.markdown.encode()).decode(),'branch':current['branch']}
    if current['sha']: payload['sha']=current['sha']
    result=await gh.request('PUT',f"/repos/{current['repository']}/contents/README.md",json=payload)
    return dict(repository=current['repository'],commit_sha=result['commit']['sha'],url=result['content']['html_url'],status='published')
