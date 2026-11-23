// /api/career-video
//
// Starts a Cloudflare Stream direct upload for the 2-minute intro video on
// /careers/apply. Returns a one-time tus upload URL the applicant's browser
// sends the file to in chunks (phone videos are often 100MB+, far past the
// form handler's body limit), plus the Stream video id that rides along with
// the application. The video is unlisted: playable only by its link.
//
// Env: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_STREAM_API_TOKEN

const MAX_BYTES = 1024 * 1024 * 1024 // 1 GB

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false })
  const account = process.env.CLOUDFLARE_ACCOUNT_ID
  const token = process.env.CLOUDFLARE_STREAM_API_TOKEN
  if (!account || !token) return res.status(500).json({ ok: false, error: 'not configured' })

  let body = req.body
  if (typeof body === 'string') { try { body = JSON.parse(body) } catch { body = {} } }
  const size = Number((body || {}).size || 0)
  if (!Number.isFinite(size) || size <= 0 || size > MAX_BYTES) {
    return res.status(400).json({ ok: false, error: 'Video must be under 1 GB.' })
  }
  const who = String((body || {}).name || 'applicant').replace(/[^\w .'-]/g, '').slice(0, 60) || 'applicant'
  const b64 = (s) => Buffer.from(String(s)).toString('base64')
  const meta = [
    `maxDurationSeconds ${b64(300)}`,
    `name ${b64(`Studio One application - ${who}`)}`,
  ].join(',')

  try {
    const r = await fetch(`https://api.cloudflare.com/client/v4/accounts/${account}/stream?direct_user=true`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Tus-Resumable': '1.0.0',
        'Upload-Length': String(size),
        'Upload-Metadata': meta,
      },
    })
    const uploadUrl = r.headers.get('location')
    const uid = r.headers.get('stream-media-id')
    if (!r.ok || !uploadUrl || !uid) {
      console.error('career-video: create failed', r.status, (await r.text().catch(() => '')).slice(0, 300))
      return res.status(502).json({ ok: false, error: 'Could not start the upload.' })
    }
    return res.status(200).json({ ok: true, uploadUrl, uid, watchUrl: `https://iframe.videodelivery.net/${uid}` })
  } catch (e) {
    console.error('career-video: error', e?.message || e)
    return res.status(502).json({ ok: false, error: 'Could not start the upload.' })
  }
}
