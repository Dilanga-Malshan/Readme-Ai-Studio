from typing import Literal
from pydantic import BaseModel, Field, field_validator
import re

USERNAME = re.compile(r'^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$')
def username(value: str):
    if not USERNAME.fullmatch(value):
        raise ValueError('Enter a valid GitHub username (1–39 characters; no consecutive hyphens).')
    return value

class AnalyzeRequest(BaseModel):
    username: str
    _validate = field_validator('username')(username)

class ProfileContent(BaseModel):
    headline: str = Field(max_length=160)
    introduction: str = Field(max_length=1400)
    about: str = Field(max_length=2000)
    skills: list[str] = Field(default_factory=list, max_length=30)
    working_on: str = Field(default='', max_length=1000)
    fun_fact: str = Field(default='', max_length=300)

class StudioConfig(BaseModel):
    template: str = 'professional'
    accent: str = Field(default='38BDF8', pattern=r'^[a-fA-F0-9]{6}$')
    align: Literal['left','center','right'] = 'left'
    badge_style: Literal['flat','flat-square','for-the-badge','plastic'] = 'for-the-badge'
    projects: list[str] = Field(default_factory=list, max_length=12)
    section_order: list[str] = Field(default_factory=lambda: ['about','skills','working','projects','stats','social','fun'])
    sections: dict[str,bool] = Field(default_factory=lambda: dict(about=True,skills=True,working=True,projects=True,stats=False,social=True,fun=False))
    banner_url: str = Field(default='',max_length=1000)
    typing_font: Literal['Fira Code','JetBrains Mono','Roboto Mono'] = 'Fira Code'
    animated_footer: bool = False
    typing: bool = False
    skill_icons: bool = False
    top_languages: bool = False
    streak: bool = False
    visitors: bool = False
    project_layout: Literal['table','list'] = 'table'
    website: str = Field(default='',max_length=500)
    linkedin: str = Field(default='',max_length=500)
    email: str = Field(default='',max_length=200)
    custom_badges: list[str] = Field(default_factory=list,max_length=10)
    footer: bool = True

class GenerateRequest(AnalyzeRequest):
    config: StudioConfig = Field(default_factory=StudioConfig)
    content: ProfileContent | None = None
    use_ai: bool = True

class RewriteRequest(BaseModel):
    username: str
    markdown: str = Field(max_length=60000)
    instruction: str = Field(min_length=1,max_length=1500)
    _validate = field_validator('username')(username)

class ProjectCreate(BaseModel):
    title: str = Field(min_length=1,max_length=120)
    markdown: str = Field(max_length=60000)
    config: dict = Field(default_factory=dict)
class ProjectUpdate(ProjectCreate):
    revision: int = Field(ge=1)
class RenderRequest(BaseModel):
    markdown: str = Field(max_length=60000)
class PublishRequest(RenderRequest):
    expected_sha: str | None = Field(default=None, max_length=64)
    expected_branch: str | None = Field(default=None,max_length=200)
    confirm: bool = False
    create_repository: bool = False
    idempotency_key: str = Field(min_length=16,max_length=80)
    message: str = Field(default='Update profile README with README.AI',max_length=200)
