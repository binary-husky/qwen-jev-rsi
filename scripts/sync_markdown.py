"""Synchronize only changed Markdown blocks; preserve unrelated HTML edits."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import argparse, difflib, hashlib, json, re
from lxml import html as lh
import markdown
ROOT=Path(__file__).resolve().parents[1]
MD=ROOT/'idea.pub.md'
HTML=ROOT/'index.html'
STATE=Path(__file__).with_name('baseline.json')
TAGS={'h1','h2','h3','p','figcaption','table','ol','ul','blockquote','summary'}
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def inline(e):
    text=e.text or ''
    for c in e:
        value=inline(c)
        if c.tag=='strong': value='**'+value+'**'
        elif c.tag=='em': value='*'+value+'*'
        elif c.tag=='a': value='['+value+']('+c.get('href','')+')'
        elif c.tag=='code': value='`'+value+'`'
        elif c.tag=='br': value='<br>'
        text+=value+(c.tail or '')
    return text.strip()
def to_md(e):
    if e.tag=='table':
        rows=e.xpath('./thead/tr|./tbody/tr|./tr')
        lines=[]
        for i,row in enumerate(rows):
            cells=[inline(c).replace('|','\\|').replace('\n',' ') for c in row]
            lines.append('| '+' | '.join(cells)+' |')
            if i==0:lines.append('| '+' | '.join(['---']*len(cells))+' |')
        caption=e.find('caption')
        if caption is not None:lines+=['',inline(caption)]
        return '\n'.join(lines)
    if e.tag in ('ol','ul'):
        return '\n'.join((str(i+1)+'. ' if e.tag=='ol' else '- ')+inline(c) for i,c in enumerate(e) if c.tag=='li')
    if e.tag in ('h1','h2','h3'):return '#'*int(e.tag[1])+' '+inline(e)
    if e.tag=='blockquote':return '> '+inline(e)
    return inline(e)
class Scan(HTMLParser):
    def __init__(self,src):
        super().__init__(convert_charrefs=False);self.src=src;self.lines=src.splitlines(keepends=True);self.offsets=[0]
        for line in self.lines:self.offsets.append(self.offsets[-1]+len(line))
        self.stack=[];self.active=None;self.blocks=[]
    def pos(self):
        line,col=self.getpos();return self.offsets[line-1]+col
    def handle_starttag(self,tag,attrs):
        if tag in {'img','br','meta','link','input','source','hr','wbr'}:return
        a=dict(attrs)
        excluded=any(t in {'svg','script','style','nav','button'} or 'language-switch' in x.get('class','') for t,x in self.stack)
        if self.active is None and tag in TAGS and any(t=='article' for t,x in self.stack) and not excluded:
            self.active=(tag,len(self.stack),self.pos(),a)
        self.stack.append((tag,a))
    def handle_endtag(self,tag):
        if self.active and tag==self.active[0] and len(self.stack)==self.active[1]+1:
            t,depth,start,attrs=self.active;end=self.src.index('>',self.pos())+1
            self.blocks.append((start,end,t,attrs));self.active=None
        if self.stack and self.stack[-1][0]==tag:self.stack.pop()
def blocks(text):
    pat=r'<!-- block:([a-z0-9-]+) -->\s*\n(.*?)(?=\n<!-- block:|\Z)'
    result={}
    for m in re.finditer(pat,text,re.S):
        if m[1] in result:raise RuntimeError('Duplicate block '+m[1])
        result[m[1]]=m[2].strip()
    return result
def initialize():
    if MD.exists() or STATE.exists():raise RuntimeError('Refusing to overwrite existing Markdown/baseline')
    src=HTML.read_text();scan=Scan(src);scan.feed(src);out=[];state={};replacements=[]
    for i,(a,b,tag,attrs) in enumerate(scan.blocks):
        fragment=src[a:b];key=f'b{i+1:03d}';body=to_md(lh.fromstring(fragment))
        if not body:continue
        out.append(f'<!-- block:{key} -->\n{body}\n')
        state[key]={'markdown':body,'html_hash':digest(fragment),'tag':tag,'attrs':attrs}
        replacements.append((a,b,f'<!-- edit:{key}:start -->'+fragment+f'<!-- edit:{key}:end -->'))
    for a,b,v in reversed(replacements):src=src[:a]+v+src[b:]
    if HTML.read_text()!=scan.src:raise RuntimeError('HTML changed during initialization')
    HTML.write_text(src);MD.write_text('<!-- 宣传页编辑稿：直接修改正文、表格、图注；保留 block 注释用于局部同步。图片、视频与交互由 HTML 保留。 -->\n\n'+'\n'.join(out))
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    print(f'Created {MD}: {len(state)} editable blocks')
def sync(apply=False):
    source=HTML.read_text();current=MD.read_text();state=json.loads(STATE.read_text());parts=blocks(current)
    if set(parts)!=set(state):raise RuntimeError('Block markers changed. Keep markers; edit/add text inside a block. Clear its content to delete it.')
    result=source;changed=[]
    for key,body in parts.items():
        old=state[key]
        if body==old['markdown']:continue
        pattern=re.compile(r'(<!-- edit:'+key+r':start -->)(.*?)(<!-- edit:'+key+r':end -->)',re.S)
        match=pattern.search(result)
        if not match or digest(match[2])!=old['html_hash']:raise RuntimeError('HTML also changed in '+key+'; manually merge before syncing')
        print(''.join(difflib.unified_diff((old['markdown']+'\n').splitlines(True),(body+'\n').splitlines(True),fromfile=key+' before',tofile=key+' after')))
        rendered=markdown.markdown(body,extensions=['tables','sane_lists']) if body else ''
        # Preserve the original block attributes, section numbers and semantic wrappers.
        if rendered:
            nodes=lh.fragments_fromstring(rendered);first=nodes[0]
            if old['tag'] in {'figcaption','summary','blockquote'} and first.tag=='p':first.tag=old['tag']
            for k,v in old['attrs'].items():first.set(k,v)
            if old['tag']=='h2':
                original=lh.fromstring(match[2]);numbers=original.xpath('./span[@class="section-number"]')
                if numbers and (first.text or '').startswith(numbers[0].text or ''):
                    number=numbers[0];first.text=first.text[len(number.text):];number.tail=first.text;first.text=None;first.insert(0,number)
            if old['tag']=='table' and len(nodes)>1:
                caption=lh.Element('caption');caption.text=nodes[1].text
                for c in list(nodes[1]):caption.append(c)
                first.insert(0,caption);nodes=nodes[:1]
            rendered='\n'.join(lh.tostring(n,encoding='unicode') for n in nodes)
        result=result[:match.start(2)]+rendered+result[match.end(2):]
        state[key].update(markdown=body,html_hash=digest(rendered));changed.append(key)
    if apply and changed:
        if HTML.read_text()!=source or MD.read_text()!=current:raise RuntimeError('Files changed during sync; retry')
        HTML.write_text(result);STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    print(('Applied' if apply else 'Previewed')+f' {len(changed)} changed blocks. Review/update embedded English translations for changed text before publishing.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--init',action='store_true');parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    initialize() if args.init else sync(args.apply)
