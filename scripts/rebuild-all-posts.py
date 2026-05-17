#!/usr/bin/env python3
"""Regenerate ALL 53 blog post pages with SEO-correct heading structure
(real <h2>/<h3> + <ul>) from the body_blocks now stored in each JSON.
Reuses build-blog.py's templates so head/nav/styles stay byte-consistent
with the rest of the site; appends the universal footer."""
import json, re, html
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
BLOG_JSON = ROOT / "content-export/blog"
BLOG_OUT = ROOT / "blog"
IMG_OUT = ROOT / "images/blog"
DEFAULT_HERO = "/images/optimized/services-bg.webp"

CATEGORIES = {
    "behind-the-scenes": "Behind the Scenes", "client-spotlights": "Client Spotlights",
    "color": "Color", "extensions": "Extensions", "hair-care": "Hair Care",
    "hair-products": "Hair Products", "salon-team": "Salon Team", "styling": "Styling",
}

# ---- pull templates + helpers straight out of build-blog.py ----
src = (ROOT / "scripts/build-blog.py").read_text()
ns = {"json": json, "html": html, "re": re}
for name in ("BODY_OPEN", "POST_PAGE_STYLE"):
    m = re.search(rf'{name} = """(.*?)"""', src, re.S)
    ns[name] = m.group(1)
for fn in ("def head_block", "def post_body_html", "def render_body_blocks"):
    m = re.search(rf'\n{fn}.*?(?=\n\ndef |\n\n# ---)', src, re.S)
    exec(m.group(0), ns)
head_block = ns["head_block"]
render_body_blocks = ns["render_body_blocks"]
BODY_OPEN = ns["BODY_OPEN"]
POST_PAGE_STYLE = ns["POST_PAGE_STYLE"]
FOOTER = Path("/tmp/blog-footer.html").read_text()

# POST_CAT_MAP from build-blog.py
m = re.search(r'POST_CAT_MAP = \{(.*?)\n\}', src, re.S)
CAT_MAP = {a: b for a, b in re.findall(r'"([^"]+)":\s*"([^"]+)"', m.group(1))}

# ---- load all posts ----
posts = {}
for fp in sorted(BLOG_JSON.glob("*.json")):
    d = json.load(open(fp))
    slug = d["slug"]
    cat = CAT_MAP.get(slug, "hair-care")
    d["mapped_cat"] = cat
    d["cat_label"] = CATEGORIES[cat]
    body = d.get("body_text") or ""
    words = re.split(r"\s+", body.strip())
    d["excerpt"] = " ".join(words[:28]) + ("…" if len(words) > 28 else "")
    d["local_hero"] = f"/images/blog/{slug}.webp" if (IMG_OUT / f"{slug}.webp").exists() else DEFAULT_HERO
    posts[slug] = d

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
    body = render_body_blocks(p["body_blocks"]) if p.get("body_blocks") else \
        "\n    ".join(f"<p>{html.escape(x)}</p>" for x in (p.get("body_text") or "").split("\n\n") if x.strip())
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
      {body}
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

n = 0
for slug, p in posts.items():
    (BLOG_OUT / f"{slug}.html").write_text(render_post(p))
    n += 1
print(f"Rebuilt {n} post pages with h2/h3 structure.")
