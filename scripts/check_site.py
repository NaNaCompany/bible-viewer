"""Validate every generated page, verse, publisher integration, and local link."""
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
PREFIX='/bible-viewer/'
VERSIONS=json.loads((ROOT/'data/versions.json').read_text(encoding='utf-8'))
DATA={v['id']:json.loads((ROOT/'data'/f'{v["id"]}.json').read_text(encoding='utf-8')) for v in VERSIONS}

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical=[];self.alternates={};self.verses={};self.options=[];self.links=set();self.copy=0;self.share=0;self.config='';self.ids=set();self.capture=None;self.current_verse=None;self.text='';self.in_picker=False;self.option=None;self.current_lang=None;self.config_capture=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, ('duplicate ID',a['id'])
            self.ids.add(a['id'])
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='link' and a.get('rel')=='alternate':self.alternates[a['hreflang']]=a['href']
        if tag in ('a','link') and a.get('href'):self.links.add(a['href'])
        if tag=='script' and a.get('src'):self.links.add(a['src'])
        if tag=='script' and a.get('id')=='page-config':self.config_capture=True
        if tag=='select' and 'data-version-picker' in a:self.in_picker=True
        if tag=='option' and self.in_picker:self.options.append(a['value'])
        if tag=='article' and a.get('class')=='verse':self.current_verse=a['data-verse']
        if tag=='p' and 'verse-text' in a.get('class','').split():self.capture='verse';self.text='';self.current_lang=a.get('lang')
        if tag=='button':
            if a.get('data-action')=='copy':self.copy+=1
            if a.get('data-action')=='share':self.share+=1
    def handle_data(self,text):
        if self.capture=='verse':self.text+=text
        if self.config_capture:self.config+=text
    def handle_endtag(self,tag):
        if tag=='p' and self.capture=='verse':
            self.verses[self.current_verse]=(self.text,self.current_lang);self.capture=None
        if tag=='select':self.in_picker=False
        if tag=='script':self.config_capture=False

def main():
    for version in VERSIONS:
        assert hashlib.sha256((ROOT/'data/source'/version['filename']).read_bytes()).hexdigest()==version['source_sha256']
        assert hashlib.sha256((ROOT/'data'/f'{version["id"]}.json').read_bytes()).hexdigest()==version['normalized_sha256']
    urls=[]
    for path in sorted(OUT.glob('sitemap-*.xml')):
        assert path.stat().st_size<50_000_000
        parsed=ET.parse(path)
        locs=[e.text for e in parsed.findall('.//{*}url/{*}loc')]
        assert len(locs)<50000 and len(locs)==len(set(locs))
        urls.extend(locs)
    assert len(urls)==len(set(urls))==14286
    index=ET.parse(OUT/'sitemap.xml')
    assert len(index.findall('.//{*}sitemap/{*}loc'))==2
    linked=set(); verses=0;total_bytes=0;chapters=0
    for n,url in enumerate(urls,1):
        route=urlsplit(url).path
        filename=OUT/route.removeprefix(PREFIX)/'index.html'
        raw=filename.read_text(encoding='utf-8');total_bytes+=len(raw.encode())
        page=Inspect();page.feed(raw)
        assert page.canonical==[url], ('canonical',url)
        assert set(page.alternates)=={'ko','en','x-default'},url
        assert page.alternates['x-default']==page.alternates['ko']
        for provider in ['G-2ZYSF0173P','GTM-NV2WWQXB','ca-pub-9767176956440077','9f3423bb0d034d91bbe1a12afeff2429','https://www.googletagmanager.com/ns.html?id=GTM-NV2WWQXB']:
            assert provider in raw,(url,provider)
        assert "if(!['nanalab.kr','www.nanalab.kr','nanacompany.github.io'].includes(location.hostname.toLowerCase()))return;" in raw
        assert not re.search(r'<meta\s+name="robots"\s+content="noindex',raw)
        assert 'https://nanalab.kr/apps/' in page.links
        config=json.loads(page.config)
        assert config['canonical']==url
        ui='en' if route.startswith(PREFIX+'en/') else 'ko'
        ordered=[v['id'] for v in sorted(VERSIONS,key=lambda v:v['language']!=ui)]
        if page.options:assert page.options==ordered,(url,'language order')
        if config['kind']=='chapter':
            chapters+=1
            expected=DATA[config['version']][config['book'].upper()][str(config['chapter'])]
            assert list(page.verses)==[r[0] for r in expected],(url,'verse numbering')
            for number,text in expected:
                got,language=page.verses[number]
                assert got==(text or ('[이 판본의 배포 원문에는 별도 본문이 없습니다.]' if ui=='ko' else '[The distributed source has no separate text for this verse.]')),(url,number,'verse mismatch')
                if text:assert language==next(v['language'] for v in VERSIONS if v['id']==config['version'])
            assert page.copy==page.share==len(expected),(url,'copy/share buttons')
            assert 'verse-picker' in page.ids and 'data-action="share-selected"' in raw
            verses+=len(expected)
        linked.update(page.links);linked.update(page.alternates.values())
        if n%3000==0:print(json.dumps({'checked':n,'of':len(urls)}),flush=True)
    for link in linked:
        u=urlsplit(link)
        if u.netloc and u.netloc!='nanalab.kr':continue
        if not u.path.startswith(PREFIX):continue
        relative=unquote(u.path.removeprefix(PREFIX))
        target=OUT/relative
        if u.path.endswith('/'):target=target/'index.html'
        assert target.is_file(),('broken local link',link)
    assert chapters==14268 and len(list(OUT.rglob('*.html')))==len(urls)
    report=dict(status='passed',html_pages=len(urls),chapter_pages=chapters,verse_renderings=verses,source_hashes_verified=6,all_verse_texts_match=True,all_verse_copy_share_buttons=True,language_order_verified=True,canonical_hreflang_links_verified=True,publisher_integrations_per_html=4,gtm_noscript_per_html=True,html_bytes=total_bytes,broken_local_links=0)
    (ROOT/'evidence/static-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
