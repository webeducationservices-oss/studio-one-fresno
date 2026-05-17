#!/usr/bin/env python3
"""Scrape the 11 blog posts that were never migrated from the live Webflow
site and write content-export/blog/<slug>.json for each, matching the
existing JSON shape that build-blog.py consumes."""
import json, re, html, urllib.request
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
OUT = ROOT / "content-export/blog"

SLUGS = [
    "ditch-the-salon-hop-find-your-forever-hair-home-at-studio-one",
    "hair-extensions-for-busy-moms-time-saving-styles-confidence-boost",
    "hair-extensions-fresno-viral-trend-vs-reality",
    "hair-extensions-overcome-fears-get-gorgeous-hair",
    "hair-salon-near-madera-studio-one-hair-design",
    "lisa-rinnas-hair-dress-extensions-as-art",
    "nail-hair-salon-near-fresno-find-your-perfect-style-at-studio-one",
    "nbr-hair-extensions-central-valleys-best-secret",
    "reclaim-your-crown-thinning-hair-solutions-fresno",
    "semi-permanent-hair-color-is-it-right-for-you",
    "spring-2026-hair-trends-the-density-era",
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def extract_richtext(h):
    """Return the inner HTML of the first w-richtext div via balanced-div parse."""
    m = re.search(r'<div[^>]*\bw-richtext\b[^>]*>', h)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    tag_re = re.compile(r'<(/?)div\b[^>]*>', re.I)
    while depth > 0:
        t = tag_re.search(h, i)
        if not t:
            break
        depth += -1 if t.group(1) else 1
        i = t.end()
    return h[start:i - len(t.group(0))] if depth == 0 else h[start:i]

def body_paragraphs(rich):
    """Block-level elements -> list of plain-text paragraphs."""
    blocks = re.findall(
        r'<(p|h2|h3|h4|li|blockquote)\b[^>]*>(.*?)</\1>', rich, re.I | re.S)
    paras = []
    for _tag, inner in blocks:
        txt = strip_tags(inner)
        txt = txt.replace("‍", "").replace("​", "").strip()
        if txt and re.search(r"[A-Za-z0-9]", txt) and txt not in paras:
            paras.append(txt)
    return paras

def first_hero(h):
    pre = h[:h.find("w-richtext")] if "w-richtext" in h else h
    imgs = re.findall(
        r'https://cdn\.prod\.website-files\.com/66c254[^"\s]+\.(?:webp|jpg|jpeg|png)',
        pre)
    for x in imgs:
        if re.search(r'-p-\d+\.', x):      # skip Webflow responsive variants
            continue
        if re.search(r'favicon|webclip|logo', x, re.I):
            continue
        return x
    return None

DATE_RE = re.compile(
    r'(January|February|March|April|May|June|July|August|September|October|'
    r'November|December)\s+\d{1,2},?\s+20\d\d')

OUT.mkdir(parents=True, exist_ok=True)
for slug in SLUGS:
    url = f"https://www.studioonefresno.com/blog/{slug}"
    h = fetch(url)
    title_m = re.search(r'<title>([^<]+)</title>', h)
    title = html.unescape(title_m.group(1)).strip() if title_m else slug
    title = re.sub(r'\s*[|\-]\s*Studio One.*$', '', title).strip()
    rich = extract_richtext(h)
    paras = body_paragraphs(rich)
    body = "\n\n".join(paras)
    dm = DATE_RE.search(h)
    date = dm.group(0).replace(",", "") if dm else ""
    hero = first_hero(h)
    excerpt = " ".join(body.split()[:32])
    data = {
        "slug": slug,
        "url_original": url,
        "title": title,
        "meta_title": None,
        "meta_description": (excerpt[:155] + "…") if excerpt else None,
        "hero_image_url": hero,
        "author": None,
        "published_date": date,
        "category": None,
        "body_text": body,
        "inline_image_urls": [],
    }
    (OUT / f"{slug}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"{slug}: {len(paras)} paras, hero={'yes' if hero else 'NO'}, date={date or 'NONE'}")
