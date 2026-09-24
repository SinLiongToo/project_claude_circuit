"""Rebuild the shared parts of every page in docs/.

Run after editing any page:  python tools/build.py

1. Refreshes the search component (tools/find.css + tools/find.html) in each page.
2. Regenerates the glossary section and auto-link script (tools/glossary.py) and
   renumbers the sections.
3. Rebuilds the cross-page search index and embeds it in each page, so search
   covers every page without fetching anything at runtime.

Requires: beautifulsoup4.
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, '..', 'docs')
sys.path.insert(0, HERE)
os.chdir(DOCS)
import glossary  # noqa: E402  (uses cwd = docs)
from bs4 import BeautifulSoup  # noqa: E402

# page file, TOC entry the glossary link goes after
PAGES = [
    ('radar77-signal-chain.html', '<li><a href="#verify">Verification</a></li>'),
    ('radar77-bist-loopback.html', '<li><a href="#checklist">Design checklist</a></li>'),
    ('radar77-continuity.html', '<li><a href="#data">Data &amp; test flow</a></li>'),
    ('radar77-dft-stress.html', '<li><a href="#checklist">DFT checklist</a></li>'),
]

rd = lambda p: io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)

FIND_CSS = rd(os.path.join(HERE, 'find.css'))
FIND_HTML = rd(os.path.join(HERE, 'find.html'))


def refresh_search(s):
    # CSS: from "/* page search */" up to "/* glossary */" (or </style>)
    if '/* page search */' in s:
        s = re.sub(r'/\* page search \*/.*?(?=/\* glossary \*/|</style>)', lambda m: FIND_CSS, s, count=1, flags=re.S)
    else:
        i = s.index('</style>'); s = s[:i] + FIND_CSS + s[i:]
    # HTML + script: from the search button to the end of its script
    s = re.sub(r'\n?<script type="application/json" id="siteIndex".*?</script>\n', '\n', s, flags=re.S)
    m = re.search(r'\n<button class="find-btn".*?</script>\n', s, flags=re.S)
    if m:
        s = s[:m.start()] + FIND_HTML + s[m.end():]
    else:
        s = s.rstrip('\n') + '\n' + FIND_HTML
    return s


SEL = 'h2,h3,p,li,tr,.eq,figcaption,dt,dd,.note,footer'

def norm(t):
    return re.sub(r'\s+', ' ', t).strip()

def page_items(fname):
    soup = BeautifulSoup(rd(fname), 'html.parser')
    title = soup.title.get_text() if soup.title else fname
    items = []
    lede = soup.select_one('header.top .lede')
    if lede:
        items.append({'p': fname, 'id': '', 'n': '', 's': 'Introduction', 't': norm(lede.get_text())})
    for sec in soup.select('main section'):
        sid = sec.get('id') or ''
        if sid == 'glossary':
            continue  # identical on every page; each page searches its own copy
        h2 = sec.find('h2'); num = sec.select_one('.num')
        st = norm(h2.get_text()) if h2 else ''
        n = norm(num.get_text()) if num else ''
        for el in sec.select(SEL):
            if el.find_parent(['svg', 'form']) or el.find_parent(class_='out'):
                continue
            if el.name == 'p' and (el.find_parent('li') or el.find_parent(class_='note')):
                continue
            if el.name == 'tr' and el.find('th'):
                continue
            t = norm(el.get_text(' '))
            t = re.sub(r'\s+([,.;:)])', r'\1', t)
            if len(t) < 2:
                continue
            it = {'p': fname, 'id': sid, 'n': n, 's': st, 't': t}
            if el.name in ('h2', 'h3'):
                it['h'] = 1
            items.append(it)
        for svg in sec.select('figure svg'):
            t = ' · '.join(norm(x.get_text()) for x in svg.find_all('text') if norm(x.get_text()))
            if t:
                items.append({'p': fname, 'id': sid, 'n': n, 's': st, 't': 'Diagram: ' + t})
    return title, items


def main():
    # 1 + 2: search component and glossary
    for fname, toc_after in PAGES:
        wr(fname, refresh_search(rd(fname)))
        glossary.inject(fname, None, toc_after)
    # 3: site index
    pages, items = {}, []
    for fname, _ in PAGES:
        title, its = page_items(fname)
        pages[fname] = {'title': title, 'url': fname}
        items += its
    for fname, _ in PAGES:
        blob = json.dumps({'pages': pages, 'items': [i for i in items if i['p'] != fname]},
                          ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        tag = '<script type="application/json" id="siteIndex" data-self="%s">%s</script>\n' % (fname, blob)
        s = rd(fname)
        i = s.index('\n<button class="find-btn"')
        s = s[:i + 1] + tag + s[i + 1:]
        wr(fname, s)
        print('%-28s index of other pages: %5.1f kB' % (fname, len(blob.encode('utf-8')) / 1024))
    print('items:', len(items))


if __name__ == '__main__':
    main()
