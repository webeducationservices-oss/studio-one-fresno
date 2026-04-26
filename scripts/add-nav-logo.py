#!/usr/bin/env python3
"""Add the Studio One logo to the menu overlay (linked to /).

Inserts a logo block before the .nav-grid in every page's <nav class="nav-overlay">.
Idempotent — skips files that already have .nav-logo.
Also updates the 3 build scripts so future regens include it.
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")

LOGO_HTML = '''<a href="/" class="nav-logo" aria-label="Studio One — back to home">
        <img src="/images/optimized/logo.avif" alt="Studio One Hair Design" width="180" height="34">
      </a>
      '''

# CSS to append to styles.css
LOGO_CSS = '''

/* Menu overlay logo */
.nav-logo{display:inline-block;margin-bottom:48px;opacity:.95;transition:opacity .3s ease}
.nav-logo:hover{opacity:1}
.nav-logo img{height:36px;width:auto;display:block}
@media (max-width:768px){
  .nav-logo{margin-bottom:32px}
  .nav-logo img{height:30px}
}
'''

# Pattern: inject logo right before <div class="nav-grid">, inside .nav-inner
inject_pat = re.compile(
    r'(<div class="nav-inner">\s*)(<div class="nav-grid">)',
    re.DOTALL
)

updated = skipped = 0
for html in sorted(ROOT.rglob("*.html")):
    rel = html.relative_to(ROOT)
    if "node_modules" in rel.parts or "content-export" in rel.parts:
        continue
    s = html.read_text()
    if 'class="nav-logo"' in s:
        skipped += 1
        continue
    new = inject_pat.sub(r'\1' + LOGO_HTML + r'\2', s, count=1)
    if new == s:
        # Pattern didn't match — page might not have nav-inner/nav-grid (only on legacy pages)
        continue
    html.write_text(new)
    updated += 1

print(f"Pages updated: {updated} | already had logo: {skipped}")

# Append CSS to styles.css if not already present
css = ROOT / "styles.css"
csstxt = css.read_text()
if '.nav-logo{' not in csstxt:
    css.write_text(csstxt + LOGO_CSS)
    print("✓ Added .nav-logo CSS to styles.css")
else:
    print("• .nav-logo CSS already present")

# Update build scripts so regens include it
for script_path in ['scripts/build-pages.py', 'scripts/build-blog.py', 'scripts/build-shop.py']:
    p = ROOT / script_path
    if not p.exists():
        continue
    src = p.read_text()
    if 'class="nav-logo"' in src:
        continue
    # Same regex approach as above
    new = inject_pat.sub(r'\1' + LOGO_HTML + r'\2', src, count=1)
    if new != src:
        p.write_text(new)
        print(f'✓ Updated {script_path}')
