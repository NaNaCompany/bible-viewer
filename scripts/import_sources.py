"""Reproducible import of attributed, public-domain Scripture text.

No AI-generated verses or inferred verse numbering. Text is preserved; source
layout/footnotes from the publisher's VPL export are not added to the text.
"""
import argparse
import collections
import concurrent.futures
import datetime
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/source'
VERSIONS = [
    dict(id='krv', name='개역한글판', abbreviation='KRV', language='ko', year=1961,
         creator='대한성서공회',
         source='https://github.com/thiagobodruk/bible/blob/master/json/ko_krv.json',
         license_url='https://www.bskorea.or.kr/bbs/board.php?bo_table=copyright_faq&wr_id=5',
         license='Public Domain; attribution and integrity rights respected',
         filename='ko_krv.json', download='https://raw.githubusercontent.com/thiagobodruk/bible/master/json/ko_krv.json'),
    dict(id='web', name='World English Bible', abbreviation='WEB', language='en', year=2025,
         creator='eBible.org / World English Bible translators', source='https://ebible.org/details.php?id=engwebp',
         license_url='https://ebible.org/engwebp/copyright.htm', license='Public Domain',
         filename='web.zip', download='https://ebible.org/Scriptures/engwebp_vpl.zip'),
    dict(id='bsb', name='Berean Standard Bible', abbreviation='BSB', language='en', year=2026,
         creator='Berean Bible Translation Committee; Bible Hub, Discovery Bible, unfoldingWord, Bible Aquifer, OpenBible.com',
         source='https://berean.bible/downloads.htm', license_url='https://berean.bible/terms.htm', license='Public Domain (CC0 dedication)',
         filename='bsb.txt', download='https://bereanbible.com/bsb.txt'),
    dict(id='asv', name='American Standard Version', abbreviation='ASV', language='en', year=1901,
         creator='American Revision Committee', source='https://ebible.org/details.php?id=eng-asv',
         license_url='https://ebible.org/eng-asv/copyright.htm', license='Public Domain',
         filename='asv.zip', download='https://ebible.org/Scriptures/eng-asv_vpl.zip'),
    dict(id='rv1909', name='Reina-Valera 1909', abbreviation='RV1909', language='es', year=1909,
         creator='Casiodoro de Reina, Cipriano de Valera; 1909 revision', source='https://ebible.org/details.php?id=spaRV1909',
         license_url='https://open.bible/bibles/reina-valera-1909', license='Public Domain',
         filename='rv1909.zip', download='https://ebible.org/Scriptures/spaRV1909_vpl.zip'),
    dict(id='lsg1910', name='Louis Segond 1910', abbreviation='LSG1910', language='fr', year=1910,
         creator='Louis Segond; 1910 revision', source='https://ebible.org/details.php?id=fraLSG',
         license_url='https://ebible.org/details.php?id=fraLSG', license='Public Domain',
         filename='lsg1910.zip', download='https://ebible.org/Scriptures/fraLSG_vpl.zip')
]
KO = '창세기 출애굽기 레위기 민수기 신명기 여호수아 사사기 룻기 사무엘상 사무엘하 열왕기상 열왕기하 역대상 역대하 에스라 느헤미야 에스더 욥기 시편 잠언 전도서 아가 이사야 예레미야 예레미야애가 에스겔 다니엘 호세아 요엘 아모스 오바댜 요나 미가 나훔 하박국 스바냐 학개 스가랴 말라기 마태복음 마가복음 누가복음 요한복음 사도행전 로마서 고린도전서 고린도후서 갈라디아서 에베소서 빌립보서 골로새서 데살로니가전서 데살로니가후서 디모데전서 디모데후서 디도서 빌레몬서 히브리서 야고보서 베드로전서 베드로후서 요한일서 요한이서 요한삼서 유다서 요한계시록'.split()
CODES = 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
EN = ['Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth','1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles','Ezra','Nehemiah','Esther','Job','Psalms','Proverbs','Ecclesiastes','Song of Solomon','Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi','Matthew','Mark','Luke','John','Acts','Romans','1 Corinthians','2 Corinthians','Galatians','Ephesians','Philippians','Colossians','1 Thessalonians','2 Thessalonians','1 Timothy','2 Timothy','Titus','Philemon','Hebrews','James','1 Peter','2 Peter','1 John','2 John','3 John','Jude','Revelation']
assert len(KO) == len(EN) == len(CODES) == 66

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0', 'Referer':'https://ebible.org/'}), timeout=90) as response:
        return response.read()

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--download', action='store_true')
    download = args.parse_args().download
    SOURCE.mkdir(parents=True, exist_ok=True)
    if download:
        def retrieve(version):
            (SOURCE / version['filename']).write_bytes(fetch(version['download']))
        with concurrent.futures.ThreadPoolExecutor(6) as pool:
            list(pool.map(retrieve, VERSIONS))
    # One official order and chapter count; English labels are presentation only.
    krv = json.loads((SOURCE / 'ko_krv.json').read_text(encoding='utf-8-sig'))
    books = [dict(code=code, slug=code.lower(), ko=ko, en=en, chapters=len(b['chapters']), testament='ot' if i < 39 else 'nt') for i,(code,ko,en,b) in enumerate(zip(CODES,KO,EN,krv))]
    (ROOT / 'data/books.json').write_text(json.dumps(books, ensure_ascii=False, separators=(',',':')), encoding='utf-8')
    by_name = {name: code for name,code in zip(EN,CODES)}
    by_name.update({'Psalm':'PSA', 'Song of Songs':'SNG'})
    report = []
    for version in VERSIONS:
        path = SOURCE / version['filename']
        grouped = {b['code']: {} for b in books}
        def add(code, chapter, verse, text):
            assert code in grouped and isinstance(text,str), (version['id'],code,chapter,verse)
            rows = grouped[code].setdefault(str(chapter), [])
            assert not any(r[0] == str(verse) for r in rows), (version['id'],code,chapter,verse,'duplicate')
            rows.append([str(verse), text])
        if version['id'] == 'krv':
            for book,meta in zip(krv,books):
                for chapter_number,chapter in enumerate(book['chapters'],1):
                    for verse_number,text in enumerate(chapter,1):
                        add(meta['code'], chapter_number, verse_number, text)
        elif version['id'] == 'bsb':
            for line in path.read_text(encoding='utf-8-sig').splitlines():
                match = re.match(r'^(.+?) (\d+):(\d+(?:-\d+)?)\t(.*)$', line)
                if not match:
                    assert not re.match(r'^.+? \d+:\d+', line), ('Unparsed BSB verse',line[:80])
                    continue
                book,chapter,verse,text = match.groups()
                add(by_name[book], int(chapter), verse, text)
        else:
            with zipfile.ZipFile(path) as archive:
                name = next(n for n in archive.namelist() if n.endswith('_vpl.txt'))
                for line in archive.read(name).decode('utf-8-sig').splitlines():
                    if not line: continue
                    match = re.fullmatch(r'([A-Z0-9]{3}) (\d+):([\d\-a-z]+) (.*)', line)
                    assert match, ('Unparsed VPL verse',line[:80])
                    code,chapter,verse,text = match.groups()
                    code = {'SOL':'SNG', 'EZE':'EZK', 'JOE':'JOL', 'NAH':'NAM', 'MAR':'MRK', 'JOH':'JHN', 'PHI':'PHP', 'JAM':'JAS', '1JO':'1JN', '2JO':'2JN', '3JO':'3JN'}.get(code,code)
                    add(code,int(chapter),verse,text)
                notice = next(n for n in archive.namelist() if n.endswith('_about.htm'))
                (SOURCE / (version['id']+'-license.html')).write_bytes(archive.read(notice))
        for book in books:
            assert list(map(int,grouped[book['code']])) == list(range(1,book['chapters']+1)), (version['id'],book['code'],'chapters')
            for chapter,rows in grouped[book['code']].items():
                numbers = [int(re.match(r'\d+',r[0])[0]) for r in rows]
                assert numbers == sorted(numbers) and len(numbers) == len(set(numbers)), (version['id'],book['code'],chapter,'order')
        payload = json.dumps(grouped,ensure_ascii=False,separators=(',',':'))
        (ROOT / 'data' / (version['id']+'.json')).write_text(payload, encoding='utf-8')
        row = dict(version, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), normalized_sha256=hashlib.sha256(payload.encode()).hexdigest(), books=66, chapters=sum(len(c) for c in grouped.values()), verses=sum(len(v) for c in grouped.values() for v in c.values()), empty_source_verses=sum(not row[1] for chapters in grouped.values() for rows in chapters.values() for row in rows))
        report.append(row)
    (ROOT / 'data/versions.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([dict(id=r['id'],books=r['books'],chapters=r['chapters'],verses=r['verses']) for r in report],ensure_ascii=False))

if __name__ == '__main__': main()
