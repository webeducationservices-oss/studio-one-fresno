# Studio One Fresno — Cutover Playbook
**Target cutover: April 30, 2026** · 8 days from 2026-04-22

This document covers every step to take the site live on `studioonefresno.com`. Steps are ordered by timing: work-in-advance, launch-day sequence, and post-launch.

---

## Summary of Current State

- **Staging site**: https://studio-one-fresno.vercel.app (live, all pages working)
- **Repo**: https://github.com/webeducationservices-oss/studio-one-fresno (`main` auto-deploys)
- **Vercel project**: `studio-one-fresno` (`prj_hVkgtPHelayJ5ANZWhKkdniXtAhn`)
- **Supabase site row**: `studio-one` slug (`9194f2b7-1c4e-41f4-a389-f60f8697447e`)
- **Production domains**: `studioonefresno.com` + `www.studioonefresno.com` added & verified in Vercel (DNS still points at Webflow)
- **Current DNS**: `studioonefresno.com` → `198.202.211.1` (Webflow)
- **After cutover**: `studioonefresno.com` → Cloudflare → Vercel (`76.76.21.21`)

---

## Phase A — Pre-Launch (Now through April 29)

Everything that can happen without touching DNS.

### 1. Client review window (~5 days)
- [ ] Send client staging URL: **https://studio-one-fresno.vercel.app**
- [ ] Collect revision list
- [ ] Address feedback

### 2. Phase 4 (PayPal) — when credentials arrive
When client provides:
```
PAYPAL_LIVE_CLIENT_ID=...
PAYPAL_LIVE_SECRET=...
PAYPAL_SANDBOX_CLIENT_ID=...
PAYPAL_SANDBOX_SECRET=...
```
1. Add to `/Users/justinbabcock/Desktop/Websites/.env.keys`
2. Run `node scripts/paypal-bootstrap.js` (creates 107-product catalog + webhook subscription)
3. Uncomment the PayPal Buttons mount in `cart.html`
4. Render `paypal.Buttons({...}).render('#paypal-button-container')` with Orders API v2 payload including `item_total`, `tax_total`, `shipping`
5. Create `/api/paypal-webhook.js` serverless function (verify signature → append to Google Sheet → email via `form-notify`)
6. QA end-to-end in sandbox; flip to live creds; run $0.01 real test order
7. Confirm receipt email + Google Sheet row + webhook fire

### 3. reCAPTCHA Domain Whitelist ⚠️ MANUAL STEP
**Cannot be automated** — requires a browser login.
1. Sign in to https://www.google.com/recaptcha/admin
2. Open the **Web Education Services** site settings (gear icon)
3. Under **Domains**, add:
   - `studioonefresno.com`
   - `studio-one-fresno.vercel.app` (for staging tests)
