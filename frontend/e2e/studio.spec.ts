import {test,expect} from '@playwright/test';
const evidence={profile:{login:'alice',name:'Alice Example',bio:'Developer',location:'Colombo',blog:'https://example.com',avatar_url:'https://example.com/avatar.png',public_repos:1},repositories:[{name:'toolkit',full_name:'alice/toolkit',description:'Fixture project',html_url:'https://github.com/alice/toolkit',language:'Python',topics:[],stargazers_count:0}],ranked:[{name:'toolkit',full_name:'alice/toolkit',description:'Fixture project',html_url:'https://github.com/alice/toolkit',language:'Python',topics:[],stargazers_count:0}],languages:['Python'],notes:[]};
test.beforeEach(async({page})=>{
 await page.route('**/api/v1/**',async route=>{
  const path=new URL(route.request().url()).pathname;
  if(path.endsWith('/auth/me'))return route.fulfill({status:401,json:{error:{message:'Sign in required'}}});
  if(path.endsWith('/health'))return route.fulfill({json:{ai_configured:false,oauth_configured:false}});
  if(path.endsWith('/github/analyze'))return route.fulfill({json:evidence});
  if(path.endsWith('/ai/generate'))return route.fulfill({json:{markdown:'# Alice Example\n\n## About me\n\nDeveloper in Colombo.\n\n## Tech stack\n\nPython',content:{headline:'Developer',introduction:'Developer in Colombo.',about:'Alice Example',skills:['Python'],working_on:'',fun_fact:''},warnings:[],source:'test fixture'}});
  return route.fulfill({status:503,json:{error:{message:'Provider unavailable'}}});
 });
});
test('validates username before importing',async({page})=>{
 await page.goto('/studio');await page.getByRole('textbox',{name:'GitHub username',exact:true}).fill('../bad');await page.getByRole('button',{name:'Analyze profile'}).click();await expect(page.getByRole('alert')).toContainText('valid GitHub username');
});
test('imports fixture evidence, generates, previews and downloads without sign-in',async({page})=>{
 await page.goto('/studio');await page.getByRole('textbox',{name:'GitHub username',exact:true}).fill('alice');await page.getByRole('button',{name:'Analyze profile'}).click();await expect(page.getByText('Alice Example',{exact:true})).toBeVisible();await page.getByRole('button',{name:'Generate README',exact:false}).click();await expect(page.locator('.markdown-body h1')).toHaveText('Alice Example');const download=page.waitForEvent('download');await page.getByRole('button',{name:'↓ .md',exact:true}).click();expect((await download).suggestedFilename()).toBe('README.md');
});
test('imports manual Markdown and preserves it across reload',async({page})=>{
 await page.goto('/studio');await page.locator('input[type=file]').setInputFiles({name:'README.md',mimeType:'text/markdown',buffer:Buffer.from('# Manual profile\n\nMy carefully written introduction.')});await expect(page.locator('.markdown-body h1')).toHaveText('Manual profile');await page.reload();await expect(page.locator('.markdown-body h1')).toHaveText('Manual profile');
});
test('sanitizes imported active content in preview',async({page})=>{
 await page.goto('/studio');await page.locator('input[type=file]').setInputFiles({name:'README.md',mimeType:'text/markdown',buffer:Buffer.from('# Safe\n\n<script>window.hacked=true</script><img src="javascript:x" onerror="window.hacked=true">')});await expect(page.locator('.markdown-body h1')).toHaveText('Safe');await expect(page.locator('.markdown-body script')).toHaveCount(0);expect(await page.evaluate(()=>Boolean((window as any).hacked))).toBe(false);
});
