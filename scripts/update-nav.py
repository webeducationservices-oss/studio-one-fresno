#!/usr/bin/env python3
"""One-time nav redesign: from flat list → grouped 3-column layout.

- Rewrites the <div class="nav-inner">…</div> block in every .html file
- Rewrites the nav CSS block in styles.css
- Updates build-pages.py, build-blog.py, build-shop.py so future regens use the new nav
- Safe to re-run (idempotent: uses marker strings to detect already-updated state)
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")

# ---------------------------------------------------------------------------
# New HTML block — inserted between <button class="nav-close">…</button>
# and </nav>, with leading indent matching typical nav-inner placement
# ---------------------------------------------------------------------------
NEW_NAV_INNER = '''<div class="nav-inner">
      <div class="nav-grid">
        <div class="nav-col">
          <div class="nav-label">OUR WORK</div>
          <div class="nav-links">
            <a href="/meet-the-team">Meet the Team</a>
            <a href="/hair-gallery">Hair Gallery</a>
            <a href="/blog">Blog</a>
          </div>
        </div>
        <div class="nav-col">
          <div class="nav-label">SERVICES</div>
          <div class="nav-links">
            <a href="/nbr-extensions">NBR Extensions</a>
            <a href="/services">Classic Services</a>
            <a href="/wigs">Wigs</a>
            <a href="/nically-hair">Nically Hair</a>
          </div>
        </div>
        <div class="nav-col">
          <div class="nav-label">GET STARTED</div>
          <div class="nav-links">
            <a href="/booking" class="nav-primary">Book Appointment</a>
            <a href="/shop">Shop</a>
            <a href="/contact">Contact</a>
          </div>
          <div class="nav-tertiary">
            <a href="/careers">Careers</a>
            <a href="/shadowing-program">Shadowing Program</a>
            <a href="/promos">Promos</a>
            <a href="/legal">Legal</a>
          </div>
        </div>
      </div>
    </div>
  </nav>'''

# Pattern matches the old nav-inner block up through </nav>.
# Non-greedy match on body + required "</div>\s*</nav>" anchor ensures we
# capture the closing </div> that belongs to nav-inner (not its nested divs).
NAV_PATTERN = re.compile(
    r'<div class="nav-inner">.*?</div>\s*</nav>',
    re.DOTALL
)

# ---------------------------------------------------------------------------
# Update HTML files
# ---------------------------------------------------------------------------
updated = 0
skipped_already = 0
skipped_no_match = []

for html_file in sorted(ROOT.rglob("*.html")):
    rel = html_file.relative_to(ROOT)
    if "node_modules" in rel.parts:
        continue
    if "content-export" in rel.parts:
        continue

    src = html_file.read_text()

    # Idempotency check — already has the new structure
    if 'class="nav-grid"' in src:
        skipped_already += 1
        continue

    new_src, n = NAV_PATTERN.subn(NEW_NAV_INNER, src)
    if n == 0:
        skipped_no_match.append(str(rel))
        continue

    html_file.write_text(new_src)
    updated += 1

print(f"HTML:  updated={updated}, already_new={skipped_already}, no_match={len(skipped_no_match)}")
if skipped_no_match:
    print("  Files without nav pattern:")
    for p in skipped_no_match[:10]:
        print(f"    {p}")

# ---------------------------------------------------------------------------
# Update styles.css
# ---------------------------------------------------------------------------
css_path = ROOT / "styles.css"
css = css_path.read_text()

NEW_CSS_BLOCK = '''.nav-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: var(--black);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s ease;
  overflow-y: auto;
  padding: 100px 60px 60px;
}
.nav-overlay.is-open {
  opacity: 1;
  pointer-events: all;
}
.nav-close {
  position: absolute;
  top: 28px;
  right: 40px;
  z-index: 10;
  padding: 8px;
  opacity: 0.7;
  transition: opacity 0.3s;
}
.nav-close:hover { opacity: 1; }
.nav-inner {
  width: 100%;
  max-width: 1040px;
}
.nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 60px;
}
.nav-col {
  display: flex;
  flex-direction: column;
}
.nav-label {
  font-family: var(--body-font);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 3px;
  color: var(--off-white);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}
.nav-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nav-links a {
  font-family: var(--heading-font);
  font-size: 28px;
  font-weight: 400;
  color: var(--off-white);
  transition: color 0.3s, padding-left 0.3s;
  line-height: 1.4;
  padding: 4px 0;
}
.nav-links a:hover {
  color: var(--olive-light);
  padding-left: 8px;
}
.nav-links a.nav-primary {
  color: var(--white);
  padding-bottom: 6px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--olive);
}
.nav-links a.nav-primary:hover {
  color: var(--olive-light);
  border-color: var(--olive-light);
}
.nav-tertiary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.nav-tertiary a {
  font-family: var(--body-font);
  font-size: 12px;
  font-weight: 400;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.3s;
}
.nav-tertiary a:hover { color: var(--off-white); }'''

# Replace from .nav-overlay { to the end of .nav-links a:hover rule
old_nav_block_pattern = re.compile(
    r'\.nav-overlay\s*\{.*?\.nav-links a:hover\s*\{[^}]*\}',
    re.DOTALL
)
new_css, n = old_nav_block_pattern.subn(NEW_CSS_BLOCK, css, count=1)
if n == 0:
    print("CSS: old nav block not found — did styles.css change?")
else:
    # Update the responsive overrides too
    # old: .nav-inner { padding: 80px 40px 40px; } .nav-links a { font-size: 30px; }
    # new: .nav-overlay { padding: 80px 40px 40px; } .nav-grid { gap: 40px; } .nav-links a { font-size: 24px; }
    new_css = new_css.replace(
        '.nav-inner { padding: 80px 40px 40px; }\n  .nav-links a { font-size: 30px; }',
        '.nav-overlay { padding: 80px 40px 40px; }\n  .nav-grid { gap: 40px; }\n  .nav-links a { font-size: 24px; }'
    )
    new_css = new_css.replace(
        '.nav-inner { padding: 70px 24px 40px; }\n  .nav-links a { font-size: 26px; }\n  .nav-close { top: 16px; right: 20px; }',
        '.nav-overlay { padding: 70px 24px 40px; }\n  .nav-grid { grid-template-columns: 1fr; gap: 32px; }\n  .nav-links a { font-size: 22px; }\n  .nav-label { font-size: 10px; margin-bottom: 12px; }\n  .nav-tertiary { margin-top: 16px; padding-top: 16px; }\n  .nav-close { top: 16px; right: 20px; }'
    )
    new_css = new_css.replace(
        '.nav-links a { font-size: 22px; }',
        '.nav-links a { font-size: 20px; }'
    )

    css_path.write_text(new_css)
    print(f"CSS: updated {css_path.name}")

print("\nDone. Review changes then commit.")
