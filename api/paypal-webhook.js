// /api/paypal-webhook  —  Vercel serverless function (Node.js runtime)
//
// Receives PayPal webhook notifications, verifies the signature, then
// hands off to the existing myaieditor.com/api/form-notify endpoint
// which handles email notifications + Google Sheet logging for free.
//
// Events subscribed (registered in scripts/paypal-bootstrap.py):
//   CHECKOUT.ORDER.APPROVED       (buyer approved order)
//   PAYMENT.CAPTURE.COMPLETED     (successful payment — primary signal)
//   PAYMENT.CAPTURE.REFUNDED      (refund issued)
//   PAYMENT.CAPTURE.REVERSED      (chargeback / dispute reversal)
//   PAYMENT.CAPTURE.DENIED        (capture denied)
//   CUSTOMER.DISPUTE.CREATED      (buyer opened a dispute)
//   CUSTOMER.DISPUTE.RESOLVED     (dispute resolved)
//   CUSTOMER.DISPUTE.UPDATED      (dispute updated)
//
// Required Vercel env vars (set in dashboard or via API):
//   PAYPAL_ENV            'live' or 'sandbox'  (default: live)
//   PAYPAL_LIVE_CLIENT_ID
//   PAYPAL_LIVE_SECRET
//   PAYPAL_LIVE_WEBHOOK_ID
//   PAYPAL_SANDBOX_CLIENT_ID  (only if PAYPAL_ENV=sandbox)
//   PAYPAL_SANDBOX_SECRET
//   PAYPAL_SANDBOX_WEBHOOK_ID
//
// Notification routing:
//   - All events POST to myaieditor.com/api/form-notify with site_slug=studio-one
//     and form_type=paypal_<event_short>, which fans out to:
//       hairbycatb@gmail.com (primary, from .env.keys.cat ORDER_NOTIFY_PRIMARY)
//       justin@webeducationservices.com (CC)
//     and appends a row to the Studio One Google Sheet "Forms Log" folder.

export const config = { api: { bodyParser: false } };  // need raw body for signature verify

const FORM_NOTIFY_URL = 'https://myaieditor.com/api/form-notify';

// Read raw body without bodyParser (so signature verifies against bytes PayPal sent)
async function readRawBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return Buffer.concat(chunks).toString('utf-8');
}

function paypalEnv() {
  const env = (process.env.PAYPAL_ENV || 'live').toLowerCase();
  if (env === 'sandbox') {
    return {
      base: 'https://api-m.sandbox.paypal.com',
      clientId: process.env.PAYPAL_SANDBOX_CLIENT_ID || '',
      secret: process.env.PAYPAL_SANDBOX_SECRET || '',
      webhookId: process.env.PAYPAL_SANDBOX_WEBHOOK_ID || '',
    };
  }
  return {
    base: 'https://api-m.paypal.com',
    clientId: process.env.PAYPAL_LIVE_CLIENT_ID || '',
    secret: process.env.PAYPAL_LIVE_SECRET || '',
    webhookId: process.env.PAYPAL_LIVE_WEBHOOK_ID || '',
  };
}

