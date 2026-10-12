// Vercel serverless proxy: forwards /api/* to the FastAPI service on GKE and
// attaches the API key server-side so it never reaches the browser.
const API_HOST = (process.env.API_HOST || '').replace(/\/$/, '')
const API_KEY = process.env.API_KEY || ''

export default async function handler(req, res) {
  if (!API_HOST) return res.status(500).json({ error: 'API_HOST is not configured' })
  const segments = [].concat(req.query['...path'] ?? req.query.path ?? [])
  const url = new URL(`${API_HOST}/${segments.join('/')}`)
  for (const [k, v] of Object.entries(req.query)) {
    if (k === 'path' || k === '...path' || k === '__debug') continue
    for (const item of [].concat(v)) url.searchParams.append(k, item)
  }
  try {
    const upstream = await fetch(url, {
      method: req.method,
      headers: { 'x-api-key': API_KEY, accept: 'application/json' },
      body: ['GET', 'HEAD'].includes(req.method) ? undefined : JSON.stringify(req.body ?? {}),
    })
    res.status(upstream.status)
    res.setHeader('content-type', upstream.headers.get('content-type') || 'application/json')
    res.setHeader('cache-control', 'no-store')
    res.send(Buffer.from(await upstream.arrayBuffer()))
  } catch (err) {
    res.status(502).json({ error: 'upstream unavailable', detail: String(err) })
  }
}
