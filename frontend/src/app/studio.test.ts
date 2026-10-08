// @vitest-environment jsdom
import '@angular/compiler';
import { Injector, runInInjectionContext } from '@angular/core';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { beforeEach,describe,it,expect,vi } from 'vitest';
import { StudioComponent } from './studio.component';
import { ApiService } from './api.service';
const evidence={profile:{login:'alice',name:'Alice',bio:'Developer',location:null,blog:null,avatar_url:'https://example.com/avatar',public_repos:0},repositories:[],ranked:[],languages:[],notes:[]};
function studio(){
 const api={request:vi.fn(async(path:string)=>path==='/health'?{ai_configured:false}:{markdown:'# Generated',content:{headline:'Developer',introduction:'Hello',about:'Alice',skills:[],working_on:'',fun_fact:''},source:'template',warnings:[]})};
 const injector=Injector.create({providers:[{provide:ApiService,useValue:api},{provide:ActivatedRoute,useValue:{snapshot:{queryParamMap:convertToParamMap({})}}}]});
 return {component:runInInjectionContext(injector,()=>new StudioComponent()),api};
}
beforeEach(()=>localStorage.clear());
describe('studio draft protection',()=>{
 it('offers a proposal instead of replacing manually edited markdown',async()=>{const {component}=studio();component.analysis.set(evidence);component.lastGenerated='# Original';component.edit('# My manual edits');await component.generate(true);expect(component.markdown()).toBe('# My manual edits');expect(component.proposal()?.markdown).toBe('# Generated');});
 it('preserves manual edit protection after browser reload',()=>{const {component}=studio();component.lastGenerated='# Original';component.edit('# Edited');const restored=studio().component;expect(restored.markdown()).toBe('# Edited');expect(restored.lastGenerated).toBe('# Original');});
 it('keeps an undo history when applying a proposal',()=>{const {component}=studio();component.edit('# Old');component.proposal.set({markdown:'# New',explanation:'Clearer'});component.applyProposal();expect(component.markdown()).toBe('# New');expect(component.localVersions[0].markdown).toBe('# Old');});
 it('shows backend failures while preserving the draft',async()=>{const {component,api}=studio();await Promise.resolve();component.analysis.set(evidence);component.edit('# Keep me');api.request.mockRejectedValue(new Error('GitHub rate limit'));await component.generate(true);expect(component.markdown()).toBe('# Keep me');expect(component.error()).toBe('GitHub rate limit');});
 it('updates the rendered preview when editor content changes',()=>{const {component}=studio();component.edit('# Live update');expect(component.rendered()).toContain('<h1>Live update</h1>');});
});
