import re
from markdown_it import MarkdownIt
from fastapi import HTTPException

def section_bounds(markdown,heading):
    tokens=MarkdownIt().parse(markdown);lines=markdown.splitlines(keepends=True)
    headings=[]
    for i,t in enumerate(tokens):
        if t.type=='heading_open' and t.tag=='h2' and t.map:
            headings.append((tokens[i+1].content,t.map[0],t.map[1]))
    for index,(name,start,body_start) in enumerate(headings):
        if name.casefold()==heading.casefold():
            end=headings[index+1][1] if index+1<len(headings) else len(lines)
            return lines,body_start,end
    raise HTTPException(422,'This section is missing. Add its heading before regenerating it.')

def replace_section(markdown,heading,body):
    if re.search(r'^#{1,2}\s',body,re.M): raise HTTPException(502,'AI returned a heading that would change the section structure. Retry.')
    lines,start,end=section_bounds(markdown,heading)
    return ''.join(lines[:start])+'\n'+body.strip()+'\n\n'+''.join(lines[end:])
