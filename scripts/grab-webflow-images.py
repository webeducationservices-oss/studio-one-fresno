#!/usr/bin/env python3
"""Grab every image from the live studioonefresno.com Webflow site.

Walks key pages, extracts all Webflow CDN image URLs, downloads them,
converts to WebP, and organizes into images/ subfolders.

Idempotent: skips files that already exist on disk.
"""
import re
import urllib.request
import urllib.parse
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
IMG_ROOT = ROOT / "images"

# Pages to scrape (URL → target subfolder, description)
PAGES = [
    ("https://www.studioonefresno.com/hair-gallery",         "gallery",    "Hair gallery transformations"),
    ("https://www.studioonefresno.com/nically-hair",         "nically",    "Nically Hair studio shoot"),
    ("https://www.studioonefresno.com/nbr-extensions",       "nbr",        "NBR Extensions page"),
    ("https://www.studioonefresno.com/services",             "services",   "Services page"),
    ("https://www.studioonefresno.com/menu",                 "menu",       "Menu page"),
    ("https://www.studioonefresno.com/wigs",                 "wigs",       "Wigs page"),
    ("https://www.studioonefresno.com/careers",              "careers",    "Careers page"),
    ("https://www.studioonefresno.com/shadowing-program",    "shadowing",  "Shadowing program page"),
    ("https://www.studioonefresno.com/promos",               "promos",     "Promos page"),
    ("https://www.studioonefresno.com/",                     "home",       "Homepage"),
    ("https://www.studioonefresno.com/meet-the-team",        "team-group", "Meet the team index"),
    ("https://www.studioonefresno.com/hair-extension-methods-fresno", "extensions-methods", "Extensions methods"),
]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Match Webflow CDN image URLs (JPG, PNG, WEBP, AVIF).
# Some URLs have query strings; we strip them.
CDN_PAT = re.compile(
    r'https://cdn\.prod\.website-files\.com/[^\s"\'<>)\\]+?\.(?:jpe?g|png|webp|avif|gif)',
    re.IGNORECASE
)


def fetch(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def slugify_from_url(url: str) -> str:
    """Produce a safe on-disk filename from a Webflow CDN URL."""
    # Webflow CDN URLs look like: .../66e0eaa1372..._8E909F3E-...JPG
    # Take the last path segment and strip the extension.
    fname = url.rstrip("/").split("/")[-1]
    stem = fname.rsplit(".", 1)[0]
    # Webflow prefixes with a hash_ — keep only the descriptive part after the underscore
    if "_" in stem:
        prefix, rest = stem.split("_", 1)
        # Clean up: lowercase, replace unsafe chars
        stem = rest
    # Lowercase, keep alphanum + hyphen
    stem = re.sub(r"[^a-z0-9-]+", "-", stem.lower()).strip("-")
    # Limit length
    return stem[:60] or "img"


def optimize_to_webp(raw: bytes, out_path: Path, max_width: int = 1440, quality: int = 75) -> int:
    """Save raw image bytes to WebP. Returns bytes written."""
    img = Image.open(BytesIO(raw))
    if img.mode in ("P", "RGBA"):
        img = img.convert("RGB")
    w, h = img.size
    if w > max_width:
        img = img.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=quality, method=6)
    return out_path.stat().st_size


def main():
    # Collect { url: [folder, ...] } — a URL may appear on multiple pages
    url_folders: dict[str, set[str]] = {}
    for page_url, folder, desc in PAGES:
        print(f"\n▸ Scraping {page_url}")
        try:
            html = fetch(page_url).decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"  × fetch failed: {e}")
            continue
        urls = set(CDN_PAT.findall(html))
        # Filter out tiny UI assets (logos, icons) by checking filename patterns
        urls = {u for u in urls if not re.search(r"(logo|studio.one|icon|arrow|star-rating|pixel)", u, re.I)}
        print(f"  {len(urls)} images")
        for u in urls:
            url_folders.setdefault(u, set()).add(folder)

    print(f"\n═ {len(url_folders)} unique image URLs across all pages")

    # Download + optimize
    downloaded = 0
    skipped = 0
    failed = 0
    total_bytes = 0

    for url, folders in sorted(url_folders.items()):
        # Pick the *first* folder for this URL (alphabetical, stable)
        folder = sorted(folders)[0]
        # Longest-hero pages deserve higher quality + wider max
        is_hero_page = folder in ("home", "nbr", "extensions-methods")
        quality = 78 if is_hero_page else 72
        max_w = 1440 if is_hero_page else 1100

        slug = slugify_from_url(url)
        out_dir = IMG_ROOT / "webflow" / folder
        out_path = out_dir / f"{slug}.webp"

        if out_path.exists():
            skipped += 1
            continue

        try:
            raw = fetch(url)
            bytes_written = optimize_to_webp(raw, out_path, max_width=max_w, quality=quality)
            total_bytes += bytes_written
            downloaded += 1
            print(f"  ✓ {folder}/{slug}.webp ({bytes_written // 1024}KB)")
        except Exception as e:
            failed += 1
            print(f"  × {folder}/{slug}: {e}")

    print(f"\n═ Done: {downloaded} downloaded, {skipped} already existed, {failed} failed")
    print(f"  Total WebP bytes written: {total_bytes / (1024*1024):.1f}MB")


if __name__ == "__main__":
    main()
