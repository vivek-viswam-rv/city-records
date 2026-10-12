# City Records web

Vite + React 18 + Tailwind v3 dashboard over NYC City Record procurement notices.

## Run

```sh
pnpm install
cp .env.example .env     # VITE_USE_MOCK=1 works without an API
pnpm dev                 # http://localhost:5173
pnpm lint
pnpm build               # output in dist/
```

Dev server proxies `/api/*` to `http://localhost:8000` (prefix stripped).
With `VITE_USE_MOCK=1` the app uses `src/lib/mock.js` and makes no network calls.

## Environment variables

| Var | Purpose |
| --- | --- |
| `VITE_API_URL` | API base URL, default `/api` |
| `VITE_API_KEY` | Sent as `x-api-key` if set |
| `VITE_USE_MOCK` | `1` to use mock data |
| `VITE_HONEYBADGER_API_KEY` | Enables Honeybadger if set |

## Deploy on Vercel

- Root directory: `web`
- Framework preset: Vite (build `pnpm build`, output `dist`)
- Environment variables: as above (leave `VITE_API_URL` unset to use the `/api` rewrite; set `VITE_API_KEY` if the API requires one)

`vercel.json` proxies `/api/*` to the API and falls back to `index.html` for SPA routes.


```json
{ "source": "/api/:path*", "destination": "http://<ip>/:path*" }
```

Also replace `GITHUB_PLACEHOLDER` in `src/components/Footer.jsx`.

## API proxy on Vercel

`api/[...path].js` is a Vercel serverless function that forwards `/api/*` to the
FastAPI service and adds the `x-api-key` header from server-side env vars, so the
key is never shipped to the browser. Set these in the Vercel project:

- `API_HOST` – e.g. `http://34.26.80.231` (the GKE LoadBalancer IP)
- `API_KEY` – the same value as the API's `API_KEY`
