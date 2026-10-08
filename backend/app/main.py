import logging, time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from redis.asyncio import Redis
from app.core.config import settings
from app.core.db import engine, Base, Session
from app.models.entities import Template
from app.services.composer import TEMPLATES
from app.api.routes import router

logger=logging.getLogger('readme-ai')
logging.basicConfig(level=logging.INFO)
_requests=defaultdict(deque)
redis=None

@asynccontextmanager
async def lifespan(app):
    global redis
    # SQLite convenience for development only. PostgreSQL uses Alembic migrations.
    if settings().database_url.startswith('sqlite'):
        async with engine.begin() as connection: await connection.run_sync(Base.metadata.create_all)
    async with Session() as db:
        for t in TEMPLATES:
            if not await db.scalar(select(Template).where(Template.slug==t['id'])):
                db.add(Template(slug=t['id'],data=t))
        await db.commit()
    if settings().redis_url: redis=Redis.from_url(settings().redis_url)
    yield
    if redis: await redis.aclose()
    await engine.dispose()

app=FastAPI(title='README.AI API',version='1.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[settings().frontend_url],allow_credentials=True,allow_methods=['GET','POST','PATCH','PUT','OPTIONS'],allow_headers=['Content-Type','X-CSRF-Token'])

@app.exception_handler(HTTPException)
async def http_error(request,error):
    return JSONResponse({'error':{'message':error.detail,'status':error.status_code}},status_code=error.status_code,headers=error.headers)
@app.exception_handler(RequestValidationError)
async def validation_error(request,error):
    messages=[{'field':'.'.join(str(x) for x in e['loc']),'message':e['msg']} for e in error.errors()]
    return JSONResponse({'error':{'message':'Request validation failed.','details':messages,'status':422}},status_code=422)

@app.middleware('http')
async def security(request: Request,call_next):
    start=time.monotonic()
    if request.method!='OPTIONS':
        key=request.client.host if request.client else 'unknown'
        if redis:
            bucket=f'limit:{key}:{int(time.time()//60)}'
            count=await redis.incr(bucket)
            if count==1: await redis.expire(bucket,65)
        else:
            now=time.monotonic();q=_requests[key]
            while q and q[0]<now-60: q.popleft()
            q.append(now);count=len(q)
            if len(_requests)>10000:
                for k in list(_requests):
                    if not _requests[k] or _requests[k][-1]<now-60: _requests.pop(k,None)
        if count>settings().request_limit_per_minute:
            return JSONResponse({'error':{'message':'Too many requests. Try again in a minute.','status':429}},status_code=429,headers={'Retry-After':'60'})
        # Bound actual streamed bodies, not just the untrusted Content-Length header.
        total=0;chunks=[]
        async for chunk in request.stream():
            total+=len(chunk)
            if total>262144: return JSONResponse({'error':{'message':'Request body exceeds 256 KiB.','status':413}},status_code=413)
            chunks.append(chunk)
        request._body=b''.join(chunks)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['Cache-Control']='no-store'
    logger.info('%s %s %s %.0fms',request.method,request.url.path,response.status_code,(time.monotonic()-start)*1000)
    return response

app.include_router(router)
