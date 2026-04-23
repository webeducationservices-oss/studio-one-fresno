#!/usr/bin/env python3
"""Inject the universal footer into every .html file that doesn't have one.

Inserts the footer immediately before the closing <script> at the bottom of
the body, if missing. Idempotent.
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FOOTER_TEMPLATE = (ROOT / "content-export/footer-template.html").read_text()

# Preserve the exact homepage footer (index.html) — it already matches
SKIP_PATHS = {"index.html", "hair-extension-methods-fresno.html"}

# Pattern to find a closing </body> we can insert before, keeping any trailing
# <script> block intact.
# Strategy: insert the footer right before the FIRST <script src=".*script.js"> we find,
# OR if none, right before </body>.
updated = 0
already = 0
for html in sorted(ROOT.rglob("*.html")):
    rel = html.relative_to(ROOT)
    if "node_modules" in rel.parts or "content-export" in rel.parts:
        continue
    if str(rel) in SKIP_PATHS:
        continue

    s = html.read_text()

    # Skip if already has a <footer class="footer"
    if re.search(r'<footer\s+class="footer"', s):
        already += 1
        continue

    # Insert before the closing </body>, but AFTER any trailing <script> tags is wrong —
    # better: insert before the LAST <script src=".*script.js"> (the shared bottom script)
    # Fallback: insert just before </body>
    m = re.search(r'<script\s+src="[^"]*script\.js"[^>]*>\s*</script>', s)
    if m:
        new = s[:m.start()] + FOOTER_TEMPLATE + "\n\n  " + s[m.start():]
    else:
        # Fall back to inserting before </body>
        m2 = re.search(r'</body>', s)
        if not m2:
            continue  # skip malformed
        new = s[:m2.start()] + FOOTER_TEMPLATE + "\n" + s[m2.start():]

    html.write_text(new)
    updated += 1

print(f"Footer injected into {updated} files. Already had footer: {already}.")
