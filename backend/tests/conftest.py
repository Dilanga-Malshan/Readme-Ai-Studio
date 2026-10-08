import os
os.environ['DATABASE_URL']='sqlite+aiosqlite:///:memory:'
os.environ['REQUEST_LIMIT_PER_MINUTE']='1000'
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine
from app.core.auth import current_user

@pytest.fixture
def client():
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()

@pytest.fixture
def evidence():
    repo=dict(name='toolkit',full_name='alice/toolkit',description='A useful toolkit',html_url='https://github.com/alice/toolkit',language='Python',topics=['tools'],stargazers_count=3,score=40)
    return dict(profile=dict(login='alice',name='Alice',bio='Developer',blog='https://example.com',avatar_url='https://avatars.githubusercontent.com/1',location='Colombo'),repositories=[repo],ranked=[repo],languages=['Python'],notes=[])
