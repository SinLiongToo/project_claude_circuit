---
name: radar-docs
description: Maintain the 77 GHz radar design-notes site in docs/ (GitHub Pages). Use for any change to its pages - new page or section, figure, calculator or simulator, Chinese translation, layout or style fix, glossary or knowledge-graph item, version bump, publish.
---

# 77 GHz radar design notes: how to change the site

Static site in `docs/`, published by GitHub Pages from `main` (`/docs`) at
https://sinliongtoo.github.io/project_claude_circuit/. Publish to GitHub only: never claude.ai artifacts, never a sync script.

## Every change, in this order

1. **Edit the source.** `docs/*.html` is the source of truth for page content (old generator scripts no longer exist). Shared parts live in `tools/` and are injected by the build:
   - `tools/find.html` + `tools/find.css`: search, theme and 中文/EN buttons, fixed top bar, figure enlarge, contents toggle. **find.html must contain exactly one `<script>`**: the build replaces from the search button to the first `</script>`, so a second script duplicates itself on every build.
   - `tools/glossary.py` (terms), `tools/graph.py` (knowledge-graph items, edges, `PAGES` keys), `tools/changelog.py`, `tools/i18n.py`.
2. **Build:** `python tools/build.py` (≈ 1 min, give it a 300 s timeout). It refreshes the search component, glossary, tabs, top bar, knowledge-graph data, changelog page, site search index, version stamp and `docs/zh/*.js`.
3. **Chinese:** list the untranslated blocks, write lines, merge, rebuild (see below).
4. **Version:** bump `VERSION` (minor = new content, patch = fix) and add an entry at the top of `LOG` in `tools/changelog.py` (no apostrophes inside the single-quoted strings; use "of" phrasing), then rebuild.
5. **Check:** `python .claude/skills/radar-docs/scripts/check.py`. It must print OK. Never commit after a failed build: OneDrive sometimes locks files and a partial build loses the search index on some pages.
6. **Look at it** in a browser (see Testing) for anything visual.
7. **Commit and push** every change, ending the message with the Co-Authored-By line.

## New page

- Copy the `<head>` and CSS of a similar page (e.g. `radar77-thermal.html`) up to `</style>`, then `<div class="wrap"><header class="top">` (eyebrow, h1, `p.lede`), `<div class="layout"><nav class="toc">` (one `<li>` per section + `a.back` links), `<main><section id="...">` with `div.sec-head` (`span.num`, h2, `span.domain`), and close `</main></div></div>`. Page scripts go after that.
- Register it: `PAGES` in `tools/build.py` (file + the TOC `<li>` the glossary link goes after), a card in the right group of `docs/index.html` (`<a class="item">` with `span.k`, h2, p; the sidebar is regenerated), and a `PAGES` key plus at least one item in `tools/graph.py` so the page gets its Knowledge graph tab.
- User preference: every general topic gets its own page and a card, not a subsection of a narrower page.

## Figures, charts, calculators

- Inline SVG with CSS variables only (`--ink`, `--muted`, `--line`, `--surface`, `--rf`, `--lo`, `--if`, `--dig`, `--test`, `--c1`, `--c2`, `--ok`, `--bad`). Blocks: `<rect class="blk if|lo|rf|dig">`, test hardware `class="tb"`; text `class="t"` (bold) or `class="s"` (mono, muted). Arrows use `marker-end="url(#ma)"` (one marker per page; the build dedupes). The build fails if a page uses an undefined variable or a `blk X` class without a stroke rule.
- Wrap in `<figure><div class="fig wide"><svg viewBox=... role="img" aria-label="...">` + `<figcaption>`. Every `main figure` and `.plot` automatically gets the square enlarge button.
- Check labels for overlap in a screenshot and fix positions before publishing; keep labels inside boxes.
- Calculators: `div.calc` with `div.panel` + `form.fields` (`label` text first, then the input) and a result panel of `.row` spans; recompute on input; verify the numbers by hand.
- Canvas plots: redraw on `themechange`, `langchange` and ResizeObserver; respect `prefers-reduced-motion` (no autoplay).

## Chinese (Traditional, Taiwan terms; abbreviations stay English)

- `tools/zh/*.txt`: one line per block, `<8-hex hash> <Chinese HTML>`. The hash is FNV-1a of the English block text, so edited English falls back to English until its line is updated.
- `python tools/i18n.py extract <page>.html` lists untranslated blocks; `python tools/i18n.py status` shows coverage.
- Write the lines to a new file, then `python .claude/skills/radar-docs/scripts/zh_merge.py <file> <target-name>`. It rejects unknown hashes (typos) and skips already translated ones.
- Keep inline links and `<b>` in the Chinese HTML. JS-generated text uses `L(en, zh)` or the `UI` map in find.html. Diagram labels, equations and changelog entries stay English.

## Testing in a browser (Windows, headless Edge)

- Run Edge from PowerShell: `Start-Process msedge.exe -ArgumentList "--headless=new","--disable-gpu","--user-data-dir=<fresh dir>","--hide-scrollbars","--window-size=1300,900","--virtual-time-budget=5000","--screenshot=<png>",<file url> -PassThru` then `.WaitForExit(90000)`.
- Pages with animation: add `--force-prefers-reduced-motion`, or the screenshot never finishes.
- To test behaviour, copy a page to `docs/_t.html` with an extra script that acts and writes results into an attribute, run with `--dump-dom`, then delete the copy. For Chinese mode, copy `docs/zh/<page>.js` to `docs/zh/_t.js` too, or open a redirect page that sets `localStorage.lang="zh"` first.
- Headless quirks: `requestAnimationFrame` does not run (shim it with `setTimeout`); smooth scrolling does not move (use `scrollTo({top, behavior:"instant"})`); screenshots ignore scroll position (use a tall window and crop with System.Drawing).
- Delete every `docs/_*` test file before committing.

## Other conventions

- Every page has: search (Ctrl+K), glossary (collapsed by default), Main page and Knowledge graph tabs, theme switch, 中文/EN switch, collapsible contents, fixed top bar after scrolling.
- Reply to the user in the language they wrote in (Chinese or English).
- Numbers are typical engineering values; say so in a footer and do not invent standard clause numbers.
