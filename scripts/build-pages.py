#!/usr/bin/env python3
"""Generates all remaining core marketing pages for Studio One Fresno.

Each page is a standalone HTML file per CLAUDE.md pattern, with all shared
head/nav/footer markup included verbatim. Page-specific body content is
defined inline as a Python string.
"""
import os
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")

# ---------------------------------------------------------------------------
# Shared chunks
# ---------------------------------------------------------------------------

def HEAD(title, description, path, preload_hero=None, extra_head="", schema=""):
    preload = ""
    if preload_hero:
        preload = f'<link rel="preload" as="image" type="image/webp" href="{preload_hero}" fetchpriority="high">'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://www.studioonefresno.com{path}">

  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="https://www.studioonefresno.com/images/og-image.jpg">
  <meta property="og:url" content="https://www.studioonefresno.com{path}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Studio One Hair Design">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">

  {preload}

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://use.typekit.net" crossorigin>

  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('consent', 'default', {{'analytics_storage':'granted','ad_storage':'denied','ad_user_data':'denied','ad_personalization':'denied'}});
  </script>
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-WQGCMZ9Q');</script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-P0H19W2KWM"></script>
  <script>gtag('js', new Date()); gtag('config', 'G-P0H19W2KWM');</script>
  <script>
    !function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init','24036206522645936');fbq('track','PageView');
  </script>

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
    .header.scrolled{{background:rgba(0,0,0,.85);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}}
    .header-inner{{display:flex;justify-content:space-between;align-items:center;max-width:1400px;margin:0 auto}}
    .logo{{height:28px;width:auto}}
    .menu-toggle{{font-size:14px;font-weight:500;letter-spacing:2px;color:var(--off-white);text-transform:uppercase}}
    .floating-phone-widget{{position:fixed;bottom:32px;left:32px;z-index:100}}
    .floating-phone{{width:56px;height:56px;background:var(--olive);border-radius:50%;display:flex;align-items:center;justify-content:center}}
    .nav-overlay{{position:fixed;inset:0;z-index:200;background:var(--black);opacity:0;pointer-events:none}}
    [data-animate]{{opacity:0;transform:translateY(40px);transition:opacity .8s cubic-bezier(.16,1,.3,1),transform .8s cubic-bezier(.16,1,.3,1)}}
    [data-animate="fade-right"]{{transform:translateX(-40px)}}
    [data-animate="fade-left"]{{transform:translateX(40px)}}
    [data-animate].is-visible{{opacity:1;transform:translate(0,0)}}
    .primary-button{{display:inline-block;padding:16px 32px;border:1px solid var(--olive);color:var(--light-gray);font-size:12px;font-weight:500;letter-spacing:3px;text-transform:uppercase;transition:background .3s,color .3s}}
    .primary-button:hover{{background:var(--olive);color:var(--white)}}
    .olive-button{{display:inline-block;padding:18px 40px;background:var(--olive);color:var(--white);font-size:12px;font-weight:600;letter-spacing:3px;text-transform:uppercase;transition:background .3s}}
    .olive-button:hover{{background:var(--olive-light)}}
    .page-hero{{position:relative;min-height:70vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:140px 40px 60px;overflow:hidden;background:var(--black)}}
    .page-hero-bg{{position:absolute;inset:0;z-index:0;opacity:.3}}
    .page-hero-bg img{{width:100%;height:100%;object-fit:cover}}
    .page-hero-overlay{{position:absolute;inset:0;background:rgba(0,0,0,.4);z-index:1}}
    .page-hero-content{{position:relative;z-index:2;max-width:960px}}
    .eyebrow{{font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:var(--olive-light);margin-bottom:16px}}
    .page-hero h1{{font-family:var(--heading-font);font-size:56px;font-weight:400;line-height:1.1;color:var(--white);margin-bottom:20px}}
    .page-hero p{{font-size:17px;color:var(--light-gray);font-weight:300;max-width:720px;line-height:1.7;margin:0 auto 32px}}
    .section{{padding:100px 40px}}
    .section--dark{{background:var(--dark)}}
    .section-inner{{max-width:1200px;margin:0 auto}}
    .section-heading{{font-family:var(--heading-font);font-size:42px;font-weight:400;color:var(--white);line-height:1.2;margin-bottom:24px}}
    .section-body p{{font-size:15px;line-height:1.8;color:var(--light-gray);font-weight:300;margin-bottom:20px}}
    .text-center{{text-align:center}}
    @media (max-width:768px){{
      .page-hero h1{{font-size:34px}}
      .page-hero{{padding:120px 24px 60px;min-height:60vh}}
      .section{{padding:64px 24px}}
      .section-heading{{font-size:30px}}
      .header{{padding:16px 20px}}
    }}
    {extra_head}
  </style>

  <link rel="stylesheet" href="/styles.css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="/styles.css"></noscript>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <link href="https://use.typekit.net/iqt4hfw.css" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://use.typekit.net/iqt4hfw.css" rel="stylesheet">
  </noscript>
