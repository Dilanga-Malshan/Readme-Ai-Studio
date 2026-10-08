// @vitest-environment jsdom
import '@angular/compiler';
import { afterEach,describe,it,expect,vi } from 'vitest';
import { ApiService } from './api.service';
afterEach(()=>vi.unstubAllGlobals());
describe('API boundary',()=>{
 it('attaches CSRF only from the authenticated session',async()=>{const fetch=vi.fn(async()=>new Response('{}',{status:200,headers:{'Content-Type':'application/json'}}));vi.stubGlobal('fetch',fetch);const api=new ApiService();api.user.set({login:'alice',csrf_token:'session-csrf'});await api.request('/readmes','POST',{title:'draft'});expect(fetch.mock.calls[0][1].headers['X-CSRF-Token']).toBe('session-csrf');});
 it('exposes a useful provider error',async()=>{vi.stubGlobal('fetch',async()=>new Response(JSON.stringify({error:{message:'Missing permissions'}}),{status:403}));await expect(new ApiService().request('/github/publish','POST',{})).rejects.toThrow('Missing permissions');});
});
