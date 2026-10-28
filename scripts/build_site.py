"""Generate real version/chapter HTML pages; no full-corpus browser download."""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
APP = json.loads((ROOT / 'APP.json').read_text(encoding='utf-8'))
BOOKS = json.loads((ROOT / 'data/books.json').read_text(encoding='utf-8'))
VERSIONS = json.loads((ROOT / 'data/versions.json').read_text(encoding='utf-8'))
ORIGIN = APP['origin']
PATH = '/bible-viewer/'
H = lambda value: html.escape(str(value), quote=True)
T = {
 'ko': dict(title='성경 뷰어', read='성경 읽기', subtitle='판본을 고르고 권·장을 선택하세요.', version='판본', books='권·장 선택', chapter='장', verse='절', ot='구약', nt='신약', filter='성경 권 검색', filterHint='권 이름 검색 · 예: 시편, John', noResults='일치하는 권이 없습니다.', versions='성경 판본', versionsHint='한국어 판본 먼저', booksCount='66권', chaptersCount='1,189장', copy='복사', share='공유', shareVerse='말씀 공유하기', previous='이전 장', next='다음 장', copyright='출처·이용 조건', privacy='개인정보 안내', home='처음', viewAll='권·장 목록', fontDown='글자 작게', fontUp='글자 크게', dark='다크 모드', copied='말씀과 페이지 URL을 복사했습니다.', shareCopied='공유 기능 대신 말씀과 페이지 URL을 복사했습니다.', shared='공유 요청을 보냈습니다.', actionFailed='처리하지 못했습니다. 다시 시도해 주세요.', missingVerse='이 판본에서는 해당 절 번호가 다를 수 있습니다.', empty='[이 판본의 배포 원문에는 별도 본문이 없습니다.]', source='본문 출처', sourceNote='판본의 원문을 그대로 표시합니다. 절 번호·합본 절·본문이 없는 절은 판본마다 다를 수 있습니다.', close='닫기', manualCopy='말씀과 URL을 선택해 복사하세요.', manualTitle='직접 복사', language='화면 언어', skip='본문 바로가기', firstChapter='1장 읽기', chapterSuffix='장', chapterMeta='본문 읽기 · 절별 복사·공유', book='권', licensesIntro='성경 본문은 아래 판본의 공개 자료를 사용합니다. 본문을 번역·윤문하거나 다른 판본으로 보충하지 않았습니다.', privacyIntro='로그인이나 서버 저장 기능이 없습니다. 글자 크기와 화면 테마는 이 브라우저에만 저장됩니다.', privacyTags='운영 페이지는 Google Analytics 4, Google Tag Manager, Google AdSense, Cloudflare Web Analytics를 사용합니다. 방문·기기 정보가 각 사업자에게 처리될 수 있으며 광고 서비스는 쿠키를 사용할 수 있습니다.', privacyInput='복사·공유한 본문, 권 검색 입력값, 읽기 설정을 별도 분석 이벤트로 전송하지 않습니다. 공유를 선택하면 기기의 공유 기능 또는 클립보드를 사용합니다.', privacyControls='브라우저의 사이트 데이터 삭제로 저장된 화면 설정을 지울 수 있습니다. 클립보드·공유 권한은 브라우저에서 제어합니다.', details='판본 정보', display='본문', sourceDate='수집한 원문 파일의 해시는 저장소 data/versions.json에 기록합니다.', allVersions='전체 판본', sameChapter='같은 장의 다른 판본'),
 'en': dict(title='Bible Reader', read='Read the Bible', subtitle='Choose a version, book, and chapter.', version='Version', books='Books & chapters', chapter='Chapter', verse='Verse', ot='Old Testament', nt='New Testament', filter='Find a book', filterHint='Book name · e.g. Psalms, John', noResults='No matching books.', versions='Bible versions', versionsHint='English versions first', booksCount='66 books', chaptersCount='1,189 chapters', copy='Copy', share='Share', shareVerse='Share a verse', previous='Previous chapter', next='Next chapter', copyright='Sources & licenses', privacy='Privacy', home='Home', viewAll='Books & chapters', fontDown='Smaller text', fontUp='Larger text', dark='Dark mode', copied='Verse and page URL copied.', shareCopied='Sharing is unavailable. Verse and page URL copied.', shared='Share request sent.', actionFailed='Could not complete this action. Please try again.', missingVerse='This version may use a different verse number.', empty='[The distributed source has no separate text for this verse.]', source='Text source', sourceNote='Text is reproduced from the named version. Verse numbering, combined verses, and omitted verses may differ between versions.', close='Close', manualCopy='Select and copy the verse and URL.', manualTitle='Copy manually', language='Interface language', skip='Skip to content', firstChapter='Read chapter 1', chapterSuffix='', chapterMeta='Read, copy, and share individual verses', book='Book', licensesIntro='Scripture text is reproduced from the public sources listed below. No translation, paraphrasing, or supplementation from other versions has been applied.', privacyIntro='There are no accounts or server-side reading records. Text size and theme are stored only in this browser.', privacyTags='Production pages use Google Analytics 4, Google Tag Manager, Google AdSense, and Cloudflare Web Analytics. These providers may process visit and device information; advertising services may use cookies.', privacyInput='No custom analytics events transmit copied/shared verse text, book-filter input, or reading preferences. Sharing uses the device share sheet or clipboard.', privacyControls='Clear this site’s browser data to remove reading preferences. Clipboard and sharing permissions are controlled by your browser.', details='Version details', display='Text', sourceDate='Source-file hashes are recorded in data/versions.json in the repository.', allVersions='All versions', sameChapter='Other versions of this chapter')
}
LANG_NAMES = {'ko':'한국어', 'en':'English', 'es':'Español', 'fr':'Français'}
DATA = {v['id']:json.loads((ROOT / 'data' / (v['id']+'.json')).read_text(encoding='utf-8')) for v in VERSIONS}
BY_ID = {v['id']:v for v in VERSIONS}
tracking = (ROOT / 'scripts/publisher-tracking.mjs').read_text(encoding='utf-8')
HEAD = re.search(r'export const HEAD=`(.*?)`;', tracking, re.S)[1]
FALLBACK = re.search(r'export const FALLBACK=`(.*?)`;', tracking, re.S)[1]
for key,value in {'ga':'G-2ZYSF0173P','gtm':'GTM-NV2WWQXB','ads':'ca-pub-9767176956440077','cf':'9f3423bb0d034d91bbe1a12afeff2429'}.items():
    HEAD = HEAD.replace('${IDS.'+key+'}',value)
    FALLBACK = FALLBACK.replace('${IDS.'+key+'}',value)
