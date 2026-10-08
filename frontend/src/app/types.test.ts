import {describe,it,expect} from 'vitest';
import {validUsername,hasManualChanges,defaultConfig,templateList} from './types';
describe('GitHub form validation',()=>{
 it.each(['alice','Dilanga-Malshan','a-b','a'.repeat(39)])('accepts %s',value=>expect(validUsername(value)).toBe(true));
 it.each(['','a--b','-alice','alice-','a/b','a'.repeat(40)])('rejects %s',value=>expect(validUsername(value)).toBe(false));
});
describe('manual editor preservation',()=>{
 it('requires review when generated controls would replace manual edits',()=>expect(hasManualChanges('# manual','# generated')).toBe(true));
 it('allows synchronized regeneration',()=>expect(hasManualChanges('# generated','# generated')).toBe(false));
 it('allows first generation',()=>expect(hasManualChanges('','')).toBe(false));
});
describe('template configuration',()=>{
 it('has six independent styles',()=>expect(new Set(templateList.map(t=>t.id)).size).toBe(6));
 it('keeps independent per-draft configuration',()=>{const a=defaultConfig(),b=defaultConfig();a.sections.about=false;expect(b.sections.about).toBe(true);});
});
