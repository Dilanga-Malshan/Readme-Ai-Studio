import { Component, computed, inject, signal, ViewChild } from '@angular/core';
import { LucideSparkles } from '@lucide/angular';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from './api.service';
import { EditorComponent } from './editor.component';
import { safeMarkdown } from './markdown';
import { Analysis, Content, Config, Draft, defaultConfig, emptyContent, templateList, validUsername, downloadFile, hasManualChanges } from './types';
@Component({standalone:true,imports:[FormsModule,EditorComponent,LucideSparkles],templateUrl:'./studio.component.html'})
export class StudioComponent{
 api=inject(ApiService);route=inject(ActivatedRoute);@ViewChild(EditorComponent)editor?:EditorComponent;
 templates=templateList;username='';analysis=signal<Analysis|null>(null);content:Content={...emptyContent,skills:[]};config:Config=defaultConfig();
 markdown=signal('');rendered=computed(()=>safeMarkdown(this.markdown()));busy=signal('');error=signal('');notice=signal('');aiEnabled=false;
 sectionToRegenerate='About me';controlTab='profile';viewTab='preview';mobile=false;previewLight=false;zoom=100;assistant='';proposal=signal<{markdown:string;explanation:string;notes?:string[];content?:Content}|null>(null);
 lastGenerated='';warnings=signal<string[]>([]);localVersions: {markdown:string;at:string}[]=[];cloudProjects:any[]=[];cloudId='';cloudRevision=1;
 showHistory=false;showCloud=false;showShare=false;shareUrl='';shareConsent=false;variants=signal<any[]>([]);publishPreview=signal<any|null>(null);publishConfirmed=false;createRepo=false;publishKey='';source='';
 sectionLabels:Record<string,string>={about:'About me',skills:'Tech stack',working:'Working on',projects:'Featured projects',stats:'GitHub activity',social:'Connect',fun:'Beyond code'};
 constructor(){
  try{const draft=JSON.parse(localStorage.getItem('readme-draft')||'null') as Draft|null;if(draft){this.username=draft.username;this.config={...defaultConfig(),...draft.config};this.content=draft.content;this.markdown.set(draft.markdown);this.analysis.set(draft.analysis);this.lastGenerated=draft.lastGenerated||'';}this.localVersions=JSON.parse(localStorage.getItem('readme-versions')||'[]');}catch{this.notice.set('Your local draft could not be restored. Start a new profile.');}
  const params=this.route.snapshot.queryParamMap;this.username=params.get('username')||this.username;const template=params.get('template');if(template)this.selectTemplate(template);
  this.api.request('/health').then(h=>{this.aiEnabled=h.ai_configured;}).catch(()=>{});
 }
 async run(label:string,action:()=>Promise<void>){if(this.busy())return;this.busy.set(label);this.error.set('');try{await action();}catch(e){this.error.set((e as Error).message);}finally{this.busy.set('');}}
 async analyze(){if(!validUsername(this.username.trim())){this.error.set('Enter a valid GitHub username.');return;}await this.run('Analyzing public repositories',async()=>{
   const data=await this.api.request<Analysis>('/github/analyze','POST',{username:this.username.trim()});this.analysis.set(data);this.username=data.profile.login;
   this.content={headline:data.profile.bio||'Developer on GitHub',introduction:data.profile.bio||'Welcome to my profile. Explore my public projects below.',about:`I’m ${data.profile.name||data.profile.login}.`+(data.profile.location?` Based in ${data.profile.location}.`:''),skills:[...data.languages],working_on:'',fun_fact:''};
   this.config.projects=data.ranked.slice(0,4).map(r=>r.name);this.config.website=data.profile.blog||'';this.persist();this.notice.set(`Analyzed ${data.repositories.length} public repositories. Verify inferred skills before generation.`);
  });}
 async generate(useExisting=false){if(!this.analysis()){this.error.set('Analyze a GitHub profile first.');return;}await this.run('Composing your README',async()=>{
  const result=await this.api.request('/ai/generate','POST',{username:this.analysis()!.profile.login,config:this.config,content:useExisting?this.content:null,use_ai:useExisting?false:this.aiEnabled});
  this.warnings.set(result.warnings);this.source=result.source;
  if(hasManualChanges(this.markdown(),this.lastGenerated)){this.proposal.set({markdown:result.markdown,explanation:'Visual controls generated a new version. Review it before replacing your manual edits.',content:result.content});}
  else{this.content=result.content;this.lastGenerated=result.markdown;this.applyMarkdown(result.markdown);}
  this.notice.set('Generated content is a proposal. Verify facts, skills, links, and project descriptions.');
 });}
 selectTemplate(id:string){const t=this.templates.find(t=>t.id===id);if(t){this.config.template=id;this.config.accent=t.accent;this.config.typing=id==='neon';this.persist();}}
 updateConfig(){this.persist();}
 toggleProject(name:string,checked:boolean){this.config.projects=checked?[...this.config.projects,name]:this.config.projects.filter(n=>n!==name);this.persist();}
 skills(value:string){this.content.skills=value.split(',').map(s=>s.trim()).filter(Boolean).slice(0,30);this.persist();}
 badges(value:string){this.config.custom_badges=value.split(',').map(s=>s.trim()).filter(Boolean).slice(0,10);this.persist();}
 moveSection(index:number,direction:number){const next=index+direction;if(next<0||next>=this.config.section_order.length)return;const list=[...this.config.section_order];[list[index],list[next]]=[list[next],list[index]];this.config.section_order=list;this.persist();}
 dragIndex=-1;dragStart(i:number){this.dragIndex=i;}dropSection(i:number,e:DragEvent){e.preventDefault();if(this.dragIndex<0)return;const list=[...this.config.section_order];const [item]=list.splice(this.dragIndex,1);list.splice(i,0,item);this.config.section_order=list;this.dragIndex=-1;this.persist();}
 edit(value:string){this.markdown.set(value);this.publishPreview.set(null);this.persist();}
 applyMarkdown(value:string){if(this.markdown()&&this.markdown()!==value)this.snapshot();this.edit(value);}
 snapshot(){this.localVersions.unshift({markdown:this.markdown(),at:new Date().toISOString()});this.localVersions=this.localVersions.slice(0,30);try{localStorage.setItem('readme-versions',JSON.stringify(this.localVersions));}catch{this.notice.set('Local history storage is full. Download a backup.');}}
 persist(){try{localStorage.setItem('readme-draft',JSON.stringify({lastGenerated:this.lastGenerated,username:this.username,markdown:this.markdown(),content:this.content,config:this.config,analysis:this.analysis()}));}catch{this.notice.set('Local autosave is unavailable. Download your README to keep it.');}}
 applyProposal(){const p=this.proposal();if(!p)return;this.applyMarkdown(p.markdown);this.lastGenerated=p.markdown;if(p.content)this.content=p.content;this.persist();this.proposal.set(null);this.notice.set('Proposed changes applied. The previous version is in history.');}
 restore(version:{markdown:string}){this.applyMarkdown(version.markdown);this.showHistory=false;this.notice.set('Version restored.');}
 async copy(){try{await navigator.clipboard.writeText(this.markdown());this.notice.set('Markdown copied.');}catch{this.error.set('Clipboard access failed. Select and copy the editor text, or download it.');}}
 download(){downloadFile(this.markdown(),'README.md');this.notice.set('README.md downloaded.');}
 exportPreview(){const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>README preview</title><body>${this.rendered()}</body></html>`;downloadFile(html,'readme-preview.html','text/html');}
 importFile(event:Event){const input=event.target as HTMLInputElement;const file=input.files?.[0];if(!file)return;if(file.size>60000){this.error.set('Import a Markdown file smaller than 60 KB.');return;}file.text().then(v=>{this.applyMarkdown(v);this.notice.set('Imported README. Manual edits are preserved until you approve regeneration.');});input.value='';}
 async ask(instruction=this.assistant){if(!this.markdown()){this.error.set('Generate or import a README first.');return;}await this.run('Preparing AI suggestions',async()=>{
   const data=await this.api.request('/ai/chat','POST',{username:this.analysis()?.profile.login||this.username,markdown:this.markdown(),instruction});this.proposal.set(data);this.warnings.set(data.warnings||[]);
 });}


 async regenerateSection(){if(!this.markdown())return;await this.run('Regenerating one section',async()=>{const proposal=await this.api.request('/ai/regenerate-section?section='+encodeURIComponent(this.sectionToRegenerate),'POST',{username:this.analysis()?.profile.login||this.username,markdown:this.markdown(),instruction:this.assistant||'Improve clarity while preserving verified facts.'});this.proposal.set(proposal);});}
 downloadBanner(){const title=this.analysis()?.profile.name||this.username||'Hello, world.';const query=new URLSearchParams({title,subtitle:this.content.headline||'Your code. Your story.',accent:this.config.accent});const a=document.createElement('a');a.href='/api/v1/banners/svg?'+query;a.download='banner.svg';a.click();}
 async generateVariants(){if(!this.analysis())return;await this.run('Generating three style variants',async()=>{const result=await this.api.request('/ai/variants','POST',{username:this.analysis()!.profile.login,config:this.config,content:this.content,use_ai:false});this.variants.set(result.variants);});}
 chooseVariant(v:any){this.proposal.set({markdown:v.markdown,content:v.content,explanation:`Review the ${v.name} variant before applying it.`});this.variants.set([]);}
 async createShare(){if(!this.shareConsent)return;await this.run('Creating read-only share link',async()=>{const r=await this.api.request(`/readmes/${this.cloudId}/share`,'POST',{enabled:true});this.shareUrl=r.url;this.notice.set('Share snapshot created. Anyone with the link can view it for seven days.');});}
 async revokeShare(){await this.run('Revoking share link',async()=>{await this.api.request(`/readmes/${this.cloudId}/share`,'POST',{enabled:false});this.shareUrl='';this.notice.set('All share links for this draft are revoked.');});}
 async copyShare(){try{await navigator.clipboard.writeText(this.shareUrl);this.notice.set('Share link copied.');}catch{this.error.set('Clipboard unavailable; copy the link shown in the dialog.');}}
 async saveCloud(){await this.run('Saving cloud draft',async()=>{
   const body={title:`${this.username} — ${this.config.template}`,markdown:this.markdown(),config:{...this.config,content:this.content,username:this.username}};
   const result=await this.api.request(this.cloudId?`/readmes/${this.cloudId}`:'/readmes',this.cloudId?'PATCH':'POST',this.cloudId?{...body,revision:this.cloudRevision}:body);this.cloudId=result.id;this.cloudRevision=result.revision;this.notice.set('Cloud draft saved with version history.');
 });}
 async loadCloud(){await this.run('Loading cloud drafts',async()=>{this.cloudProjects=await this.api.request('/readmes');this.showCloud=true;});}
 async openCloud(p:any){this.applyMarkdown(p.markdown);this.config={...defaultConfig(),...p.config};this.content=p.config.content||{...emptyContent};this.username=p.config.username||this.username;this.analysis.set(null);this.cloudId=p.id;this.cloudRevision=p.revision;this.lastGenerated='';this.showCloud=false;this.persist();this.notice.set('Cloud draft loaded. Analyze the username to refresh GitHub data.');}
 async cloudHistory(){await this.run('Loading version history',async()=>{const data=await this.api.request(`/readmes/${this.cloudId}/versions`);this.localVersions=data.map((v:any)=>({markdown:v.markdown,at:v.created_at}));this.showHistory=true;});}
 async beginPublish(){if(!this.markdown())return;await this.run('Comparing with GitHub',async()=>{this.publishPreview.set(await this.api.request('/github/publish-preview','POST',{markdown:this.markdown()}));this.publishConfirmed=false;this.createRepo=false;this.publishKey=crypto.randomUUID();});}
 async publish(){const p=this.publishPreview();if(!p||!this.publishConfirmed)return;await this.run('Publishing README to GitHub',async()=>{
   const result=await this.api.request('/github/publish','POST',{markdown:p.proposed,expected_sha:p.sha,expected_branch:p.branch,confirm:true,create_repository:this.createRepo,idempotency_key:this.publishKey});this.publishPreview.set(null);this.notice.set(`Published to ${result.repository}. Commit: ${result.commit_sha.slice(0,7)}`);
 });}
 quality=computed(()=>{const md=this.markdown();return [{label:'A clear introduction',ok:/^#|<h1/i.test(md)},{label:'Projects linked',ok:/github\.com\/[\w-]+\/[\w.-]+/.test(md)},{label:'Skills included',ok:/tech stack|skills/i.test(md)},{label:'Contact or social links',ok:/mailto:|linkedin\.com|## Connect/.test(md)},{label:'Readable length',ok:md.length>100&&md.length<12000},{label:'No unsafe HTML',ok:!/<script|javascript:|onerror=/i.test(md)}];});
 imageError(event:Event){const img=event.target as HTMLImageElement;if(img.tagName==='IMG'){img.classList.add('image-unavailable');img.setAttribute('title',`${img.alt||'External image'} is unavailable`);}}
}
