#!/usr/bin/env python3
"""Build shop.html, 107 product pages, cart, and order-confirmation.

The PayPal checkout flow is WIRED IN but INERT — the buy button on each
product page dispatches an `addToCart` event and the cart page reads the
resulting localStorage items. The PayPal Smart Payment Buttons block is
commented out until credentials arrive (will be swapped in Phase 4).
"""
import json, html, urllib.request, os
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
PRODUCTS_JSON = ROOT / "content-export/products.json"
PRODUCT_OUT = ROOT / "product"
IMG_OUT = ROOT / "images/products"
PRODUCT_OUT.mkdir(exist_ok=True)
IMG_OUT.mkdir(parents=True, exist_ok=True)

products = json.load(open(PRODUCTS_JSON))
print(f"Loaded {len(products)} products")

# ---------------------------------------------------------------------------
# Download & optimize product images
# ---------------------------------------------------------------------------
print("\nDownloading product images...")
for p in products:
    for i, url in enumerate(p["image_urls"]):
        if not url:
            continue
        out = IMG_OUT / f"{p['slug']}-{i+1}.webp"
        if out.exists():
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read()
            img = Image.open(BytesIO(raw))
            if img.mode in ("P", "RGBA"):
                img = img.convert("RGB")
            w, h = img.size
            if w > 900:
                img = img.resize((900, int(h * 900 / w)), Image.LANCZOS)
            img.save(out, "WEBP", quality=78, method=6)
        except Exception as e:
            print(f"  × {p['slug']}#{i+1}: {e}")

print(f"  ✓ Product images in {IMG_OUT}")
# Attach local image paths to each product
for p in products:
    p["local_images"] = [
        f"/images/products/{p['slug']}-{i+1}.webp"
        for i in range(len(p["image_urls"]))
        if (IMG_OUT / f"{p['slug']}-{i+1}.webp").exists()
    ]
    if not p["local_images"]:
        p["local_images"] = ["/images/og-image.jpg"]  # fallback placeholder

