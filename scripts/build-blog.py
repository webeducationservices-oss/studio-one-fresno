#!/usr/bin/env python3
"""Build the Studio One blog:
- 42 individual post pages → /blog/<slug>
- 8 category pages → /blog-categories/<slug>
- 1 landing page → /blog

Reads content-export/blog/*.json, maps each post to a canonical category,
downloads & optimizes hero images where available, generates all HTML.
"""
import json, os, html, urllib.request, re, datetime
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
BLOG_JSON = ROOT / "content-export/blog"
BLOG_OUT = ROOT / "blog"
CAT_OUT = ROOT / "blog-categories"
IMG_OUT = ROOT / "images/blog"
BLOG_OUT.mkdir(exist_ok=True)
CAT_OUT.mkdir(exist_ok=True)
IMG_OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Canonical categories (from sitemap /blog-categories/*)
# ---------------------------------------------------------------------------
CATEGORIES = {
    "behind-the-scenes":  "Behind the Scenes",
    "client-spotlights":  "Client Spotlights",
    "color":              "Color",
    "extensions":         "Extensions",
    "hair-care":          "Hair Care",
    "hair-products":      "Hair Products",
    "salon-team":         "Salon Team",
    "styling":            "Styling",
}

# Map each slug to its canonical category
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

DEFAULT_HERO = "/images/optimized/services-bg.webp"

# ---------------------------------------------------------------------------
# Load & enrich posts
# ---------------------------------------------------------------------------
posts = []
for fp in sorted(BLOG_JSON.glob("*.json")):
    d = json.load(open(fp))
    slug = d["slug"]
    d["mapped_cat"] = POST_CAT_MAP.get(slug, "hair-care")  # fallback
    d["cat_label"] = CATEGORIES[d["mapped_cat"]]
    body = d.get("body_text") or ""
    words = re.split(r"\s+", body.strip())
    d["excerpt"] = " ".join(words[:28]) + ("…" if len(words) > 28 else "")
    d["local_hero"] = DEFAULT_HERO  # will update below
    posts.append(d)

print(f"Loaded {len(posts)} posts")

# ---------------------------------------------------------------------------
# Download & optimize hero images
# ---------------------------------------------------------------------------
print("Downloading hero images...")
for p in posts:
    url = p.get("hero_image_url")
    if not url:
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        img = Image.open(BytesIO(raw))
        if img.mode in ("P", "RGBA"):
            img = img.convert("RGB")
        w, h = img.size
        if w > 1200:
            img = img.resize((1200, int(h * 1200 / w)), Image.LANCZOS)
        out = IMG_OUT / f"{p['slug']}.webp"
        img.save(out, "WEBP", quality=72, method=6)
        p["local_hero"] = f"/images/blog/{p['slug']}.webp"
        print(f"  ✓ {p['slug']}.webp ({out.stat().st_size // 1024}KB)")
    except Exception as e:
        print(f"  × {p['slug']}: {e}")

# Group by category
posts_by_cat = {cat: [] for cat in CATEGORIES}
for p in posts:
    posts_by_cat[p["mapped_cat"]].append(p)
# Sort each category newest-first (best effort — dates are free-form)
def sort_key(p):
    return p.get("published_date", "") or ""
for cat in posts_by_cat:
    posts_by_cat[cat].sort(key=sort_key, reverse=True)

# Sort all posts newest-first
all_posts_sorted = sorted(posts, key=sort_key, reverse=True)

# ---------------------------------------------------------------------------
# Shared chunks
# ---------------------------------------------------------------------------
def head_block(title, desc, path, hero=None, schema=""):
    preload = f'<link rel="preload" as="image" type="image/webp" href="{hero}" fetchpriority="high">' if hero else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="https://www.studioonefresno.com{path}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="https://www.studioonefresno.com{hero or '/images/og-image.jpg'}">
  <meta property="og:url" content="https://www.studioonefresno.com{path}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Studio One Hair Design">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  {preload}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://use.typekit.net" crossorigin>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('consent','default',{{'analytics_storage':'granted','ad_storage':'denied','ad_user_data':'denied','ad_personalization':'denied'}});</script>
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-WQGCMZ9Q');</script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-P0H19W2KWM"></script>
  <script>gtag('js',new Date());gtag('config','G-P0H19W2KWM');</script>
  <script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','24036206522645936');fbq('track','PageView');</script>
  {schema}
  <style>
    *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--olive:#4c5223;--olive-light:#6b7332;--black:#000;--dark:#0a0a0a;--white:#fff;--off-white:#f5f5f5;--light-gray:#d9d9d9;--body-font:Arial, sans-serif;--heading-font:'freight-big-pro',Georgia,serif}}
    html{{-webkit-font-smoothing:antialiased;scroll-behavior:smooth}}
    body{{font-family:var(--body-font);background:var(--black);color:var(--light-gray);font-size:16px;line-height:1.6;overflow-x:hidden}}
    img{{max-width:100%;height:auto;display:block}}
    a{{color:inherit;text-decoration:none}}
    button{{cursor:pointer;background:none;border:none;color:inherit;font-family:inherit}}
    .header{{position:fixed;top:0;left:0;right:0;z-index:90;padding:24px 40px;transition:background .3s ease}}
    .header.scrolled{{background:rgba(0,0,0,.9);backdrop-filter:blur(10px)}}
    .header-inner{{display:flex;justify-content:space-between;align-items:center;max-width:1400px;margin:0 auto}}
    .logo{{height:28px;width:auto}}
    .menu-toggle{{font-size:14px;font-weight:500;letter-spacing:2px;color:var(--off-white);text-transform:uppercase}}
    .floating-phone-widget{{position:fixed;bottom:32px;left:32px;z-index:100}}
    .floating-phone{{width:56px;height:56px;background:var(--olive);border-radius:50%;display:flex;align-items:center;justify-content:center}}
    .nav-overlay{{position:fixed;inset:0;z-index:200;background:var(--black);opacity:0;pointer-events:none}}
    [data-animate]{{opacity:0;transform:translateY(40px);transition:opacity .8s cubic-bezier(.16,1,.3,1),transform .8s cubic-bezier(.16,1,.3,1)}}
    [data-animate].is-visible{{opacity:1;transform:translate(0,0)}}
    .primary-button{{display:inline-block;padding:16px 32px;border:1px solid var(--olive);color:var(--light-gray);font-size:12px;font-weight:500;letter-spacing:3px;text-transform:uppercase;transition:background .3s,color .3s}}
    .primary-button:hover{{background:var(--olive);color:var(--white)}}
    .olive-button{{display:inline-block;padding:18px 40px;background:var(--olive);color:var(--white);font-size:12px;font-weight:600;letter-spacing:3px;text-transform:uppercase;transition:background .3s}}
    .olive-button:hover{{background:var(--olive-light)}}
    .eyebrow{{font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:var(--olive-light);margin-bottom:16px}}
    @media (max-width:768px){{.header{{padding:16px 20px}}}}
  </style>
  <link rel="stylesheet" href="/styles.css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="/styles.css"></noscript><link href="https://use.typekit.net/epq0gor.css" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://use.typekit.net/epq0gor.css" rel="stylesheet">
  </noscript>"""

BODY_OPEN = """</head>
<body>
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WQGCMZ9Q" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

  <div class="floating-phone-widget" id="phoneWidget">
    <div class="phone-actions" id="phoneActions">
      <a href="https://www.google.com/maps/dir//2950+E+Nees+Ave+%23103,+Fresno,+CA+93720" target="_blank" rel="noopener" class="phone-action-btn"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" stroke="#f5f5f5" stroke-width="2"/><circle cx="12" cy="10" r="3" stroke="#f5f5f5" stroke-width="2"/></svg><span>Directions</span></a>
      <a href="sms:5597959724" class="phone-action-btn"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="#f5f5f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Text</span></a>
      <a href="tel:5597959724" class="phone-action-btn"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" stroke="#f5f5f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Call</span></a>
    </div>
    <button class="floating-phone" id="phoneToggle" aria-label="Contact Studio One"><svg class="phone-icon" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" stroke="#f5f5f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><svg class="close-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" style="display:none"><path d="M18 6L6 18M6 6l12 12" stroke="#f5f5f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
  </div>

  <header class="header">
    <div class="header-inner">
      <a href="/" class="logo-link"><img src="/images/optimized/logo.avif" alt="Studio One" class="logo"></a>
      <button class="menu-toggle" id="menuToggle"><span class="menu-text">MENU</span></button>
    </div>
  </header>

  <nav class="nav-overlay" id="navOverlay">
    <button class="nav-close" id="navClose"><svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="#f5f5f5" stroke-width="1.5" stroke-linecap="round"/></svg></button>
    <div class="nav-inner">
      <a href="/" class="nav-logo" aria-label="Studio One — back to home">
        <img src="/images/optimized/logo.avif" alt="Studio One Hair Design" width="180" height="34">
      </a>
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
  </nav>
"""

FOOT = """
  <script src="/script.js" defer></script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Post page
# ---------------------------------------------------------------------------
POST_PAGE_STYLE = """
<style>
.post-hero{position:relative;min-height:60vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:140px 40px 60px;overflow:hidden;background:var(--black)}
.post-hero-bg{position:absolute;inset:0;z-index:0;opacity:.28}
.post-hero-bg img{width:100%;height:100%;object-fit:cover}
.post-hero-overlay{position:absolute;inset:0;background:rgba(0,0,0,.45);z-index:1}
.post-hero-content{position:relative;z-index:2;max-width:900px}
.post-hero h1{font-family:var(--heading-font);font-size:54px;font-weight:400;line-height:1.1;color:var(--white);margin-bottom:20px}
.post-meta{display:flex;justify-content:center;gap:24px;font-size:11px;letter-spacing:2px;color:var(--light-gray);text-transform:uppercase;font-weight:500}
.post-meta a{color:var(--olive-light);border-bottom:1px solid var(--olive);padding-bottom:2px}
.post-body{max-width:720px;margin:0 auto;padding:80px 40px}
.post-body p{font-size:17px;line-height:1.85;color:var(--light-gray);font-weight:300;margin-bottom:24px}
.post-body h2{font-family:var(--heading-font);font-size:34px;font-weight:400;color:var(--white);margin:48px 0 16px;line-height:1.2}
.post-body h3{font-size:16px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--off-white);margin:32px 0 12px}
.related-posts{background:var(--dark);padding:80px 40px}
.related-inner{max-width:1200px;margin:0 auto}
.related-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:32px}
.related-card{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:4px;overflow:hidden;transition:transform .3s,border-color .3s;display:flex;flex-direction:column}
.related-card:hover{transform:translateY(-4px);border-color:var(--olive)}
.related-card-img{aspect-ratio:16/10;overflow:hidden;background:#1a1a1a}
.related-card-img img{width:100%;height:100%;object-fit:cover}
.related-card-body{padding:24px;flex:1;display:flex;flex-direction:column}
.related-card-cat{font-size:10px;letter-spacing:2px;color:var(--olive-light);text-transform:uppercase;font-weight:600;margin-bottom:8px}
.related-card h3{font-family:var(--heading-font);font-size:20px;color:var(--white);line-height:1.25;font-weight:400;margin-bottom:12px;flex:1}
.related-card p{font-size:13px;color:var(--light-gray);font-weight:300;line-height:1.6}
.post-cta{padding:80px 40px;text-align:center;background:var(--black)}
.post-cta h2{font-family:var(--heading-font);font-size:36px;font-weight:400;color:var(--white);margin-bottom:20px;max-width:680px;margin-left:auto;margin-right:auto}
.post-cta p{font-size:15px;color:var(--light-gray);margin-bottom:32px;max-width:520px;margin-left:auto;margin-right:auto;font-weight:300}
@media (max-width:1024px){.related-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:768px){.post-hero h1{font-size:32px}.post-hero{padding:110px 24px 50px;min-height:50vh}.post-meta{flex-direction:column;gap:8px}.post-body{padding:60px 24px}.post-body p{font-size:15px}.post-body h2{font-size:26px}.related-grid{grid-template-columns:1fr}.related-posts{padding:60px 24px}}
</style>
"""

def post_body_html(body_text):
    """Convert \\n\\n-separated paragraphs to <p> tags."""
    paras = [p.strip() for p in (body_text or "").split("\n\n") if p.strip()]
    return "\n    ".join(f"<p>{html.escape(p)}</p>" for p in paras)

def render_post(p):
    cat = p["mapped_cat"]
    related = [x for x in posts_by_cat[cat] if x["slug"] != p["slug"]][:3]
    # fill with any other posts if the category is thin
    if len(related) < 3:
        for x in all_posts_sorted:
            if x["slug"] != p["slug"] and x not in related:
                related.append(x)
                if len(related) == 3:
                    break

    related_html = "\n        ".join(f'''<a href="/blog/{r["slug"]}" class="related-card">
          <div class="related-card-img"><img src="{r["local_hero"]}" alt="{html.escape(r["title"])[:80]}" loading="lazy" decoding="async"></div>
          <div class="related-card-body">
            <p class="related-card-cat">{r["cat_label"]}</p>
            <h3>{html.escape(r["title"])}</h3>
            <p>{html.escape(r["excerpt"])}</p>
          </div>
        </a>''' for r in related)

    schema = f'''<script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"BlogPosting",
    "headline":{json.dumps(p["title"])},
    "image":"https://www.studioonefresno.com{p["local_hero"]}",
    "author":{{"@type":"Organization","name":"Studio One Hair Design"}},
    "publisher":{{"@type":"Organization","name":"Studio One Hair Design","logo":{{"@type":"ImageObject","url":"https://www.studioonefresno.com/images/optimized/logo.avif"}}}},
    "datePublished":{json.dumps(p.get("published_date",""))},
    "mainEntityOfPage":"https://www.studioonefresno.com/blog/{p["slug"]}"
  }}
  </script>'''

    meta_desc = p.get("meta_description") or p["excerpt"]
    author = p.get("author") or "Studio One Team"
    date_display = p.get("published_date") or ""

    content = head_block(
        title=f'{p["title"]} | Studio One Blog',
        desc=meta_desc,
        path=f'/blog/{p["slug"]}',
        hero=p["local_hero"],
        schema=schema,
    )
    content += POST_PAGE_STYLE + BODY_OPEN
    content += f'''
  <article>
    <section class="post-hero">
      <div class="post-hero-bg"><img src="{p["local_hero"]}" alt="{html.escape(p["title"])}" fetchpriority="high" decoding="async"></div>
      <div class="post-hero-overlay"></div>
      <div class="post-hero-content" data-animate>
        <p class="eyebrow"><a href="/blog-categories/{cat}" style="color:var(--olive-light);border-bottom:1px solid var(--olive)">{p["cat_label"]}</a></p>
        <h1>{html.escape(p["title"])}</h1>
        <div class="post-meta">
          <span>{html.escape(author)}</span>
          <span>{html.escape(date_display)}</span>
        </div>
      </div>
    </section>

    <section class="post-body" data-animate>
      {post_body_html(p.get("body_text",""))}
    </section>
  </article>

  <section class="post-cta">
    <div data-animate>
      <h2>Ready for your own transformation?</h2>
      <p>Book a consultation with a Studio One stylist and let's talk about what's possible for your hair.</p>
      <a href="/booking" class="olive-button">book now</a>
    </div>
  </section>

  <section class="related-posts">
    <div class="related-inner">
      <p class="eyebrow" data-animate>More from the blog</p>
      <h2 style="font-family:var(--heading-font);font-size:32px;color:var(--white);font-weight:400" data-animate>Keep reading</h2>
      <div class="related-grid" data-animate>
        {related_html}
      </div>
    </div>
  </section>
'''
    content += FOOT
    return content

# ---------------------------------------------------------------------------
# Category page
# ---------------------------------------------------------------------------
CAT_STYLE = """
<style>
.cat-hero{min-height:50vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:140px 40px 60px;background:var(--black)}
.cat-hero h1{font-family:var(--heading-font);font-size:64px;font-weight:400;color:var(--white);margin-bottom:16px;line-height:1.1}
.cat-hero p{font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto;font-weight:300}
.cat-wrap{padding:60px 40px;background:var(--dark)}
.cat-inner{max-width:1200px;margin:0 auto}
.cat-nav{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:48px}
.cat-nav a{font-size:11px;letter-spacing:2px;color:var(--light-gray);text-transform:uppercase;padding:8px 2px;border-bottom:1px solid transparent;transition:color .3s,border-color .3s}
.cat-nav a:hover,.cat-nav a.active{color:var(--white);border-color:var(--olive)}
.cat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.cat-card{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:4px;overflow:hidden;display:flex;flex-direction:column;transition:transform .3s,border-color .3s}
.cat-card:hover{transform:translateY(-4px);border-color:var(--olive)}
.cat-card-img{aspect-ratio:16/10;overflow:hidden;background:#1a1a1a}
.cat-card-img img{width:100%;height:100%;object-fit:cover;transition:transform .5s}
.cat-card:hover img{transform:scale(1.05)}
.cat-card-body{padding:24px;flex:1;display:flex;flex-direction:column}
.cat-card-cat{font-size:10px;letter-spacing:2px;color:var(--olive-light);text-transform:uppercase;font-weight:600;margin-bottom:10px}
.cat-card h3{font-family:var(--heading-font);font-size:22px;color:var(--white);line-height:1.25;font-weight:400;margin-bottom:12px;flex:1}
.cat-card p{font-size:13px;color:var(--light-gray);font-weight:300;line-height:1.6;margin-bottom:14px}
.cat-card-read{font-size:11px;letter-spacing:2px;color:var(--olive-light);text-transform:uppercase;font-weight:500;padding-bottom:2px;border-bottom:1px solid var(--olive);align-self:flex-start}
.cat-empty{text-align:center;padding:60px;color:var(--light-gray);font-weight:300}
@media(max-width:1024px){.cat-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:768px){.cat-grid{grid-template-columns:1fr}.cat-hero h1{font-size:40px}.cat-wrap{padding:40px 20px}}
</style>
"""

def cat_nav_html(active=None):
    all_cls = ' class="active"' if active is None else ''
    parts = [f'<a href="/blog"{all_cls}>All Posts</a>']
    for slug, label in CATEGORIES.items():
        cls = ' class="active"' if active == slug else ""
        parts.append(f'<a href="/blog-categories/{slug}"{cls}>{label}</a>')
    return "\n        ".join(parts)

def render_category(cat_slug):
    label = CATEGORIES[cat_slug]
    cat_posts = posts_by_cat[cat_slug]
    desc = f"{label} posts from the Studio One Hair Design blog — tips, guides, and transformations from our Fresno salon."

    if cat_posts:
        cards = "\n        ".join(f'''<a href="/blog/{p["slug"]}" class="cat-card">
          <div class="cat-card-img"><img src="{p["local_hero"]}" alt="{html.escape(p["title"])[:80]}" loading="lazy" decoding="async"></div>
          <div class="cat-card-body">
            <p class="cat-card-cat">{p["cat_label"]}</p>
            <h3>{html.escape(p["title"])}</h3>
            <p>{html.escape(p["excerpt"])}</p>
            <span class="cat-card-read">Read More</span>
          </div>
        </a>''' for p in cat_posts)
        body_section = f'<div class="cat-grid" data-animate>\n        {cards}\n      </div>'
    else:
        body_section = f'<div class="cat-empty">No posts in this category yet. Check back soon.</div>'

    content = head_block(
        title=f"{label} | Studio One Blog",
        desc=desc,
        path=f"/blog-categories/{cat_slug}",
    )
    content += CAT_STYLE + BODY_OPEN
    content += f'''
  <section class="cat-hero">
    <div data-animate>
      <p class="eyebrow">Category</p>
      <h1>{label}</h1>
      <p>{len(cat_posts)} {"post" if len(cat_posts)==1 else "posts"} in {label.lower()}</p>
    </div>
  </section>

  <section class="cat-wrap">
    <div class="cat-inner">
      <nav class="cat-nav" data-animate>
        {cat_nav_html(active=cat_slug)}
      </nav>
      {body_section}
    </div>
  </section>
'''
    content += FOOT
    return content

# ---------------------------------------------------------------------------
# Blog landing page
# ---------------------------------------------------------------------------
def render_landing():
    desc = "Tips, guides, and client transformations from Studio One Hair Design in Fresno. NBR extensions, color, keratin, and hair care."

    # Featured: 3 most recent overall
    featured = all_posts_sorted[:3]
    rest = all_posts_sorted[3:]

    featured_html = "\n        ".join(f'''<a href="/blog/{p["slug"]}" class="cat-card">
          <div class="cat-card-img"><img src="{p["local_hero"]}" alt="{html.escape(p["title"])[:80]}" loading="lazy" decoding="async"></div>
          <div class="cat-card-body">
            <p class="cat-card-cat">{p["cat_label"]}</p>
            <h3>{html.escape(p["title"])}</h3>
            <p>{html.escape(p["excerpt"])}</p>
            <span class="cat-card-read">Read More</span>
          </div>
        </a>''' for p in featured)

    rest_html = "\n        ".join(f'''<a href="/blog/{p["slug"]}" class="cat-card">
          <div class="cat-card-img"><img src="{p["local_hero"]}" alt="{html.escape(p["title"])[:80]}" loading="lazy" decoding="async"></div>
          <div class="cat-card-body">
            <p class="cat-card-cat">{p["cat_label"]}</p>
            <h3>{html.escape(p["title"])}</h3>
            <p>{html.escape(p["excerpt"])}</p>
            <span class="cat-card-read">Read More</span>
          </div>
        </a>''' for p in rest)

    content = head_block(
        title="Blog | Studio One Hair Design Fresno",
        desc=desc,
        path="/blog",
    )
    content += CAT_STYLE + BODY_OPEN
    content += f'''
  <section class="cat-hero">
    <div data-animate>
      <p class="eyebrow">Studio One Blog</p>
      <h1>Hair stories, tips &amp; transformations.</h1>
      <p>{len(all_posts_sorted)} posts on extensions, color, keratin, and everything in between.</p>
    </div>
  </section>

  <section class="cat-wrap">
    <div class="cat-inner">
      <nav class="cat-nav" data-animate>
        {cat_nav_html(active=None)}
      </nav>
      <p class="eyebrow" data-animate style="text-align:center">Featured</p>
      <div class="cat-grid" data-animate style="margin-bottom:64px">
        {featured_html}
      </div>
      <p class="eyebrow" data-animate style="text-align:center">All Posts</p>
      <div class="cat-grid" data-animate>
        {rest_html}
      </div>
    </div>
  </section>
'''
    content += FOOT
    return content

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
print("\nBuilding post pages...")
for p in posts:
    out = BLOG_OUT / f"{p['slug']}.html"
    out.write_text(render_post(p))
print(f"  ✓ {len(posts)} posts written to /blog/")

print("\nBuilding category pages...")
for slug in CATEGORIES:
    out = CAT_OUT / f"{slug}.html"
    out.write_text(render_category(slug))
    count = len(posts_by_cat[slug])
    print(f"  ✓ {slug}.html ({count} posts)")

print("\nBuilding blog landing...")
(ROOT / "blog.html").write_text(render_landing())
print("  ✓ blog.html")

print(f"\nTotal: {len(posts)} posts + {len(CATEGORIES)} categories + 1 landing = {len(posts)+len(CATEGORIES)+1} pages")
