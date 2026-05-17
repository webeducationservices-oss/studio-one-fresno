#!/usr/bin/env python3
"""Generate sitemap.xml listing every URL in the site."""
import json
from pathlib import Path
from datetime import date

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
TODAY = date.today().isoformat()
DOMAIN = "https://www.studioonefresno.com"

urls = []

# Homepage
urls.append((f"{DOMAIN}/", TODAY, "1.0", "weekly"))

# Core pages (non-blog, non-product, non-team)
CORE = [
    "menu", "meet-the-team", "services", "booking", "nbr-extensions",
    "shadowing-program", "blog", "shop", "legal", "hair-gallery",
    "promos", "nically-hair", "careers", "wigs", "cart", "contact",
    "hair-extension-methods-fresno",
]
for slug in CORE:
    urls.append((f"{DOMAIN}/{slug}", TODAY, "0.8", "monthly"))

# Team members
for slug in ["amber", "carina-lopez", "cat-barco", "hope-sanchez", "makayla-davila"]:
    urls.append((f"{DOMAIN}/team-members/{slug}", TODAY, "0.7", "monthly"))

# Blog posts
for jp in (ROOT / "content-export/blog").glob("*.json"):
    slug = jp.stem
    urls.append((f"{DOMAIN}/blog/{slug}", TODAY, "0.6", "monthly"))

# Blog categories
for cat in ["behind-the-scenes", "client-spotlights", "color", "extensions",
            "hair-care", "hair-products", "salon-team", "styling"]:
    urls.append((f"{DOMAIN}/blog-categories/{cat}", TODAY, "0.5", "weekly"))

# Products
for p in json.load(open(ROOT / "content-export/products.json")):
    urls.append((f"{DOMAIN}/product/{p['slug']}", TODAY, "0.6", "monthly"))

# Build XML
xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for url, lastmod, priority, changefreq in urls:
    xml += f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>{changefreq}</changefreq>\n    <priority>{priority}</priority>\n  </url>\n'
xml += '</urlset>\n'

(ROOT / "sitemap.xml").write_text(xml)
print(f"sitemap.xml: {len(urls)} URLs")
