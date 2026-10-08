import {Component, inject, signal, computed} from '@angular/core';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {ApiService} from './api.service';
import {safeMarkdown} from './markdown';
import {downloadFile} from './types';
@Component({standalone:true,imports:[RouterLink],template:`<main class="shared-page"><div class="section-heading"><span class="eyebrow">SHARED README PREVIEW</span><h1>A story worth sharing.</h1><p class="muted">Read-only snapshot. {{expires()?'This link expires '+expires().slice(0,10)+'.':''}}</p></div>@if(error()){<p class="message error">{{error()}}</p>}@else if(!markdown()){<p class="muted">Loading preview…</p>}@else{<article class="markdown-body shared-readme" [innerHTML]="html()"></article><div class="modal-actions"><button class="button subtle" (click)="download()">Download README.md ↓</button><a class="button primary" routerLink="/studio">Create your own ↗</a></div>}</main>`})
export class ShareComponent{
 api=inject(ApiService);route=inject(ActivatedRoute);markdown=signal('');expires=signal('');error=signal('');html=computed(()=>safeMarkdown(this.markdown()));
 constructor(){this.api.request('/shared/'+encodeURIComponent(this.route.snapshot.paramMap.get('token')||'')).then(r=>{this.markdown.set(r.markdown);this.expires.set(r.expires_at);}).catch(e=>this.error.set(e.message));}
 download(){downloadFile(this.markdown(),'README.md');}
}
