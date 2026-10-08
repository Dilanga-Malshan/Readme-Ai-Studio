import { marked } from 'marked';
import DOMPurify from 'dompurify';
export function safeMarkdown(markdown:string):string {
 const html=marked.parse(markdown,{async:false,gfm:true}) as string;
 return DOMPurify.sanitize(html,{ALLOWED_TAGS:['p','br','hr','h1','h2','h3','h4','h5','h6','a','img','strong','em','del','blockquote','code','pre','ul','ol','li','table','thead','tbody','tr','th','td','div','span','sub','sup','details','summary'],ALLOWED_ATTR:['href','src','alt','title','align','width','height'],ALLOW_DATA_ATTR:false,FORBID_ATTR:['style'],ALLOWED_URI_REGEXP:/^(?:https?:\/\/|mailto:)/i});
}
