#!/usr/bin/env python3
"""Make the homepage gallery match /hair-gallery behavior:
- All 15 existing photos retagged data-category="extensions"
- Append 6 color photos from /images/gallery-color/
- Empty 'Coming Soon' state when Keratin filter is selected
- Updates filter button labels
- Patches script.js to wire empty-state toggle into the existing filter handler
"""
import re
from pathlib import Path

ROOT = Path('/Users/justinbabcock/Desktop/Websites/studio-one-fresno')
INDEX = ROOT / 'index.html'
SCRIPT = ROOT / 'script.js'

s = INDEX.read_text()

# 1. Re-tag all data-category values inside gallery-item div tags
def retag(m):
    return re.sub(r'data-category="[^"]*"', 'data-category="extensions"', m.group(0))
s = re.sub(r'<div class="gallery-item"[^>]*>', retag, s)

# 2. Update the filter button labels (kept the data-filter values pointing to
#    'extensions' / 'color' / 'keratin' for clarity)
s = s.replace(
    '<button class="filter-btn" data-filter="nbr">NBR EXTENSIONS</button>',
    '<button class="filter-btn" data-filter="extensions">EXTENSIONS</button>'
)

# 3. Append 6 Luxury Color photos right before the gallery-grid closes
NEW_COLOR_TILES = '\n'.join([
    f'        <div class="gallery-item" data-category="color" data-animate="fade-up" data-delay="{i % 3}">\n'
    f'          <div class="gallery-pair">\n'
    f'            <img src="images/gallery-color/color-{i}.webp" alt="Luxury hair color transformation, Studio One Fresno" loading="lazy" width="800" height="800" decoding="async">\n'
    f'          </div>\n'
    f'          <button class="gallery-expand"><img src="images/optimized/expand.svg" alt="Expand"></button>\n'
    f'        </div>'
    for i in range(1, 7)
])

# Insert before closing </div> of gallery-grid (the </div> right after the last gallery-item)
# Find the last </div> that follows a '.gallery-item' — and insert before the </div>
last_gallery_item_idx = s.rfind('class="gallery-item"')
# From there, find the closing </div> of the LAST gallery-item, then the next </div> closes the grid
# Walk forward: count opens/closes from last_gallery_item_idx
open_div = last_gallery_item_idx
# Find the </div> that closes the last gallery-item (1 level deep from "<div class=\"gallery-item\"")
end_of_last_item = s.find('</div>', s.find('</div>', open_div) + 6) + len('</div>')
# After this end, the very next </div> closes the .gallery-grid
grid_close_idx = s.find('</div>', end_of_last_item)
if grid_close_idx > 0:
    s = s[:grid_close_idx] + NEW_COLOR_TILES + '\n      ' + s[grid_close_idx:]

# 4. Add the empty state right after the gallery-grid closing </div> (and inside .gallery-inner)
EMPTY_STATE = '''
      <div id="homeGalleryEmpty" class="gallery-empty" hidden>
        <p class="eyebrow">Coming Soon</p>
        <h3>Keratin Treatment gallery is on the way.</h3>
        <p>We're collecting fresh before-and-afters of our keratin smoothing &amp; Brazilian Blowout work in Fresno. Check back soon &mdash; or <a href="/services" style="color:var(--olive-light);border-bottom:1px solid var(--olive)">read about the service</a> in the meantime.</p>
      </div>
'''
# Insert before the closing </div> of .gallery-inner (the one before </section>)
s = re.sub(
    r'(</div>\s*</section>\s*<!-- Gallery Modal)',
    EMPTY_STATE + r'    \1',
    s, count=1
)

# 5. Add CSS for the empty state and styling tweaks (only once)
if '.gallery-empty.is-shown' not in s:
    css = '''
    .section-gallery .gallery-empty{display:none;padding:80px 24px 40px;text-align:center;max-width:640px;margin:0 auto}
    .section-gallery .gallery-empty.is-shown{display:block}
    .section-gallery .gallery-empty .eyebrow{font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:var(--olive-light);margin-bottom:16px;display:block}
    .section-gallery .gallery-empty h3{font-family:var(--heading-font);font-size:28px;color:var(--white);font-weight:400;line-height:1.25;margin-bottom:14px}
    .section-gallery .gallery-empty p{font-size:14px;color:var(--light-gray);font-weight:300;line-height:1.7}'''
    # Inject right before the closing </style> of the inline critical CSS in <head>
    s = s.replace('</style>\n\n  <!-- Defer full stylesheet -->', css + '\n  </style>\n\n  <!-- Defer full stylesheet -->', 1)

INDEX.write_text(s)
print(f'index.html: re-tagged + 6 color tiles + empty state')

# 6. Patch script.js — extend the gallery filter to toggle the empty state
js = SCRIPT.read_text()
NEW_FILTER_JS = '''/* ===== Gallery Filter ===== */
(function () {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const items = document.querySelectorAll('.gallery-item');
  const empty = document.getElementById('homeGalleryEmpty');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      let visible = 0;

      items.forEach(item => {
        const match = filter === 'all' || item.dataset.category === filter;
        if (match) {
          item.classList.remove('hidden');
          item.style.display = '';
          visible++;
        } else {
          item.classList.add('hidden');
          item.style.display = 'none';
        }
      });

      if (empty) {
        empty.hidden = visible !== 0;
        empty.classList.toggle('is-shown', visible === 0);
      }
    });
  });
})();'''

old = re.compile(r'/\* ===== Gallery Filter ===== \*/\s*\(function \(\) \{[\s\S]*?\}\)\(\);', re.DOTALL)
js2, n = old.subn(NEW_FILTER_JS, js, count=1)
if n == 0:
    print('  ! Could not find Gallery Filter IIFE in script.js')
else:
    SCRIPT.write_text(js2)
    print(f'script.js: filter handler patched to toggle empty state')

# Quick stats
import re as _re
ext = len(_re.findall(r'data-category="extensions"', s))
col = len(_re.findall(r'data-category="color"', s))
ker = len(_re.findall(r'data-category="keratin"', s))
print(f'\nFinal counts:  extensions={ext}, color={col}, keratin={ker}')