</head>
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
      <div class="nav-label">NAVIGATE:</div>
      <div class="nav-links">
        <a href="/">Home</a>
        <a href="/meet-the-team">Meet the Team</a>
        <a href="/services">Classic Services</a>
        <a href="/nbr-extensions">NBR Extensions</a>
        <a href="/wigs">Wigs</a>
        <a href="/shop">Shop</a>
        <a href="/hair-gallery">Hair Gallery</a>
        <a href="/blog">Blog</a>
        <a href="/booking">Book Appointment</a>
        <a href="/contact">Contact</a>
        <a href="/nically-hair">Nically Hair</a>
        <a href="/careers">Careers</a>
        <a href="/shadowing-program">Shadowing Program</a>
      </div>
    </div>
  </nav>
'''

FOOT = '''
  <script src="/script.js" defer></script>
</body>
</html>
'''

# ---------------------------------------------------------------------------
# Page definitions
# ---------------------------------------------------------------------------

PAGES = {}

# ===== SERVICES =====
PAGES["services.html"] = dict(
    title="Salon Services Fresno | Studio One Hair Design",
    description="The true salon classics and more — cut, color, keratin, extensions, and styling services at Studio One Hair Design in Fresno.",
    path="/services",
    extra_head=".service-row{display:grid;grid-template-columns:300px 1fr 140px;gap:40px;padding:32px 0;border-bottom:1px solid rgba(255,255,255,.08);align-items:start}.service-row h3{font-family:var(--heading-font);font-size:26px;color:var(--white);font-weight:400;line-height:1.2}.service-row p{font-size:14px;color:var(--light-gray);font-weight:300;line-height:1.7}.service-row .price{font-size:13px;letter-spacing:2px;color:var(--olive-light);text-transform:uppercase;font-weight:500;text-align:right}.service-note{font-size:12px;color:var(--light-gray);font-weight:300;opacity:.7;margin-top:8px}@media(max-width:768px){.service-row{grid-template-columns:1fr;gap:8px}.service-row .price{text-align:left}}",
    body='''
  <section class="page-hero">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Classic Services</p>
      <h1>The true salon classics and more.</h1>
      <p>We are a hybrid salon. Pricing varies by stylist &mdash; please refer to the stylist's name under each service for accurate pricing.</p>
      <a href="https://www.vagaro.com/us02/studioone4/services" target="_blank" rel="noopener" class="olive-button">book online</a>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner">
      <div data-animate class="text-center">
        <p class="eyebrow">Hair Services</p>
        <h2 class="section-heading">Everything you need under one roof.</h2>
        <p style="font-size:15px;color:var(--light-gray);max-width:640px;margin:0 auto 8px;font-weight:300">From signature color to precision cuts, keratin smoothing, and luxury extensions &mdash; every service at Studio One is tailored to your hair, your stylist, and your goals.</p>
      </div>
      <div data-animate style="max-width:960px;margin:60px auto 0">
        <div class="service-row">
          <h3>NBR Extensions</h3>
          <div><p>Our signature hand-tied beaded row method using ISLA Hair. Certified artists only. Custom installed for fullness, length, and blend.</p><p class="service-note">First install requires application + consultation.</p></div>
          <div class="price"><a href="/nbr-extensions" style="color:var(--olive-light);border-bottom:1px solid var(--olive-light);padding-bottom:2px">View Packages</a></div>
        </div>
        <div class="service-row">
          <h3>Luxury Color</h3>
          <div><p>Dimensional color, highlights, balayage, gray coverage, and corrective work. We specialize in low-maintenance transformations that look natural as they grow out.</p></div>
          <div class="price">By Stylist</div>
        </div>
        <div class="service-row">
          <h3>Keratin Treatment</h3>
          <div><p>A smoothing, conditioning treatment for all hair types. Softens curls, reduces frizz, and restores shine &mdash; especially effective on over-processed or dry hair.</p></div>
          <div class="price">By Stylist</div>
        </div>
        <div class="service-row">
          <h3>Haircuts &amp; Styling</h3>
          <div><p>Precision cuts, blowouts, and event styling. Every cut is designed around your face shape, texture, and daily routine.</p></div>
          <div class="price">By Stylist</div>
        </div>
        <div class="service-row">
          <h3>Wigs &amp; Hair Replacement</h3>
          <div><p>Luxury, medical, and topper options for thinning hair, medical hair loss, or style variety. Fitted, cut, and styled for a natural look.</p></div>
          <div class="price"><a href="/wigs" style="color:var(--olive-light);border-bottom:1px solid var(--olive-light);padding-bottom:2px">Learn More</a></div>
        </div>
        <div class="service-row">
          <h3>Textured &amp; Curly Hair</h3>
          <div><p>Specialized services for natural curls, waves, and textured hair &mdash; cuts, conditioning, and curl-supportive styling.</p></div>
          <div class="price">By Stylist</div>
        </div>
      </div>
      <div data-animate style="text-align:center;margin-top:60px">
        <a href="https://www.vagaro.com/us02/studioone4/services" target="_blank" rel="noopener" class="olive-button">see pricing &amp; book</a>
      </div>
    </div>
  </section>

  <section class="section text-center">
    <div class="section-inner" data-animate>
      <p class="eyebrow">Meet Your Stylist</p>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Every chair at Studio One is led by a specialist.</h2>
      <p style="font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 32px;font-weight:300">Browse our stylists and book directly with the artist who fits your goals.</p>
      <a href="/meet-the-team" class="primary-button">meet the team</a>
    </div>
  </section>
