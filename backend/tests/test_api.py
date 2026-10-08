from unittest.mock import AsyncMock
import asyncio
import pytest
from fastapi import HTTPException
from app.main import app
from app.core.auth import current_user
from app.core.db import Session
from app.models.entities import User
from app.api import routes
from app.services import publishing
from app.ai import engine

@pytest.fixture
def signed_client(client):
    async def seed():
        async with Session() as db:
            user=User(github_id='1',login='alice');db.add(user);await db.commit();return user
    user=asyncio.run(seed())
    app.dependency_overrides[current_user]=lambda:user
    return client

def test_invalid_request(client):
    r=client.post('/api/v1/github/analyze',json={'username':'../x'})
    assert r.status_code==422 and 'error' in r.json()
def test_render_without_login(client):
    assert client.post('/api/v1/readmes/render',json={'markdown':'# Hello'}).json()['html'].startswith('<h1>')
def test_cloud_requires_login(client):
    assert client.post('/api/v1/readmes',json={'title':'x','markdown':'a'}).status_code==401
def test_oauth_state_mismatch(client):
    assert client.get('/api/v1/auth/github/callback?code=x&state=y').status_code==400
def test_missing_ai_key(client):
    r=client.post('/api/v1/ai/rewrite',json={'username':'alice','markdown':'# hi','instruction':'shorten'})
    assert r.status_code==503
def test_generation_without_ai(client,evidence,monkeypatch):
    monkeypatch.setattr(routes,'analyze',AsyncMock(return_value=evidence))
    r=client.post('/api/v1/ai/generate',json={'username':'alice','use_ai':False})
    assert r.status_code==200 and 'toolkit' in r.json()['markdown']
def test_mock_ai_generation(client,evidence,monkeypatch):
    from app.core.config import settings
    cfg=settings();monkeypatch.setattr(cfg,'openai_api_key','test-key')
    monkeypatch.setattr(routes,'analyze',AsyncMock(return_value=evidence))
    monkeypatch.setattr(engine,'generate',AsyncMock(return_value=routes.fallback_content(evidence)))
    r=client.post('/api/v1/ai/generate',json={'username':'alice','use_ai':True})
    assert r.status_code==200 and r.json()['source'].startswith('AI proposal')
def test_cloud_revision_conflict(signed_client):
    c=signed_client
    p=c.post('/api/v1/readmes',json={'title':'draft','markdown':'# original'}).json()
    r=c.patch(f"/api/v1/readmes/{p['id']}",json={'title':'draft','markdown':'# new','revision':1})
    assert r.status_code==200 and r.json()['revision']==2
    stale=c.patch(f"/api/v1/readmes/{p['id']}",json={'title':'draft','markdown':'# stale','revision':1})
    assert stale.status_code==409
    assert c.get(f"/api/v1/readmes/{p['id']}").json()['markdown']=='# new'
    assert len(c.get(f"/api/v1/readmes/{p['id']}/versions").json())==2
    exported=c.get(f"/api/v1/readmes/{p['id']}/export")
    assert exported.text=='# new' and 'README.md' in exported.headers['content-disposition']
def test_unknown_project(signed_client):
    assert signed_client.get('/api/v1/readmes/unknown').status_code==404
def test_publish_idempotency(signed_client,monkeypatch):
    monkeypatch.setattr(routes,'user_token',AsyncMock(return_value='fake'))
    action=AsyncMock(return_value={'status':'published','commit_sha':'abc','url':'https://github.com/alice/alice','repository':'alice/alice'})
    monkeypatch.setattr(publishing,'publish',action)
    body={'markdown':'new','idempotency_key':'a'*20,'confirm':True}
    first=signed_client.post('/api/v1/github/publish',json=body)
    second=signed_client.post('/api/v1/github/publish',json=body)
    assert first.status_code==200 and second.json()==first.json() and action.call_count==1
    assert signed_client.post('/api/v1/github/publish',json={**body,'markdown':'changed'}).status_code==409

def test_failed_publish_recorded(signed_client,monkeypatch):
    monkeypatch.setattr(routes,'user_token',AsyncMock(return_value='fake'))
    monkeypatch.setattr(publishing,'publish',AsyncMock(side_effect=HTTPException(403,'Missing permissions')))
    assert signed_client.post('/api/v1/github/publish',json={'markdown':'new','idempotency_key':'b'*20,'confirm':True}).status_code==403

def test_request_body_limit(client):
    r=client.post('/api/v1/readmes/render',content='x'*262145)
    assert r.status_code==413

