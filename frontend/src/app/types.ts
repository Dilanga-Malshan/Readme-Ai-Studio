export interface Repo { name:string; full_name:string; description:string|null; html_url:string; language:string|null; topics:string[]; stargazers_count:number; score?:number; }
export interface Profile { login:string; name:string|null; bio:string|null; location:string|null; blog:string|null; avatar_url:string; public_repos:number; }
export interface Analysis { profile:Profile; repositories:Repo[]; ranked:Repo[]; languages:string[]; notes:string[]; }
export interface Content { headline:string; introduction:string; about:string; skills:string[]; working_on:string; fun_fact:string; }
export interface Config { template:string;accent:string;align:string;badge_style:string;projects:string[];section_order:string[];sections:Record<string,boolean>;banner_url:string;typing_font:string;animated_footer:boolean;typing:boolean;skill_icons:boolean;top_languages:boolean;streak:boolean;visitors:boolean;project_layout:string;website:string;linkedin:string;email:string;custom_badges:string[];footer:boolean; }
export interface Template { id:string;name:string;subtitle:string;accent:string;emoji:string; }
export interface Draft { lastGenerated?:string; username:string;markdown:string;content:Content;config:Config;analysis:Analysis|null; }
export const templateList:Template[]=[
{id:'minimal',name:'Minimal Developer',subtitle:'Quiet confidence. Just the essentials.',accent:'94A3B8',emoji:'01'},
{id:'professional',name:'Professional Engineer',subtitle:'A clear story for your next opportunity.',accent:'38BDF8',emoji:'02'},
{id:'neon',name:'Futuristic Neon',subtitle:'A bold signal in a sea of profiles.',accent:'C8F77C',emoji:'03'},
{id:'ai',name:'AI / ML Engineer',subtitle:'Put your intelligence work in focus.',accent:'A78BFA',emoji:'04'},
{id:'fullstack',name:'Full-Stack Developer',subtitle:'Show the whole system, front to back.',accent:'38BDF8',emoji:'05'},
{id:'creative',name:'Creative Portfolio',subtitle:'A little personality. A lot of craft.',accent:'F472B6',emoji:'06'}];
export function validUsername(value:string):boolean {return /^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$/.test(value);}
export function defaultConfig():Config{return {template:'professional',accent:'38BDF8',align:'left',badge_style:'for-the-badge',projects:[],section_order:['about','skills','working','projects','stats','social','fun'],sections:{about:true,skills:true,working:true,projects:true,stats:false,social:true,fun:false},banner_url:'',typing_font:'Fira Code',animated_footer:false,typing:false,skill_icons:false,top_languages:false,streak:false,visitors:false,project_layout:'table',website:'',linkedin:'',email:'',custom_badges:[],footer:true};}
export const emptyContent:Content={headline:'',introduction:'',about:'',skills:[],working_on:'',fun_fact:''};
export function hasManualChanges(markdown:string,lastGenerated:string):boolean{return !!markdown && markdown!==lastGenerated;}
export function downloadFile(contents:string,name:string,type='text/markdown'):void {const url=URL.createObjectURL(new Blob([contents],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