assert '${' not in HEAD+FALLBACK
ASSET_VERSION = hashlib.sha256(((ROOT/'src/app.js').read_text(encoding='utf-8')+(ROOT/'src/style.css').read_text(encoding='utf-8')).encode()).hexdigest()[:12]
URLS = {'ko':[], 'en':[]}
ICON = '<svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M3 4c4-1 6 0 9 2 3-2 5-3 9-2v15c-4-1-6 0-9 2-3-2-5-3-9-2zM12 6v15" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>'

def base(lang): return PATH + ('' if lang == 'ko' else 'en/')
def route(lang, version=None, book=None, chapter=None):
    return base(lang) + (version+'/' if version else '') + (book+'/'+str(chapter)+'/' if book else '')
def absolute(path): return 'https://nanalab.kr'+path
def preferred(lang): return sorted(VERSIONS,key=lambda v:v['language'] != lang)
def default(lang): return 'krv' if lang == 'ko' else 'web'
def chapter_title(lang, book, chapter): return f"{book[lang]} {chapter}" + ('장' if lang == 'ko' else '')
def version_picker(lang, current):
    t=T[lang]
    opts=''.join(f'<option value="{v["id"]}"'+(' selected' if v['id']==current else '')+f'>{H(v["name"])} · {v["abbreviation"]}</option>' for v in preferred(lang))
    return f'<label class="version-label">{t["version"]}<select data-version-picker aria-label="{t["version"]}">{opts}</select></label>'
