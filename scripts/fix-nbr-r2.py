#!/usr/bin/env python3
"""Round 2 NBR fixes:
1. Reorder: Hero → TICKER → Video → Process → Testimonials → ... (ticker moves up)
2. Center "See It In Action" video section
3. Add client photos to each testimonial in "Why choose NBR at Studio One?"
"""
import re
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FILE = ROOT / "nbr-extensions.html"
s = FILE.read_text()

# ---------------------------------------------------------------------------
# 1. Reorder ticker → right after hero
# ---------------------------------------------------------------------------
hero_end_marker  = '<!-- ==================== HERO ==================== -->'
video_marker     = '<!-- ==================== VIDEO ==================== -->'
ticker_marker    = '<!-- ==================== GALLERY TICKER ==================== -->'

# Extract the ticker section
m = re.search(
    re.escape(ticker_marker) + r'.*?</section>',
    s, re.DOTALL
)
if not m:
    print('× ticker section not found')
    raise SystemExit(1)

ticker_block = m.group(0)
# Remove ticker from its current location
s2 = s[:m.start()] + s[m.end():]
# Clean any stray empty whitespace
s2 = re.sub(r'\n\s*\n\s*\n', '\n\n', s2)

# Insert ticker right before the VIDEO marker
v_idx = s2.find(video_marker)
if v_idx < 0:
    print('× video marker not found')
    raise SystemExit(1)
s2 = s2[:v_idx] + ticker_block + '\n\n  ' + s2[v_idx:]

# ---------------------------------------------------------------------------
# 2. Center the video section (full text-align:center on the inner)
# ---------------------------------------------------------------------------
# Already has class="section-inner text-center" — make sure text-align is applied
# and add a guarded CSS rule
if '.text-center{text-align:center}' not in s2:
    s2 = s2.replace(
        '  </style>',
        '    .text-center{text-align:center}\n  </style>',
        1
    )

# Also ensure the video-wrap inside is centered (margin auto)
# Already has margin:0 auto in CSS. Good.

# ---------------------------------------------------------------------------
# 3. Add client photos to testimonials
# ---------------------------------------------------------------------------
testimonial_section_pat = re.compile(
    r'(<!-- =+ TESTIMONIALS =+ -->\s*<section[^>]*>\s*<div class="section-inner">.*?<div class="testimonials-strip"[^>]*>)(.*?)(</div>\s*</div>\s*</section>)',
    re.DOTALL
)
m2 = testimonial_section_pat.search(s2)
if not m2:
    print('× testimonials section not found')
    raise SystemExit(1)

prefix, body, suffix = m2.group(1), m2.group(2), m2.group(3)

# Map authors to images
TESTIMONIAL_IMG = {
    'Barbara G.': '/images/blog/barbaras-nbr-hair-extension-journey-at-studio-one.webp',
    'Sontoya R.': '/images/webflow/gallery/3cf0c884-111c-4ef0-a376-89d3c38f82af-p-800.webp',
}

def inject_image(testimonial_html):
    # Find author
    am = re.search(r'class="testimonial-author">[—\-\s&mdash;]*([^<]+?)<', testimonial_html)
    if not am:
        return testimonial_html
    author = am.group(1).strip()
    img = TESTIMONIAL_IMG.get(author)
    if not img:
        return testimonial_html
    # Wrap the testimonial content with a flex layout: image left, copy right
    image_html = f'<div class="testimonial-photo"><img src="{img}" alt="Hair transformation by Studio One" loading="lazy"></div>'
    # Insert image_html as first child after the opening <div class="testimonial">
    return testimonial_html.replace('<div class="testimonial">', '<div class="testimonial testimonial--with-photo">\n          ' + image_html + '\n          <div class="testimonial-text">', 1) + '          </div>'

# Find each <div class="testimonial"> ... </div> block (top-level, balanced)
# Use a non-greedy split approach
items = []
depth = 0
buf = ''
i = 0
while i < len(body):
    if body[i:i+22] == '<div class="testimonial">':
        # Find matching closing </div>
        # Count nested divs
        start = i
        d = 0
        j = i
        while j < len(body):
            if body[j:j+5] == '<div ' or body[j:j+5] == '<div>':
                # Find end of opening tag
                close_open = body.find('>', j) + 1
                d += 1
                j = close_open
            elif body[j:j+6] == '</div>':
                d -= 1
                j += 6
                if d == 0:
                    items.append(body[start:j])
                    i = j
                    break
            else:
                j += 1
        else:
            break
    else:
        i += 1

# Simpler: regex with greedy matching but bounded by the next <div class="testimonial"> or end
# Re-do simpler:
test_pat = re.compile(r'<div class="testimonial">.*?(?=<div class="testimonial">|$)', re.DOTALL)
matches = list(test_pat.finditer(body))
new_body = body
for tm in matches:
    block = tm.group(0).rstrip()
    # Find the trailing </div> (close of this testimonial, not nested)
    # The testimonial block has one outer <div class="testimonial"> and inner spans/<p>s.
    # Simplest: find the LAST </div> in the block and anchor on it.
    # Actually since the testimonials are flat (just <p> tags inside), the block ends with one </div>.
    # Process the block:
    am = re.search(r'class="testimonial-author">[—\-\s&mdash;]*([^<]+?)<', block)
    if not am:
        continue
    author = am.group(1).strip()
    img = TESTIMONIAL_IMG.get(author)
    if not img:
        continue
    # Build replacement: wrap inner content with photo + text columns
    # Find the body inside <div class="testimonial">…</div>
    inner = block.replace('<div class="testimonial">', '', 1)
    # Strip trailing </div> + any trailing whitespace
    inner_stripped = re.sub(r'</div>\s*$', '', inner)
    new_block = f'''<div class="testimonial testimonial--with-photo">
          <div class="testimonial-photo"><img src="{img}" alt="Hair transformation by {author}" loading="lazy"></div>
          <div class="testimonial-text">{inner_stripped}
          </div>
        </div>'''
    new_body = new_body.replace(block, new_block, 1)

s2 = s2.replace(prefix + body + suffix, prefix + new_body + suffix, 1)

# ---------------------------------------------------------------------------
# Update CSS for testimonial photos
# ---------------------------------------------------------------------------
testimonial_css = '''
    /* Testimonials with photos */
    .testimonial--with-photo{display:grid;grid-template-columns:200px 1fr;gap:24px;align-items:center;padding:32px 28px}
    .testimonial--with-photo .testimonial-photo{width:200px;height:200px;overflow:hidden;border-radius:4px;background:#1a1a1a}
    .testimonial--with-photo .testimonial-photo img{width:100%;height:100%;object-fit:cover}
    .testimonial--with-photo .testimonial-text{display:flex;flex-direction:column;gap:0}
    @media (max-width:768px){
      .testimonial--with-photo{grid-template-columns:1fr;text-align:left;gap:20px}
      .testimonial--with-photo .testimonial-photo{width:100%;height:240px}
    }
'''
if '.testimonial--with-photo' not in s2:
    s2 = s2.replace('  </style>', testimonial_css + '  </style>', 1)

FILE.write_text(s2)
print('✓ Updated nbr-extensions.html')
print('  - Ticker moved to right after hero')
print('  - Video section centered (text-align:center on inner)')
print(f'  - Photos added to {len([k for k in TESTIMONIAL_IMG if k in body])} testimonials (Barbara, Sontoya)')
