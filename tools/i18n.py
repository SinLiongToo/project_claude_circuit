"""Traditional Chinese (zh-Hant) display for the pages in docs/.

Translations live in tools/zh/*.txt, one per line:   <hash><TAB><Chinese HTML>
The hash identifies the English block it replaces (FNV-1a of the block's whitespace-normalised
text), so a translation stops applying by itself when the English text changes, and the page then
shows English for that block until the line is updated. Lines starting with # are comments.

build.py calls write_page_js() for every page: docs/zh/<page>.js holds the translations of the
blocks found on that page and is only loaded by the browser when the reader switches to 中文.

Command line (from the repo root):
  python tools/i18n.py extract radar77-power.html   untranslated blocks of a page: <hash><TAB><English HTML>
  python tools/i18n.py status                       coverage per page
"""
import io, os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, '..', 'docs')
ZH_SRC = os.path.join(HERE, 'zh')

# Blocks that can be translated. The browser runs the same selector (see tools/find.html).
SEL = ('h1,h2,h3,h4,p,li,th,td,figcaption,summary,footer,dt,dd,option,.eyebrow,.note,.lede,'
       'nav.toc a,a.back,.row>span:first-child,.chart-legend span,span.domain,span.tag,.grp-h,.big-l,.k')
# a block with one of these inside would lose its controls or live values if its HTML were replaced
BLOCKERS = 'input,select,textarea,button,svg,canvas,script,[id]'
SKIP_IN = 'svg,script,style,pre,.eq,.find-ov,form .out'


def norm(t):
    return re.sub(r'\s+', ' ', t).strip()


def fnv(s):
    h = 0x811c9dc5
    b = s.encode('utf-16-le')
    for i in range(0, len(b), 2):
        h ^= b[i] | (b[i + 1] << 8)
        h = (h * 0x01000193) & 0xffffffff
    return '%08x' % h


def blocks(path):
    """[(hash, kind, english_html)] in page order; kind is 'html', 'text' (option) or 'label' (label caption)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(io.open(path, encoding='utf-8').read(), 'html.parser')
    out = []
    if soup.title:
        t = norm(soup.title.get_text())
        out.append((fnv(t), 'text', t))
    body = soup
    for el in body.select(SEL):
        if el.find_parent(['svg', 'script', 'style', 'pre']) or el.find_parent(class_=['eq', 'find-ov']):
            continue
        if el.name == 'td' and 'v' in (el.get('class') or []) and el.parent is not None and el.parent.get('data-abbr'):
            continue  # glossary abbreviation column stays as is
        if el.select_one(SEL) is not None and el.name != 'option':
            continue  # not a leaf: its children are translated one by one
        if el.name != 'option' and el.select_one(BLOCKERS) is not None:
            continue
        t = norm(el.get_text())
        if not re.search('[A-Za-z]{2}', t):
            continue
        kind = 'text' if el.name == 'option' else 'html'
        out.append((fnv(t), kind, norm(el.decode_contents()) if kind == 'html' else t))
    for lab in body.select('label'):
        if lab.find_parent(class_='find-ov'):
            continue
        first = next((c for c in lab.children if isinstance(c, str) and norm(c)), None)
        if first and re.search('[A-Za-z]{2}', first):
            t = norm(first)
            out.append((fnv(t), 'label', t))
    return out


def load_pool():
    pool = {}
    for f in sorted(glob.glob(os.path.join(ZH_SRC, '*.txt'))):
        for n, line in enumerate(io.open(f, encoding='utf-8'), 1):
            line = line.rstrip('\n')
            if not line.strip() or line.startswith('#'):
                continue
            m = re.fullmatch(r'([0-9a-f]{8})[ \t]+(\S.*)', line)
            if not m:
                sys.exit('%s:%d: expected <8-hex hash> <text>' % (f, n))
            pool[m.group(1)] = m.group(2).strip()
    return pool


def write_page_js(fname, pool, wr):
    """docs/zh/<page>.js with the translations of this page's blocks; returns (translated, total)."""
    import json
    bl = blocks(os.path.join(DOCS, fname))
    seen, data = set(), {}
    for h, _, _ in bl:
        if h in seen:
            continue
        seen.add(h)
        if h in pool:
            data[h] = pool[h]
    os.makedirs(os.path.join(DOCS, 'zh'), exist_ok=True)
    js = 'ZH_ADD(%s);\n' % json.dumps(data, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    wr(os.path.join(DOCS, 'zh', fname[:-5] + '.js'), js)
    return len(data), len(seen)


def pages():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(DOCS, 'radar77-*.html'))) + ['index.html']


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    pool = load_pool()
    if cmd == 'extract':
        done = set()
        for fname in sys.argv[2:]:
            for h, kind, en in blocks(os.path.join(DOCS, fname)):
                if h in pool or h in done:
                    continue
                done.add(h)
                sys.stdout.buffer.write(('%s\t%s%s\n' % (h, '' if kind == 'html' else '[%s] ' % kind, en)).encode('utf-8'))
    else:
        tot = [0, 0]
        for fname in pages():
            hs = {h for h, _, _ in blocks(os.path.join(DOCS, fname))}
            n = len(hs & set(pool))
            tot[0] += n; tot[1] += len(hs)
            print('%-34s %4d / %4d' % (fname, n, len(hs)))
        print('total %d / %d' % tuple(tot))
