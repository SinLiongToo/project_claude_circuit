"""Site check to run after `python tools/build.py` and before committing. Prints OK or the problems.

Checks: every page in build.py PAGES exists and has the search index; main-page cards and PAGES agree;
the version stamp matches VERSION; links and #anchors resolve; ids are unique; no leftover docs/_* test
files; every inline script and docs/zh/*.js passes `node --check` (if node is installed); translation
lines refer to real blocks.
"""
import collections, glob, io, os, re, shutil, subprocess, sys, tempfile

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
D = os.path.join(R, 'docs')
sys.path.insert(0, os.path.join(R, 'tools'))
problems = []
rd = lambda p: io.open(p, encoding='utf-8').read()

build = rd(os.path.join(R, 'tools', 'build.py'))
plist = re.findall(r"\('(radar77-[^']+\.html)',", build)
pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(D, 'radar77-*.html')))
if sorted(set(plist)) != pages:
    problems.append('build.py PAGES vs pages on disk: missing %s, extra %s' % (sorted(set(pages) - set(plist)), sorted(set(plist) - set(pages))))
txt = {p: rd(os.path.join(D, p)) for p in pages + ['index.html']}
cards = re.findall(r'<a class="item" href="([^"]+)"', txt['index.html'])
if sorted(cards) != pages:
    problems.append('main-page cards vs pages: missing %s, extra %s' % (sorted(set(pages) - set(cards)), sorted(set(cards) - set(pages))))
for p, s in txt.items():
    if 'id="siteIndex"' not in s:
        problems.append('%s: no search index (partial build?)' % p)
ver = rd(os.path.join(R, 'VERSION')).strip()
st = re.search(r'<!--stamp-->Version ([0-9.]+)', txt['index.html'])
if not st or st.group(1) != ver:
    problems.append('version stamp %s != VERSION %s (rebuild)' % (st.group(1) if st else None, ver))

ids = {p: set(re.findall(r'\sid="([^"]+)"', re.sub(r'<script\b.*?</script>', '', s, flags=re.S))) for p, s in txt.items()}
for p, s in txt.items():
    body = re.sub(r'<script\b.*?</script>', '', s, flags=re.S)
    dup = [k for k, v in collections.Counter(re.findall(r'\sid="([^"]+)"', body)).items() if v > 1]
    if dup:
        problems.append('%s: duplicate ids %s' % (p, dup[:6]))
    for href in re.findall(r'href="([^"]+)"', body):
        if href.startswith(('http://', 'https://', 'mailto:')):
            continue
        f, _, a = href.partition('#')
        tgt = f or p
        if tgt not in txt:
            problems.append('%s: link to missing page %s' % (p, href))
        elif a and not a.startswith(('p=', 'n=')) and a not in ids[tgt]:
            problems.append('%s: missing anchor %s' % (p, href))

left = glob.glob(os.path.join(D, '_*')) + glob.glob(os.path.join(D, 'zh', '_*'))
if left:
    problems.append('leftover test files: %s' % [os.path.relpath(x, R) for x in left])

if shutil.which('node'):
    tmp = os.path.join(tempfile.gettempdir(), 'radar_check.js')
    for p, s in txt.items():
        for i, m in enumerate(re.finditer(r'<script(?![^>]*type="application/json")[^>]*>(.*?)</script>', s, re.S)):
            io.open(tmp, 'w', encoding='utf-8').write(m.group(1))
            r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
            if r.returncode:
                problems.append('%s script %d: %s' % (p, i, r.stderr.strip().splitlines()[-1][:160]))
    for j in glob.glob(os.path.join(D, 'zh', '*.js')):
        r = subprocess.run(['node', '--check', j], capture_output=True, text=True)
        if r.returncode:
            problems.append('%s: syntax error' % os.path.relpath(j, R))

import i18n  # noqa: E402
known = set()
for f in i18n.pages():
    known.update(h for h, _, _ in i18n.blocks(os.path.join(D, f)))
stale = [h for h in i18n.load_pool() if h not in known]
print('translations: %d lines, %d no longer match any block (English changed or removed)' % (len(i18n.load_pool()), len(stale)))

if problems:
    print('PROBLEMS:')
    for x in problems:
        print('  -', x)
    sys.exit(1)
print('OK: %d pages, version %s' % (len(pages), ver))