''')

# ===== NICALLY HAIR =====
PAGES["nically-hair.html"] = dict(
    title="Nically Hair Extensions | Studio One Fresno",
    description="Nically Hair is more than a brand. Premium hand-tied extensions designed for natural movement and lasting wear. Apply to become a Nically stylist.",
    path="/nically-hair",
    extra_head=".feature-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin-top:48px}.feature-card{padding:32px 24px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:4px}.feature-card h3{font-family:var(--heading-font);font-size:22px;font-weight:400;color:var(--white);margin-bottom:12px}.feature-card p{font-size:14px;color:var(--light-gray);font-weight:300;line-height:1.7}@media(max-width:1024px){.feature-grid{grid-template-columns:1fr 1fr}}@media(max-width:768px){.feature-grid{grid-template-columns:1fr}}",
    body='''
  <section class="page-hero">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">The Future of Hair Extensions</p>
      <h1>Why Nically Hair?</h1>
      <p>Nically Hair is more than just a brand &mdash; born from experience, designed for you. Premium hand-tied extensions built to move, wear, and blend like your own hair.</p>
      <a href="https://form.jotform.com/243497737778075" target="_blank" rel="noopener" class="olive-button">apply now</a>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner">
      <div data-animate class="text-center">
        <p class="eyebrow">What Makes Nically Different</p>
        <h2 class="section-heading" style="max-width:780px;margin:0 auto 16px">Built on decades of chair time, not a factory floor.</h2>
        <p style="font-size:16px;color:var(--light-gray);max-width:700px;margin:0 auto;font-weight:300">Nically Hair was developed by stylists who know exactly what extensions need to look, feel, and wear like &mdash; because they install them every day.</p>
      </div>
      <div class="feature-grid" data-animate>
        <div class="feature-card">
          <h3>Premium Quality</h3>
          <p>Sourced for longevity and a seamless blend. Each weft is hand-tied for a natural finish that doesn't look like an extension.</p>
        </div>
        <div class="feature-card">
          <h3>Made for Stylists</h3>
          <p>Designed by pros, for pros. Nically works with your installation method and color work &mdash; not against it.</p>
        </div>
        <div class="feature-card">
          <h3>Consistent Color</h3>
          <p>Color consistency across batches means your move-up looks as flawless as day one, every time.</p>
        </div>
        <div class="feature-card">
          <h3>Durability That Lasts</h3>
          <p>With proper care, Nically Hair is built to last through multiple move-up cycles without shedding or matting.</p>
        </div>
        <div class="feature-card">
          <h3>Stylist Education</h3>
          <p>Join a community of certified Nically stylists with access to ongoing education, technique refinement, and support.</p>
        </div>
        <div class="feature-card">
          <h3>Born from Experience</h3>
          <p>Developed by Cat Barco, a stylist with nearly three decades behind the chair. Real-world tested, guest approved.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section text-center">
    <div class="section-inner" data-animate>
      <p class="eyebrow">For Stylists</p>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Apply to become a Nically Hair stylist.</h2>
      <p style="font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 32px;font-weight:300">Join a growing network of certified stylists offering Nically Hair to their guests. Share your background and we'll reach out.</p>
      <a href="https://form.jotform.com/243497737778075" target="_blank" rel="noopener" class="olive-button">apply now</a>
    </div>
  </section>
