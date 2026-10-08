import html, re
from urllib.parse import quote, urlparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from markdown_it import MarkdownIt
import bleach
from app.schemas.contracts import ProfileContent, StudioConfig

TEMPLATES = [
 dict(id='minimal',name='Minimal Developer',subtitle='Quiet confidence. Just the essentials.',accent='94A3B8',emoji=''),
 dict(id='professional',name='Professional Engineer',subtitle='A clear story for your next opportunity.',accent='38BDF8',emoji='👋'),
 dict(id='neon',name='Futuristic Neon',subtitle='A bold signal in a sea of profiles.',accent='C8F77C',emoji='⚡'),
 dict(id='ai',name='AI / ML Engineer',subtitle='Put your intelligence work in focus.',accent='A78BFA',emoji='🧠'),
 dict(id='fullstack',name='Full-Stack Developer',subtitle='Show the whole system, front to back.',accent='38BDF8',emoji='🛠️'),
 dict(id='creative',name='Creative Portfolio',subtitle='A little personality. A lot of craft.',accent='F472B6',emoji='✨')]

def safe_url(value):
    if not value: return ''
    value=value.strip()
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',value) and not value.startswith(('https://','http://')): return ''
    if not value.startswith(('https://','http://')): value='https://'+value
    u=urlparse(value)
    return value if u.scheme in ('https','http') and u.hostname and not u.username and not u.password else ''

def text(value):
    # GitHub metadata is text, never executable HTML or Markdown directives.
    value=html.escape(str(value or ''),quote=True)
    return re.sub(r'([\\`*_{}\[\]()#+!|>])',r'\\\1',value)

ICON_IDS={'Python':'python','TypeScript':'ts','JavaScript':'js','Java':'java','HTML':'html','CSS':'css','C++':'cpp','C':'c','Go':'go','Rust':'rust','Dart':'dart','Ruby':'ruby','PHP':'php','Swift':'swift','Kotlin':'kotlin','FastAPI':'fastapi','Angular':'angular','PostgreSQL':'postgres','Docker':'docker','React':'react','Git':'git'}

def fallback_content(data):
    p=data['profile']
    return ProfileContent(headline=p.get('bio') or 'Developer on GitHub',introduction=p.get('bio') or f"Welcome to my profile. Explore my public projects below.",about=f"I'm {p.get('name') or p['login']}."+(f" Based in {p['location']}." if p.get('location') else ''),skills=data['languages'],working_on='')

