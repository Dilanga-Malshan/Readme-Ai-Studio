import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { ApiService } from './api.service';
@Component({selector:'app-root',standalone:true,imports:[RouterLink,RouterOutlet],template:`
<div class="app-shell" [class.light]="light()">
<header class="topbar"><a class="brand" routerLink="/"><span class="brand-mark">R<span>↗</span></span> README<span class="brand-ai">.AI</span></a><nav><a routerLink="/studio">Studio</a><a href="/#templates">Templates</a><a href="/#how">How it works</a></nav><div class="header-actions"><button class="icon-button" (click)="toggleTheme()" [attr.aria-label]="light()?'Use dark mode':'Use light mode'">{{light()?'☾':'☀'}}</button>@if(api.user()){<span class="user-label">&#64;{{api.user()!.login}}</span><button class="button subtle small" (click)="api.logout()">Sign out</button>}@else{<button class="button subtle small" (click)="signIn()">Sign in with GitHub ↗</button>}</div></header>
@if(error()){<div class="global-error" role="alert">{{error()}} <button (click)="error.set('')">Dismiss</button></div>}
<router-outlet></router-outlet></div>`})
export class AppComponent{
 api=inject(ApiService);light=signal(localStorage.getItem('readme-theme')==='light');error=signal('');
 constructor(){this.api.session();}
 toggleTheme(){this.light.update(v=>!v);localStorage.setItem('readme-theme',this.light()?'light':'dark');}
 async signIn(){try{const health=await this.api.request('/health');if(!health.oauth_configured)throw new Error('GitHub sign-in requires OAuth configuration. See docs/SETUP.md.');this.api.login();}catch(e){this.error.set((e as Error).message);}}
}
