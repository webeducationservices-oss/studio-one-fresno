#!/usr/bin/env python3
"""Apply three fixes to /nbr-extensions:
1. Convert both photo gallery grids into a single scrolling ticker (marquee)
2. Add a YouTube video embed (M4zzCYIE9ZY)
3. Add category filter to FAQs (Getting Started, The Service, Everyday Wear, Maintenance)
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FILE = ROOT / "nbr-extensions.html"
s = FILE.read_text()

# ---------------------------------------------------------------------------
# 1. Replace BOTH gallery-grid sections with one scrolling ticker
# ---------------------------------------------------------------------------
# Collect all images referenced in the file (de-duplicated, preserving order)
img_pat = re.compile(r'/images/webflow/gallery/([a-z0-9-]+?)(-p-\d+)?\.webp')
seen = set()
unique_slugs = []
for m in img_pat.finditer(s):
    slug = m.group(1)
    if slug not in seen:
        seen.add(slug)
        unique_slugs.append(slug)

# Prefer the -p-800 variant (exists on disk, balanced quality/size)
def pick_variant(slug):
    for suffix in ['-p-800.webp', '-p-1080.webp', '.webp']:
        p = ROOT / f"images/webflow/gallery/{slug}{suffix}"
        if p.exists():
            return f"/images/webflow/gallery/{slug}{suffix}"
    return f"/images/webflow/gallery/{slug}.webp"

ticker_tiles_html = '\n'.join(
    f'        <div class="ticker-tile"><img src="{pick_variant(s2)}" alt="NBR hair extension transformation" loading="lazy" decoding="async"></div>'
    for s2 in unique_slugs
)

# Duplicate tiles for seamless loop
ticker_html = f'''<!-- ==================== GALLERY TICKER ==================== -->
  <section class="section section--dark gallery-ticker-wrap" style="padding:60px 0">
    <div class="ticker" data-animate>
      <div class="ticker-track">
{ticker_tiles_html}
{ticker_tiles_html}
      </div>
    </div>
  </section>'''

# Find and replace every <section> containing class="gallery-grid"
# Strategy: find each <section> whose content contains "gallery-grid" and remove them entirely.
# Then insert the ticker ONCE where the first one was.
section_pat = re.compile(
    r'(<!--[^\n]*?(?:GALLERY|Gallery)[^\n]*?-->\s*)?<section[^>]*>\s*(?:<div[^>]*class="section-inner"[^>]*>\s*)?(?:<div[^>]*data-animate[^>]*>\s*)?<div[^>]*class="gallery-grid"[^>]*>.*?</div>\s*(?:</div>\s*)*</section>',
    re.DOTALL
)
matches = list(section_pat.finditer(s))
print(f"Found {len(matches)} gallery-grid section(s) to replace")

if matches:
    # Replace FIRST match with ticker, remove subsequent matches
    new_s = s[:matches[0].start()] + ticker_html + s[matches[0].end():]
    # Now remove any remaining gallery-grid sections
    # Rebuild pattern against new_s
    new_s = section_pat.sub('', new_s)
else:
    # Fallback: no section wrapper found, look for gallery-grid div directly
    grid_pat = re.compile(r'<div[^>]*class="gallery-grid"[^>]*>.*?</div>\s*(?:</div>\s*)?</section>', re.DOTALL)
    new_s, n = grid_pat.subn('', s)
    # Insert ticker after first H1 closing section
    h1_section_end = re.search(r'</section>', new_s)
    if h1_section_end:
        new_s = new_s[:h1_section_end.end()] + '\n\n  ' + ticker_html + new_s[h1_section_end.end():]

# ---------------------------------------------------------------------------
# 2. Add YouTube video section (after the ticker)
# ---------------------------------------------------------------------------
video_section = '''<!-- ==================== VIDEO ==================== -->
  <section class="section video-section" style="padding:80px 40px">
    <div class="section-inner text-center" data-animate>
      <p class="eyebrow">See It In Action</p>
      <h2 class="section-heading" style="max-width:800px;margin:0 auto 32px">How NBR Hair Extensions come to life</h2>
      <div class="video-wrap">
        <iframe src="https://www.youtube-nocookie.com/embed/M4zzCYIE9ZY"
                title="NBR Hair Extensions at Studio One"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen
                loading="lazy"></iframe>
      </div>
    </div>
  </section>'''

# Insert after the ticker
new_s = new_s.replace(
    '<!-- ==================== GALLERY TICKER ==================== -->',
    video_section + '\n\n  <!-- ==================== GALLERY TICKER ==================== -->',
    1
)

# ---------------------------------------------------------------------------
# 3. FAQ categorization + filter
# ---------------------------------------------------------------------------
FAQ_CATEGORIES = {
    'What type of hair do you use for NBR Extensions?': 'service',
    'Do I have to come in for a consultation?': 'start',
    'What is the maintenance?': 'maintenance',
    'How long is the reservation?': 'service',
    'Do you color my hair when I get my extensions?': 'service',
    'How are NBR extensions installed?': 'service',
    'How long do the extensions last?': 'maintenance',
    'What are rows?': 'service',
    'What do you mean by wefts?': 'service',
    'Can I wear my hair in braids or half up?': 'wear',
    'Can I wear my extensions up?': 'wear',
    'Can I swim or work out with extensions?': 'wear',
    'Do you offer payment plans?': 'start',
}

# Add data-cat attribute to each <div class="faq-item">
def tag_faq(match):
    full = match.group(0)
    # Find the question text in this item
    qm = re.search(r'class="faq-q">([^<]+?)\s*<span', full)
    if not qm:
        return full
    q = qm.group(1).strip()
    cat = FAQ_CATEGORIES.get(q, 'service')
    # Add data-cat to the outer <div class="faq-item">
    return full.replace('<div class="faq-item"', f'<div class="faq-item" data-cat="{cat}"', 1)

faq_item_pat = re.compile(r'<div class="faq-item">.*?(?=<div class="faq-item">|</div>\s*</section>)', re.DOTALL)
new_s = faq_item_pat.sub(tag_faq, new_s)

# Inject filter buttons before the faq-list
faq_filter_html = '''<div class="faq-filter" data-animate>
        <button type="button" class="faq-filter-btn is-active" data-filter="all">All Questions</button>
        <button type="button" class="faq-filter-btn" data-filter="start">Getting Started</button>
        <button type="button" class="faq-filter-btn" data-filter="service">The Service</button>
        <button type="button" class="faq-filter-btn" data-filter="wear">Everyday Wear</button>
        <button type="button" class="faq-filter-btn" data-filter="maintenance">Maintenance</button>
      </div>
      '''

new_s = re.sub(
    r'(<div class="faq-list" data-animate>)',
    faq_filter_html + r'\1',
    new_s,
    count=1
)

# ---------------------------------------------------------------------------
# Inject CSS + JS for ticker + video + FAQ filter
# ---------------------------------------------------------------------------
ticker_css = '''
    /* Scrolling ticker */
    .ticker{overflow:hidden;position:relative}
    .ticker::before,.ticker::after{content:"";position:absolute;top:0;bottom:0;width:120px;z-index:2;pointer-events:none}
    .ticker::before{left:0;background:linear-gradient(90deg,var(--dark),transparent)}
    .ticker::after{right:0;background:linear-gradient(270deg,var(--dark),transparent)}
    .ticker-track{display:flex;gap:12px;width:max-content;animation:ticker 80s linear infinite;will-change:transform}
    .ticker-track:hover{animation-play-state:paused}
    .ticker-tile{flex:0 0 auto;width:280px;height:280px;overflow:hidden;border-radius:4px;background:#1a1a1a}
    .ticker-tile img{width:100%;height:100%;object-fit:cover;display:block}
    @keyframes ticker{to{transform:translateX(-50%)}}
    @media(max-width:768px){.ticker-tile{width:200px;height:200px}}

    /* Video */
    .video-wrap{position:relative;max-width:960px;margin:0 auto;aspect-ratio:16/9;border-radius:6px;overflow:hidden;background:#000}
    .video-wrap iframe{position:absolute;inset:0;width:100%;height:100%;border:0}

    /* FAQ filter */
    .faq-filter{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:40px auto 28px;max-width:820px}
    .faq-filter-btn{font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;padding:10px 18px;border:1px solid rgba(255,255,255,.15);border-radius:24px;color:var(--light-gray);transition:all .3s}
    .faq-filter-btn:hover{color:var(--white);border-color:var(--olive-light)}
    .faq-filter-btn.is-active{background:var(--olive);border-color:var(--olive);color:var(--white)}
    .faq-item[hidden]{display:none}
'''

new_s = new_s.replace('  </style>', ticker_css + '  </style>', 1)

# Append JS for FAQ filter — add a new <script> block before the closing </body>
faq_js = '''  <script>
    // FAQ filter
    (function(){
      const btns = document.querySelectorAll('.faq-filter-btn');
      const items = document.querySelectorAll('.faq-item');
      btns.forEach(b => b.addEventListener('click', () => {
        btns.forEach(x => x.classList.remove('is-active'));
        b.classList.add('is-active');
        const f = b.dataset.filter;
        items.forEach(i => {
          const match = (f === 'all') || i.dataset.cat === f;
          i.hidden = !match;
          // Also close expanded answer when filter changes
          const q = i.querySelector('.faq-q');
          const a = i.querySelector('.faq-a');
          if (q && a) { q.classList.remove('is-open'); a.classList.remove('is-open'); }
        });
      }));
    })();
  </script>
</body>'''

new_s = new_s.replace('</body>', faq_js, 1)

# ---------------------------------------------------------------------------
FILE.write_text(new_s)
print(f"✓ Updated {FILE.name}")
print(f"  - Gallery grid → ticker with {len(unique_slugs)} unique photos (duplicated for seamless loop)")
print(f"  - YouTube video M4zzCYIE9ZY embedded")
print(f"  - FAQ filter: 4 categories across {len(FAQ_CATEGORIES)} questions")