''')

# ===== WIGS =====
PAGES["wigs.html"] = dict(
    title="Wigs &amp; Hair Replacement Fresno | Studio One",
    description="Luxury wigs, medical wigs, and hair toppers at Studio One Fresno. Custom fitted, cut, and styled for a natural look. Book a consultation.",
    path="/wigs",
    extra_head=".wig-categories{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:48px}.wig-cat{padding:40px 24px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:4px;text-align:center}.wig-cat h3{font-family:var(--heading-font);font-size:22px;color:var(--white);margin-bottom:8px;font-weight:400}.wig-cat p{font-size:13px;color:var(--light-gray);font-weight:300;line-height:1.6}@media(max-width:1024px){.wig-categories{grid-template-columns:repeat(2,1fr)}}@media(max-width:640px){.wig-categories{grid-template-columns:1fr}}",
    body='''
  <section class="page-hero">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Wigs &amp; Hair Replacement</p>
      <h1>Natural hair, beautifully reimagined.</h1>
      <p>Whether you're navigating hair loss, medical treatment, or style variety &mdash; we fit, cut, and style each wig so it looks and feels like your own hair.</p>
      <a href="https://form.jotform.com/253186527338161" target="_blank" rel="noopener" class="olive-button">book a consultation</a>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner">
      <div data-animate class="text-center">
        <p class="eyebrow">Our Offerings</p>
        <h2 class="section-heading">Four paths to the right wig.</h2>
        <p style="font-size:15px;color:var(--light-gray);max-width:640px;margin:0 auto;font-weight:300">Not every wig needs to feel like a wig. Every option at Studio One is hand-selected, fitted, and styled to look invisibly natural.</p>
      </div>
      <div class="wig-categories" data-animate>
        <div class="wig-cat">
          <h3>Luxury</h3>
          <p>High-end, premium synthetic and human-hair wigs for daily wear or style variety.</p>
        </div>
        <div class="wig-cat">
          <h3>Medical</h3>
          <p>Designed for medical hair loss &mdash; comfortable, secure, and fitted with care and discretion.</p>
        </div>
        <div class="wig-cat">
          <h3>Toppers</h3>
          <p>Partial hair solutions for thinning at the crown. Adds fullness without replacing your whole hair.</p>
        </div>
        <div class="wig-cat">
          <h3>Blended</h3>
          <p>A hybrid approach mixing toppers, clip-ins, or extensions for a customized fullness solution.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="section-inner" data-animate>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center">
        <div>
          <p class="eyebrow">Why Work with Hope</p>
          <h2 class="section-heading">Trusted, discreet, and trained in texture services.</h2>
          <p style="font-size:15px;color:var(--light-gray);font-weight:300;line-height:1.8">Hope Sanchez leads our wig and hair replacement work at Studio One. With deep experience in hair texture, cuts, and color, every wig is finished to match your face, lifestyle, and expression.</p>
          <div style="margin-top:32px"><a href="/team-members/hope-sanchez" class="primary-button">meet hope</a></div>
        </div>
        <div>
          <img src="/images/team/hope.webp" alt="Hope Sanchez, wig specialist at Studio One" loading="lazy" decoding="async" style="border-radius:4px">
        </div>
      </div>
    </div>
    <style>@media(max-width:1024px){.section-inner > div{grid-template-columns:1fr!important;gap:32px!important}}</style>
  </section>

  <section class="section section--dark text-center">
    <div class="section-inner" data-animate>
      <p class="eyebrow">Next Step</p>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Ready for a wig consultation?</h2>
      <p style="font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 32px;font-weight:300">Share a bit about you and we'll schedule a private consultation to discuss fit, style, and care.</p>
      <a href="https://form.jotform.com/253186527338161" target="_blank" rel="noopener" class="olive-button">book a consultation</a>
    </div>
  </section>
