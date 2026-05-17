#!/usr/bin/env python3
"""Re-scrape all blog posts from the live Webflow site, this time PRESERVING
heading structure (h2/h3) instead of flattening everything to <p>. Adds a
`body_blocks` field to each content-export/blog/<slug>.json — an ordered list
of {"tag": "h2|h3|p|li", "text": "..."} blocks for SEO-correct rendering."""
import json, re, html, urllib.request, time
from pathlib import Path

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
BLOG_JSON = ROOT / "content-export/blog"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

def strip_tags(s):
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("‍", "").replace("​", "")
    return re.sub(r"\s+", " ", s).strip()

def extract_richtext(h):
    m = re.search(r'<div[^>]*\bw-richtext\b[^>]*>', h)
    if not m:
        return ""
    start = m.end()
    depth, i = 1, start
    tag_re = re.compile(r'<(/?)div\b[^>]*>', re.I)
    last = None
    while depth > 0:
        t = tag_re.search(h, i)
        if not t:
            return h[start:i]
        depth += -1 if t.group(1) else 1
        i = t.end()
        last = t
    return h[start:i - len(last.group(0))]

def parse_blocks(rich):
    """Ordered list of {tag,text}. h1/h2 -> h2, h3/h4 -> h3, p/blockquote -> p,
    li -> li. Skips empties."""
    blocks = []
    for m in re.finditer(
            r'<(h1|h2|h3|h4|p|li|blockquote)\b[^>]*>(.*?)</\1>', rich, re.I | re.S):
        raw_tag = m.group(1).lower()
        txt = strip_tags(m.group(2))
        if not txt or not re.search(r"[A-Za-z0-9]", txt):
            continue
        if raw_tag in ("h1", "h2"):
            tag = "h2"
        elif raw_tag in ("h3", "h4"):
            tag = "h3"
        elif raw_tag == "li":
            tag = "li"
        else:
            tag = "p"
        blocks.append({"tag": tag, "text": txt})
    return blocks

def dedupe_title_heading(blocks, title):
    """Drop a leading heading that just repeats the post title."""
    def norm(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())
    while blocks and blocks[0]["tag"] in ("h2", "h3") and norm(blocks[0]["text"]) == norm(title):
        blocks.pop(0)
    return blocks

count = 0
for fp in sorted(BLOG_JSON.glob("*.json")):
    d = json.load(open(fp))
    slug = d["slug"]
    url = d.get("url_original") or f"https://www.studioonefresno.com/blog/{slug}"
    try:
        h = fetch(url)
    except Exception as e:
        print(f"  × {slug}: fetch failed {e}")
        continue
    rich = extract_richtext(h)
    blocks = dedupe_title_heading(parse_blocks(rich), d["title"])
    if not blocks:
        print(f"  ! {slug}: no blocks parsed — left as-is")
        continue
    d["body_blocks"] = blocks
    # keep body_text in sync (plain concatenation, for excerpts)
    d["body_text"] = "\n\n".join(b["text"] for b in blocks)
    fp.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    h2 = sum(1 for b in blocks if b["tag"] == "h2")
    h3 = sum(1 for b in blocks if b["tag"] == "h3")
    print(f"  ✓ {slug}: {len(blocks)} blocks (h2={h2} h3={h3})")
    count += 1
    time.sleep(0.2)

print(f"\nRe-scraped {count} posts.")
