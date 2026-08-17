// /api/phone-consult  —  Vercel serverless function (Node.js runtime)
//
// Powers the /phone-consultation booking page.
//
//   GET  -> upcoming Friday-morning slots (9:00 + 9:30 AM Pacific) with
//           taken/free state, read from Cat's Vagaro calendar.
//   POST -> books a slot: records the lead via form-notify (trusted
//           x-internal-secret path -> emails Cat + admin inbox row) and
//           creates a personal task on Cat's Vagaro calendar so the call
//           shows up right on her book.
//
// Why personal tasks and not the Vagaro availability API: a recurring
// "Phone Consultations (website)" personal task blocks Friday 9-10am from
// ALL online salon booking (that hour belongs to phone consults only), which
// also makes the hour look "busy" to the availability API. So slot state
// comes from reading the personal tasks in that hour instead: the recurring
// block is filtered out, and each booked call is a single (non-recurring)
// task that marks its half hour as taken.
//
// Required Vercel env vars:
//   VAGARO_CLIENT_ID       Vagaro API client id     (from .env.keys.cat)
//   VAGARO_SECRET          Vagaro API client secret (from .env.keys.cat)
//   INTERNAL_FORM_SECRET   form-notify trusted-path secret (already set for
//                          the PayPal webhook)

const VAGARO_BASE = 'https://api.vagaro.com/us02/api/v2';
const BUSINESS_ID = 'Dm1SiNS~LVBx~J6YZaU9aA==';
const CAT_PROVIDER_ID = 'd3lscujGMO02shBdCuMH-g==';   // Cathy Barco
const FORM_NOTIFY_URL = 'https://myaieditor.com/api/form-notify';

const SLOT_TIMES = ['09:00', '09:30'];                 // Pacific, Fridays only
const WEEKS_OFFERED = 4;                               // next 4 Fridays
const BLOCK_NAME = 'Phone Consultations (website)';    // the recurring reserve
const TASK_PREFIX = 'Phone Consult:';                  // per-booking task name

// ---------------------------------------------------------------- Vagaro

// Module-scope token cache (survives warm invocations)
const tokenCache = {};