''')

# ===== BOOKING =====
PAGES["booking.html"] = dict(
    title="Book an Appointment | Studio One Hair Design Fresno",
    description="Book your appointment at Studio One Fresno. Choose your stylist and service online through Vagaro, or start an NBR extensions application.",
    path="/booking",
    extra_head=".booking-paths{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:48px}.booking-card{padding:48px 36px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.08);border-radius:4px;text-align:center}.booking-card h2{font-family:var(--heading-font);font-size:32px;font-weight:400;color:var(--white);margin-bottom:16px;line-height:1.2}.booking-card p{font-size:14px;color:var(--light-gray);font-weight:300;line-height:1.7;margin-bottom:28px;min-height:80px}@media(max-width:768px){.booking-paths{grid-template-columns:1fr}}",
    body='''
  <section class="page-hero" style="min-height:60vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Book Now</p>
      <h1>Let&rsquo;s get you in the chair.</h1>
      <p>We use Vagaro for classic services and JotForm for NBR extension applications. Pick the path that matches your appointment.</p>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner">
      <div class="booking-paths" data-animate>
        <div class="booking-card">
          <p class="eyebrow">Classic Services</p>
          <h2>Book with Vagaro</h2>
          <p>Cut, color, keratin, styling, textured services, and move-up appointments. Choose your stylist, pick a time, done.</p>
          <a href="https://www.vagaro.com/us02/studioone4/services" target="_blank" rel="noopener" class="olive-button">book online</a>
        </div>
        <div class="booking-card">
          <p class="eyebrow">New NBR Guests</p>
          <h2>NBR Application</h2>
          <p>First-time extension guests start with an application and consultation. Share your hair history and upload inspo photos.</p>
          <a href="https://form.jotform.com/83406488092160" target="_blank" rel="noopener" class="olive-button">start application</a>
        </div>
      </div>
      <div style="text-align:center;margin-top:60px" data-animate>
        <p style="font-size:14px;color:var(--light-gray);margin-bottom:16px;font-weight:300">Prefer to call or text?</p>
        <p style="font-size:24px;font-family:var(--heading-font);color:var(--white)"><a href="tel:5597959724" style="border-bottom:1px solid var(--olive);padding-bottom:4px">559-795-9724</a></p>
      </div>
    </div>
  </section>

  <section class="section text-center">
    <div class="section-inner" data-animate>
      <p class="eyebrow">Not Sure Where to Start?</p>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Meet the team first.</h2>
      <p style="font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 32px;font-weight:300">Every stylist at Studio One has a specialty. Find the one who fits your hair goals, then book directly with them.</p>
      <a href="/meet-the-team" class="primary-button">meet the team</a>
    </div>
  </section>
''')

# ===== CAREERS =====
PAGES["careers.html"] = dict(
    title="Careers &amp; Booth Rent at Studio One Fresno",
    description="Join Studio One Hair Design. Booth rent and commission opportunities for experienced stylists in Fresno. Apply today.",
    path="/careers",
    body='''
  <section class="page-hero" style="min-height:60vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Careers</p>
      <h1>Build your career at Studio One.</h1>
      <p>We're always looking for experienced stylists who want to elevate their craft in a luxury hybrid salon environment. Booth rent and commission options available.</p>
      <a href="https://form.jotform.com/catbarco/application-for-booth-rent-commissi" target="_blank" rel="noopener" class="olive-button">apply now</a>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner">
      <div data-animate class="text-center">
        <p class="eyebrow">What We Offer</p>
        <h2 class="section-heading" style="max-width:780px;margin:0 auto 16px">A salon that invests in its stylists.</h2>
        <p style="font-size:16px;color:var(--light-gray);max-width:700px;margin:0 auto 48px;font-weight:300">Studio One is built on the belief that great stylists thrive when they have the right environment, tools, and support. Whether you're renting a booth or working on commission, we make it easy to do your best work.</p>
      </div>
      <div data-animate style="display:grid;grid-template-columns:repeat(3,1fr);gap:32px;max-width:1000px;margin:0 auto">
        <div style="text-align:center"><p style="font-size:11px;letter-spacing:3px;color:var(--olive-light);text-transform:uppercase;margin-bottom:8px;font-weight:600">Environment</p><p style="font-size:14px;color:var(--light-gray);font-weight:300;line-height:1.7">Modern, professional salon with the amenities and ambience your guests deserve.</p></div>
        <div style="text-align:center"><p style="font-size:11px;letter-spacing:3px;color:var(--olive-light);text-transform:uppercase;margin-bottom:8px;font-weight:600">Tools</p><p style="font-size:14px;color:var(--light-gray);font-weight:300;line-height:1.7">Access to the products, education, and support you need to deliver premium results.</p></div>
        <div style="text-align:center"><p style="font-size:11px;letter-spacing:3px;color:var(--olive-light);text-transform:uppercase;margin-bottom:8px;font-weight:600">Flexibility</p><p style="font-size:14px;color:var(--light-gray);font-weight:300;line-height:1.7">Booth rent or commission &mdash; we'll find the structure that fits your practice.</p></div>
      </div>
      <style>@media(max-width:768px){.section-inner > div:last-child{grid-template-columns:1fr!important}}</style>
    </div>
  </section>

  <section class="section text-center">
    <div class="section-inner" data-animate>
      <p class="eyebrow">Ready?</p>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Apply for booth rent or commission.</h2>
      <p style="font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 32px;font-weight:300">Tell us about your experience, your clientele, and what you're looking for &mdash; we'll follow up within a few business days.</p>
      <a href="https://form.jotform.com/catbarco/application-for-booth-rent-commissi" target="_blank" rel="noopener" class="olive-button">submit application</a>
    </div>
  </section>