def compose(data,content,config):
    template=next((t for t in TEMPLATES if t['id']==config.template),TEMPLATES[1])
    p=data['profile']; login=p['login']; color=config.accent
    header=f'<h1 align="{config.align}">{template["emoji"]} {html.escape(p.get("name") or login)}</h1>\n<p align="{config.align}">{html.escape(content.headline)}</p>'
    banner=safe_url(config.banner_url)
    if banner.startswith('https://'): header=f'![Profile banner]({quote(banner,safe=":/?&=#%")})\n\n'+header
    if config.typing:
        header+=f'\n\n![Animated headline](https://readme-typing-svg.demolab.com?font={quote(config.typing_font,safe="")}&color={color}&lines={quote(content.headline,safe="")})'
    sections={}
    sections['about']='## About me\n\n'+text(content.introduction)+'\n\n'+text(content.about)
    badges=[]
    for skill in content.skills+config.custom_badges:
        badges.append(f'![{html.escape(skill,quote=True)}](https://img.shields.io/badge/{quote(skill.replace("-","--").replace("_","__"),safe="")}-{color}?style={config.badge_style}&logoColor=white)')
    if config.skill_icons:
        ids=[ICON_IDS[s] for s in content.skills if s in ICON_IDS]
        if ids: badges.insert(0,f'![Technology icons](https://skillicons.dev/icons?i={",".join(ids)})\n')
    sections['skills']='## Tech stack\n\n'+' '.join(badges)
    sections['working']='## What I’m working on\n\n'+text(content.working_on) if content.working_on else ''
    selected=[r for r in data['repositories'] if r['name'] in config.projects] if config.projects else data['ranked'][:4]
    if config.project_layout=='table':
        projects='| Project | Description | Language |\n| --- | --- | --- |\n'+'\n'.join(f'| [{text(r["name"])}]({r["html_url"]}) | {text(r["description"] or "Public GitHub repository").replace(chr(10)," ")} | {text(r["language"] or "—")} |' for r in selected)
    else:
        projects='\n'.join(f'- **[{text(r["name"])}]({r["html_url"]})** — {text(r["description"] or "Public GitHub repository")}' for r in selected)
    sections['projects']='## Featured projects\n\n'+projects if selected else ''
    stats=[f'![GitHub statistics](https://github-readme-stats.vercel.app/api?username={login}&show_icons=true&theme=transparent&title_color={color}&icon_color={color})']
    if config.top_languages: stats.append(f'![Top languages](https://github-readme-stats.vercel.app/api/top-langs/?username={login}&layout=compact&theme=transparent)')
    if config.streak: stats.append(f'![Contribution streak](https://streak-stats.demolab.com?user={login}&theme=transparent)')
    sections['stats']='## GitHub activity\n\n'+'\n\n'.join(stats)
    socials=[f'[GitHub](https://github.com/{login})']
    for label,value in [('Website',config.website or p.get('blog')),('LinkedIn',config.linkedin)]:
        url=safe_url(value)
        if url: socials.append(f'[{label}]({quote(url,safe=":/?&=#%")})')
    if config.email and re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+',config.email):
        socials.append(f'[Email](mailto:{quote(config.email,safe="@.")})')
    sections['social']='## Connect\n\n'+' · '.join(socials)
    sections['fun']='## Beyond code\n\n'+text(content.fun_fact) if content.fun_fact else ''
    order=list(dict.fromkeys(config.section_order+list(sections)))
    parts=[header]+[sections[k] for k in order if k in sections and config.sections.get(k,False) and sections[k]]
    if config.visitors: parts.append(f'![Profile views](https://komarev.com/ghpvc/?username={login}&color={color})')
    if config.animated_footer: parts.append(f'![Thank you for visiting](https://readme-typing-svg.demolab.com?font={quote(config.typing_font,safe="")}&color={color}&lines=Thanks+for+visiting!)')
    if config.footer: parts.append('---\n\n<sub>Built with care · README.AI</sub>')
    env=Environment(loader=FileSystemLoader(Path(__file__).parent.parent/'templates'),autoescape=False)
    return env.get_template('readme.md.j2').render(parts=parts).strip()+'\n'

TAGS={'p','br','hr','h1','h2','h3','h4','h5','h6','a','img','strong','em','del','s','blockquote','code','pre','ul','ol','li','table','thead','tbody','tr','th','td','div','span','sub','sup','details','summary'}
def attr(tag,name,value):
    if name in ('alt','title'): return True
    if name=='align' and value in ('left','center','right'): return True
    if name in ('width','height') and re.fullmatch(r'\d{1,4}',value): return True
    if (tag,name) in (('a','href'),('img','src')):
        u=urlparse(value)
        if tag=='img': return u.scheme=='https' and bool(u.hostname) and not u.username
        return u.scheme in ('https','http','mailto') and (bool(u.hostname) or u.scheme=='mailto')
    return False

def render(markdown):
    raw=MarkdownIt('commonmark',{'html':True}).enable('table').render(markdown)
    return bleach.clean(raw,tags=TAGS,attributes=attr,protocols=['https','http','mailto'],strip=True)

def validate(markdown):
    warnings=[]
    if re.search(r'<\s*(script|iframe|object|embed|style)|\bon\w+\s*=|javascript:',markdown,re.I):
        warnings.append('Unsafe HTML or URL found. Remove it before publishing.')
    if len(markdown)>25000: warnings.append('README is long; consider shortening it.')
    if '![ ](' in markdown or '![](' in markdown: warnings.append('Add descriptive alternative text to images.')
    if 'github-readme-stats' in markdown or 'demolab.com' in markdown: warnings.append('Third-party widgets can be unavailable. Their alt text is the fallback.')
    return warnings
