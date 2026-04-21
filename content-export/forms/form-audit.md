# Studio One Fresno — Form Audit

Audit date: 2026-04-21
Source site: https://www.studioonefresno.com (Webflow)
Target platform: Vercel rebuild

---

## Summary

Studio One Fresno does not use Webflow's native form builder for its primary conversion flows. Instead, it relies on a small set of third-party embeds and link-outs:

- **Vagaro** for general salon service booking (link-out)
- **JotForm** for NBR extension consultation, stylist career/booth-rent applications, Nically Hair stylist applications, and wig consultations
- **Cherry** for payment-plan financing (link-out)
- A **Webflow/Mailchimp-style newsletter signup** in the global footer (email field only)
- **Direct tel:/sms:** links for basic contact (no HTML contact form exists)

The only true HTML form that lives on-page and submits to the site itself is the footer newsletter form. Everything else is either an external iframe embed (JotForm) or an outbound link to a hosted booking/application page (Vagaro, Cherry).

---

## Forms by Page

### 1. Home — https://www.studioonefresno.com/

| Item | Detail |
|------|--------|
| HTML `<form>` on page | None on-page except footer newsletter |
| Booking entry point | "BOOK NOW" buttons link to `/booking` |
| Contact | `tel:5597959724` and `sms:5597959724` only — no contact form |
| Newsletter | Footer: "GET STUDIO UPDATES STRAIGHT TO YOUR INBOX" (email field) |
| Embedded scripts | Google Analytics (G-P0H19W2KWM), GTM (GTM-WQGCMZ9Q), Facebook Pixel (24036206522645936), Webflow Commerce |

---

### 2. Booking — https://www.studioonefresno.com/booking

This page is a router, not a form. It offers two outbound choices:

| Purpose | Destination | Method |
|---------|-------------|--------|
| Book extension services | `https://form.jotform.com/83406488092160` | Link out to JotForm |
| Book other salon services | `https://www.vagaro.com/studioone4/services` | Link out to Vagaro |

Contact fallbacks: `tel:` and `sms:` to 559-795-9724.
Success message note on page: "please check your email to see if a consultation form has been requested."
No on-page `<form>` element.

---

### 3. Careers — https://www.studioonefresno.com/careers

| Item | Detail |
|------|--------|
| Form purpose | Booth rent / commission stylist application |
| Form platform | JotForm (link-out, not iframe) |
| Action URL | `https://form.jotform.com/catbarco/application-for-booth-rent-commissi` |
| Submit button (on-page CTA) | "APPLY NOW" |
| On-page fields | None — page is CTA-only; fields live in JotForm |
| Newsletter | Same footer email signup |

---

### 4. Shadowing Program — https://www.studioonefresno.com/shadowing-program

| Item | Detail |
|------|--------|
| Form purpose | Stylist shadowing program application |
| Form platform | JotForm (link-out) |
| Action URL | `https://form.jotform.com/catbarco/application-for-booth-rent-commissi` (same form as Careers) |
| Submit button (on-page CTA) | "apply now" / "i'm ready" |
| On-page fields | None |
| Newsletter | Footer |

Note: Shadowing and Careers share the same JotForm endpoint.

---

### 5. NBR Extensions — https://www.studioonefresno.com/nbr-extensions

| Item | Detail |
|------|--------|
| Primary form purpose | NBR extension consultation questionnaire + booking |
| Form platform | JotForm |
| Action URL | `https://form.jotform.com/83406488092160` |
| Submit button (on-page CTA) | "start your nbr application" / "apply now" |
| Fields | Hosted in JotForm — includes hair history, current hair photo upload, inspiration photo upload, contact info |
| Secondary form purpose | Payment plan / financing application |
| Secondary platform | Cherry |
| Secondary action URL | `https://pay.withcherry.com/catbarcohair` |
| Secondary CTA | "apply for a payment plan" |
| Newsletter | Footer |

---

### 6. Menu — https://www.studioonefresno.com/menu

No forms on page. Navigation link to `/booking` only. Footer newsletter present.

---

### 7. Nically Hair — https://www.studioonefresno.com/nically-hair

| Item | Detail |
|------|--------|
| Form purpose | Stylist application to work with Nically Hair |
| Form platform | JotForm |
| Action URL | `https://form.jotform.com/243497737778075` |
| Submit button (on-page CTA) | "APPLY NOW" |
| On-page fields | None (external form) |
| Also present | Webflow Commerce cart (quantity input, "CHECKOUT" button) for Nically Hair product sales |
| Newsletter | Footer |

---

### 8. Wigs — https://www.studioonefresno.com/wigs

| Item | Detail |
|------|--------|
| Form purpose | Private wig consultation booking |
| Form platform | JotForm (embedded iframe via `window.jotformEmbedHandler`) |
| Form ID | 253186527338161 |
| Action URL | `https://form.jotform.com/253186527338161` |
| Submit button | JotForm default submission |
| On-page fields | Rendered dynamically inside iframe — not enumerable from parent page |
| Success handling | JotForm default confirmation flow |
| Newsletter | Footer |