''')

# ===== SHADOWING PROGRAM =====
PAGES["shadowing-program.html"] = dict(
    title="Stylist Shadowing Program | Studio One Fresno",
    description="Learn from Cat Barco and the Studio One team. Our shadowing program is designed for stylists looking to level up their craft and client experience.",
    path="/shadowing-program",
    body='''
  <section class="page-hero" style="min-height:60vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Education &amp; Growth</p>
      <h1>Shadowing Program</h1>
      <p>Shadow Cat Barco and the Studio One team. Built for stylists ready to sharpen their craft, refine their consultations, and elevate the guest experience.</p>
      <a href="https://form.jotform.com/catbarco/application-for-booth-rent-commissi" target="_blank" rel="noopener" class="olive-button">apply to shadow</a>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner">
      <div data-animate class="text-center" style="max-width:780px;margin:0 auto">
        <p class="eyebrow">What You'll Experience</p>
        <h2 class="section-heading">Real chairs, real guests, real craft.</h2>
        <p style="font-size:16px;color:var(--light-gray);font-weight:300;line-height:1.8;margin-bottom:20px">The Studio One shadowing program is hands-on. You'll watch the full guest journey &mdash; from consultation to color, cut, extensions, and finishing &mdash; and get time with the team to ask the questions that matter to your practice.</p>
        <p style="font-size:16px;color:var(--light-gray);font-weight:300;line-height:1.8">This isn't a class. It's an immersion.</p>
      </div>
    </div>
  </section>

  <section class="section text-center">
    <div class="section-inner" data-animate>
      <p class="eyebrow">Next Step</p>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Apply to the shadowing program.</h2>
      <p style="font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 32px;font-weight:300">Programs run by application. Tell us about yourself and we'll reach out with availability and next steps.</p>
      <a href="https://form.jotform.com/catbarco/application-for-booth-rent-commissi" target="_blank" rel="noopener" class="olive-button">submit application</a>
    </div>
  </section>
''')

# ===== PROMOS =====
PAGES["promos.html"] = dict(
    title="Current Promotions | Studio One Hair Design Fresno",
    description="Check back for current offers and promotions at Studio One Fresno. Call or text 559-795-9724 to hear about what's running this month.",
    path="/promos",
    body='''
  <section class="page-hero" style="min-height:60vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Promotions</p>
      <h1>Special offers running now.</h1>
      <p>We rotate promotions seasonally &mdash; the best way to hear about current offers is to call, text, or follow us on Instagram.</p>
    </div>
  </section>

  <section class="section section--dark text-center">
    <div class="section-inner" data-animate>
      <p class="eyebrow">Stay in the Loop</p>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">How to hear about every promo.</h2>
      <p style="font-size:16px;color:var(--light-gray);max-width:560px;margin:0 auto 32px;font-weight:300">Call or text 559-795-9724, follow @studioonefresno on Instagram, or subscribe to our newsletter &mdash; we'll make sure you don't miss a thing.</p>
      <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
        <a href="tel:5597959724" class="olive-button">call 559-795-9724</a>
        <a href="sms:5597959724" class="primary-button">text us</a>
      </div>
      <p style="margin-top:40px"><a href="https://www.instagram.com/studioonefresno/" target="_blank" rel="noopener" style="font-size:12px;letter-spacing:3px;text-transform:uppercase;color:var(--off-white);border-bottom:1px solid var(--olive);padding-bottom:4px">@studioonefresno on instagram</a></p>
    </div>
  </section>
