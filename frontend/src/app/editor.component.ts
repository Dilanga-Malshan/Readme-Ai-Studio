import { AfterViewInit, Component, ElementRef, EventEmitter, Input, OnChanges, OnDestroy, Output, ViewChild } from '@angular/core';
import type * as Monaco from 'monaco-editor';
declare global {interface Window {require:any;monaco:typeof Monaco;}}
let monacoPromise:Promise<typeof Monaco>|undefined;
function loadMonaco(){
 if(!monacoPromise)monacoPromise=new Promise<typeof Monaco>((resolve,reject)=>{
  const setup=()=>{window.require.config({paths:{vs:'/assets/monaco/vs'}});window.MonacoEnvironment={getWorkerUrl:()=>'/assets/monaco/vs/base/worker/workerMain.js'};window.require(['vs/editor/editor.main'],()=>resolve(window.monaco),reject);};
  if(window.require){setup();return;}
  const script=document.createElement('script');script.src='/assets/monaco/vs/loader.js';script.onload=setup;script.onerror=reject;document.head.appendChild(script);
 });
 return monacoPromise;
}
@Component({selector:'markdown-editor',standalone:true,template:`<div #host class="monaco-host" aria-label="Markdown code editor"></div>@if(failed){<label class="fallback-label">Markdown editor (Monaco unavailable)</label><textarea class="fallback-editor" [value]="value" (input)="onFallback($event)" aria-label="Markdown source"></textarea>}`})
export class EditorComponent implements AfterViewInit,OnChanges,OnDestroy{
 @ViewChild('host')host!:ElementRef<HTMLDivElement>;
 @Input()value='';@Input()light=false;@Output()valueChange=new EventEmitter<string>();
 editor?:Monaco.editor.IStandaloneCodeEditor;failed=false;destroyed=false;applying=false;
 async ngAfterViewInit(){try{const m=await loadMonaco();if(this.destroyed)return;this.editor=m.editor.create(this.host.nativeElement,{value:this.value,language:'markdown',theme:this.light?'vs':'vs-dark',automaticLayout:true,minimap:{enabled:false},fontSize:13,lineHeight:23,wordWrap:'on',scrollBeyondLastLine:false,padding:{top:20},tabSize:2});this.editor.onDidChangeModelContent(()=>{if(!this.applying)this.valueChange.emit(this.editor!.getValue());});}catch{this.failed=true;}}
 ngOnChanges(){if(this.editor&&this.value!==this.editor.getValue()){this.applying=true;const model=this.editor.getModel()!;this.editor.pushUndoStop();this.editor.executeEdits('visual-controls',[{range:model.getFullModelRange(),text:this.value}]);this.editor.pushUndoStop();this.applying=false;}if(this.editor)window.monaco.editor.setTheme(this.light?'vs':'vs-dark');}
 onFallback(e:Event){this.valueChange.emit((e.target as HTMLTextAreaElement).value);}
 search(){this.editor?.getAction('actions.find')?.run();}
 undo(){this.editor?.trigger('toolbar','undo',null);}
 redo(){this.editor?.trigger('toolbar','redo',null);}
 format(){const text=this.editor?.getValue()||this.value;this.valueChange.emit(text.split('\n').map(line=>line.replace(/\s+$/,'')).join('\n').replace(/\n{4,}/g,'\n\n\n'));}
 ngOnDestroy(){this.destroyed=true;this.editor?.dispose();}
}
