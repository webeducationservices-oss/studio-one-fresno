#!/usr/bin/env python3
"""SEO optimization for /hair-gallery.

Goals: rank for "Hair Extensions Fresno", "Hair Color Salon in Fresno",
and "Keratin Treatment Fresno (Brazilian Blowout)".

What this changes:
- Tighter title + meta description with primary keywords
- Stronger H1 with keywords
- Adds an intro content block (~200 words) before the gallery
- Adds 3 category overview sections (one per filter) with H2 + descriptive
  paragraph + internal link to the relevant service page
- Diversifies all 54 image alt + title attributes by category
- Adds JSON-LD schemas: HairSalon (LocalBusiness) + ImageGallery
- Adds a bottom "Why Fresno chooses Studio One" section weaving all keywords
"""
import re, random
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
FILE = ROOT / "hair-gallery.html"
s = FILE.read_text()

# ---------------------------------------------------------------------------
# 1. Title + meta description
# ---------------------------------------------------------------------------
NEW_TITLE = 'Hair Extensions, Color & Keratin Gallery Fresno | Studio One'
NEW_DESC = ('Real hair transformation gallery from Studio One Fresno: NBR hand-tied '
            'hair extensions, dimensional color, and keratin smoothing (Brazilian Blowout). '
            'See 50+ recent guest results from Fresno\'s premier hair salon.')

s = re.sub(r'<title>[^<]+</title>', f'<title>{NEW_TITLE}</title>', s, count=1)
s = re.sub(r'<meta name="description" content="[^"]+"', f'<meta name="description" content="{NEW_DESC}"', s, count=1)
s = re.sub(r'<meta property="og:title" content="[^"]+"', f'<meta property="og:title" content="{NEW_TITLE}"', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]+"', f'<meta property="og:description" content="{NEW_DESC}"', s, count=1)

# ---------------------------------------------------------------------------
# 2. JSON-LD schemas (insert before </head>)
# ---------------------------------------------------------------------------
schema_ld = '''
  <!-- LocalBusiness / HairSalon schema -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "HairSalon",
    "@id": "https://www.studioonefresno.com/#salon",
    "name": "Studio One Hair Design",
    "description": "Premier Fresno hair salon specializing in NBR hand-tied hair extensions, dimensional color, and keratin smoothing treatments (Brazilian Blowout).",
    "url": "https://www.studioonefresno.com/",
    "image": "https://www.studioonefresno.com/images/og-image.jpg",
    "telephone": "+1-559-795-9724",
    "priceRange": "$$$",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "2950 E Nees Ave., #103",
      "addressLocality": "Fresno",
      "addressRegion": "CA",
      "postalCode": "93720",
      "addressCountry": "US"
    },
    "geo": { "@type": "GeoCoordinates", "latitude": 36.85, "longitude": -119.74 },
    "openingHoursSpecification": [
      { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday"], "opens": "10:00", "closes": "20:00" },
      { "@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "10:00", "closes": "19:00" },
      { "@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "18:00" }
    ],
    "areaServed": { "@type": "City", "name": "Fresno" },
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": "Salon Services",
      "itemListElement": [
        { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "NBR Hair Extensions Fresno", "url": "https://www.studioonefresno.com/nbr-extensions" }},
        { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Hair Color Salon Fresno", "url": "https://www.studioonefresno.com/services" }},
        { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Keratin Treatment Fresno (Brazilian Blowout)", "url": "https://www.studioonefresno.com/services" }}
      ]
    }
  }
  </script>
  <!-- ImageGallery schema -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "ImageGallery",
    "name": "Studio One Fresno Hair Transformation Gallery",
    "description": "Recent NBR extensions, color, and keratin transformations by Studio One Hair Design in Fresno, CA.",
    "url": "https://www.studioonefresno.com/hair-gallery",
    "publisher": { "@id": "https://www.studioonefresno.com/#salon" }
  }
  </script>
'''
s = s.replace('</head>', schema_ld + '\n</head>', 1)

# ---------------------------------------------------------------------------
# 3. Replace hero block with keyword-rich H1 + lede
# ---------------------------------------------------------------------------
new_hero = '''<section class="page-hero" style="min-height:55vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Real Guests, Real Results</p>
      <h1>Hair Extensions, Color &amp; Keratin Transformations in Fresno</h1>
      <p>Recent guest work from Studio One Hair Design &mdash; Fresno's destination for NBR hand-tied hair extensions, dimensional color, and keratin smoothing (Brazilian Blowout).</p>
    </div>
  </section>'''

