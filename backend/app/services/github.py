import asyncio, time, math
from datetime import datetime, timezone
import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.contracts import username

class GitHub:
    def __init__(self, token: str = ''):
        self.token = token
    async def request(self, method, path, **kwargs):
        headers = {'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        try:
            async with httpx.AsyncClient(base_url='https://api.github.com', timeout=20, follow_redirects=False) as client:
                r = await client.request(method,path,headers=headers,**kwargs)
        except httpx.RequestError:
            raise HTTPException(502,'GitHub is unreachable. Try again later.')
        if r.status_code == 404:
            raise HTTPException(404,'GitHub resource was not found or access is unavailable.')
        if r.status_code in (403,429):
            raise HTTPException(429 if r.headers.get('x-ratelimit-remaining') == '0' or r.status_code == 429 else 403,
                'GitHub rate limit reached.' if r.headers.get('x-ratelimit-remaining') == '0' else 'GitHub permissions are insufficient.',
                headers={'Retry-After':r.headers.get('retry-after','60')})
        if r.status_code in (409,422):
            raise HTTPException(409,'GitHub changed since the preview. Refresh the diff and try again.')
        if r.status_code == 401:
            raise HTTPException(401,'GitHub authentication expired; sign in again.')
        if r.status_code >= 400:
            raise HTTPException(502,'GitHub rejected this request.')
        return r.json() if r.content else {}
    async def profile(self, login):
        username(login)
        p = await self.request('GET',f'/users/{login}')
        return {k:p.get(k) for k in ['login','name','bio','location','blog','avatar_url','html_url','public_repos','followers','following','company']}
    async def repositories(self, login):
        username(login)
        repos = []
        for page in range(1,101):
            data = await self.request('GET',f'/users/{login}/repos',params={'per_page':100,'page':page,'sort':'updated','type':'owner'})
            repos.extend(r for r in data if not r.get('private'))
            if len(data)<100:
                break
        else:
            raise HTTPException(422,'More than 10,000 repositories. Analyze a smaller account.')
        return [{k:r.get(k) for k in ['name','full_name','description','html_url','language','topics','stargazers_count','forks_count','updated_at','size','fork','archived','default_branch']} for r in repos]

_cache: dict[str,tuple[float,dict]] = {}
_lock = asyncio.Lock()
async def analyze(login):
    username(login)
    key = login.lower()
    async with _lock:
        cached = _cache.get(key)
        if cached and cached[0]>time.time():
            return cached[1]
    gh = GitHub(settings().github_token)
    profile,repos = await asyncio.gather(gh.profile(login),gh.repositories(login))
    eligible = [r for r in repos if not r['fork'] and not r['archived']]
    def score(r):
        try:
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(r['updated_at'].replace('Z','+00:00'))).days
        except (ValueError,TypeError): age=365
        return round((20 if r['description'] else 0)+(10 if r['language'] else 0)+min(len(r['topics'] or [])*3,12)+max(0,20-age/30)+min(math.log1p(r['stargazers_count'] or 0)*3,12)+min(math.log1p(r['size'] or 0),10),2)
    eligible.sort(key=score,reverse=True)
    # README existence is verified for shortlisted repositories, without executing content.
    async def enrich(r):
        try:
            await gh.request('GET',f"/repos/{r['full_name']}/readme")
            r['has_readme'] = True
        except HTTPException as e:
            if e.status_code != 404: raise
            r['has_readme'] = False
        r['score'] = score(r)+(8 if r['has_readme'] else 0)
        return r
    short = []
    for start in range(0,min(12,len(eligible)),4):
        short.extend(await asyncio.gather(*(enrich(dict(r)) for r in eligible[start:start+4])))
    short.sort(key=lambda r:r['score'],reverse=True)
    languages = sorted({r['language'] for r in eligible if r['language']})
    result = dict(profile=profile,repositories=repos,ranked=short,languages=languages,
        notes=['Ranking uses metadata and documentation; stars do not measure professional ability.',
               'Pinned repositories require an authorized GraphQL integration and are not inferred.',
               'Languages are inferred from primary repository languages. Verify skills before publishing.'])
    async with _lock:
        if len(_cache)>200: _cache.clear()
        _cache[key]=(time.time()+300,result)
    return result
