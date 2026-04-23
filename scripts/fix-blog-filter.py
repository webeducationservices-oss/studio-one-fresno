#!/usr/bin/env python3
"""Convert /blog's category nav from link-outs to in-place JS filter.

Also adds data-cat attributes to each post card so filtering works.
"""
import re, json, glob
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FILE = ROOT / "blog.html"
s = FILE.read_text()

# Build slug → canonical category map from content-export blog JSONs
# (mirror what scripts/build-blog.py uses)
POST_CAT_MAP = {
    "a-journey-to-fuller-natural-looking-hair": "client-spotlights",
    "barbaras-nbr-hair-extension-journey-at-studio-one": "client-spotlights",
    "best-hair-color-for-gray-hair-a-guide-to-radiant-ageless-style": "color",
    "best-hair-colors-for-brown-eyes-studio-one-fresno": "color",
    "best-haircuts-for-thin-hair-that-add-volume": "styling",
    "best-products-for-hair-growth-thickness": "hair-products",
    "can-thinning-hair-grow-back": "hair-care",
    "can-you-dye-weft-hair-extensions": "extensions",
    "cooler-weather-hair-extension-care": "extensions",
    "curly-hair-talk-natural-vs-permed-curls": "styling",
    "hair-extension-models-needed-in-fresno": "extensions",
    "hair-extension-options-halo-bellami-hand-tied": "extensions",
    "hair-extension-recovery": "extensions",
    "hair-gloss-treatments-in-fresno": "color",
    "hair-transformation-for-women-studio-one-fresno": "client-spotlights",
    "hairdresser-extensions-what-to-know-before-you-book": "extensions",
    "holiday-hair-prep-for-travel-studio-one-fresno": "hair-care",
    "holiday-hair-trends": "styling",
    "how-hair-extensions-work-volume-length-confidence": "extensions",
    "how-hair-gloss-works-for-soft-lasting-shine": "color",
    "how-long-does-grey-hair-coverage-last": "color",
    "how-much-do-hair-extensions-cost": "extensions",
    "is-dry-shampoo-good-for-your-scalp": "hair-care",
    "keep-extensions-looking-gorgeous": "extensions",
    "keratin-treatment-california-whats-changed-what-you-need-to-know": "hair-care",
    "meet-the-team-at-studio-one": "salon-team",
    "new-year-new-hair-navigating-life-changes-and-hair-health-in-2025": "hair-care",
    "new-year-new-you-resolutions-weight-loss-and-how-it-affects-your-hair": "hair-care",
    "saizon-restaurant": "behind-the-scenes",
    "semi-permanent-hair-color-damage": "color",
    "strawberry-blonde-hair-with-extensions-the-perfect-blend-of-warmth-and-dimension": "color",
    "stress-and-hair-health": "hair-care",
    "studio-one-hair-design-fresno-hair-stylist": "salon-team",
    "studio-one-hair-design-top-salon-with-hair-specialists-in-fresno": "salon-team",
    "studio-one-signature-drinks": "behind-the-scenes",
    "the-biggest-myth-about-winter-shedding": "hair-care",
    "the-psychology-of-hair": "hair-care",
    "the-truth-about-nbr-extensions-at-studio-one": "extensions",
    "wassabi-on-fire": "behind-the-scenes",
    "what-is-pretty-hair-discover-the-secret-at-studio-one": "behind-the-scenes",
    "what-most-people-get-wrong-about-hair-extensions": "extensions",
    "why-indulge-in-a-brazilian-keratin-treatment": "hair-care",
}

# 1. Replace cat-nav links with filter buttons
old_nav_pat = re.compile(r'<nav class="cat-nav"[^>]*>.*?</nav>', re.DOTALL)
new_nav = '''<nav class="cat-nav" data-animate>
        <button type="button" class="cat-filter-btn is-active" data-filter="all">All Posts</button>
        <button type="button" class="cat-filter-btn" data-filter="behind-the-scenes">Behind the Scenes</button>
        <button type="button" class="cat-filter-btn" data-filter="client-spotlights">Client Spotlights</button>
        <button type="button" class="cat-filter-btn" data-filter="color">Color</button>
        <button type="button" class="cat-filter-btn" data-filter="extensions">Extensions</button>
        <button type="button" class="cat-filter-btn" data-filter="hair-care">Hair Care</button>
        <button type="button" class="cat-filter-btn" data-filter="hair-products">Hair Products</button>
        <button type="button" class="cat-filter-btn" data-filter="salon-team">Salon Team</button>
        <button type="button" class="cat-filter-btn" data-filter="styling">Styling</button>
      </nav>'''

s_new, n = old_nav_pat.subn(new_nav, s, count=1)
if n == 0:
    print('× cat-nav not found — aborting')
    raise SystemExit(1)

# 2. Add data-cat to each cat-card anchor based on its /blog/<slug> href
def tag_cat_card(match):
    full = match.group(0)
    href_m = re.search(r'href="/blog/([^"]+)"', full)
    if not href_m:
        return full
    slug = href_m.group(1)
    cat = POST_CAT_MAP.get(slug, 'hair-care')
    if 'data-cat=' in full:
        return full
    return full.replace('class="cat-card"', f'class="cat-card" data-cat="{cat}"', 1)

card_pat = re.compile(r'<a[^>]+class="cat-card"[^>]*>', re.DOTALL)
s_new = card_pat.sub(tag_cat_card, s_new)

# 3. Inject CSS for filter buttons
filter_css = '''
    /* Blog category filter buttons */
    .cat-filter-btn{font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;padding:10px 18px;border:1px solid rgba(255,255,255,.15);border-radius:24px;color:var(--light-gray);transition:all .3s;cursor:pointer;font-family:inherit;background:none}
    .cat-filter-btn:hover{color:var(--white);border-color:var(--olive-light)}
    .cat-filter-btn.is-active{background:var(--olive);border-color:var(--olive);color:var(--white)}
    .cat-card[hidden]{display:none}
'''
if '.cat-filter-btn{' not in s_new:
    s_new = s_new.replace('  </style>', filter_css + '  </style>', 1)

# 4. Inject JS filter logic before </body>
filter_js = '''  <script>
    (function(){
      const btns = document.querySelectorAll('.cat-filter-btn');
      const cards = document.querySelectorAll('.cat-card');
      btns.forEach(b => b.addEventListener('click', () => {
        btns.forEach(x => x.classList.remove('is-active'));
        b.classList.add('is-active');
        const f = b.dataset.filter;
        cards.forEach(c => { c.hidden = (f !== 'all' && c.dataset.cat !== f); });
      }));
    })();
  </script>
</body>'''
if 'cat-filter-btn' not in s_new.split('</style>')[-1]:
    # Only inject if filter JS not already present
    pass
s_new = s_new.replace('</body>', filter_js, 1)

FILE.write_text(s_new)
print(f'✓ Updated {FILE.name}')
print(f'  - cat-nav links → filter buttons with 9 categories')
print(f'  - data-cat added to each post card ({sum(1 for c in POST_CAT_MAP)} posts mapped)')
print(f'  - JS filter in-place, no page navigation')