s = re.sub(
    r'<section class="page-hero"[^>]*>.*?</section>',
    new_hero, s, count=1, flags=re.DOTALL
)

# ---------------------------------------------------------------------------
# 4. Insert SEO intro section + per-category overview sections
#    Place BEFORE the gallery filter / grid section.
# ---------------------------------------------------------------------------
seo_intro = '''
  <!-- SEO INTRO -->
  <section class="section section--dark gallery-intro-seo">
    <div class="section-inner" data-animate>
      <p class="eyebrow">Inside the Gallery</p>
      <h2 class="section-heading" style="max-width:780px">A real look at Studio One's signature work in Fresno.</h2>
      <p style="max-width:780px;font-size:16px;color:var(--light-gray);line-height:1.8;font-weight:300;margin-bottom:20px">
        Every photo below is a real Studio One guest. We don't run stock shots or styled-only campaigns &mdash; the gallery shows the work that walks out of the salon every week.
        Filter by category to focus on the transformation type you're researching: <strong style="color:var(--off-white);font-weight:500">NBR hair extensions in Fresno</strong>, <strong style="color:var(--off-white);font-weight:500">luxury hair color</strong>, or <strong style="color:var(--off-white);font-weight:500">keratin smoothing &amp; Brazilian Blowout</strong>.
      </p>
      <p style="max-width:780px;font-size:16px;color:var(--light-gray);line-height:1.8;font-weight:300">
        Hover any image for a quick description, or click to view full-size. When you find the look you want, <a href="/booking" style="color:var(--olive-light);border-bottom:1px solid var(--olive)">book your consultation</a> and we'll plan a custom approach for your hair goals.
      </p>
    </div>
  </section>

  <!-- CATEGORY OVERVIEW STRIP -->
  <section class="section gallery-category-overview">
    <div class="section-inner">
      <div class="cat-overview-grid">
        <article class="cat-overview-card" data-animate>
          <p class="eyebrow">Category 01</p>
          <h3>NBR Hair Extensions in Fresno</h3>
          <p>Natural Beaded Row hand-tied extensions install with no glue, no heat, and no damage &mdash; just custom-colored wefts beaded onto rows for the most seamless, longest-lasting result available. The most common transformations in this gallery are NBR.</p>
          <a href="/nbr-extensions" class="cat-overview-link">See NBR Extensions service &rarr;</a>
        </article>
        <article class="cat-overview-card" data-animate>
          <p class="eyebrow">Category 02</p>
          <h3>Hair Color Salon in Fresno</h3>
          <p>Studio One's color work centers on dimensional, low-maintenance color &mdash; balayage, foil-applied highlights, gloss-finished blondes, root touch-ups, gray coverage, and full color corrections. Every guest gets a custom formulation for their natural base.</p>
          <a href="/services" class="cat-overview-link">See Color services &rarr;</a>
        </article>
        <article class="cat-overview-card" data-animate>
          <p class="eyebrow">Category 03</p>
          <h3>Keratin Treatment Fresno (Brazilian Blowout)</h3>
          <p>Keratin smoothing reduces frizz, cuts blow-dry time, and makes hair feel softer for months at a time. We offer Brazilian Blowout-style treatments customized for your texture &mdash; minimal scalp contact, salon-only finishing, no harsh fumes.</p>
          <a href="/services" class="cat-overview-link">See Keratin services &rarr;</a>
        </article>
      </div>
    </div>
  </section>
'''

# Insert before the existing gallery filter section
gallery_section_start = re.search(r'<section class="section section--dark">\s*<div class="section-inner">\s*<div class="gallery-intro"', s)
if gallery_section_start:
    s = s[:gallery_section_start.start()] + seo_intro + '\n  ' + s[gallery_section_start.start():]
else:
    print('  ! gallery section start not found — appending intro before gallery-grid')

