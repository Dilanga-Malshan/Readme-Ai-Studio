import { Injectable, signal } from '@angular/core';
@Injectable({providedIn:'root'})
export class ApiService {
  user=signal<{login:string;csrf_token:string}|null>(null);
  async request<T=any>(path:string,method='GET',body?:unknown):Promise<T>{
    const headers:Record<string,string>={'Content-Type':'application/json'};
    if(this.user())headers['X-CSRF-Token']=this.user()!.csrf_token;
    let response:Response;
    try{response=await fetch('/api/v1'+path,{method,headers,credentials:'include',...(body!==undefined?{body:JSON.stringify(body)}:{})});}
    catch{throw new Error('The backend is unavailable. Start FastAPI and try again.');}
    if(response.status===204)return undefined as T;
    const data=await response.json().catch(()=>({}));
    if(!response.ok)throw new Error(data.error?.message||data.detail||`Request failed (${response.status})`);
    return data;
  }
  async session(){try{this.user.set(await this.request('/auth/me'));}catch{this.user.set(null);}}
  login(){location.href='/api/v1/auth/github/login';}
  async logout(){await this.request('/auth/logout','POST');this.user.set(null);}
}
