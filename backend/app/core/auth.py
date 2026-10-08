import hashlib, secrets
from datetime import datetime, timezone
from cryptography.fernet import Fernet, InvalidToken
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import database
from app.core.config import settings
from app.models.entities import AuthSession, User, GitHubAccount

def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def cipher():
    key=settings().token_encryption_key
    if not key: raise HTTPException(503,'OAuth requires TOKEN_ENCRYPTION_KEY. Generate a Fernet key; see setup documentation.')
    try: return Fernet(key.encode())
    except ValueError: raise HTTPException(503,'TOKEN_ENCRYPTION_KEY must be a valid Fernet key.')

async def current_user(request: Request,db: AsyncSession=Depends(database)):
    token=request.cookies.get('readme_session','')
    session=await db.scalar(select(AuthSession).where(AuthSession.token_hash==digest(token))) if token else None
    if not session or session.expires_at.replace(tzinfo=timezone.utc)<=datetime.now(timezone.utc):
        raise HTTPException(401,'Sign in with GitHub to save or publish.')
    if request.method not in ('GET','HEAD','OPTIONS'):
        if request.headers.get('origin') != settings().frontend_url:
            raise HTTPException(403,'Request origin rejected.')
        if not secrets.compare_digest(request.headers.get('x-csrf-token',''),session.csrf_token):
            raise HTTPException(403,'CSRF token missing or invalid.')
    user=await db.get(User,session.user_id)
    request.state.auth_session=session
    return user

async def user_token(user,db):
    account=await db.scalar(select(GitHubAccount).where(GitHubAccount.user_id==user.id))
    if not account: raise HTTPException(401,'GitHub account is not connected.')
    try: return cipher().decrypt(account.token_ciphertext.encode()).decode()
    except InvalidToken: raise HTTPException(401,'Stored credentials could not be decrypted. Sign in again.')