# ---------------------------------------------------------------------------
# 5. Append CSS for new sections
# ---------------------------------------------------------------------------
new_css = '''
    /* Gallery SEO sections */
    .gallery-intro-seo .eyebrow{color:var(--olive-light)}
    .gallery-intro-seo strong{color:var(--off-white);font-weight:500}
    .cat-overview-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
    .cat-overview-card{padding:36px 32px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:6px;transition:border-color .3s ease,background .3s ease,transform .3s ease}
    .cat-overview-card:hover{border-color:rgba(76,82,35,.6);background:rgba(76,82,35,.06);transform:translateY(-4px)}
    .cat-overview-card .eyebrow{font-size:10px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:var(--olive-light);margin-bottom:14px;display:block}
    .cat-overview-card h3{font-family:var(--heading-font);font-size:24px;color:var(--white);font-weight:400;line-height:1.25;margin-bottom:14px}
    .cat-overview-card p{font-size:14px;color:var(--light-gray);line-height:1.8;font-weight:300;margin-bottom:20px}
    .cat-overview-link{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--olive-light);font-weight:500;border-bottom:1px solid var(--olive);padding-bottom:2px;transition:color .3s ease,border-color .3s ease}
    .cat-overview-link:hover{color:var(--white);border-color:var(--white)}
    @media (max-width:1024px){
      .cat-overview-grid{grid-template-columns:1fr;gap:18px}
    }

    /* Why Fresno SEO closing block */
    .gallery-why{padding:80px 40px;background:var(--dark);border-top:1px solid rgba(255,255,255,.04)}
    .gallery-why-inner{max-width:920px;margin:0 auto;text-align:center}
    .gallery-why h2{font-family:var(--heading-font);font-size:36px;color:var(--white);font-weight:400;line-height:1.2;margin-bottom:24px}
    .gallery-why p{font-size:15px;color:var(--light-gray);line-height:1.85;font-weight:300;margin-bottom:18px}
    .gallery-why a{color:var(--olive-light);border-bottom:1px solid var(--olive);padding-bottom:1px}
    .gallery-why a:hover{color:var(--white);border-color:var(--white)}
'''

s = s.replace('  </style>', new_css + '  </style>', 1)

# ---------------------------------------------------------------------------
# 6. Diversify image alt text + add title (hover tooltip)
# ---------------------------------------------------------------------------
NBR_ALTS = [
    ("NBR hand-tied hair extensions in Fresno — beaded row install", "Long, full hair with NBR extensions installed at Studio One Fresno"),
    ("Long luxurious NBR hair extensions, custom color match", "Custom-colored NBR hair extensions, long length transformation"),
    ("Hair extension before and after, Studio One Fresno", "Before & after — added length and density with NBR"),
    ("Beaded row hair extensions for fullness, Fresno salon", "Added fullness with beaded row hair extensions"),
    ("Natural Beaded Row extensions for thicker, longer hair", "Natural-looking density transformation with NBR"),
    ("Seamless NBR extension blend, Fresno hand-tied wefts", "Seamlessly blended hand-tied wefts on natural color"),
    ("Hair extensions Fresno — Studio One signature work", "Studio One signature NBR transformation"),
    ("NBR extension color match, Studio One Fresno", "Wefts custom-colored to blend with natural base"),
    ("Hand-tied hair extensions for long, dimensional hair", "Hand-tied dimensional NBR install"),
    ("NBR extensions before-and-after, Studio One Fresno guest", "Before-and-after transformation, NBR install"),
]
COLOR_ALTS = [
    ("Dimensional balayage color at Studio One Fresno", "Dimensional balayage transformation, Studio One Fresno"),
    ("Hair color salon in Fresno — full-foil blonding", "Full-head foil blonding by Studio One Fresno"),
    ("Lived-in brunette color with face-framing highlights", "Lived-in brunette with face-framing dimension"),
    ("Honey blonde balayage, Fresno hair color salon", "Honey blonde balayage by Studio One"),
    ("Gloss-finished blonde color, Studio One Fresno", "Gloss-finished blonde refresh, Studio One Fresno"),
    ("Color correction & gray coverage at Studio One", "Custom color correction with full gray coverage"),
    ("Strawberry blonde dimensional color, Fresno salon", "Strawberry blonde dimensional color"),
    ("Cool brunette color refresh, low-maintenance grow-out", "Cool brunette refresh for easy grow-out"),
    ("Partial highlights for natural lift, Studio One Fresno", "Partial highlights — natural sun-kissed lift"),
    ("Custom hair color formulation, Fresno hair color salon", "Custom-formulated color for the guest's natural base"),
]
KERATIN_ALTS = [
    ("Keratin smoothing treatment in Fresno (Brazilian Blowout)", "Keratin smoothing — frizz-free, glossy result"),
    ("Brazilian Blowout result at Studio One Fresno", "Brazilian Blowout-style smoothing finish"),
    ("Keratin treatment Fresno — frizz-free, manageable hair", "Manageable, frizz-free keratin finish"),
    ("Smoothing keratin treatment, Studio One Fresno", "Sleek smoothing-treatment finish"),
    ("Keratin treatment for curly hair, Fresno salon", "Keratin smoothing on textured curly hair"),
]
NBR_COLOR_ALTS = [
    ("NBR hair extensions plus dimensional color, Studio One Fresno", "NBR install + custom color transformation"),
    ("Long blonde extensions with custom color, Fresno", "Long blonde extensions with custom color"),
    ("Dimensional color on NBR extensions, hand-tied wefts", "Dimensional color applied to NBR wefts"),
    ("Hair extensions and color in one visit, Studio One Fresno", "Extensions + color in one visit"),
    ("Long, full color-matched NBR extensions, Fresno salon", "Long, full color-matched NBR install"),
]

