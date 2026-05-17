#!/usr/bin/env python3
"""Generate the 11 newly-scraped blog post pages WITHOUT touching the
existing 42. Reuses build-blog.py's head/body/style templates verbatim so
the output is byte-consistent with the already-migrated posts, then appends
the universal footer (extracted from an existing post)."""
import json, re, html, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
BLOG_JSON = ROOT / "content-export/blog"
BLOG_OUT = ROOT / "blog"
IMG_OUT = ROOT / "images/blog"

CATEGORIES = {
    "behind-the-scenes": "Behind the Scenes", "client-spotlights": "Client Spotlights",
    "color": "Color", "extensions": "Extensions", "hair-care": "Hair Care",
    "hair-products": "Hair Products", "salon-team": "Salon Team", "styling": "Styling",
}
NEW_CAT_MAP = {
    "ditch-the-salon-hop-find-your-forever-hair-home-at-studio-one": "behind-the-scenes",
    "hair-extensions-for-busy-moms-time-saving-styles-confidence-boost": "extensions",
    "hair-extensions-fresno-viral-trend-vs-reality": "extensions",
    "hair-extensions-overcome-fears-get-gorgeous-hair": "extensions",
    "hair-salon-near-madera-studio-one-hair-design": "behind-the-scenes",
    "lisa-rinnas-hair-dress-extensions-as-art": "extensions",
    "nail-hair-salon-near-fresno-find-your-perfect-style-at-studio-one": "behind-the-scenes",
    "nbr-hair-extensions-central-valleys-best-secret": "extensions",
    "reclaim-your-crown-thinning-hair-solutions-fresno": "hair-care",
    "semi-permanent-hair-color-is-it-right-for-you": "color",
    "spring-2026-hair-trends-the-density-era": "styling",
}
DEFAULT_HERO = "/images/optimized/services-bg.webp"

# ---- pull template constants straight out of build-blog.py (no drift) ----
src = (ROOT / "scripts/build-blog.py").read_text()
ns = {"json": json, "html": html, "re": re}
for name in ("BODY_OPEN", "POST_PAGE_STYLE"):
    m = re.search(rf'{name} = """(.*?)"""', src, re.S)
    ns[name] = m.group(1)
# head_block + post_body_html function defs
for fn in ("def head_block", "def post_body_html"):
    m = re.search(rf'\n{fn}.*?(?=\n\ndef |\n\n# ---)', src, re.S)
    exec(m.group(0), ns)
head_block = ns["head_block"]
post_body_html = ns["post_body_html"]
BODY_OPEN = ns["BODY_OPEN"]
POST_PAGE_STYLE = ns["POST_PAGE_STYLE"]
FOOTER = (ROOT / "scripts/../").resolve()  # placeholder
FOOTER = Path("/tmp/blog-footer.html").read_text()

# ---- load every post (42 existing + 11 new) for related-post picking ----
posts = {}
for fp in sorted(BLOG_JSON.glob("*.json")):
    d = json.load(open(fp))
    posts[d["slug"]] = d

# map categories for ALL posts
import importlib.util
# crude: read POST_CAT_MAP out of build-blog.py for the existing 42
m = re.search(r'POST_CAT_MAP = \{(.*?)\n\}', src, re.S)
EXIST_MAP = {}
for km in re.finditer(r'"([^"]+)":\s*"([^"]+)"', m.group(1)):
    EXIST_MAP[km.group(1)] = km.group(2)
FULL_MAP = {**EXIST_MAP, **NEW_CAT_MAP}

for slug, d in posts.items():
    cat = FULL_MAP.get(slug, "hair-care")
    d["mapped_cat"] = cat
    d["cat_label"] = CATEGORIES[cat]
    body = d.get("body_text") or ""
    words = re.split(r"\s+", body.strip())
    d["excerpt"] = " ".join(words[:28]) + ("…" if len(words) > 28 else "")
    d["local_hero"] = f"/images/blog/{slug}.webp" if (IMG_OUT / f"{slug}.webp").exists() else DEFAULT_HERO

def sort_key(p):
    return p.get("published_date", "") or ""

def render_post(p):
    cat = p["mapped_cat"]
    same = sorted([x for x in posts.values() if x["mapped_cat"] == cat and x["slug"] != p["slug"]],
                  key=sort_key, reverse=True)
    related = same[:3]
    if len(related) < 3:
        extra = sorted([x for x in posts.values() if x["slug"] != p["slug"] and x not in related],
                       key=sort_key, reverse=True)
        related += extra[:3 - len(related)]
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
    "image":"https://studioonefresno.com{p["local_hero"]}",
    "author":{{"@type":"Organization","name":"Studio One Hair Design"}},
    "publisher":{{"@type":"Organization","name":"Studio One Hair Design","logo":{{"@type":"ImageObject","url":"https://studioonefresno.com/images/optimized/logo.avif"}}}},
    "datePublished":{json.dumps(p.get("published_date",""))},
    "mainEntityOfPage":"https://studioonefresno.com/blog/{p["slug"]}"
  }}
  </script>'''
    meta_desc = p.get("meta_description") or p["excerpt"]
    author = p.get("author") or "Studio One Team"
    date_display = p.get("published_date") or ""
    content = head_block(
        title=f'{p["title"]} | Studio One Blog',
        desc=meta_desc, path=f'/blog/{p["slug"]}',
        hero=p["local_hero"], schema=schema)
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

    <!-- Universal Footer -->
  {FOOTER}

  <script src="/script.js" defer></script>
</body>
</html>'''
    return content

# ---- download hero images for the 11 new posts ----
IMG_OUT.mkdir(parents=True, exist_ok=True)
for slug in NEW_CAT_MAP:
    p = posts[slug]
    url = p.get("hero_image_url")
    if not url:
        print(f"  × {slug}: no hero url")
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=25).read()
        img = Image.open(BytesIO(raw))
        if img.mode in ("P", "RGBA"):
            img = img.convert("RGB")
        w, h = img.size
        if w > 1200:
            img = img.resize((1200, int(h * 1200 / w)), Image.LANCZOS)
        out = IMG_OUT / f"{slug}.webp"
        img.save(out, "WEBP", quality=72, method=6)
        p["local_hero"] = f"/images/blog/{slug}.webp"
        print(f"  ✓ {slug}.webp ({out.stat().st_size // 1024}KB)")
    except Exception as e:
        print(f"  × {slug}: {e}")

# ---- write the 11 post pages ----
for slug in NEW_CAT_MAP:
    (BLOG_OUT / f"{slug}.html").write_text(render_post(posts[slug]))
    print(f"  wrote blog/{slug}.html")

print(f"\nDone: 11 new post pages.")
