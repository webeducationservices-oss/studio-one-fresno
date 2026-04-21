# URL Redirect Map — Webflow → Vercel Migration

**Principle**: Preserve every public-facing URL 1:1 wherever possible to protect 40+ blog-post SEO equity. Only 3 URLs change (ecommerce flow), all 301-redirected.

## Summary

| Bucket | Count | Change? |
|---|---|---|
| Homepage | 1 | No change |
| Core marketing pages | 14 | No change |
| Team member pages | 5 | No change |
| Blog posts | ~40 | No change |
| Blog category pages | 8 | No change |
| Product pages | ~105 | No change |
| Ecommerce flow | 3 | **301 redirects** |
| **Total URLs preserved** | **~173** | **~98%** |
| **Total URLs redirected** | **3** | **~2%** |

## URLs with NO Change (keep identical)

All of these keep their exact paths. No redirect needed.

### Core pages (14)
- `/` (home)
- `/menu`
- `/meet-the-team`
- `/services`
- `/booking`
- `/nbr-extensions`
- `/shadowing-program`
- `/blog`
- `/shop`
- `/legal`
- `/hair-gallery`
- `/promos`
- `/nically-hair`
- `/careers`
- `/wigs`

### Team members (5)
- `/team-members/amber`
- `/team-members/carina-lopez`
- `/team-members/cat-barco`
- `/team-members/hope-sanchez`
- `/team-members/makayla-davila`

### Blog posts (40)
All `/blog/<slug>` URLs preserved identically — these carry the most SEO value.

### Blog categories (8)
- `/blog-categories/behind-the-scenes`
- `/blog-categories/client-spotlights`
- `/blog-categories/color`
- `/blog-categories/extensions`
- `/blog-categories/hair-care`
- `/blog-categories/hair-products`
- `/blog-categories/salon-team`
- `/blog-categories/styling`

### Products (~105)
All `/product/<slug>` URLs preserved identically.

## URLs that CHANGE (301 redirect in vercel.json)

Three ecommerce endpoints need redirects because PayPal handles its own hosted checkout flow now:

| Old Webflow URL | New URL | Status | Rationale |
|---|---|---|---|
| `/checkout` | `/cart` | 301 | Webflow's self-hosted checkout is gone; `/cart` shows line items + PayPal button |
| `/paypal-checkout` | `/cart` | 301 | PayPal's modal now handles the payment step; no separate page needed |
| `/order-confirmation` | `/order-confirmation` | *keep URL, new impl* | URL unchanged but the page is re-implemented to read `?oid=` from URL (PayPal returns with order ID) |

### vercel.json redirect block to add

```json
{
  "redirects": [
    { "source": "/checkout", "destination": "/cart", "permanent": true },
    { "source": "/paypal-checkout", "destination": "/cart", "permanent": true }
  ]
}
```

No redirect needed for `/order-confirmation` — URL stays, just new content.

## Slug Normalization Checks

A few slugs to verify don't break during migration:

- `/blog/barbaras-nbr-hair-extension-journey-at-studio-one` — apostrophe-like slug okay, no special chars to escape
- `/blog/best-hair-color-for-gray-hair-a-guide-to-radiant-ageless-style` — long but valid
- `/blog/keratin-treatment-california-whats-changed-what-you-need-to-know` — long but valid
- `/blog/new-year-new-you-resolutions-weight-loss-and-how-it-affects-your-hair` — long but valid

All look clean — no `%` encoding, no special chars, no trailing slashes to strip.

## Trailing Slashes

- **Webflow**: serves without trailing slash (e.g., `/blog/foo`)
- **New Vercel config**: `trailingSlash: false` per FIRST-TIME-DEPLOYMENT.md
- **Result**: identical behavior, no redirects needed for trailing slash variants

## Pages NOT in the sitemap but may need preserving

Check Google Search Console for any ranking URLs NOT in the sitemap before cutover. Common suspects:
- `/404` (we'll have our own custom 404)
- `/sitemap.xml` (rebuild)
- `/robots.txt` (rebuild)
- Any image direct-link URLs (likely Webflow CDN — not migratable; resolve via new `/images/...` paths and rely on Google re-crawl)

## Action Items Before Cutover

- [ ] Export Google Search Console "Pages" report for studioonefresno.com
- [ ] Cross-reference top-100 landing URLs against this map to catch any missing paths
- [ ] Add all missing paths (if any) to this file + vercel.json
- [ ] Test redirects on staging before DNS cutover
- [ ] Submit new sitemap to Google Search Console within 24h of cutover
