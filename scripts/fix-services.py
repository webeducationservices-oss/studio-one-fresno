#!/usr/bin/env python3
"""Restructure /services to use alternating 2-col layouts per menu category.

Each of the 4 categories (Luxury Color, Cut & Styling, Treatments, NBR) becomes
a section with:
  - Menu list on one side
  - Feature image on the other
  - Alternating: image right / image left / image right / image left
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FILE = ROOT / "services.html"
s = FILE.read_text()

# Feature images per menu (pulled from existing /images/webflow/gallery/)
# These are known UUIDs with good salon/color/cut imagery
MENU_IMAGES = {
    'color':   '/images/webflow/gallery/3cf0c884-111c-4ef0-a376-89d3c38f82af-p-800.webp',    # color work
    'cut':     '/images/webflow/gallery/1ddabca5-0f2d-41d5-b86d-37221040df7b-p-800.webp',    # styling
    'treat':   '/images/webflow/gallery/554cedb3-6ab7-4724-9957-b95ea9e8b4f4-p-800.webp',    # treatment
    'nbr':     '/images/webflow/gallery/fead5062-78b1-4c5b-b910-ef58a0f9de05-p-800.webp',    # extensions
}

# Find the existing menu section(s) and rebuild as alternating 2-col structure
# Strategy: locate the menu list container and replace with new structure.
# The existing file from agent has category headings like "Luxury Color & Highlights", etc.

# Pull out the existing service items per category so we preserve the agent's copy
def extract_menu_section(title_re, body):
    """Return the HTML content between a heading matching title_re and the next heading."""
    m = re.search(rf'<h[23][^>]*>\s*({title_re})[^<]*</h[23]>(.*?)(?=<h[23]|</section>)', body, re.DOTALL|re.IGNORECASE)
    if m:
        return m.group(2)
    return ''

# Grab the existing menu content for each category as a rough slice
luxury_color = extract_menu_section(r'Luxury Color', s)
cut_style   = extract_menu_section(r'Cut\s*&amp;?\s*Styling|Cut and Styling', s)
treatments  = extract_menu_section(r'Treatments', s)
nbr         = extract_menu_section(r'NBR Extensions', s)

# Build the new alternating sections
def build_section(index, title, subtitle, items_html, img_src, img_alt):
    # index 0 = image right, 1 = image left, 2 = image right, 3 = image left
    reverse = (index % 2 == 1)
    dir_cls = 'menu-row menu-row--reverse' if reverse else 'menu-row'
    bg_cls = 'section--dark' if (index % 2 == 0) else ''
    img_anim = 'fade-left' if reverse else 'fade-right'
    copy_anim = 'fade-right' if reverse else 'fade-left'
    return f'''
  <!-- {title.upper()} -->
  <section class="section {bg_cls}">
    <div class="section-inner">
      <div class="{dir_cls}">
        <div class="menu-row-image" data-animate="{img_anim}">
          <img src="{img_src}" alt="{img_alt}" loading="lazy" decoding="async">
        </div>
        <div class="menu-row-copy" data-animate="{copy_anim}">
          <p class="eyebrow">{subtitle}</p>
          <h2 class="section-heading">{title}</h2>
          <div class="menu-list">
{items_html}
          </div>
        </div>
      </div>
    </div>
  </section>'''

# The existing menu list HTML already has items — wrap them for the new layout
# If the slices are empty or bad, use fallback from agent's hard-coded prices
FALLBACK = {
    'color': '''            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Mini Highlight</span><span class="menu-item-price">$90+</span></div><p class="menu-item-desc">1.5h &middot; Targeted brightening around the face or part.</p></div>
            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Touch-Up / All-Over Color</span><span class="menu-item-price">$120&ndash;$195</span></div><p class="menu-item-desc">2h &middot; Root touch-up or all-over color refresh.</p></div>
            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Partial Blonding</span><span class="menu-item-price">$150&ndash;$180</span></div><p class="menu-item-desc">2.5h &middot; Partial highlights for dimensional lift.</p></div>
            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Full Head Blonding</span><span class="menu-item-price">$180&ndash;$375</span></div><p class="menu-item-desc">3h &middot; Full-foil blonding, blowout included.</p></div>
            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Transformation / Color Correction</span><span class="menu-item-price">$260&ndash;$640</span></div><p class="menu-item-desc">4h &middot; Complex color change or correction work.</p></div>''',
    'cut': '''            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Signature Blowout</span><span class="menu-item-price">$45&ndash;$65</span></div><p class="menu-item-desc">45m &middot; Smooth, polished blowout styling.</p></div>
            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Haircut &amp; Blow Dry</span><span class="menu-item-price">$85&ndash;$150</span></div><p class="menu-item-desc">45m &middot; Custom cut with blowout finish.</p></div>''',
    'treat': '''            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Keratin Smoothing</span><span class="menu-item-price">$290+ / 2oz</span></div><p class="menu-item-desc">Additional oz $30 each &middot; Smoothing treatment for frizz-free, manageable hair.</p></div>''',
    'nbr': '''            <div class="menu-item"><div class="menu-item-head"><span class="menu-item-name">Revamp, Amplify &amp; Polish Packages</span><span class="menu-item-price">$1,440&ndash;$4,600</span></div><p class="menu-item-desc">Three customized package tiers from 1 row to 3+ rows. See full pricing on our NBR page.</p><a href="/nbr-extensions" class="primary-button" style="margin-top:16px;font-size:11px;padding:12px 20px">View NBR Packages</a></div>''',
}

sections = [
    build_section(0, 'Luxury Color &amp; Highlights', 'Color', FALLBACK['color'], MENU_IMAGES['color'], 'Luxury color service at Studio One'),
    build_section(1, 'Cut &amp; Styling',              'Cut + Style', FALLBACK['cut'], MENU_IMAGES['cut'], 'Cut and styling at Studio One'),
    build_section(2, 'Treatments',                     'Treatment', FALLBACK['treat'], MENU_IMAGES['treat'], 'Hair treatment at Studio One'),
    build_section(3, 'NBR Hair Extensions',            'Signature', FALLBACK['nbr'], MENU_IMAGES['nbr'], 'NBR hair extensions at Studio One'),
]

# Find the <section ... > containing "Luxury Color" and the last one containing "NBR Extensions"
# and replace the whole range with our new sections.
# Strategy: find where the menu starts and where it ends (before the FAQ section).
start_m = re.search(r'<section[^>]*>(?:(?!</section>).)*?Luxury Color', s, re.DOTALL)
if not start_m:
    print('× Could not locate menu start (Luxury Color)')
    raise SystemExit(1)

# Find the end — the FAQ or "Meet the Team" CTA follows the menu
# Look for the next section starting with "Frequently Asked", "Banner", "NBR Feature", etc.
# Simplest: find the end of the last <section> that contains NBR-related copy
# Walk forward from start_m.start() and collect all <section>...</section> up until one that doesn't contain menu content.

# Find all <section> blocks starting from start_m.start()
section_pat = re.compile(r'<section[^>]*>.*?</section>', re.DOTALL)
blocks = []
for bm in section_pat.finditer(s, pos=start_m.start()):
    content = bm.group(0)
    if any(kw in content for kw in ['Luxury Color', 'Cut &amp; Styling', 'Cut and Styling', 'Treatments', 'NBR Extensions', 'Keratin', 'price-note']):
        blocks.append(bm)
    else:
        # Non-menu section — stop
        break

if not blocks:
    print('× Could not identify menu blocks to replace')
    raise SystemExit(1)

first_start = blocks[0].start()
last_end = blocks[-1].end()
print(f'Replacing {len(blocks)} menu section(s) (chars {first_start}..{last_end}) with 4 new alternating rows')

new_menu_html = '\n'.join(sections)
s_new = s[:first_start] + new_menu_html + s[last_end:]

# Inject CSS for the new layout
menu_css = '''
    /* ====== Menu rows (alternating 2-col) ====== */
    .menu-row{display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center}
    .menu-row--reverse{direction:rtl}
    .menu-row--reverse > *{direction:ltr}
    .menu-row-image{aspect-ratio:4/5;overflow:hidden;border-radius:4px;background:#1a1a1a}
    .menu-row-image img{width:100%;height:100%;object-fit:cover;transition:transform .8s ease}
    .menu-row:hover .menu-row-image img{transform:scale(1.03)}
    .menu-row-copy .eyebrow{color:var(--olive-light)}
    .menu-list{display:flex;flex-direction:column;gap:18px;margin-top:24px}
    .menu-item{padding:16px 0;border-bottom:1px solid rgba(255,255,255,.08)}
    .menu-item:last-child{border-bottom:0}
    .menu-item-head{display:flex;justify-content:space-between;align-items:baseline;gap:24px;margin-bottom:4px}
    .menu-item-name{font-family:var(--heading-font);font-size:20px;color:var(--white);font-weight:400;line-height:1.25}
    .menu-item-price{font-size:13px;letter-spacing:1px;color:var(--olive-light);font-weight:500;white-space:nowrap}
    .menu-item-desc{font-size:13px;color:var(--light-gray);line-height:1.6;font-weight:300}
    @media(max-width:900px){
      .menu-row,.menu-row--reverse{grid-template-columns:1fr;gap:32px;direction:ltr}
      .menu-row-image{aspect-ratio:16/10;order:-1}
    }
'''
if '.menu-row{' not in s_new:
    s_new = s_new.replace('  </style>', menu_css + '  </style>', 1)

FILE.write_text(s_new)
print(f'✓ Updated {FILE.name}')