''')

# ===== LEGAL =====
PAGES["legal.html"] = dict(
    title="Legal &amp; Privacy | Studio One Hair Design Fresno",
    description="Legal notices, privacy policy, and terms of use for Studio One Hair Design. Questions? Contact us at 559-795-9724.",
    path="/legal",
    extra_head=".legal-body h2{font-family:var(--heading-font);font-size:30px;color:var(--white);font-weight:400;margin:48px 0 16px}.legal-body h3{font-size:14px;color:var(--off-white);font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:32px 0 12px}.legal-body p{font-size:15px;color:var(--light-gray);font-weight:300;line-height:1.8;margin-bottom:16px}",
    body='''
  <section class="page-hero" style="min-height:40vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Legal</p>
      <h1>Legal &amp; Privacy</h1>
    </div>
  </section>

  <section class="section">
    <div class="section-inner" style="max-width:800px">
      <div class="legal-body" data-animate>
        <p><em>Last updated: April 2026</em></p>

        <h2>Privacy Policy</h2>
        <p>Studio One Hair Design ("we", "us", "our") respects your privacy. This policy explains what information we collect when you visit studioonefresno.com, book an appointment, or interact with us.</p>

        <h3>Information We Collect</h3>
        <p>We collect information you voluntarily provide through forms (name, email, phone, hair history), and information automatically collected via analytics tools (pages visited, device type, referring site). We use Google Analytics, Google Tag Manager, and Meta Pixel to understand how our site is used.</p>

        <h3>How We Use Your Information</h3>
        <p>We use your information to respond to inquiries, schedule appointments, send service-related communications, and improve the site. We do not sell your personal data.</p>

        <h3>Third-Party Services</h3>
        <p>We use third-party platforms for specific functions: Vagaro (booking), JotForm (applications and consultations), Cherry (payment plans), PayPal (ecommerce), and Google Maps. Each has its own privacy policy governing your data.</p>

        <h3>Cookies &amp; Tracking</h3>
        <p>Our site uses cookies for analytics and functionality. You can manage cookies through your browser settings.</p>

        <h3>Your Rights</h3>
        <p>You may request access, correction, or deletion of your personal data at any time by contacting us at 559-795-9724.</p>

        <h2>Terms of Service</h2>

        <h3>Appointments &amp; Cancellations</h3>
        <p>Appointments are booked through Vagaro or directly with a stylist. We request at least 24 hours notice for cancellations. Repeated no-shows may result in a card-on-file requirement for future bookings.</p>

        <h3>Service Guarantees</h3>
        <p>If you're not happy with a service, contact us within 7 days and we'll make it right. Extensions and color services include a consultation step so expectations are aligned before the appointment.</p>

        <h3>Returns &amp; Refunds on Products</h3>
        <p>Unopened, unused products may be returned within 30 days of purchase with receipt. Opened or used products are not eligible for return. Hair extension orders are non-refundable once cut or custom-ordered.</p>

        <h2>Contact</h2>
        <p>Questions about this policy or your data? Reach us at:</p>
        <p>Studio One Hair Design<br>2950 E Nees Ave., #103<br>Fresno, CA 93720<br><a href="tel:5597959724" style="color:var(--olive-light);border-bottom:1px solid var(--olive-light)">559-795-9724</a></p>
      </div>
    </div>
  </section>
''')

# ===== MENU (DRINKS MENU) =====
PAGES["menu.html"] = dict(
    title="Drinks Menu | Studio One Hair Design Fresno",
    description="Enjoy a signature drink during your appointment. From matcha green tea lemonade to protein coffee — the Studio One menu rotates with the seasons.",
    path="/menu",
    extra_head=".drinks-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:48px}.drink-card{padding:32px 24px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:4px;text-align:center}.drink-card h3{font-family:var(--heading-font);font-size:22px;color:var(--white);margin-bottom:8px;font-weight:400}.drink-card p{font-size:13px;color:var(--light-gray);font-weight:300;line-height:1.6}@media(max-width:768px){.drinks-grid{grid-template-columns:1fr}}",
    body='''
  <section class="page-hero" style="min-height:55vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Refreshments</p>
      <h1>The Studio One menu.</h1>
      <p>Every appointment comes with a drink on the house. The menu rotates with the seasons &mdash; here's what we're loving right now.</p>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner">
      <div data-animate class="text-center">
        <p class="eyebrow">Signature Drinks</p>
        <h2 class="section-heading">Because the chair deserves a treat.</h2>
      </div>
      <div class="drinks-grid" data-animate>
        <div class="drink-card"><h3>Protein Coffee</h3><p>Iced or hot. A creamy, high-protein spin on the classic espresso drink. Cat's personal go-to.</p></div>
        <div class="drink-card"><h3>Matcha Green Tea Lemonade</h3><p>Bright, refreshing, and loaded with antioxidants. A warm-weather favorite.</p></div>
        <div class="drink-card"><h3>Classic Cold Brew</h3><p>Slow-steeped overnight. Smooth, low-acid, and ready to keep you going through your appointment.</p></div>
        <div class="drink-card"><h3>Chai Latte</h3><p>Spiced, warm, and frothed. A cozy option for longer sessions.</p></div>
        <div class="drink-card"><h3>Sparkling Water</h3><p>A rotating selection of flavored and unflavored sparkling options.</p></div>
        <div class="drink-card"><h3>Hot Tea</h3><p>A curated selection of loose-leaf and specialty teas. Ask your stylist what's steeping.</p></div>
      </div>
      <div style="text-align:center;margin-top:48px" data-animate>
        <p style="font-size:14px;color:var(--light-gray);font-weight:300">Have a favorite we don't have? Let your stylist know &mdash; we love suggestions.</p>
      </div>
    </div>
  </section>

  <section class="section text-center">
    <div class="section-inner" data-animate>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Book your next visit.</h2>
      <a href="/booking" class="olive-button">book an appointment</a>
    </div>
  </section>