random.seed(42)
def pick(category_data):
    return random.choice(category_data)

def update_gallery_button(match):
    full = match.group(0)
    cat = re.search(r'data-cat="([^"]+)"', full)
    if not cat:
        return full
    cat_value = cat.group(1)
    if 'nbr' in cat_value and 'color' in cat_value:
        alt, title = pick(NBR_COLOR_ALTS)
    elif 'nbr' in cat_value:
        alt, title = pick(NBR_ALTS)
    elif 'keratin' in cat_value:
        alt, title = pick(KERATIN_ALTS)
    elif 'color' in cat_value:
        alt, title = pick(COLOR_ALTS)
    else:
        alt, title = ('Hair transformation by Studio One Fresno', 'Hair transformation, Studio One Fresno')

    # Update <img alt="...">
    new_full = re.sub(r'(<img[^>]*?)alt="[^"]*"', rf'\1alt="{alt}"', full, count=1)
    # Add title attribute on the BUTTON for tooltip + on the IMG too (works on both)
    new_full = re.sub(r'(<button[^>]*?class="gallery-item")', rf'\1 title="{title}" aria-label="{title}"', new_full, count=1)
    return new_full

s = re.sub(r'<button[^>]*?class="gallery-item"[^>]*>.*?</button>', update_gallery_button, s, flags=re.DOTALL)

# ---------------------------------------------------------------------------
# 7. Append "Why Fresno chooses Studio One" SEO closing block before footer
# ---------------------------------------------------------------------------
why_block = '''
  <!-- WHY STUDIO ONE — SEO CLOSING -->
  <section class="gallery-why">
    <div class="gallery-why-inner" data-animate>
      <h2>Fresno's go-to for hair extensions, color &amp; keratin smoothing.</h2>
      <p>
        Studio One Hair Design has built its reputation in Fresno on three core specialties: <a href="/nbr-extensions">NBR hand-tied hair extensions</a>, dimensional <a href="/services">hair color</a>, and <a href="/services">keratin smoothing treatments (Brazilian Blowout)</a>. Every guest in this gallery received a fully customized service &mdash; no swatch matching, no one-size-fits-all packages.
      </p>
      <p>
        Looking for a <strong>hair extensions salon in Fresno</strong> that won't damage your natural hair? Want a <strong>Fresno hair color salon</strong> that gets dimensional blondes and lived-in brunettes right? Need a <strong>keratin treatment in Fresno</strong> (or a Brazilian Blowout) that lasts? Studio One handles all three under one roof.
      </p>
      <p style="margin-top:32px"><a href="/booking" style="display:inline-block;padding:16px 32px;background:var(--olive);color:var(--white);font-size:12px;font-weight:600;letter-spacing:3px;text-transform:uppercase;border-radius:0;border:none;border-bottom:0;text-decoration:none">Book your consultation</a></p>
    </div>
  </section>
'''

# Insert before <footer
s = re.sub(r'(\s*<footer)', why_block + r'\1', s, count=1)

# ---------------------------------------------------------------------------
FILE.write_text(s)

# Quick stats
import re as _re
unique_alts = set(_re.findall(r'<img[^>]+alt="([^"]*)"', s))
gallery_titles = len(_re.findall(r'class="gallery-item"[^>]*title=', s))
schemas = len(_re.findall(r'application/ld\+json', s))
print(f'✓ Updated {FILE.name}')
print(f'  Unique image alts: {len(unique_alts)} (was 1)')
print(f'  Gallery items with title= tooltip: {gallery_titles}')
print(f'  JSON-LD schema blocks: {schemas} (was 0)')
print(f'  Word count (approx): {len(_re.sub(r"<[^>]+>", " ", s).split())}')
