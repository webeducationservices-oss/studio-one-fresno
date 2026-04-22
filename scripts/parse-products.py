#!/usr/bin/env python3
"""Parse the Webflow product CSV into clean JSON.

Groups variant rows under their parent product, infers brand from name/description,
normalizes categories.
"""
import csv, json, re
from pathlib import Path
from collections import defaultdict

ROOT = Path("/Users/justinbabcock/Desktop/Websites/studio-one-fresno")
CSV_PATH = ROOT / "content-export/Studio One - Products.csv"
OUT_PATH = ROOT / "content-export/products.json"

# Brand inference from product name keywords
BRAND_KEYWORDS = {
    "Oribe": ["gold lust", "signature", "serene scalp", "supershine", "impermeable",
              "royal blowout", "airstyle", "gel serum", "matte waves", "rough luxury",
              "maximista", "swept up", "thick dry", "free styler", "flash form",
              "apres beach", "fiber groom", "gold lust", "dry texturizing",
              "straight away", "bright blonde", "featherbalm", "hair alchemy",
              "cleansing creme", "curl gelee", "curl gloss", "run-through",
              "priming lotion", "the cleanse", "creme for", "superfine",
              "grandiose", "airbrush root", "invisible defense", "curl control",
              "moisture control", "tres set", "conditioner for beautiful color",
              "shampoo for beautiful color", "conditioner for magnificent volume",
              "shampoo for magnificent volume", "shampoo for moisture",
              "intense conditioner"],
    "Davines": ["pasta", "dede", "volu", "love", "momo", "melu",
                "oi", "hair building", "a single", "your hair assistant",
                "more inside", "this is", "authentic"],
}

# Category inference from name/type/description
CATEGORY_KEYWORDS = {
    "shampoo": ["shampoo"],
    "conditioner": ["conditioner", "masque", "rinse", "mask"],
    "treatment": ["treatment", "serum", "scalp", "oil", "elixir", "tonic"],
    "styling": ["spray", "cream", "creme", "paste", "gel", "mousse",
                "pomade", "wax", "balm", "lotion", "texturizing",
                "blowout", "heat", "styling", "finishing", "texture"],
    "color": ["level", "color-touch", "root touch", "gloss", "lightening"],
}


def infer_brand(name, desc):
    text = (name + " " + (desc or "")).lower()
    for brand, kws in BRAND_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return brand
    return "Other"


def infer_category(name, desc, ptype):
    text = (name + " " + (desc or "") + " " + (ptype or "")).lower()
    # Check color first (level 1, level 10, etc.) before shampoo
    if "level" in text and re.search(r"level\s+\d", text):
        return "color"
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return cat
    return "other"


def cents(price_str):
    """Convert '$53.00' or '53' to cents as int."""
    if not price_str:
        return 0
    cleaned = re.sub(r"[^\d.]", "", str(price_str))
    if not cleaned:
        return 0
    try:
        return int(round(float(cleaned) * 100))
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Parse CSV, grouping by Product Handle
# ---------------------------------------------------------------------------
products = {}
with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        handle = row.get("Product Handle", "").strip()
        if not handle:
            continue

        if handle not in products:
            name = (row.get("Product Name") or "").strip()
            desc = (row.get("Product Description") or "").strip()
            ptype = (row.get("Product Type") or "").strip()
            categories_field = (row.get("Product Categories") or "").strip()

            products[handle] = {
                "slug": handle,
                "name": name,
                "product_type": ptype,
                "description": desc,
                "brand": infer_brand(name, desc),
                "category": infer_category(name, desc, ptype),
                "webflow_categories": categories_field,
                "variants": [],
                "image_urls": [],  # will dedupe after
                "url_original": f"https://www.studioonefresno.com/product/{handle}",
            }

        # Variant row
        main_img = (row.get("Main Variant Image") or "").strip()
        more_imgs = (row.get("More Variant Images") or "").strip()
        imgs = []
        if main_img:
            imgs.append(main_img)
        if more_imgs:
            imgs.extend(m.strip() for m in more_imgs.split(";") if m.strip())

        # Build variant option label (e.g., "Travel (2.5 oz)")
        parts = []
        for i in (1, 2, 3):
            n = row.get(f"Option{i} Name", "").strip()
            v = row.get(f"Option{i} Value", "").strip()
            if v:
                parts.append(v)
        variant_name = " / ".join(parts) if parts else "Standard"

        price = cents(row.get("Variant Price"))
        compare_price = cents(row.get("Variant Compare-at Price"))
        inventory = row.get("Variant Inventory", "").strip()
        sku = (row.get("Variant Sku") or "").strip()
        weight = (row.get("Variant Weight") or "").strip()

        variant = {
            "name": variant_name,
            "price_cents": price,
            "price_display": f"${price/100:.2f}".rstrip("0").rstrip("."),
            "compare_at_cents": compare_price or None,
            "sku": sku,
            "inventory": inventory,
            "weight": weight,
            "main_image": main_img,
        }
        products[handle]["variants"].append(variant)
        products[handle]["image_urls"].extend(imgs)

# Dedupe images, keep order
for p in products.values():
    seen = set()
    deduped = []
    for u in p["image_urls"]:
        if u and u not in seen:
            deduped.append(u)
            seen.add(u)
    p["image_urls"] = deduped
    # Compute min/max variant price
    prices = [v["price_cents"] for v in p["variants"] if v["price_cents"] > 0]
    p["min_price_cents"] = min(prices) if prices else 0
    p["max_price_cents"] = max(prices) if prices else 0
    p["in_stock"] = any(
        v["inventory"].lower() not in ("0", "out of stock", "sold out", "", "false")
        or v["inventory"] == ""  # Webflow default when unlimited
        for v in p["variants"]
    )

# Write out
out = list(products.values())
OUT_PATH.write_text(json.dumps(out, indent=2))
print(f"Parsed {len(out)} products ({sum(len(p['variants']) for p in out)} variant rows)")

# Quick summary
from collections import Counter
brand_counts = Counter(p["brand"] for p in out)
cat_counts = Counter(p["category"] for p in out)
print(f"\nBrands: {dict(brand_counts)}")
print(f"Categories: {dict(cat_counts)}")
print(f"Products with variants: {sum(1 for p in out if len(p['variants']) > 1)}")
print(f"Total unique images: {sum(len(p['image_urls']) for p in out)}")
print(f"Price range: ${min((p['min_price_cents'] for p in out if p['min_price_cents']))/100:.0f} - ${max((p['max_price_cents'] for p in out))/100:.0f}")
print(f"\nSaved to {OUT_PATH}")