# ---------------------------------------------------------------------------
# Shared markup
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
  <meta property="og:type" content="product">
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
    :root{{--olive:#4c5223;--olive-light:#6b7332;--black:#000;--dark:#0a0a0a;--white:#fff;--off-white:#f5f5f5;--light-gray:#d9d9d9;--body-font:'Inter',Arial,sans-serif;--heading-font:'freight-big-pro',Georgia,serif}}
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
    .cart-icon{{position:relative;margin-right:24px;color:var(--off-white)}}
    .cart-count{{position:absolute;top:-6px;right:-8px;background:var(--olive);color:var(--white);font-size:10px;min-width:16px;height:16px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:600;padding:0 4px}}
    .cart-count.is-empty{{display:none}}
    .floating-phone-widget{{position:fixed;bottom:32px;left:32px;z-index:100}}
    .floating-phone{{width:56px;height:56px;background:var(--olive);border-radius:50%;display:flex;align-items:center;justify-content:center}}
    .nav-overlay{{position:fixed;inset:0;z-index:200;background:var(--black);opacity:0;pointer-events:none}}
    [data-animate]{{opacity:0;transform:translateY(40px);transition:opacity .8s cubic-bezier(.16,1,.3,1),transform .8s cubic-bezier(.16,1,.3,1)}}
    [data-animate].is-visible{{opacity:1;transform:translate(0,0)}}
    .primary-button{{display:inline-block;padding:16px 32px;border:1px solid var(--olive);color:var(--light-gray);font-size:12px;font-weight:500;letter-spacing:3px;text-transform:uppercase;transition:background .3s,color .3s}}
    .primary-button:hover{{background:var(--olive);color:var(--white)}}
    .olive-button{{display:inline-block;padding:16px 32px;background:var(--olive);color:var(--white);font-size:12px;font-weight:600;letter-spacing:3px;text-transform:uppercase;transition:background .3s;border:none;cursor:pointer}}
    .olive-button:hover{{background:var(--olive-light)}}
    .olive-button:disabled{{opacity:.5;cursor:not-allowed}}
    .eyebrow{{font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:var(--olive-light);margin-bottom:16px}}
    @media (max-width:768px){{.header{{padding:16px 20px}}}}
  </style>
  <link rel="stylesheet" href="/styles.css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="/styles.css"></noscript>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <link href="https://use.typekit.net/iqt4hfw.css" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://use.typekit.net/iqt4hfw.css" rel="stylesheet">
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
      <div style="display:flex;align-items:center">
        <a href="/cart" class="cart-icon" aria-label="Cart"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M3 3h2l2 14h12l2-10H6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9" cy="20" r="1.5" fill="currentColor"/><circle cx="17" cy="20" r="1.5" fill="currentColor"/></svg><span class="cart-count is-empty" id="cartCount">0</span></a>
        <button class="menu-toggle" id="menuToggle"><span class="menu-text">MENU</span></button>
      </div>
    </div>
  </header>

  <nav class="nav-overlay" id="navOverlay">
    <button class="nav-close" id="navClose"><svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="#f5f5f5" stroke-width="1.5" stroke-linecap="round"/></svg></button>
    <div class="nav-inner">
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
  <script src="/cart.js" defer></script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Shop landing (product grid)
# ---------------------------------------------------------------------------
SHOP_STYLE = """
<style>
.shop-hero{min-height:40vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:140px 40px 40px;background:var(--black)}
.shop-hero h1{font-family:var(--heading-font);font-size:56px;font-weight:400;color:var(--white);line-height:1.1;margin-bottom:16px}
.shop-hero p{font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 24px;font-weight:300}
.shop-filters{display:flex;gap:24px;justify-content:center;flex-wrap:wrap;padding:0 40px 48px;background:var(--black)}
.shop-filter-group{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.shop-filter-label{font-size:10px;letter-spacing:2px;color:var(--olive-light);text-transform:uppercase;font-weight:600;margin-right:8px}
.shop-filter-btn{font-size:11px;font-weight:500;letter-spacing:2px;color:var(--light-gray);text-transform:uppercase;padding:6px 12px;border:1px solid rgba(255,255,255,.1);border-radius:20px;background:transparent;transition:color .3s,border-color .3s,background .3s}
.shop-filter-btn:hover,.shop-filter-btn.active{color:var(--white);border-color:var(--olive);background:rgba(76,82,35,.15)}
.shop-grid-wrap{padding:40px;background:var(--dark);min-height:400px}
.shop-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;max-width:1400px;margin:0 auto}
.product-card{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:4px;overflow:hidden;transition:transform .3s,border-color .3s;display:flex;flex-direction:column}
.product-card:hover{transform:translateY(-3px);border-color:var(--olive)}
.product-card.is-hidden{display:none}
.product-img{aspect-ratio:1;overflow:hidden;background:#1a1a1a;padding:20px;display:flex;align-items:center;justify-content:center}
.product-img img{max-width:100%;max-height:100%;object-fit:contain;transition:transform .5s}
.product-card:hover .product-img img{transform:scale(1.05)}
.product-body{padding:20px 20px 24px;flex:1;display:flex;flex-direction:column}
.product-brand{font-size:10px;letter-spacing:2px;color:var(--olive-light);text-transform:uppercase;font-weight:600;margin-bottom:6px}
.product-name{font-family:var(--heading-font);font-size:19px;color:var(--white);line-height:1.25;font-weight:400;margin-bottom:8px;flex:1}
.product-price{font-size:14px;color:var(--off-white);font-weight:500;margin-bottom:4px}
.product-price-range{font-size:12px;color:var(--light-gray);font-weight:300}
.shop-empty{text-align:center;padding:80px 20px;color:var(--light-gray);font-weight:300}
@media(max-width:1024px){.shop-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:768px){.shop-grid{grid-template-columns:repeat(2,1fr);gap:16px}.shop-hero h1{font-size:38px}.shop-grid-wrap{padding:20px}}
@media(max-width:480px){.shop-grid{grid-template-columns:1fr}}
</style>
"""

def shop_page():
    # unique brands + categories for filter buttons
    brands = sorted({p["brand"] for p in products})
    cats = sorted({p["category"] for p in products})

    cards_html = "\n    ".join(
        f'''<a href="/product/{p["slug"]}" class="product-card" data-brand="{p["brand"]}" data-cat="{p["category"]}">
      <div class="product-img"><img src="{p["local_images"][0]}" alt="{html.escape(p["name"])}" loading="lazy" decoding="async"></div>
      <div class="product-body">
        <p class="product-brand">{html.escape(p["brand"])}</p>
        <h3 class="product-name">{html.escape(p["name"])}</h3>
        <p class="product-price">${p["min_price_cents"]/100:.0f}{"" if p["min_price_cents"]==p["max_price_cents"] else f' – ${p["max_price_cents"]/100:.0f}'}</p>
      </div>
    </a>'''
        for p in products
    )

    brand_buttons = "\n        ".join(
        f'<button class="shop-filter-btn" data-filter="brand" data-value="{b}">{b}</button>' for b in brands
    )
    cat_buttons = "\n        ".join(
        f'<button class="shop-filter-btn" data-filter="cat" data-value="{c}">{c.title()}</button>' for c in cats
    )

    content = head_block(
        title="Shop | Studio One Hair Design Fresno",
        desc=f"Shop {len(products)} premium hair care products curated by Studio One — Oribe, Davines, and more. Shampoo, conditioner, treatment, styling.",
        path="/shop",
    )
    content += SHOP_STYLE + BODY_OPEN + f'''
  <section class="shop-hero">
    <div data-animate>
      <p class="eyebrow">Studio One Shop</p>
      <h1>Salon-quality products, delivered.</h1>
      <p>{len(products)} curated products from Oribe, Davines, and specialty brands. Everything we use in the chair, ready for your shelf at home.</p>
    </div>
  </section>

  <div class="shop-filters" data-animate>
    <div class="shop-filter-group">
      <span class="shop-filter-label">Brand</span>
      <button class="shop-filter-btn active" data-filter="brand" data-value="all">All</button>
      {brand_buttons}
    </div>
    <div class="shop-filter-group">
      <span class="shop-filter-label">Category</span>
      <button class="shop-filter-btn active" data-filter="cat" data-value="all">All</button>
      {cat_buttons}
    </div>
  </div>

  <section class="shop-grid-wrap">
    <div class="shop-grid" data-animate id="shopGrid">
    {cards_html}
    </div>
    <div class="shop-empty" id="shopEmpty" style="display:none">No products match those filters.</div>
  </section>

  <script>
    (function() {{
      const state = {{ brand: 'all', cat: 'all' }};
      const buttons = document.querySelectorAll('.shop-filter-btn');
      const cards = document.querySelectorAll('.product-card');
      const emptyMsg = document.getElementById('shopEmpty');

      function apply() {{
        let visible = 0;
        cards.forEach(c => {{
          const okBrand = state.brand === 'all' || c.dataset.brand === state.brand;
          const okCat = state.cat === 'all' || c.dataset.cat === state.cat;
          const show = okBrand && okCat;
          c.classList.toggle('is-hidden', !show);
          if (show) visible++;
        }});
        emptyMsg.style.display = visible === 0 ? 'block' : 'none';
      }}

      buttons.forEach(b => {{
        b.addEventListener('click', () => {{
          const filter = b.dataset.filter;
          state[filter] = b.dataset.value;
          document.querySelectorAll(`[data-filter="${{filter}}"]`).forEach(x => x.classList.remove('active'));
          b.classList.add('active');
          apply();
        }});
      }});
    }})();
  </script>
'''
    content += FOOT
    return content

# ---------------------------------------------------------------------------
# Individual product pages
# ---------------------------------------------------------------------------
PRODUCT_PAGE_STYLE = """
<style>
.product-wrap{padding:120px 40px 80px;background:var(--black);min-height:calc(100vh - 200px)}
.product-wrap-inner{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:start}
.product-gallery{position:sticky;top:100px}
.product-main-img{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:4px;aspect-ratio:1;padding:40px;display:flex;align-items:center;justify-content:center;margin-bottom:16px}
.product-main-img img{max-width:100%;max-height:100%;object-fit:contain}
.product-thumbs{display:grid;grid-template-columns:repeat(auto-fill,72px);gap:8px}
.product-thumbs button{aspect-ratio:1;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:4px;padding:6px;transition:border-color .3s;cursor:pointer}
.product-thumbs button.active{border-color:var(--olive)}
.product-thumbs button img{width:100%;height:100%;object-fit:contain}
.product-info .breadcrumb{font-size:11px;letter-spacing:2px;color:var(--light-gray);text-transform:uppercase;margin-bottom:24px;opacity:.7}
.product-info .breadcrumb a{color:var(--olive-light)}
.product-info .brand-label{font-size:11px;letter-spacing:3px;color:var(--olive-light);text-transform:uppercase;font-weight:600;margin-bottom:12px}
.product-info h1{font-family:var(--heading-font);font-size:44px;font-weight:400;color:var(--white);line-height:1.1;margin-bottom:16px}
.product-info .price{font-family:var(--heading-font);font-size:32px;color:var(--off-white);margin-bottom:32px}
.variant-selector{margin-bottom:32px}
.variant-selector label{display:block;font-size:11px;letter-spacing:2px;color:var(--off-white);text-transform:uppercase;font-weight:600;margin-bottom:10px}
.variant-selector select{width:100%;padding:14px 16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);color:var(--white);font-family:inherit;font-size:14px;border-radius:4px;-webkit-appearance:none;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8' fill='none'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%23d9d9d9' stroke-width='1.5'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 16px center}
.qty-selector{display:flex;align-items:center;gap:0;margin-bottom:24px}
.qty-selector label{font-size:11px;letter-spacing:2px;color:var(--off-white);text-transform:uppercase;font-weight:600;margin-right:16px}
.qty-btn{width:36px;height:36px;border:1px solid rgba(255,255,255,.12);color:var(--white);background:rgba(255,255,255,.04);font-size:16px}
.qty-val{width:56px;height:36px;text-align:center;border:1px solid rgba(255,255,255,.12);border-left:none;border-right:none;background:rgba(255,255,255,.04);color:var(--white);font-family:inherit;font-size:14px}
.add-to-cart{width:100%;padding:18px;background:var(--olive);color:var(--white);font-size:12px;font-weight:600;letter-spacing:3px;text-transform:uppercase;border:none;cursor:pointer;transition:background .3s;margin-bottom:16px}
.add-to-cart:hover{background:var(--olive-light)}
.add-to-cart.is-added{background:#3a4019}
.paypal-note{padding:16px;background:rgba(76,82,35,.1);border:1px solid rgba(76,82,35,.3);border-radius:4px;font-size:12px;color:var(--light-gray);font-weight:300;margin-top:16px;line-height:1.7}
.product-desc{margin-top:40px;padding-top:32px;border-top:1px solid rgba(255,255,255,.08)}
.product-desc h3{font-size:13px;letter-spacing:2px;color:var(--off-white);text-transform:uppercase;font-weight:600;margin-bottom:16px}
.product-desc p{font-size:15px;color:var(--light-gray);line-height:1.8;font-weight:300;margin-bottom:16px}
.related-section{padding:80px 40px;background:var(--dark)}
.related-inner{max-width:1400px;margin:0 auto}
.related-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:32px}
@media(max-width:1024px){.product-wrap-inner{grid-template-columns:1fr;gap:40px}.product-gallery{position:static}.related-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:768px){.product-wrap{padding:110px 20px 60px}.product-info h1{font-size:32px}.related-grid{grid-template-columns:repeat(2,1fr)}}
</style>
"""

def render_product_page(p):
    # Pick up to 4 related products from same category, different slug
    related = [x for x in products if x["category"] == p["category"] and x["slug"] != p["slug"]][:4]

    thumbs_html = "\n      ".join(
        f'<button class="product-thumb{" active" if i==0 else ""}" data-img="{img}"><img src="{img}" alt=""></button>'
        for i, img in enumerate(p["local_images"])
    ) if len(p["local_images"]) > 1 else ""

    variant_opts = "".join(
        f'<option value="{i}" data-price-cents="{v["price_cents"]}">{html.escape(v["name"])} — ${v["price_cents"]/100:.0f}</option>'
        for i, v in enumerate(p["variants"])
    )

    has_variants = len(p["variants"]) > 1
    variant_block = f'''
    <div class="variant-selector">
      <label for="variantSel">Size</label>
      <select id="variantSel">{variant_opts}</select>
    </div>''' if has_variants else ""

    related_html = "\n      ".join(
        f'''<a href="/product/{r["slug"]}" class="product-card">
        <div class="product-img"><img src="{r["local_images"][0]}" alt="{html.escape(r["name"])}" loading="lazy" decoding="async"></div>
        <div class="product-body">
          <p class="product-brand">{html.escape(r["brand"])}</p>
          <h3 class="product-name">{html.escape(r["name"])}</h3>
          <p class="product-price">${r["min_price_cents"]/100:.0f}</p>
        </div>
      </a>'''
        for r in related
    )

    if related:
        related_section = f'''<section class="related-section">
    <div class="related-inner">
      <p class="eyebrow">You May Also Like</p>
      <h2 style="font-family:var(--heading-font);font-size:32px;color:var(--white);font-weight:400">More in {p["category"].title()}</h2>
      <div class="related-grid">
      {related_html}
      </div>
    </div>
  </section>'''
    else:
        related_section = ""

    schema = f'''<script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"Product",
    "name":{json.dumps(p["name"])},
    "image":"https://www.studioonefresno.com{p["local_images"][0]}",
    "description":{json.dumps(p["description"][:500])},
    "brand":{{"@type":"Brand","name":{json.dumps(p["brand"])}}},
    "offers":{{"@type":"{"AggregateOffer" if has_variants else "Offer"}","priceCurrency":"USD","{"lowPrice" if has_variants else "price"}":"{p["min_price_cents"]/100:.2f}"{f',"highPrice":"{p["max_price_cents"]/100:.2f}"' if has_variants else ""},"availability":"https://schema.org/InStock"}}
  }}
  </script>'''

    min_p = p["min_price_cents"] / 100
    max_p = p["max_price_cents"] / 100
    price_str = f"${min_p:.2f}".rstrip("0").rstrip(".") if min_p == max_p else f"${min_p:.0f} – ${max_p:.0f}"

    content = head_block(
        title=f'{p["name"]} | Studio One Shop',
        desc=(p["description"][:160] or f'{p["brand"]} {p["name"]}. Shop at Studio One Hair Design Fresno.'),
        path=f'/product/{p["slug"]}',
        hero=p["local_images"][0],
        schema=schema,
    )
    content += PRODUCT_PAGE_STYLE + BODY_OPEN
    content += f'''
  <section class="product-wrap">
    <div class="product-wrap-inner">
      <div class="product-gallery">
        <div class="product-main-img"><img id="mainProductImg" src="{p["local_images"][0]}" alt="{html.escape(p["name"])}" fetchpriority="high" decoding="async"></div>
        <div class="product-thumbs">
      {thumbs_html}
        </div>
      </div>
      <div class="product-info">
        <div class="breadcrumb"><a href="/shop">Shop</a> / {html.escape(p["category"].title())}</div>
        <p class="brand-label">{html.escape(p["brand"])}</p>
        <h1>{html.escape(p["name"])}</h1>
        <p class="price" id="priceDisplay">{price_str}</p>
        {variant_block}
        <div class="qty-selector">
          <label>Qty</label>
          <button class="qty-btn" id="qtyDec" type="button">−</button>
          <input class="qty-val" id="qtyVal" type="number" value="1" min="1" max="99">
          <button class="qty-btn" id="qtyInc" type="button">+</button>
        </div>
        <button class="add-to-cart" id="addToCart" data-slug="{p["slug"]}" data-name="{html.escape(p["name"])}" data-brand="{html.escape(p["brand"])}" data-image="{p["local_images"][0]}">Add to Cart</button>
        <div class="paypal-note">
          <strong>Coming Soon:</strong> PayPal Checkout is being wired in. Add to your cart now — the full checkout flow launches with our PayPal integration.
        </div>
        <div class="product-desc">
          <h3>About this product</h3>
          {"".join(f"<p>{html.escape(para)}</p>" for para in (p["description"] or "").split(chr(10)+chr(10)) if para.strip())}
        </div>
      </div>
    </div>
  </section>

  {related_section}

  <script>
    (function() {{
      const variantSel = document.getElementById('variantSel');
      const priceEl = document.getElementById('priceDisplay');
      const qtyInput = document.getElementById('qtyVal');
      const addBtn = document.getElementById('addToCart');
      const mainImg = document.getElementById('mainProductImg');
      const thumbs = document.querySelectorAll('.product-thumb');

      // Variant change updates price
      if (variantSel) {{
        variantSel.addEventListener('change', () => {{
          const cents = parseInt(variantSel.selectedOptions[0].dataset.priceCents, 10);
          priceEl.textContent = '$' + (cents/100).toFixed(2).replace(/\\.?0+$/, '');
        }});
      }}

      // Qty +/-
      document.getElementById('qtyInc').addEventListener('click', () => {{ qtyInput.value = Math.min(99, parseInt(qtyInput.value)+1); }});
      document.getElementById('qtyDec').addEventListener('click', () => {{ qtyInput.value = Math.max(1, parseInt(qtyInput.value)-1); }});

      // Thumbs
      thumbs.forEach(t => {{
        t.addEventListener('click', () => {{
          thumbs.forEach(x => x.classList.remove('active'));
          t.classList.add('active');
          mainImg.src = t.dataset.img;
        }});
      }});

      // Add to cart (uses cart.js's window.Cart API)
      addBtn.addEventListener('click', () => {{
        const qty = parseInt(qtyInput.value, 10);
        const variantIdx = variantSel ? variantSel.selectedIndex : 0;
        const price = variantSel ? parseInt(variantSel.selectedOptions[0].dataset.priceCents, 10) : {p["min_price_cents"]};
        const variantName = variantSel ? variantSel.selectedOptions[0].text : '';
        if (window.Cart) {{
          window.Cart.add({{
            slug: addBtn.dataset.slug,
            name: addBtn.dataset.name,
            brand: addBtn.dataset.brand,
            image: addBtn.dataset.image,
            variant: variantName.split(' — ')[0] || null,
            price_cents: price,
            qty: qty
          }});
          addBtn.textContent = 'Added to Cart ✓';
          addBtn.classList.add('is-added');
          setTimeout(() => {{ addBtn.textContent = 'Add to Cart'; addBtn.classList.remove('is-added'); }}, 2000);
        }}
      }});
    }})();
  </script>
'''
    content += FOOT
    return content

# ---------------------------------------------------------------------------
# Cart + order-confirmation pages
# ---------------------------------------------------------------------------
CART_STYLE = """
<style>
.cart-section{padding:120px 40px 80px;min-height:80vh;background:var(--black)}
.cart-inner{max-width:1000px;margin:0 auto}
.cart-header{text-align:center;margin-bottom:48px}
.cart-header h1{font-family:var(--heading-font);font-size:48px;color:var(--white);font-weight:400;line-height:1.1;margin-bottom:12px}
.cart-header p{font-size:15px;color:var(--light-gray);font-weight:300}
.cart-empty{text-align:center;padding:80px 20px}
.cart-empty p{font-size:17px;color:var(--light-gray);margin-bottom:32px;font-weight:300}
.cart-items{border-top:1px solid rgba(255,255,255,.08)}
.cart-item{display:grid;grid-template-columns:80px 1fr 120px 120px 40px;gap:20px;padding:20px 0;border-bottom:1px solid rgba(255,255,255,.08);align-items:center}
.cart-item-img{background:rgba(255,255,255,.04);border-radius:4px;padding:8px;aspect-ratio:1;display:flex;align-items:center;justify-content:center}
.cart-item-img img{max-width:100%;max-height:100%;object-fit:contain}
.cart-item-info h3{font-size:15px;color:var(--white);margin-bottom:4px;font-weight:500}
.cart-item-info .variant{font-size:12px;color:var(--light-gray);font-weight:300}
.cart-item-info .brand{font-size:10px;letter-spacing:2px;color:var(--olive-light);text-transform:uppercase;font-weight:600;margin-bottom:4px}
.cart-qty{display:flex;align-items:center}
.cart-qty button{width:28px;height:28px;background:rgba(255,255,255,.05);color:var(--white);border:1px solid rgba(255,255,255,.1);font-size:14px}
.cart-qty input{width:40px;height:28px;text-align:center;background:transparent;color:var(--white);border:1px solid rgba(255,255,255,.1);border-left:none;border-right:none;font-family:inherit}
.cart-item-price{font-size:14px;color:var(--off-white);text-align:right;font-weight:500}
.cart-remove{color:var(--light-gray);font-size:18px;opacity:.6;transition:opacity .3s}
.cart-remove:hover{opacity:1}
.cart-summary{background:rgba(255,255,255,.03);padding:32px;margin-top:32px;border-radius:4px}
.cart-row{display:flex;justify-content:space-between;padding:8px 0;font-size:14px;color:var(--light-gray)}
.cart-row--total{border-top:1px solid rgba(255,255,255,.08);margin-top:12px;padding-top:16px;font-size:18px;color:var(--white);font-weight:500}
.paypal-placeholder{margin-top:24px;padding:24px;background:rgba(76,82,35,.1);border:1px dashed rgba(76,82,35,.4);border-radius:4px;text-align:center}
.paypal-placeholder h3{font-size:14px;color:var(--off-white);letter-spacing:1px;margin-bottom:8px;font-weight:600}
.paypal-placeholder p{font-size:13px;color:var(--light-gray);font-weight:300;line-height:1.7;margin-bottom:16px}
@media(max-width:768px){
  .cart-item{grid-template-columns:60px 1fr;grid-template-rows:auto auto;gap:12px 16px}
  .cart-item-img{grid-row:span 2}
  .cart-qty{grid-column:2}
  .cart-item-price{text-align:left;grid-column:2}
  .cart-remove{position:absolute;top:16px;right:0}
  .cart-item{position:relative;padding:20px 0}
  .cart-section{padding:110px 20px 60px}
}
</style>
"""

def cart_page():
    content = head_block(
        title="Cart | Studio One Shop",
        desc="Review items in your Studio One cart and check out.",
        path="/cart",
    )
    content += CART_STYLE + BODY_OPEN
    content += '''
  <section class="cart-section">
    <div class="cart-inner">
      <div class="cart-header">
        <p class="eyebrow">Your Cart</p>
        <h1>Review your order.</h1>
        <p id="cartItemCount">0 items</p>
      </div>

      <div id="cartEmpty" class="cart-empty" style="display:none">
        <p>Your cart is empty.</p>
        <a href="/shop" class="olive-button">start shopping</a>
      </div>

      <div id="cartContent" style="display:none">
        <div class="cart-items" id="cartItems"></div>

        <div class="cart-summary">
          <div class="cart-row"><span>Subtotal</span><span id="sumSubtotal">$0.00</span></div>
          <div class="cart-row"><span>Shipping</span><span id="sumShipping">Calculated at checkout</span></div>
          <div class="cart-row"><span>Tax (CA 7.975%)</span><span id="sumTax">$0.00</span></div>
          <div class="cart-row cart-row--total"><span>Total</span><span id="sumTotal">$0.00</span></div>
        </div>

        <div class="paypal-placeholder">
          <h3>PayPal Checkout — Launching Soon</h3>
          <p>We're finalizing our PayPal integration. In the meantime, call or text us at 559-795-9724 and we'll process your order by phone, or stop by the salon.</p>
          <a href="tel:5597959724" class="olive-button">call 559-795-9724</a>
        </div>

        <!-- PAYPAL BUTTONS MOUNT POINT (Phase 4)
        <div id="paypal-button-container" style="margin-top:24px"></div>
        -->
      </div>
    </div>
  </section>

  <script>
    // Render cart on page load
    document.addEventListener('DOMContentLoaded', () => {
      if (window.Cart) window.Cart.renderCartPage();
    });
  </script>
'''
    content += FOOT
    return content


def order_confirmation_page():
    content = head_block(
        title="Order Confirmation | Studio One Shop",
        desc="Thank you for your order with Studio One Hair Design.",
        path="/order-confirmation",
    )
    content += '''
<style>
.thanks-section{min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:140px 40px 80px;background:var(--black)}
.thanks-inner{max-width:640px}
.thanks-icon{width:80px;height:80px;margin:0 auto 32px;border-radius:50%;background:rgba(76,82,35,.2);border:1px solid var(--olive);display:flex;align-items:center;justify-content:center}
.thanks-icon svg{color:var(--olive-light)}
.thanks-inner h1{font-family:var(--heading-font);font-size:48px;color:var(--white);line-height:1.1;margin-bottom:16px;font-weight:400}
.thanks-inner p{font-size:16px;color:var(--light-gray);font-weight:300;line-height:1.7;margin-bottom:24px}
.order-id{display:inline-block;padding:10px 20px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:4px;font-family:monospace;font-size:13px;color:var(--off-white);margin-bottom:32px}
.thanks-actions{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
</style>
''' + BODY_OPEN + '''
  <section class="thanks-section">
    <div class="thanks-inner" data-animate>
      <div class="thanks-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <p class="eyebrow">Thank You</p>
      <h1>Your order is confirmed.</h1>
      <p id="thanksOrderIntro">We&rsquo;ve received your order and emailed the confirmation to you. Questions? Call us at 559-795-9724.</p>
      <div class="order-id" id="orderIdDisplay" style="display:none"></div>
      <p>Studio One Hair Design &mdash; 2950 E Nees Ave., #103, Fresno, CA 93720</p>
      <div class="thanks-actions">
        <a href="/shop" class="primary-button">continue shopping</a>
        <a href="/" class="olive-button">back to home</a>
      </div>
    </div>
  </section>

  <script>
    // Show order ID from PayPal return (?oid= param)
    const params = new URLSearchParams(location.search);
    const oid = params.get('oid');
    if (oid) {
      const el = document.getElementById('orderIdDisplay');
      el.textContent = 'Order #' + oid;
      el.style.display = 'inline-block';
    }
    // Clear cart
    if (window.Cart) window.Cart.clear();
  </script>
'''
    content += FOOT
    return content

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
print("\nBuilding shop.html...")
(ROOT / "shop.html").write_text(shop_page())
print("  ✓ shop.html")

print(f"\nBuilding {len(products)} product pages...")
for p in products:
    (PRODUCT_OUT / f"{p['slug']}.html").write_text(render_product_page(p))
print(f"  ✓ {len(products)} product pages")

print("\nBuilding cart.html + order-confirmation.html...")
(ROOT / "cart.html").write_text(cart_page())
(ROOT / "order-confirmation.html").write_text(order_confirmation_page())
print("  ✓ cart.html + order-confirmation.html")

print(f"\nTotal: 1 shop + {len(products)} products + 1 cart + 1 order-confirmation = {len(products)+3} pages")
