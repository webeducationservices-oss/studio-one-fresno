# Phase 0 — Discovery & Prep Report

**Site**: studioonefresno.com → Vercel migration
**Date**: 2026-04-21
**Local path**: `/Users/justinbabcock/Desktop/Websites/studio-one-fresno/`
**Vercel project** (current): `studio-one-staging` (`prj_hVkgtPHelayJ5ANZWhKkdniXtAhn`) — will rename to `studio-one-fresno` in Phase A
**Staging URL**: https://studio-one-staging.vercel.app

---

## 1. Content Inventory

### Blog (42 posts)
- Saved: `content-export/blog/<slug>.json` × 42
- Schema: `slug, url_original, title, meta_title, meta_description, hero_image_url, author, published_date, category, body_text, inline_image_urls`
- **Completeness**:
  - ✅ Title, body text, published date — all 42
  - ⚠️ Hero image — missing on ~13 posts (Webflow uses varied hero embed patterns; will fall back to first inline image, or assign a category-default hero)
  - ⚠️ Meta title/description — missing on ~15 posts (Webflow may fall back to H1 — we'll generate clean meta tags from title + excerpt during the build)
  - ⚠️ Author byline — missing on ~22 posts (current site doesn't consistently show authors; we'll default to "Studio One Team" where unknown)
  - ⚠️ Category inconsistency — the sitemap lists 8 clean category slugs, but individual post pages use 20+ free-form names ("Hair Care & Styling", "Local Spotlight", "Success Stories") that don't match
- **Date range**: July 2023 → February 2026 (active blog)
- **Recommended fix for categories during build**: Map each post to exactly one of the 8 canonical category slugs from the sitemap:
  - `behind-the-scenes`, `client-spotlights`, `color`, `extensions`, `hair-care`, `hair-products`, `salon-team`, `styling`

### Team (5 stylists)
- Saved: `content-export/team/<slug>.json` × 5 + `meet-the-team-index.json`
- **Display order on /meet-the-team**: Carina, Makayla, Hope, Amber, Cat
- **Notable**:
  - Cat Barco is Owner
  - Carina Lopez is currently on maternity leave (per site note)
  - Amber has a unique Vagaro BusinessWidget booking URL; others share `vagaro.com/studioone4/staff`
  - Amber's headshot is a low-quality PNG vs. the other stylists' branded AVIF → **flag client for replacement**
  - Only Cat and Hope have individual contact emails
  - No per-stylist Facebook links

### Forms (1 on-page + 9 third-party integrations)
- Saved: `content-export/forms/form-audit.md`
- **On-page forms to rebuild with `myaieditor.com/api/form-notify`**:
  - Footer newsletter signup (single email field) — all pages
- **Third-party to preserve as-is** (URLs will be preserved 1:1 — just link-outs or iframe embeds):
  - **Vagaro** × 3 URLs (booking calendar)
  - **JotForm** × 4 (NBR extensions form `83406488092160`, booth rent `catbarco/application-for-booth-rent-commissi`, Nically Hair stylist `243497737778075`, wig consult `253186527338161` — iframe-embedded on /wigs)
  - **Cherry** × 1 (payment plan link `pay.withcherry.com/catbarcohair`)
- **No contact form currently exists** — the salon uses `tel:559-795-9724` and `sms:559-795-9724` instead. *Question for client: do you want a proper Contact Us form on the new site?*

### Products (105 — awaiting client export)
- Folder `content-export/products/` exists but is empty
- **Blocked on client action**: export CMS from Webflow admin (Settings → Ecommerce → Export products CSV)
- **Fallback**: I can scrape all 105 product pages (~15 min of agent time) if the client can't access Webflow admin. The scrape won't have SKUs or inventory counts though — so the CMS export is strongly preferred.

### Tracking to port forward (from the live site)
- **GA4**: `G-P0H19W2KWM`
- **GTM**: `GTM-WQGCMZ9Q`
- **Facebook Pixel**: `24036206522645936`

---

## 2. URL Redirect Map

Full map at `content-export/url-redirect-map.md`. TL;DR:

- **170 of 173 URLs preserved identically** (all blog posts, all team pages, all products, all core pages)
- **Only 3 redirects needed** (all in `vercel.json`):
  - `/checkout` → `/cart` (301)
  - `/paypal-checkout` → `/cart` (301)
  - `/order-confirmation` kept, re-implemented to read `?oid=` from PayPal

SEO impact: minimal. We're protecting essentially all ranking URLs.

---

## 3. Architecture Decision (reconfirmed)

- **Static HTML** (typical build pattern from CLAUDE.md) — NOT Next.js
- **Ecommerce**: PayPal Smart Payment Buttons + REST API automation (no Shopify, no Stripe)
- **Forms**: `myaieditor.com/api/form-notify` for newsletter; keep all existing third-party booking/application embeds
- **`vercel.json`**: iframe-friendly per FIRST-TIME-DEPLOYMENT.md (`X-Frame-Options: ALLOWALL`, `CSP frame-ancestors *`)

---

## 4. Open Questions for the Client

These block Phases 4 (PayPal) and H (launch). Everything else we can build in the meantime.

### PayPal (Phase 4 blockers)

1. **PayPal Business account**: does Studio One have one? If so, who has admin access to create a REST app at developer.paypal.com?
2. **API credentials**: when ready, paste `PAYPAL_LIVE_CLIENT_ID`, `PAYPAL_LIVE_SECRET`, `PAYPAL_SANDBOX_CLIENT_ID`, `PAYPAL_SANDBOX_SECRET` into `.env.keys`
3. **Tax**: charge CA sales tax only (7.975% or other rate?) or flat rate regardless of ship-to state?
4. **Shipping**: flat fee ($X), free over $Y, weight-based, or in-store pickup only? (current Webflow config unknown)
5. **Funding sources**: PayPal-only, OR allow guest checkout with credit card through PayPal (same processor, no extra vendor, much higher conversion)?
6. **Stock tracking**: should PayPal track inventory per product, or is stock a non-issue?
7. **Order notifications**: which salon email receives new-order emails? Justin cc'd on disputes only, or every order?

### Content

8. **Product export**: can someone export the products CSV from Webflow admin? (Settings → Ecommerce → Export) If not, I'll scrape.
9. **Amber's headshot**: need a high-quality photo matching the other stylists' branded AVIF format
10. **Contact form**: add a Contact Us form, or keep the phone/text-only CTA pattern?
11. **Blog authors**: default to "Studio One Team" where unknown, or assign all to Cat Barco?

### Logistics

12. **Cutover window**: when do you want to aim for DNS cutover? (~3–4 weeks from now seems realistic)
13. **Soft launch vs. big bang**: launch core pages to staging subdomain first and migrate piecewise, or hold everything for one cutover?
14. **Webflow subscription**: who manages billing and when should we cancel? (Recommend waiting 7 days post-cutover before cancel.)

---

## 5. What's Next (Phase A — Infrastructure Setup)

Once I have answers to the content-related questions (4, 5, 6, 7, 8, 10, 11), I'll kick off Phase A:

1. Rewrite `vercel.json` with iframe headers + asset caching
2. `git init` the project
3. Create GitHub repo `studio-one-fresno` under `webeducationservices-oss`
4. Rename Vercel project `studio-one-staging` → `studio-one-fresno`
5. Link GitHub ↔ Vercel for auto-deploy
6. Disable SSO Deployment Protection
7. Insert `studio-one` slug in Supabase `sites` table
8. Update CLAUDE.md Sites + Form slug tables
9. Verify myaieditor preview iframe loads the staging URL

Phase A takes ~0.5 day. It can run in parallel with Phases C/D/E (content pages + team + blog builds).

Phase 4 (PayPal/shop) is the only phase strictly blocked on client action — everything else moves.

---

## Files Produced in Phase 0

```
studio-one-fresno/
└── content-export/
    ├── PHASE-0-REPORT.md              ← this file
    ├── url-redirect-map.md
    ├── blog/
    │   └── <slug>.json × 42
    ├── team/
    │   ├── <slug>.json × 5
    │   └── meet-the-team-index.json
    ├── forms/
    │   └── form-audit.md
    └── products/                      ← empty, awaiting client export or scrape
```
