// /api/booking-intent
//
// A visitor clicked a Vagaro "Book" button, said they are a NEW guest, and gave
// a first name and phone number before going on to Vagaro. This records them as
// a lead (form_type 'vagaro-new-guest') so the later Vagaro booking can be
// matched back to the visit by phone, and so anyone who never finishes booking
// can be followed up.
//
// The browser never waits on this call: Vagaro has already opened in a new tab.
// So it never needs a reCAPTCHA token (which is what refuses real people on the
// other forms). It posts to form-notify on the trusted path WITH the content
// check still on, and asks form-notify not to email Cat for every one of these.

const FORM_NOTIFY_URL = 'https://myaieditor.com/api/form-notify';

const ATTR_KEYS = [
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
  'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid',
  'analytics_source', 'analytics_source_data_1', 'analytics_source_data_2',
  'first_referrer', 'first_url',
];

function clean(v, max) {
  return String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, max);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false });

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }
  body = body || {};

  // Honeypot: a hidden field no person fills in.
  if (clean(body.company, 200)) return res.status(200).json({ ok: true });

  const firstName = clean(body.first_name, 60);
  let digits = String(body.phone || '').replace(/\D/g, '');
  if (digits.length === 11 && digits[0] === '1') digits = digits.slice(1);
  if (!firstName || digits.length !== 10) {
    return res.status(400).json({ ok: false, error: 'name and a 10-digit phone are required' });
  }
  const phonePretty = `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;

  const secret = process.env.INTERNAL_FORM_SECRET || '';
  if (!secret) {
    console.error('booking-intent: INTERNAL_FORM_SECRET missing');
    return res.status(200).json({ ok: false });
  }

  const attribution = {};
  const a = body.attribution && typeof body.attribution === 'object' ? body.attribution : {};
  for (const k of ATTR_KEYS) { const v = clean(a[k], 500); if (v) attribution[k] = v; }

  const page = clean(body.page, 300);
  const vagaroUrl = clean(body.vagaro_url, 600);

  try {
    const r = await fetch(FORM_NOTIFY_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-internal-secret': secret,
        'x-internal-content-check': '1',
      },
      body: JSON.stringify({
        site_slug: 'studio-one',
        form_type: 'vagaro-new-guest',
        first_name: firstName,
        phone: phonePretty,
        phone_digits: digits,
        guest_type: 'new',
        booking_page: page,
        vagaro_url: vagaroUrl,
        sms_consent_text: "We'll only text you about your booking.",
        skip_notification: 'true',
        summary: `New guest ${firstName} (${phonePretty}) clicked Book on ${page || 'the website'} and went on to Vagaro.`,
        ...attribution,
      }),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || j.accepted === false) {
      console.error('booking-intent: form-notify did not accept', r.status, JSON.stringify(j).slice(0, 300));
      return res.status(200).json({ ok: false });
    }
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error('booking-intent: dispatch failed', e?.message || e);
    return res.status(200).json({ ok: false });
  }
}
