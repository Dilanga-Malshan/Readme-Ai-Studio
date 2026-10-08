// @vitest-environment jsdom
import {describe,it,expect} from 'vitest';
import {safeMarkdown} from './markdown';
describe('live preview security',()=>{
 it('removes executable HTML and unsafe URLs',()=>{const html=safeMarkdown('<script>x</script><img src="x" onerror="alert(1)"><a href="javascript:x">x</a>');expect(html).not.toContain('<script');expect(html).not.toContain('onerror');expect(html).not.toContain('javascript:');});
 it('preserves GitHub tables and image alt text',()=>{const html=safeMarkdown('| A |\n| --- |\n| B |\n\n![Descriptive alt](https://example.com/image.svg)');expect(html).toContain('<table>');expect(html).toContain('alt="Descriptive alt"');});
 it('reflects edited markdown immediately',()=>{expect(safeMarkdown('# Updated')).toContain('<h1>Updated</h1>');});
});
