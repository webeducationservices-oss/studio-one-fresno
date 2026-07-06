// /api/verify-payment  —  Vercel serverless function (Node.js runtime)
//
// Called (same-origin) by /pay right after a PayPal checkout captures. It VERIFIES the
// payment with PayPal's Orders API, then — only if it's a real, COMPLETED capture whose
// custom_id matches the order — calls the admin /api/pay-confirm (with the shared secret)
// to flip that wholesale order to Paid.
//
// This is the hardening: the browser can no longer mark an order paid on its own. A paid
// flip requires a payment that PayPal confirms server-side. The PayPal-signed webhook
// (/api/paypal-webhook) is an async backstop that does the same thing.
//
// Env: PAYPAL_ENV, PAYPAL_LIVE_CLIENT_ID/SECRET (or SANDBOX), PAY_CONFIRM_SECRET.

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const ADMIN_CONFIRM_URL = 'https://admin.studioonefresno.com/api/pay-confirm';

function paypalEnv() {
  const env = (process.env.PAYPAL_ENV || 'live').toLowerCase();
  if (env === 'sandbox') {
    return {
      base: 'https://api-m.sandbox.paypal.com',
      clientId: process.env.PAYPAL_SANDBOX_CLIENT_ID || '',
      secret: process.env.PAYPAL_SANDBOX_SECRET || '',
    };
  }
  return {
    base: 'https://api-m.paypal.com',
    clientId: process.env.PAYPAL_LIVE_CLIENT_ID || '',
    secret: process.env.PAYPAL_LIVE_SECRET || '',
  };
}

async function getAccessToken({ base, clientId, secret }) {
  const auth = Buffer.from(`${clientId}:${secret}`).toString('base64');
  const r = await fetch(`${base}/v1/oauth2/token`, {
    method: 'POST',
    headers: { Authorization: `Basic ${auth}`, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'grant_type=client_credentials',
  });
  if (!r.ok) throw new Error(`PayPal token request failed: ${r.status}`);
  return (await r.json()).access_token;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'method not allowed' });
  }

  const body = req.body || {};
  const leadId = String(body.lead_id || '').trim();
  const paypalId = String(body.paypal_order_id || '').trim();
  if (!UUID_RE.test(leadId)) return res.status(400).json({ ok: false, error: 'invalid lead_id' });
  if (!paypalId) return res.status(400).json({ ok: false, error: 'missing paypal_order_id' });

  const ppEnv = paypalEnv();

  // 1) Verify the payment with PayPal.
  let order;
  try {
    const token = await getAccessToken(ppEnv);
    const r = await fetch(`${ppEnv.base}/v2/checkout/orders/${encodeURIComponent(paypalId)}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!r.ok) return res.status(502).json({ ok: false, error: 'paypal lookup failed' });
    order = await r.json();
  } catch (e) {
    console.error('verify-payment paypal error:', e?.message || e);
    return res.status(502).json({ ok: false, error: 'paypal error' });
  }

  const pu = (order.purchase_units && order.purchase_units[0]) || {};
  const cap = (pu.payments && pu.payments.captures && pu.payments.captures[0]) || {};
  const completed = order.status === 'COMPLETED' && (cap.status ? cap.status === 'COMPLETED' : true);
  const custom = pu.custom_id || cap.custom_id || '';

  if (!completed) return res.status(409).json({ ok: false, error: 'payment not completed' });
  // Tie the payment to the order it was for — can't mark a different order paid with someone else's payment.
  if (custom && custom !== leadId) return res.status(409).json({ ok: false, error: 'order mismatch' });

  const amountVal = (cap.amount && cap.amount.value) || (pu.amount && pu.amount.value) || '0';
  const amountCents = Math.round(parseFloat(amountVal || '0') * 100) || 0;

  // 2) Tell the admin to flip the order Paid (server-to-server, secret-gated).
  try {
    const r = await fetch(ADMIN_CONFIRM_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-pay-secret': process.env.PAY_CONFIRM_SECRET || '' },
      body: JSON.stringify({ lead_id: leadId, paypal_order_id: paypalId, amount_cents: amountCents }),
    });
    const j = await r.json().catch(() => ({}));
    return res.status(200).json({ ok: !!j.ok, confirmed: !!j.ok });
  } catch (e) {
    console.error('verify-payment confirm error:', e?.message || e);
    return res.status(502).json({ ok: false, error: 'confirm failed' });
  }
}
