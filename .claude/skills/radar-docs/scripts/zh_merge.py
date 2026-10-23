"""Append Chinese lines to tools/zh/<target>.txt.

Usage: python zh_merge.py <lines.txt> <target-name>
Each input line: <8-hex hash> <Chinese HTML>. Hashes that match no block on any page are rejected
(usually a typo); blocks that already have a translation are skipped.
"""
import io, os, re, sys

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(R, 'tools'))
import i18n  # noqa: E402

part, target = sys.argv[1], sys.argv[2]
known = set()
for f in i18n.pages():
    for h, k, en in i18n.blocks(os.path.join(R, 'docs', f)):
        known.add(h)
pool = i18n.load_pool()
out, bad, dup = [], [], 0
for line in io.open(part, encoding='utf-8'):
    line = line.rstrip('\n')
    if not line.strip():
        continue
    m = re.fullmatch(r'([0-9a-f]{8})[ \t]+(\S.*)', line)
    if not m or m.group(1) not in known:
        bad.append(line[:60]); continue
    if m.group(1) in pool:
        dup += 1; continue
    pool[m.group(1)] = m.group(2)
    out.append('%s %s' % (m.group(1), m.group(2).strip()))
with io.open(os.path.join(R, 'tools', 'zh', target + '.txt'), 'a', encoding='utf-8', newline='\n') as f:
    for l in out:
        f.write(l + '\n')
print('added %d, skipped %d, rejected %d' % (len(out), dup, len(bad)))
for b in bad:
    print('  rejected:', b)