async function vagaroToken(scope) {
  const hit = tokenCache[scope];
  if (hit && hit.exp > Date.now()) return hit.token;
  const r = await fetch(`${VAGARO_BASE}/merchants/generate-access-token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      clientId: process.env.VAGARO_CLIENT_ID || '',
      clientSecretKey: process.env.VAGARO_SECRET || '',
      scope,
    }),
  });
  if (!r.ok) throw new Error(`vagaro token mint failed: ${r.status}`);
  const j = await r.json();
  const token = j?.data?.accessToken || j?.data?.access_token || j?.accessToken;
  if (!token) throw new Error('vagaro token missing in response');
  tokenCache[scope] = { token, exp: Date.now() + 50 * 60 * 1000 }; // TTL 3600s, keep 50min
  return token;
}

async function vagaro(path, body, scope) {
  const token = await vagaroToken(scope);
  const r = await fetch(`${VAGARO_BASE}/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', accessToken: token },
    body: JSON.stringify(body),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(`vagaro ${path} failed: ${r.status} ${JSON.stringify(j).slice(0, 200)}`);
  return j;
}

// ------------------------------------------------------------- Date math

// Today's date (YYYY-MM-DD) in the salon's timezone
function laToday() {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Los_Angeles',
    year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(new Date());
}

// The next N Fridays strictly after today (LA time)
function upcomingFridays(count) {
  const [y, m, d] = laToday().split('-').map(Number);
  const base = Date.UTC(y, m - 1, d);
  const out = [];
  for (let i = 1; out.length < count && i <= 7 * (count + 2); i++) {
    const dt = new Date(base + i * 86400000);
    if (dt.getUTCDay() === 5) out.push(dt.toISOString().slice(0, 10));
  }
  return out;
}

function dateLabel(ymd) {
  const [y, m, d] = ymd.split('-').map(Number);
  return new Intl.DateTimeFormat('en-US', {
    timeZone: 'UTC', weekday: 'long', month: 'long', day: 'numeric',
  }).format(new Date(Date.UTC(y, m - 1, d)));
}

function timeLabel(hhmm) {
  const [h, min] = hhmm.split(':').map(Number);
  const h12 = ((h + 11) % 12) + 1;
  return `${h12}:${String(min).padStart(2, '0')} ${h < 12 ? 'AM' : 'PM'}`;
}

function slotEnd(hhmm) {
  const [h, m] = hhmm.split(':').map(Number);
  const t = h * 60 + m + 30;
  return `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`;
}

// ---------------------------------------------------------- Availability

// Minutes since midnight from a Vagaro local datetime string
function minutesOf(dt) {
  const m = /T(\d{2}):(\d{2})/.exec(dt || '');
  return m ? Number(m[1]) * 60 + Number(m[2]) : null;
}

// Which of SLOT_TIMES are taken on a given Friday.
// A slot is taken when any SINGLE (non-recurring) personal task on Cat's
// calendar overlaps it. The recurring reserve block and any recurring
// series masters (Vagaro returns those for every window they intersect)
// are ignored.
async function takenSlots(ymd) {
  const j = await vagaro('personal-tasks/retrieve', {
    businessId: BUSINESS_ID,
    serviceProviderId: CAT_PROVIDER_ID,
    startTime: `${ymd}T00:00:00`,
    endTime: `${ymd}T23:59:59`,
  }, 'read access');
  const tasks = j?.data?.personalTasks || [];
  const taken = new Set();
  for (const t of tasks) {
    if (t.recurrence) continue;                       // series masters
    if (!(t.startTime || '').startsWith(ymd)) continue; // singles on this day only
    const s = minutesOf(t.startTime);
    const e = minutesOf(t.endTime);
    if (s == null) continue;
    for (const slot of SLOT_TIMES) {
      const ss = minutesOf(`T${slot}`);
      const se = ss + 30;
      if (s < se && (e == null ? s + 30 : e) > ss) taken.add(slot);
    }
  }
  return taken;
}

async function buildAvailability() {
  const fridays = upcomingFridays(WEEKS_OFFERED);
  const days = await Promise.all(fridays.map(async (ymd) => {
    let taken = new Set();
    try { taken = await takenSlots(ymd); }
    catch (e) {
      console.error('takenSlots failed for', ymd, e?.message || e);
      // Fail closed: if we can't read the calendar, don't offer the day
      return { date: ymd, label: dateLabel(ymd), slots: SLOT_TIMES.map((t) => ({ time: t, label: timeLabel(t), taken: true })) };
    }
    return {
      date: ymd,
      label: dateLabel(ymd),
      slots: SLOT_TIMES.map((t) => ({ time: t, label: timeLabel(t), taken: taken.has(t) })),
    };
  }));
  return days;
}

// ---------------------------------------------------------------- Handler

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      const days = await buildAvailability();
      res.setHeader('Cache-Control', 'no-store');
      return res.status(200).json({ ok: true, timezone: 'America/Los_Angeles', days });
    } catch (e) {
      console.error('availability error:', e?.message || e);
      return res.status(502).json({ ok: false, error: 'calendar unavailable' });
    }
  }

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ error: 'method not allowed' });
  }

  const b = req.body || {};

  // Honeypot: pretend success, record nothing
  if (b._honey) return res.status(200).json({ ok: true, accepted: true });

  // ---- Validate
  const first = String(b.first_name || '').trim().slice(0, 60);
  const last = String(b.last_name || '').trim().slice(0, 60);
  const phoneDigits = String(b.phone || '').replace(/\D/g, '');
  const email = String(b.email || '').trim().slice(0, 120);
  const interest = String(b.interest || '').trim().slice(0, 80);
  const notes = String(b.notes || '').trim().slice(0, 1000);
  const date = String(b.date || '').trim();
  const time = String(b.time || '').trim();

  const problems = [];
  if (!first) problems.push('first name');
  if (phoneDigits.length !== 10) problems.push('10-digit phone number');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) problems.push('email');
  if (!upcomingFridays(WEEKS_OFFERED).includes(date)) problems.push('date');
  if (!SLOT_TIMES.includes(time)) problems.push('time');
  if (problems.length) {
    return res.status(400).json({ ok: false, accepted: false, error: `Please check: ${problems.join(', ')}.` });
  }

  const phonePretty = `(${phoneDigits.slice(0, 3)}) ${phoneDigits.slice(3, 6)}-${phoneDigits.slice(6)}`;
  const whenPretty = `${dateLabel(date)} at ${timeLabel(time)} Pacific`;

  // ---- Slot still free? (re-check right before booking)
  try {
    const taken = await takenSlots(date);
    if (taken.has(time)) {
      return res.status(409).json({ ok: false, accepted: false, error: 'That time was just booked. Please pick another slot.' });
    }
  } catch (e) {
    console.error('slot re-check failed:', e?.message || e);
    return res.status(502).json({ ok: false, accepted: false, error: 'calendar unavailable' });
  }

  // ---- 1) Record the lead (email to Cat + admin portal row). This is the
  //         critical record: if it fails, the booking fails.
  let leadOk = false;
  try {
    const r = await fetch(FORM_NOTIFY_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-internal-secret': process.env.INTERNAL_FORM_SECRET || '',
      },
      body: JSON.stringify({
        site_slug: 'studio-one',
        form_type: 'phone-consultation',
        first_name: first,
        last_name: last,
        phone: phonePretty,
        email,
        interest,
        notes,
        consult_date: date,
        consult_time: time,
        scheduled_for: whenPretty,
        summary: `PHONE consultation booked for ${whenPretty}. Cat calls ${first} at ${phonePretty}.`,
        send_visitor_copy: 'true',
        visitor_email_subject: 'Your phone consultation with Cat is booked — Studio One Hair Design',
      }),
    });
    const j = await r.json().catch(() => ({}));
    leadOk = r.ok && j.accepted !== false;
    if (!leadOk) console.error('form-notify rejected phone consult:', r.status, JSON.stringify(j).slice(0, 300));
  } catch (e) {
    console.error('form-notify dispatch failed:', e?.message || e);
  }
  if (!leadOk) {
    return res.status(502).json({ ok: false, accepted: false, error: 'booking could not be recorded' });
  }

  // ---- 2) Put the call on Cat's Vagaro calendar. Best effort: the lead is
  //         already recorded and emailed, so a calendar hiccup must not fail
  //         the visitor's booking.
  let calendarOk = false;
  try {
    const comment = [
      `PHONE CONSULTATION - Cat calls the client at ${phonePretty}.`,
      `Client: ${first} ${last}`.trim(),
      email ? `Email: ${email}` : '',
      interest ? `Interested in: ${interest}` : '',
      notes ? `Notes: ${notes}` : '',
      'Booked on studioonefresno.com/phone-consultation',
    ].filter(Boolean).join('\n').slice(0, 500);
    await vagaro('personal-tasks/create', {
      businessId: BUSINESS_ID,
      serviceProviderId: CAT_PROVIDER_ID,
      personalTaskName: `${TASK_PREFIX} ${first} ${last}`.trim().slice(0, 100),
      personalTaskComment: comment,
      personalTaskHexCode: '#4c5223',
      blockOnlineBooking: true,
      startTime: `${date}T${time}:00`,
      endTime: `${date}T${slotEnd(time)}:00`,
    }, 'write employee');
    calendarOk = true;
  } catch (e) {
    // The lead email doubles as the backstop: Cat still hears about the call.
    console.error('vagaro task create failed (lead already recorded):', e?.message || e);
  }

  return res.status(200).json({ ok: true, accepted: true, calendar: calendarOk, scheduled_for: whenPretty });
}
