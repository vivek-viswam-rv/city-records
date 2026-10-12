# City Records web

Vite + React 18 + Tailwind v3 dashboard over NYC City Record procurement notices.

## Run

```sh
pnpm install
cp .env.example .env
pnpm dev                 # http://localhost:5173
pnpm lint
pnpm build               # output in dist/
```

Dev server proxies `/api/*` to `http://localhost:8000` (prefix stripped), so run the API first.

## Structure

- `src/apis/` - axios setup (`axios.js`, `registerIntercepts()` called in `main.jsx`) and one file per resource (`notices`, `vendors`, `stats`, `filters`) exporting a `<resource>Api` object.
- `src/hooks/reactQuery/` - react-query hooks (`useFetchNotices`, `useShowNotice`, `useShowVendor`, `useFetchStats`, `useFetchFilters`) that `select` `response.data`.
- `src/constants/query.js` - `QUERY_KEYS` used for every query key.
- `src/utils/queryClient.js` - shared QueryClient and defaults; `src/utils/index.js` - small helpers such as `isPresent`.
- `src/hooks/useDebouncedValue.js` - lodash-based debounce hook (300ms default) used by the search inputs.
- Import via aliases (`apis`, `hooks`, `components`, `utils`, `constants`, `lib`), configured in `vite.config.js` and `jsconfig.json`.

## Environment variables

| Var | Purpose |
| --- | --- |
| `VITE_API_URL` | API base URL, default `/api` |
| `VITE_API_KEY` | Sent as `x-api-key` if set |
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

`api/proxy.js` is a Vercel serverless function (reached via the `/api/(.*)` rewrite in `vercel.json`) that forwards `/api/*` to the
FastAPI service and adds the `x-api-key` header from server-side env vars, so the
key is never shipped to the browser. Set these in the Vercel project:

- `API_HOST` – e.g. `http://34.26.80.231` (the GKE LoadBalancer IP)
- `API_KEY` – the same value as the API's `API_KEY`
