// /api/wholesale-license-url  —  Vercel serverless function (Node.js runtime)
//
// Mints a one-time SIGNED UPLOAD URL for a wholesale-application license file, so the
// applicant's browser can upload the file straight to the private Supabase Storage
// bucket `wholesale-licenses` (no anon storage policy needed, no Vercel body-size limit).
// Returns { path, token }; the client then uploads via supabase-js uploadToSignedUrl.
//
// Env: STUDIOONE_WHOLESALE_SUPABASE_URL, STUDIOONE_WHOLESALE_SERVICE_ROLE_KEY

const ALLOWED_EXT = { jpg: 1, jpeg: 1, png: 1, webp: 1, heic: 1, heif: 1, pdf: 1 }

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST')
    return res.status(405).json({ error: 'method not allowed' })
  }
  const url = process.env.STUDIOONE_WHOLESALE_SUPABASE_URL
  const svc = process.env.STUDIOONE_WHOLESALE_SERVICE_ROLE_KEY
  if (!url || !svc) return res.status(500).json({ error: 'not configured' })

  const body = req.body || {}
  const extRaw = String(body.ext || '').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 5)
  const ext = ALLOWED_EXT[extRaw] ? extRaw : 'dat'
  const rand = Date.now().toString(36) + Math.random().toString(36).slice(2, 10)
  const path = `applications/${rand}.${ext}`

  try {
    const r = await fetch(`${url}/storage/v1/object/upload/sign/wholesale-licenses/${path}`, {
      method: 'POST',
      headers: { apikey: svc, Authorization: `Bearer ${svc}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    if (!r.ok) {
      const t = await r.text().catch(() => '')
      console.error('sign upload url failed', r.status, t)
      return res.status(502).json({ error: 'could not prepare upload' })
    }
    const j = await r.json()
    const token = (j.url || '').split('token=')[1] || ''
    if (!token) return res.status(502).json({ error: 'no token' })
    return res.status(200).json({ path, token })
  } catch (e) {
    console.error('sign upload url error', e?.message || e)
    return res.status(502).json({ error: 'upload prep error' })
  }
}