def test_share_snapshot_privacy_and_revocation(signed_client):
    c=signed_client
    p=c.post('/api/v1/readmes',json={'title':'private draft','markdown':'# Snapshot'}).json()
    shared=c.post(f"/api/v1/readmes/{p['id']}/share",json={'enabled':True}).json()
    token=shared['url'].split('/')[-1]
    assert c.get(f'/api/v1/shared/{token}').json()['markdown']=='# Snapshot'
    c.patch(f"/api/v1/readmes/{p['id']}",json={'title':'private draft','markdown':'# Not shared yet','revision':1})
    assert c.get(f'/api/v1/shared/{token}').json()['markdown']=='# Snapshot'
    c.post(f"/api/v1/readmes/{p['id']}/share",json={'enabled':False})
    assert c.get(f'/api/v1/shared/{token}').status_code==404

def test_variants_use_verified_same_content(client,evidence,monkeypatch):
    monkeypatch.setattr(routes,'analyze',AsyncMock(return_value=evidence))
    r=client.post('/api/v1/ai/variants',json={'username':'alice','use_ai':False})
    assert r.status_code==200
    variants=r.json()['variants']
    assert len(variants)==3 and len({v['markdown'] for v in variants})==3
    assert all('toolkit' in v['markdown'] for v in variants)

def test_banner_escapes_untrusted_text(client):
    r=client.get('/api/v1/banners/svg',params={'title':'<script>alert(1)</script>'})
    assert r.status_code==200 and '<script>' not in r.text and '&lt;script&gt;' in r.text
    assert client.get('/api/v1/banners/svg?accent=oops').status_code==422

def test_atomic_ai_quota(client,evidence,monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings(),'openai_api_key','test-key')
    monkeypatch.setattr(settings(),'ai_daily_limit',1)
    monkeypatch.setattr(routes,'analyze',AsyncMock(return_value=evidence))
    monkeypatch.setattr(engine,'generate',AsyncMock(return_value=routes.fallback_content(evidence)))
    assert client.post('/api/v1/ai/generate',json={'username':'alice'}).status_code==200
    assert client.post('/api/v1/ai/generate',json={'username':'alice'}).status_code==429

def test_other_owner_cannot_read_or_share(signed_client):
    c=signed_client;p=c.post('/api/v1/readmes',json={'title':'mine','markdown':'private'}).json()
    app.dependency_overrides[current_user]=lambda:User(id='another-user',github_id='2',login='bob')
    assert c.get(f"/api/v1/readmes/{p['id']}").status_code==404
    assert c.post(f"/api/v1/readmes/{p['id']}/share",json={'enabled':True}).status_code==404

def test_oauth_callback_session_and_csrf(client,monkeypatch):
    import secrets
    from datetime import datetime,timedelta,timezone
    from cryptography.fernet import Fernet
    from app.core.config import settings
    from app.core.auth import digest
    from app.models.entities import OAuthState
    from app.services.github import GitHub
    cfg=settings();monkeypatch.setattr(cfg,'token_encryption_key',Fernet.generate_key().decode())
    state=secrets.token_urlsafe(32)
    async def seed():
        async with Session() as db:
            db.add(OAuthState(state_hash=digest(state),verifier='verifier',expires_at=datetime.now(timezone.utc)+timedelta(minutes=10)));await db.commit()
    asyncio.run(seed())
    class Exchange:
        def json(self):return {'access_token':'fake-provider-token'}
    monkeypatch.setattr(routes.httpx.AsyncClient,'post',AsyncMock(return_value=Exchange()))
    monkeypatch.setattr(GitHub,'request',AsyncMock(return_value={'id':9,'login':'alice'}))
    client.cookies.set('oauth_state',state)
    r=client.get('/api/v1/auth/github/callback',params={'state':state,'code':'code'},follow_redirects=False)
    assert r.status_code==307 and 'HttpOnly' in r.headers['set-cookie']
    session=client.get('/api/v1/auth/me').json()
    assert session['login']=='alice'
    assert client.post('/api/v1/auth/logout').status_code==403
    assert client.post('/api/v1/auth/logout',headers={'Origin':cfg.frontend_url,'X-CSRF-Token':'wrong'}).status_code==403
    assert client.post('/api/v1/auth/logout',headers={'Origin':cfg.frontend_url,'X-CSRF-Token':session['csrf_token']}).status_code==204
    assert client.get('/api/v1/auth/me').status_code==401
    assert client.get('/api/v1/auth/github/callback',params={'state':state,'code':'code'}).status_code==400
