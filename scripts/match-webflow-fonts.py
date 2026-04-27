#!/usr/bin/env python3
"""Match the new site's font loading exactly to the live Webflow site.

Live Webflow uses:
  - Body: Arial, sans-serif  (no web font for body)
  - Headings: freight-big-pro from Typekit kit epq0gor

We were using:
  - Body: Inter (Google Fonts)
  - Headings: freight-big-pro from Typekit kit iqt4hfw  (different kit, possibly different weights)

This script swaps:
  1. iqt4hfw → epq0gor (Typekit URL, both .css and .js variants)
  2. --body-font: 'Inter', Arial, sans-serif → Arial, sans-serif
  3. Removes all Google Fonts Inter <link> tags + preconnects
  4. Updates inline font stacks that reference Inter
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")

OLD_KIT = 'iqt4hfw'
NEW_KIT = 'epq0gor'

INTER_GFONTS_PATTERNS = [
    # <link href="https://fonts.googleapis.com/css2?family=Inter..."> with various extras
    re.compile(r'\s*<link[^>]+fonts\.googleapis\.com/css2\?family=Inter[^>]*>\s*', re.IGNORECASE),
    # noscript wrapper
    re.compile(r'\s*<noscript>\s*<link[^>]+fonts\.googleapis\.com/css2\?family=Inter[^>]*>\s*</noscript>\s*', re.IGNORECASE),
]

# Also remove the unused Google Fonts preconnects (Typekit doesn't need them)
GFONT_PRECONNECT = re.compile(r'\s*<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\s*', re.IGNORECASE)

# Inter font-family stacks → swap to Arial
INTER_STACKS = [
    (re.compile(r"'Inter',\s*Arial,\s*sans-serif"), "Arial, sans-serif"),
    (re.compile(r'"Inter",\s*Arial,\s*sans-serif'), "Arial, sans-serif"),
    (re.compile(r"'Inter',\s*sans-serif"), "Arial, sans-serif"),
    (re.compile(r'"Inter",\s*sans-serif'), "Arial, sans-serif"),
    # When Inter appears alone in a font-family value
    (re.compile(r"font-family:\s*Inter,\s*sans-serif", re.IGNORECASE), "font-family: Arial, sans-serif"),
    (re.compile(r"font-family:\s*['\"]Inter['\"]", re.IGNORECASE), "font-family: Arial"),
]

updated_html = 0
updated_css = 0

# 1. Patch all HTML files
for html in sorted(ROOT.rglob("*.html")):
    rel = html.relative_to(ROOT)
    if "node_modules" in rel.parts or "content-export" in rel.parts:
        continue
    s = html.read_text()
    orig = s

    # Swap Typekit kit
    s = s.replace(OLD_KIT, NEW_KIT)

    # Remove Inter Google Fonts links (link + noscript)
    for pat in INTER_GFONTS_PATTERNS:
        s = pat.sub('\n', s)

    # Remove orphan Google Fonts preconnects (Typekit uses use.typekit.net, not fonts.gstatic.com)
    s = GFONT_PRECONNECT.sub('\n', s)

    # Swap font stacks
    for pat, repl in INTER_STACKS:
        s = pat.sub(repl, s)

    # Collapse triple+ blank lines that the removals leave behind
    s = re.sub(r'\n{4,}', '\n\n\n', s)

    if s != orig:
        html.write_text(s)
        updated_html += 1

print(f'HTML files updated: {updated_html}')

# 2. Patch styles.css and any other CSS
for css in sorted(ROOT.rglob("*.css")):
    rel = css.relative_to(ROOT)
    if "node_modules" in rel.parts or "content-export" in rel.parts:
        continue
    s = css.read_text()
    orig = s

    # Swap kit
    s = s.replace(OLD_KIT, NEW_KIT)

    # Swap font stacks
    for pat, repl in INTER_STACKS:
        s = pat.sub(repl, s)

    if s != orig:
        css.write_text(s)
        updated_css += 1
        print(f'  css updated: {rel}')

print(f'CSS files updated: {updated_css}')

# 3. Patch build scripts so future regens use the right fonts
for py in [ROOT / 'scripts/build-pages.py', ROOT / 'scripts/build-blog.py', ROOT / 'scripts/build-shop.py']:
    if not py.exists():
        continue
    s = py.read_text()
    orig = s
    s = s.replace(OLD_KIT, NEW_KIT)
    for pat, repl in INTER_STACKS:
        s = pat.sub(repl, s)
    # Remove Inter Google Fonts links inside template strings
    for pat in INTER_GFONTS_PATTERNS:
        s = pat.sub('', s)
    if s != orig:
        py.write_text(s)
        print(f'  build script updated: {py.name}')

print('\nDone. Site now uses Arial body + freight-big-pro headings (kit epq0gor) — exact match to live Webflow.')