This is the only page with a truly embedded (iframe) form rather than a link-out.

---

### 9. Services — https://www.studioonefresno.com/services

| Item | Detail |
|------|--------|
| Booking links | Multiple "book online" CTAs linking to `https://www.vagaro.com/us02/studioone4/services` and `https://www.vagaro.com/studioone4/book-now` |
| NBR questionnaire link | `https://form.jotform.com/83406488092160` |
| On-page form | None on page body — footer newsletter only |
| Newsletter | Footer (email field, required, Mailchimp-style integration) |

---

## Global Footer Newsletter (all pages)

| Item | Detail |
|------|--------|
| Label | "GET STUDIO UPDATES STRAIGHT TO YOUR INBOX:" |
| Field | Email input (required) |
| Submit | Standard (text not definitively exposed — likely "Subscribe" or arrow icon) |
| Action URL | Not exposed in Webflow rendered source — appears to be Mailchimp or Webflow Forms native handler |
| Success | Webflow-style inline success/error state (standard `.w-form-done` / `.w-form-fail` pattern) |
| Data attrs | Webflow-typical `data-name`, `data-wf-page`, `data-wf-element-id` (not fully inspectable via rendered HTML alone) |

---

## Third-Party Integrations to Preserve

| Service | Use | Embed method | URL / ID |
|---------|-----|--------------|----------|
| Vagaro | General salon booking | Outbound link (new tab) | `vagaro.com/studioone4/services`, `vagaro.com/us02/studioone4/services`, `vagaro.com/studioone4/book-now` |
| JotForm — NBR extensions | Extension consultation | Link-out + referenced on Services page | Form ID `83406488092160` |
| JotForm — Booth rent/commission | Careers + Shadowing | Link-out | `form.jotform.com/catbarco/application-for-booth-rent-commissi` |
| JotForm — Nically Hair stylist | Stylist application | Link-out | Form ID `243497737778075` |
| JotForm — Wig consultation | Wig booking | Embedded iframe (`jotformEmbedHandler`) | Form ID `253186527338161` |
| Cherry | Payment plan financing | Link-out | `pay.withcherry.com/catbarcohair` |
| Google Analytics | Tracking | Script tag | `G-P0H19W2KWM` |
| Google Tag Manager | Tracking | Script tag | `GTM-WQGCMZ9Q` |
| Facebook Pixel | Tracking | Script tag | `24036206522645936` |

---

## Rebuild Plan (Vercel)

### Keep as third-party embed / link-out

1. **Vagaro booking** — Keep all outbound links as-is. Vagaro is the salon's operational booking system; do not attempt to replicate. Reuse the same URLs on `/booking`, `/services`, and any "Book Now" CTAs.
2. **JotForm — NBR consultation (83406488092160)** — Keep as link-out from `/nbr-extensions`, `/booking`, and `/services`. Optional: embed inline via `<iframe>` using JotForm's embed snippet if the team wants the flow on-page.
3. **JotForm — Wig consultation (253186527338161)** — Keep as inline iframe on `/wigs`. Port the `jotformEmbedHandler` script or use a React wrapper that calls it on mount.
4. **JotForm — Booth rent/commission (`catbarco/application-for-booth-rent-commissi`)** — Keep as link-out from `/careers` and `/shadowing-program`.
5. **JotForm — Nically Hair stylist (243497737778075)** — Keep as link-out from `/nically-hair`.
6. **Cherry payment plan** — Keep as outbound link.
7. **GA4, GTM, Facebook Pixel** — Port IDs verbatim into Vercel layout / `<Script>` components.

### Rebuild with `myaieditor.com/api/form-notify`

1. **Footer newsletter signup** — Replace the Webflow/Mailchimp email capture with a simple form posting to `myaieditor.com/api/form-notify`. Single email field, required, with inline success and error states. This is the only form currently attached to Webflow's own submission pipeline and is the clearest candidate to move to the `form-notify` endpoint.
2. **(Optional new) Contact form** — The current site has no HTML contact form (only `tel:` and `sms:`). If the rebuild wants a "Contact Us" form (name, email, phone, message), add it and route it through `myaieditor.com/api/form-notify`.

### Do not rebuild

- No on-site booking form, no on-site career/shadowing form, no on-site consultation form exists today. Do not build custom replacements for these — the salon's workflows (intake attachments, photo uploads, applicant tracking, Vagaro calendar) live in JotForm and Vagaro. Replacing them adds ops burden with no upside.

---

## Open questions / verification needed

1. Confirm the footer newsletter's actual submission endpoint (Webflow native vs Mailchimp) by inspecting the live form's `action` and any `data-` attrs directly in DOM. WebFetch output did not expose the exact endpoint.
2. Confirm whether the salon wants the NBR and wig JotForms embedded inline (iframe) vs. link-out in the new build.
3. Confirm Vagaro account slug `studioone4` is current and that both `vagaro.com/studioone4/services` and `vagaro.com/us02/studioone4/services` should remain as separate CTAs or be consolidated.