def layout(lang, title, content, path, version=None, book=None, chapter=None, kind='home', other_path=None):
    t=T[lang]; canonical=absolute(path)
    other_lang='en' if lang=='ko' else 'ko'
    other_path=other_path or route(other_lang,version,book['slug'] if book else None,chapter)
    config=dict(labels={k:t[k] for k in ('copied','shareCopied','shared','actionFailed','missingVerse')},base=base(lang),version=version or default(lang),book=book['slug'] if book else None,bookName=book[lang] if book else None,chapter=chapter,versionName=BY_ID[version]['name'] if version else None,canonical=canonical,kind=kind)
    config_json=json.dumps(config,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    ui_paths={lang:path,other_lang:other_path}
    footer_languages=' · '.join(f'<a href="{H(ui_paths[l])}" data-preserve-hash lang="{l}"'+(' aria-current="page"' if l==lang else '')+f'>{LANG_NAMES[l]}</a>' for l in ('ko','en'))
    alternate=''.join(f'<link rel="alternate" hreflang="{l}" href="{H(absolute(p))}">' for l,p in sorted(ui_paths.items()))+f'<link rel="alternate" hreflang="x-default" href="{H(absolute(ui_paths["ko"]))}">'
    page=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H(title)} · {t['title']}</title><meta name="description" content="{H(title+' — '+t['chapterMeta'])}"><meta name="robots" content="index,follow"><link rel="canonical" href="{H(canonical)}">{alternate}<meta property="og:title" content="{H(title)}"><meta property="og:description" content="{H(t['chapterMeta'])}"><meta property="og:url" content="{H(canonical)}"><meta property="og:type" content="website"><link rel="icon" href="{PATH}icon.svg" type="image/svg+xml"><link rel="stylesheet" href="{PATH}style.css?v={ASSET_VERSION}">{HEAD}</head><body>{FALLBACK}<a class="skip" href="#main">{t['skip']}</a><header class="site-header"><a class="brand" href="{base(lang)}">{ICON}{t['title']}</a><nav class="header-links" aria-label="{t['home']}"><a href="{base(lang)}#books">{t['books']}</a><a href="{base(lang)}#versions">{t['allVersions']}</a></nav></header>{content}<footer class="page-footer"><a href="{base(lang)}licenses/">{t['copyright']}</a><a href="{base(lang)}privacy/">{t['privacy']}</a><span class="footer-languages" aria-label="{t['language']}">{footer_languages}</span><a class="more-apps" href="https://nanalab.kr/apps/">More Apps</a></footer><div id="status" class="toast" role="status" aria-live="polite"></div><dialog id="copy-dialog" aria-labelledby="copy-heading"><h2 id="copy-heading">{t['manualTitle']}</h2><p>{t['manualCopy']}</p><textarea readonly aria-label="{t['manualTitle']}"></textarea><button data-action="close-dialog">{t['close']}</button></dialog><script type="application/json" id="page-config">{config_json}</script><script src="{PATH}app.js?v={ASSET_VERSION}" defer></script></body></html>'''
    destination=OUT/path.removeprefix(PATH)/'index.html'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(page,encoding='utf-8')
    URLS[lang].append(canonical)

def home(lang, version=None):
    t=T[lang]; current=version or default(lang); v=BY_ID[current]
    groups=[]
    for testament in ('ot','nt'):
        rows=[]
        for book in BOOKS:
            if book['testament']!=testament:continue
            links=''.join(f'<a class="chapter-link" href="{route(lang,current,book["slug"],c)}" aria-label="{H(chapter_title(lang,book,c))}">{c}</a>' for c in range(1,book['chapters']+1))
            rows.append(f'<details class="book" data-search="{H((book["ko"]+" "+book["en"]+" "+book["code"]).lower())}"'+(' open' if book['code'] in ('GEN','MAT') else '')+f'><summary>{book[lang]}<small>{book["chapters"]} {t["chapter"]}</small></summary><div class="chapter-grid">{links}</div></details>')
        groups.append(f'<section class="testament"><h2>{t[testament]}</h2>'+''.join(rows)+'</section>')
    cards=''.join(f'<a class="version-card" href="{route(lang,x["id"])}"><span class="abbr">{x["abbreviation"]} · {LANG_NAMES[x["language"]]}</span><strong>{H(x["name"])}</strong><span>{t["booksCount"]} · {t["chaptersCount"]}</span></a>' for x in preferred(lang))
    info=(f'<p class="source-note">{H(v["creator"])} · <a href="{H(v["source"])}" rel="noopener">{t["source"]}</a> · <a href="{base(lang)}licenses/#{current}">{t["details"]}</a></p>' if version else '')
    title=v['name'] if version else t['read']
    content=f'''<main class="shell" id="main"><div class="home-top"><div><p class="eyebrow">{v['abbreviation']} · {LANG_NAMES[v['language']]}</p><h1>{H(title)}</h1><p class="lead">{t['subtitle']}</p></div>{version_picker(lang,current)}</div><div class="meta-line"><span class="tag">{t['booksCount']}</span><span class="tag">{t['chaptersCount']}</span><span>{H(v['name'])}</span></div>{info}<div class="section-heading" id="books"><h2>{t['books']}</h2><label>{t['filter']}<input class="book-filter" id="book-filter" type="search" placeholder="{t['filterHint']}" autocomplete="off"></label></div><p class="no-results" id="no-results" role="status" hidden>{t['noResults']}</p><div class="testament-grid">{''.join(groups)}</div><div class="section-heading" id="versions"><h2>{t['versions']}</h2><p>{t['versionsHint']}</p></div><div class="version-cards">{cards}</div></main>'''
    layout(lang,title,content,route(lang,version),version,kind='version' if version else 'home')

def reading(lang, version, book, chapter):
    t=T[lang]; v=BY_ID[version]; rows=DATA[version][book['code']][str(chapter)]
    title=chapter_title(lang,book,chapter)
    book_opts=''.join(f'<option value="{b["slug"]}"'+(' selected' if b['code']==book['code'] else '')+f'>{b[lang]}</option>' for b in BOOKS)
    chapter_opts=''.join(f'<option value="{c}"'+(' selected' if c==chapter else '')+f'>{c}</option>' for c in range(1,book['chapters']+1))
    side_chapters=''.join(f'<a href="{route(lang,version,book["slug"],c)}"'+(' aria-current="page"' if c==chapter else '')+f'>{c}</a>' for c in range(1,book['chapters']+1))
    verses=[]
    for number,text in rows:
        text_class='verse-text' if text else 'verse-text verse-note'
        verses.append(f'<article class="verse" id="v{number}" data-verse="{number}"><div class="verse-line"><a class="verse-number" href="#v{number}" aria-label="{H(title+":"+number)}">{number}</a><p class="{text_class}" lang="{v["language"] if text else lang}">{H(text or t["empty"])}</p></div><div class="verse-tools"><button data-action="copy" aria-label="{H(title+":"+number+" "+t["copy"])}">{t["copy"]}</button><button data-action="share" aria-label="{H(title+":"+number+" "+t["share"])}">{t["share"]}</button></div></article>')
    index=BOOKS.index(book); prev_book=book if chapter>1 else BOOKS[index-1] if index else None; next_book=book if chapter<book['chapters'] else BOOKS[index+1] if index<65 else None
    prev=(f'<a rel="prev" href="{route(lang,version,prev_book["slug"],chapter-1 if chapter>1 else prev_book["chapters"])}">← {t["previous"]} · {H(chapter_title(lang,prev_book,chapter-1 if chapter>1 else prev_book["chapters"]))}</a>' if prev_book else '<span></span>')
    nxt=(f'<a rel="next" href="{route(lang,version,next_book["slug"],chapter+1 if chapter<book["chapters"] else 1)}">{t["next"]} · {H(chapter_title(lang,next_book,chapter+1 if chapter<book["chapters"] else 1))} →</a>' if next_book else '<span></span>')
    opts=''.join(f'<option value="{number}">{number}</option>' for number,_ in rows)
    no_script_versions=' · '.join(f'<a href="{route(lang,x["id"],book["slug"],chapter)}">{x["abbreviation"]}</a>' for x in preferred(lang))
    content=f'''<main class="shell reader-shell" id="main"><nav class="breadcrumb" aria-label="{t['home']}"><a href="{base(lang)}">{t['home']}</a><span>/</span><a href="{route(lang,version)}">{v['abbreviation']}</a><span>/</span><span>{H(title)}</span></nav><div class="reader-layout"><aside class="reader-side"><form onsubmit="return false">{version_picker(lang,version)}<label>{t['book']}<select id="book-picker">{book_opts}</select></label><label>{t['chapter']}<select id="chapter-picker">{chapter_opts}</select></label></form><a class="side-title" href="{route(lang,version)}#books">{t['viewAll']} ↗</a><nav class="side-chapters" aria-label="{t['chapter']}">{side_chapters}</nav><noscript><p>{t['sameChapter']}: {no_script_versions}</p><a href="{route(lang,version)}">{t['viewAll']}</a></noscript></aside><section class="reading-area" aria-label="{H(title)}"><div class="chapter-heading"><div><p class="eyebrow">{v['abbreviation']}</p><h1>{H(title)}</h1><p class="edition">{H(v['name'])}</p></div><button data-action="theme" aria-pressed="false">{t['dark']}</button></div><div class="reading-tools"><label>{t['verse']}<select id="verse-picker">{opts}</select></label><button class="primary" data-action="share-selected">{t['shareVerse']}</button><button data-action="font-down" aria-label="{t['fontDown']}">A−</button><button data-action="font-up" aria-label="{t['fontUp']}">A+</button></div><div class="verses">{''.join(verses)}</div><nav class="chapter-nav" aria-label="{t['chapter']}">{prev}{nxt}</nav><p class="source-note">{H(v['creator'])} · <a href="{base(lang)}licenses/#{version}">{t['source']}: {H(v['name'])}</a><br>{t['sourceNote']}</p></section></div></main>'''
    layout(lang,title+' · '+v['abbreviation'],content,route(lang,version,book['slug'],chapter),version,book,chapter,kind='chapter')

def legal(lang):
    t=T[lang]
    notes={
      'ko':{'krv':'성경전서 개역한글판(대한성서공회, 1961). 대한성서공회는 저작재산권 보호기간 만료로 저작권료 없이 사용할 수 있다고 안내하며, 성명표시권과 동일성유지권 준수를 요구합니다. 디지털 본문은 thiagobodruk/bible의 ko_krv.json을 사용하며 MIT 고지를 함께 제공합니다. 원문의 합본 절·없음 표기도 보존합니다.', 'web':'본문은 Public Domain입니다. World English Bible은 eBible.org의 상표입니다. 본문을 변경한 결과물을 같은 이름으로 배포하지 않습니다. 개신교 66권 판본(engwebp)을 사용합니다.', 'bsb':'2023년 4월 30일 본문이 Public Domain으로 공개됐습니다. The Holy Bible, Berean Standard Bible, BSB is produced in cooperation with Bible Hub, Discovery Bible, unfoldingWord, Bible Aquifer, OpenBible.com, and the Berean Bible Translation Committee. 원문에 있는 고지를 보존합니다.', 'general':'본문은 Public Domain으로 명시된 해당 연도 판본의 eBible.org 배포 파일을 사용합니다. 최근 개정판이나 다른 출판사의 주석·삽화는 포함하지 않습니다.'},
      'en':{'krv':'Korean Revised Version (Korean Bible Society, 1961). The Korean Bible Society states that the economic copyright term has expired and requests respect for attribution and integrity rights. The digital text is ko_krv.json from thiagobodruk/bible, with its MIT notice preserved below. Source markers for combined or absent verses are retained.', 'web':'The text is Public Domain. World English Bible is a trademark of eBible.org. An altered text must not be distributed under that name. This reader uses the Protestant 66-book edition, engwebp.', 'bsb':'The text was dedicated to the public domain on April 30, 2023. The Holy Bible, Berean Standard Bible, BSB is produced in cooperation with Bible Hub, Discovery Bible, unfoldingWord, Bible Aquifer, OpenBible.com, and the Berean Bible Translation Committee. The source attribution is retained.', 'general':'The text is taken from the eBible.org distribution of the named public-domain edition. Later revisions and third-party commentary or artwork are not included.'}}
    sections=[]
    for v in VERSIONS:
        sections.append(f'<section id="{v["id"]}"><h2>{H(v["name"])} · {v["abbreviation"]}</h2><p>{H(notes[lang].get(v["id"],notes[lang]["general"]))}</p><p>{H(v["creator"])}<br>{H(v["license"])}</p><p><a href="{H(v["source"])}">{t["source"]}</a> · <a href="{H(v["license_url"])}">{t["copyright"]}</a> · <a href="{route(lang,v["id"])}">{t["read"]}</a></p></section>')
    mit=(ROOT/'data/source/thiagobodruk-LICENSE').read_text(encoding='utf-8')
    page=f'<main class="shell prose" id="main"><h1>{t["copyright"]}</h1><p>{t["licensesIntro"]}</p><p>{t["sourceDate"]}</p>{"".join(sections)}<section><h2>Digital source · MIT</h2><a href="https://github.com/thiagobodruk/bible">thiagobodruk/bible</a><pre>{H(mit)}</pre></section></main>'
    layout(lang,t['copyright'],page,base(lang)+'licenses/',kind='legal',other_path=base('en' if lang=='ko' else 'ko')+'licenses/')
    page=f'<main class="shell prose" id="main"><h1>{t["privacy"]}</h1><p>{t["privacyIntro"]}</p><p>{t["privacyTags"]}</p><p>{t["privacyInput"]}</p><p>{t["privacyControls"]}</p><ul><li><a href="https://policies.google.com/privacy">Google Privacy Policy</a></li><li><a href="https://www.cloudflare.com/privacypolicy/">Cloudflare Privacy Policy</a></li></ul></main>'
    layout(lang,t['privacy'],page,base(lang)+'privacy/',kind='legal',other_path=base('en' if lang=='ko' else 'ko')+'privacy/')

def main():
    OUT.mkdir(exist_ok=True)
    for filename in ('app.js','style.css','icon.svg'):(OUT/filename).write_bytes((ROOT/'src'/filename).read_bytes())
    for lang in ('ko','en'):
        home(lang)
        for version in VERSIONS:
            home(lang,version['id'])
            for book in BOOKS:
                for chapter in range(1,book['chapters']+1):reading(lang,version['id'],book,chapter)
        legal(lang)
        xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+H(url)+'</loc></url>' for url in URLS[lang])+'</urlset>\n'
        (OUT/f'sitemap-{lang}.xml').write_text(xml,encoding='utf-8')
    index='<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<sitemap><loc>{ORIGIN}/sitemap-{lang}.xml</loc></sitemap>' for lang in ('ko','en'))+'</sitemapindex>\n'
    (OUT/'sitemap.xml').write_text(index,encoding='utf-8')
    (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n',encoding='utf-8')
    (OUT/'ads.txt').write_text('google.com, pub-9767176956440077, DIRECT, f08c47fec0942fa0\n',encoding='utf-8')
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    report=dict(status='built',versions=len(VERSIONS),ui_languages=['ko','en'],chapter_pages=6*1189*2,version_pages=12,html_pages=sum(map(len,URLS.values())),sitemap_pages={k:len(v) for k,v in URLS.items()},html_bytes=sum(p.stat().st_size for p in OUT.rglob('*.html')))
    (ROOT/'evidence/build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