''')

# ===== HAIR GALLERY =====
PAGES["hair-gallery.html"] = dict(
    title="Hair Gallery | Studio One Hair Design Fresno",
    description="Browse our work — NBR extensions, dimensional color, keratin treatments, and curl transformations from Studio One Fresno.",
    path="/hair-gallery",
    extra_head=".gallery-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:4px}.gallery-grid img{aspect-ratio:1;object-fit:cover;width:100%;transition:transform .5s}.gallery-grid a:hover img{transform:scale(1.03)}.gallery-filter{display:flex;gap:24px;justify-content:center;flex-wrap:wrap;margin:32px 0 48px}.gallery-filter button{font-size:12px;font-weight:500;letter-spacing:2px;text-transform:uppercase;color:var(--light-gray);padding:8px 2px;border-bottom:1px solid transparent;transition:color .3s,border-color .3s}.gallery-filter button:hover,.gallery-filter button.active{color:var(--white);border-color:var(--olive)}@media(max-width:1024px){.gallery-grid{grid-template-columns:repeat(3,1fr)}}@media(max-width:640px){.gallery-grid{grid-template-columns:repeat(2,1fr)}}",
    body='''
  <section class="page-hero" style="min-height:55vh">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content" data-animate>
      <p class="eyebrow">Our Work</p>
      <h1>Hair Gallery</h1>
      <p>Real transformations from real guests. Browse by category or scroll the full feed.</p>
    </div>
  </section>

  <section class="section section--dark">
    <div class="section-inner" data-animate>
      <div class="gallery-filter">
        <button class="active" data-filter="all">View All</button>
        <button data-filter="nbr">NBR Extensions</button>
        <button data-filter="color">Luxury Color</button>
        <button data-filter="keratin">Keratin</button>
      </div>
      <div class="gallery-grid" data-animate>
        <!-- Gallery will pull from existing optimized homepage images + team portfolios -->
        <a href="#"><img src="/images/optimized/gallery-1.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-2.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-3.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-4.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-5.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-6.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-7.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-8.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-9.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-10.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-11.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-12.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-13.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-14.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/optimized/gallery-15.webp" alt="Hair transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/cat/portfolio-1.webp" alt="Cat Barco transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/cat/portfolio-2.webp" alt="Cat Barco transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/cat/portfolio-3.webp" alt="Cat Barco transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/cat/portfolio-4.webp" alt="Cat Barco transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/hope/portfolio-1.webp" alt="Hope Sanchez transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/hope/portfolio-2.webp" alt="Hope Sanchez transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/hope/portfolio-3.webp" alt="Hope Sanchez transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/amber/portfolio-1.webp" alt="Amber Kehoe transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/amber/portfolio-2.webp" alt="Amber Kehoe transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/carina-lopez/portfolio-1.webp" alt="Carina Lopez transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/carina-lopez/portfolio-2.webp" alt="Carina Lopez transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/makayla-davila/portfolio-1.webp" alt="Makayla Davila transformation" loading="lazy" decoding="async"></a>
        <a href="#"><img src="/images/team/makayla-davila/portfolio-2.webp" alt="Makayla Davila transformation" loading="lazy" decoding="async"></a>
      </div>
    </div>
  </section>

  <section class="section text-center">
    <div class="section-inner" data-animate>
      <h2 class="section-heading" style="max-width:720px;margin:0 auto 20px">Your transformation starts here.</h2>
      <a href="/booking" class="olive-button">book your consultation</a>
    </div>
  </section>
''')

# ===== 404 =====
PAGES["404.html"] = dict(
    title="Page Not Found | Studio One Hair Design Fresno",
    description="The page you're looking for doesn't exist. Let's get you back to Studio One.",
    path="/404",
    body='''
  <section style="min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 40px;background:var(--black)">
    <div data-animate>
      <p class="eyebrow">404</p>
      <h1 style="font-family:var(--heading-font);font-size:72px;font-weight:400;color:var(--white);line-height:1;margin-bottom:20px">Lost in the mirror.</h1>
      <p style="font-size:17px;color:var(--light-gray);max-width:520px;margin:0 auto 40px;font-weight:300">The page you were looking for isn't here anymore &mdash; or maybe never was. Let's get you back to the good stuff.</p>
      <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
        <a href="/" class="olive-button">back home</a>
        <a href="/booking" class="primary-button">book an appointment</a>
      </div>
    </div>
  </section>
''')

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

for filename, config in PAGES.items():
    head = HEAD(
        title=config["title"],
        description=config["description"],
        path=config["path"],
        preload_hero=config.get("preload_hero"),
        extra_head=config.get("extra_head", ""),
        schema=config.get("schema", ""),
    )
    html_out = head + config["body"] + FOOT
    outpath = ROOT / filename
    outpath.write_text(html_out)
    size_kb = os.path.getsize(outpath) // 1024
    print(f"✓ {filename} ({size_kb}KB)")

print(f"\nBuilt {len(PAGES)} pages.")
