#!/usr/bin/env python3
"""Convert the 'Inside the Salon' grid into a horizontal scrolling ticker
matching the NBR Extensions one. Reuses .ticker / .ticker-track / .ticker-tile
pattern.
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FILE = ROOT / "meet-the-team.html"
s = FILE.read_text()

# Extract all images currently in the salon-gallery
section_match = re.search(r'<section class="salon-gallery-section".*?</section>', s, re.DOTALL)
if not section_match:
    print('× salon-gallery-section not found')
    raise SystemExit(1)

old_section = section_match.group(0)
imgs = re.findall(r'<img\s+src="([^"]+)"', old_section)
print(f'  {len(imgs)} images in current grid')

tiles = '\n'.join(f'        <div class="ticker-tile"><img src="{src}" alt="Inside Studio One salon" loading="lazy" decoding="async"></div>' for src in imgs)

new_section = f'''<section class="salon-gallery-section">
    <div class="salon-gallery-inner">
      <div class="salon-gallery-heading" data-animate>
        <span class="eyebrow">Our Space</span>
        <h2>Inside the Salon</h2>
      </div>
      <div class="ticker" data-animate>
        <div class="ticker-track">
{tiles}
{tiles}
        </div>
      </div>
    </div>
  </section>'''

s = s.replace(old_section, new_section)

# Add ticker CSS if not already present
if '.ticker-track{' not in s and '.ticker-track {' not in s:
    ticker_css = '''
    /* Scrolling ticker (shared with /nbr-extensions) */
    .salon-gallery-section .ticker{overflow:hidden;position:relative}
    .salon-gallery-section .ticker::before,.salon-gallery-section .ticker::after{content:"";position:absolute;top:0;bottom:0;width:120px;z-index:2;pointer-events:none}
    .salon-gallery-section .ticker::before{left:0;background:linear-gradient(90deg,var(--black),transparent)}
    .salon-gallery-section .ticker::after{right:0;background:linear-gradient(270deg,var(--black),transparent)}
    .ticker-track{display:flex;gap:12px;width:max-content;animation:ticker 90s linear infinite;will-change:transform}
    .ticker-track:hover{animation-play-state:paused}
    .ticker-tile{flex:0 0 auto;width:280px;height:280px;overflow:hidden;border-radius:4px;background:#1a1a1a}
    .ticker-tile img{width:100%;height:100%;object-fit:cover;display:block}
    @keyframes ticker{to{transform:translateX(-50%)}}
    @media(max-width:768px){.ticker-tile{width:200px;height:200px}}
'''
    s = s.replace('  </style>\n</head>', ticker_css + '  </style>\n</head>', 1)

FILE.write_text(s)
print(f'✓ Converted {len(imgs)}-image grid → scrolling ticker')