async function getAccessToken({ base, clientId, secret }) {
  const auth = Buffer.from(`${clientId}:${secret}`).toString('base64');
  const r = await fetch(`${base}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${auth}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
  });
  if (!r.ok) throw new Error(`PayPal token request failed: ${r.status}`);
  const j = await r.json();
  return j.access_token;
}

async function verifySignature(req, rawBody, ppEnv) {
  const token = await getAccessToken(ppEnv);
  const verifyBody = {
    auth_algo: req.headers['paypal-auth-algo'] || '',
    cert_url: req.headers['paypal-cert-url'] || '',
    transmission_id: req.headers['paypal-transmission-id'] || '',
    transmission_sig: req.headers['paypal-transmission-sig'] || '',
    transmission_time: req.headers['paypal-transmission-time'] || '',
    webhook_id: ppEnv.webhookId,
    webhook_event: JSON.parse(rawBody),
  };
  const r = await fetch(`${ppEnv.base}/v1/notifications/verify-webhook-signature`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(verifyBody),
  });
  if (!r.ok) return false;
  const result = await r.json();
  return result.verification_status === 'SUCCESS';
}

function summarize(event) {
  const t = event.event_type || '';
  const r = event.resource || {};
  const out = {
    event_id: event.id || '',
    event_type: t,
    create_time: event.create_time || '',
    resource_id: r.id || '',
  };
  // Surface the most useful fields per event type
  if (t.startsWith('PAYMENT.CAPTURE')) {
    out.amount = r.amount?.value || '';
    out.currency = r.amount?.currency_code || '';
    out.status = r.status || '';
    out.payer_email = r.payer?.email_address || '';
    out.invoice_id = r.invoice_id || '';
    out.custom_id = r.custom_id || '';
    out.note_to_payer = r.note_to_payer || '';
    if (r.supplementary_data?.related_ids?.order_id) {
      out.order_id = r.supplementary_data.related_ids.order_id;
    }
  } else if (t === 'CHECKOUT.ORDER.APPROVED') {
    out.order_id = r.id || '';
    out.payer_email = r.payer?.email_address || '';
    out.amount = r.purchase_units?.[0]?.amount?.value || '';
    out.currency = r.purchase_units?.[0]?.amount?.currency_code || '';
    const items = (r.purchase_units?.[0]?.items || []).map(i => `${i.quantity}× ${i.name}`).join(' | ');
    if (items) out.items = items;
    const ship = r.purchase_units?.[0]?.shipping?.address;
    if (ship) {
      out.ship_to = `${ship.address_line_1 || ''}, ${ship.admin_area_2 || ''}, ${ship.admin_area_1 || ''} ${ship.postal_code || ''}`;
    }
  } else if (t.startsWith('CUSTOMER.DISPUTE')) {
    out.dispute_id = r.dispute_id || r.id || '';
    out.dispute_status = r.status || '';
    out.dispute_reason = r.reason || '';
    out.amount = r.disputed_transactions?.[0]?.gross_amount?.value || '';
    out.currency = r.disputed_transactions?.[0]?.gross_amount?.currency_code || '';
  }
  return out;
}

function shortFormType(eventType) {
  const t = (eventType || 'unknown').toLowerCase();
  if (t.includes('capture.completed')) return 'paypal_order';
  if (t.includes('capture.refunded')) return 'paypal_refund';
  if (t.includes('capture.reversed')) return 'paypal_reversal';
  if (t.includes('capture.denied')) return 'paypal_denied';
  if (t.includes('order.approved')) return 'paypal_order_approved';
  if (t.includes('dispute.created')) return 'paypal_dispute_new';
  if (t.includes('dispute.resolved')) return 'paypal_dispute_resolved';
  if (t.includes('dispute.updated')) return 'paypal_dispute_updated';
  return 'paypal_other';
}

export default async function handler(req, res) {
  if (req.method === 'GET') {
    // Health check
    return res.status(200).json({
      ok: true,
      service: 'paypal-webhook',
      env: process.env.PAYPAL_ENV || 'live',
      webhook_id_configured: !!paypalEnv().webhookId,
    });
  }
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST, GET');
    return res.status(405).json({ error: 'method not allowed' });
  }

  let rawBody;
  try {
    rawBody = await readRawBody(req);
  } catch (e) {
    return res.status(400).json({ error: 'cannot read body' });
  }

  const ppEnv = paypalEnv();

  // Verify signature against the raw body
  let verified = false;
  try {
    verified = await verifySignature(req, rawBody, ppEnv);
  } catch (e) {
    console.error('verify error', e?.message || e);
  }

  if (!verified) {
    console.warn('paypal webhook signature verification failed');
    // Still return 200 so PayPal doesn't keep retrying garbage; just don't process
    return res.status(200).json({ ok: true, ignored: 'unverified' });
  }

  let event;
  try {
    event = JSON.parse(rawBody);
  } catch (e) {
    return res.status(400).json({ error: 'invalid json' });
  }

  const summary = summarize(event);
  const formType = shortFormType(event.event_type);

  // Hand off to existing form-notify infrastructure (email + Google Sheet)
  try {
    await fetch(FORM_NOTIFY_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        site_slug: 'studio-one',
        form_type: formType,
        // Hidden honeypot must be blank to pass form-notify spam filter
        _honey: '',
        // Skip reCAPTCHA — internal server-to-server call
        recaptcha_token: 'server-to-server',
        ...summary,
      }),
    });
  } catch (e) {
    console.error('form-notify dispatch failed:', e?.message || e);
    // Don't fail the webhook — we already verified, will be in Vercel logs
  }

  // Always 200 quickly (< 10s) so PayPal doesn't retry
  return res.status(200).json({ ok: true, event_id: summary.event_id, event_type: summary.event_type });
}