4. Save
5. Without this, the contact form silently drops ALL submissions (form-notify returns `{success:true}` but does nothing — this is the #1 cause of "forms aren't working" on a new site)

### 4. Client myaieditor Invite (do after content is locked)
Once the client has finished reviewing and wants edit access:
```bash
curl -s -X POST "https://myaieditor.com/api/invite-user" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "CLIENT_EMAIL_HERE",
    "name": "CLIENT_NAME_HERE",
    "site_slug": "studio-one"
  }'
```
Client receives branded welcome email from `login@myaieditor.com` → creates password → can chat-edit the site via https://myaieditor.com/chat/studio-one.

### 5. Cloudflare Account Setup (can do anytime before launch)
1. At https://dash.cloudflare.com, click **Add a site** → `studioonefresno.com` → Free plan
2. Cloudflare scans existing DNS; review. (There may be MX/SPF for email we need to preserve.)
3. Cloudflare provides nameservers like `ada.ns.cloudflare.com`, `bob.ns.cloudflare.com` — note these for Launch Day

---

## Phase B — Launch Day Sequence (April 30)

Plan for a **1-hour window** with monitoring afterward. Best time: weekday morning (clients aren't booking yet, Search Console indexing has the full business day to settle).

### Step 1 — DNS Cutover (the actual flip)

Two paths. **Path A is strongly recommended** (adds Cloudflare DDoS + caching layer per CLAUDE.md Phase 8).

#### Path A — Cloudflare in front of Vercel (recommended)
1. **At the registrar** (wherever studioonefresno.com is registered today):
   - Change nameservers to Cloudflare's (from Phase A step 5)
2. **In Cloudflare DNS**:
   | Type | Name | Value | Proxy |
   |---|---|---|---|
   | A | `@` | `76.76.21.21` | **Proxied** (orange cloud) |
   | CNAME | `www` | `cname.vercel-dns.com` | **Proxied** (orange cloud) |
   | MX/SPF/DKIM/DMARC | *(keep existing for email)* | *(preserve)* | **DNS only** (grey cloud) |
3. **Cloudflare SSL/TLS**:
   - Encryption mode: **Full (strict)**
   - Edge Certificates: enable **Always Use HTTPS** + **Automatic HTTPS Rewrites**
4. **Cloudflare Security**: enable **Bot Fight Mode**
5. Propagation usually takes 5–30 minutes

#### Path B — Direct to Vercel (skip Cloudflare)
At the registrar:
- A `@` → `76.76.21.21`
- CNAME `www` → `cname.vercel-dns.com`
- Delete any existing parking/Webflow A records

### Step 2 — Verify Site Serves Correctly

From a clean browser:
- [ ] https://studioonefresno.com — home page loads
- [ ] https://www.studioonefresno.com — redirects to apex
- [ ] Green padlock / valid SSL
- [ ] `curl -I https://studioonefresno.com` shows `cf-ray` header (confirms Cloudflare proxy, if Path A)
- [ ] Sample 5 URLs across buckets:
  - `/meet-the-team`
  - `/blog/the-truth-about-nbr-extensions-at-studio-one`
  - `/product/gold-lust-repair-restore-shampoo`
  - `/contact`
  - `/checkout` (should 308 → `/cart`)

### Step 3 — Update Supabase production_url
```bash
curl -s -X PATCH "https://sqeegvibwqkiugiwomqd.supabase.co/rest/v1/sites?slug=eq.studio-one" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"production_url": "studioonefresno.com"}'
```
This is what myaieditor uses for the client's preview iframe.

### Step 4 — Submit New Sitemap to Google Search Console
1. https://search.google.com/search-console
2. Verify property ownership for `studioonefresno.com` (DNS TXT or HTML meta — already set from Webflow days; should carry over)
3. **Sitemaps** → Add new sitemap → `https://studioonefresno.com/sitemap.xml`
4. Expected: 180 URLs submitted

### Step 5 — Test Contact Form End-to-End
- [ ] Submit test message from https://studioonefresno.com/contact
- [ ] Confirm email arrives (to users with `site_access` to `studio-one`, falling back to Justin + webeducationservices@gmail.com)
- [ ] Confirm row appears in Google Sheet in "Forms Log" folder (auto-created on first submission)
- [ ] If nothing happens → check reCAPTCHA domain whitelist (Phase A step 3)

### Step 6 — Update CLAUDE.md Status
Change the Studio One row from "Active - staging" to "Active - launched 2026-04-30".

### Step 7 — Cancel Old Webflow Subscription
**Wait 7 days** post-cutover before cancelling, so Webflow stays as a fallback if we discover any issues. Put a calendar reminder for **May 7**.

---

## Phase C — Same-Day & Next-Day (April 30 – May 1)

### Domain Categorization (corporate firewall compatibility)
Corporate/medical-office firewalls block "uncategorized" domains. Submit `studioonefresno.com` to each of these (5 min total, browser required):

| Service | URL | Request Category |
|---|---|---|
| Cisco/OpenDNS | https://community.opendns.com/domaintagging/ | "Health and Wellness" (salon = health/beauty) |
| Fortinet | https://www.fortiguard.com/webfilter | "Health and Wellness" |
| Palo Alto | https://urlfiltering.paloaltonetworks.com/ | "Business and Economy" |
| BrightCloud | https://www.brightcloud.com/tools/url-ip-lookup.php | "Business" |
| McAfee | https://trustedsource.org/sources/index.pl | "Business" |
| Symantec/BlueCoat | https://sitereview.bluecoat.com/ | "Business" |
| Google Safe Browsing | https://transparencyreport.google.com/safe-browsing/search | verify clean (no submission needed) |

These take 24 hours to a week to propagate. Most important: **Fortinet** and **Cisco** (highest corporate coverage).

### GTM Continuity Check
- [ ] Open GTM dashboard (tagmanager.google.com) → `GTM-WQGCMZ9Q`
- [ ] Verify existing triggers/tags still fire correctly on new URLs
- [ ] Check GA4 Real-Time report is registering hits from studioonefresno.com
- [ ] If conversions tracked: re-verify each conversion tag's page path pattern still matches

### Facebook Pixel Continuity
- [ ] Open Meta Business Suite → Events Manager → Pixel `24036206522645936`
- [ ] Confirm "PageView" events firing from studioonefresno.com

---

## Phase D — Week 1 Post-Launch Monitoring

### Day 1
- [ ] Google Search Console — check Coverage report 24h after submission
- [ ] Monitor 404 errors in Search Console (ensure no expected URLs are missing)
- [ ] Verify blog posts still rank on key queries (spot-check 5 posts)

### Day 3
- [ ] Check Google Analytics 4 is recording organic sessions
- [ ] Confirm a real form submission reached email + Google Sheet
- [ ] If PayPal live: confirm at least one sandbox-or-live order completed end-to-end

### Day 7
- [ ] **Cancel Webflow subscription**
- [ ] Run full SEO audit per SEO-REVIEW.md; target score 85+
- [ ] Verify all redirects still work: `/checkout` and `/paypal-checkout` → `/cart`

### Day 30
- [ ] Re-audit SEO score
- [ ] Review Search Console Performance → top queries and landing pages
- [ ] Review Google Sheet "Studio One Orders" (if PayPal live) for patterns
- [ ] Schedule next 30-day audit

---

## Known Manual Steps Requiring Human Action

These cannot be automated and will need Justin (or the client) to do them in a browser:

1. **reCAPTCHA domain whitelist** (Phase A step 3) — must be done BEFORE launch or contact form silently drops submissions
2. **Cloudflare nameserver change at registrar** (Launch Step 1) — must be done by whoever controls the domain registrar
3. **Cloudflare site setup** (Phase A step 5) — one-time account/site setup
4. **Google Search Console sitemap submission** (Launch Step 4) — requires GSC login
5. **Domain categorization submissions** (Phase C) — 7 websites, CAPTCHAs on most
6. **PayPal app creation** (when creds arrive) — client must log into their PayPal Business account to create the REST app

An automated email listing these can be sent to `support@webeducationservices.com` on launch day per FIRST-TIME-DEPLOYMENT.md Phase 10.

---

## Rollback Plan

If something goes catastrophically wrong post-cutover:
1. At the registrar, change DNS A record back to `198.202.211.1` (Webflow)
2. Propagation in 5–30 minutes
3. Site returns to the old Webflow version while we diagnose
4. No data is lost — both Webflow and Vercel sites are separately deployed

The repo, Vercel project, and all content stay intact during rollback. We can re-attempt cutover after fixing the issue.

---

## Open Questions for Client (answers improve launch)

1. PayPal: Business account exists? Who has login? When credentials available?
2. Tax rule: CA 7.975% on CA shipments only, flat rate everywhere, or no sales tax?
3. Shipping: Flat $X, free-over-$Y, or weight-based? In-store pickup option?
4. PayPal funding sources: PayPal-only, or allow credit card via PayPal guest checkout?
5. Stock tracking: Should PayPal track inventory, or handle manually?
6. Amber's headshot: Can we get a higher-quality replacement matching other stylists?
7. Where does the domain registrar live (GoDaddy, Namecheap, etc.)? Who has access?
8. Preferred cutover time of day on April 30?
