#!/usr/bin/env bash
# Creates/updates k8s secrets from the repo-root .env. Never prints values.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
set -a; source "$ROOT/.env"; set +a

kubectl apply -f "$ROOT/infra/k8s/dagster-namespace.yaml" -f "$ROOT/infra/k8s/namespace.yaml" >/dev/null

apply_secret() { # ns name args...
  local ns=$1 name=$2; shift 2
  kubectl -n "$ns" create secret generic "$name" "$@" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
  echo "applied secret $ns/$name"
}

# Password portion of DATABASE_URL (postgresql://user:PASSWORD@host:port/db), URL-decoded.
DB_PASSWORD="$(python3 -c 'import os,urllib.parse as u; print(u.unquote(u.urlparse(os.environ["DATABASE_URL"]).password or ""), end="")')"

ARGS=()
for v in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_REGION S3_BUCKET BEDROCK_MODEL_ID DATABASE_URL \
         HONEYBADGER_API_KEY LANGFUSE_SECRET_KEY LANGFUSE_PUBLIC_KEY LANGFUSE_HOST SOCRATA_APP_TOKEN; do
  if [ -n "${!v:-}" ]; then ARGS+=("--from-literal=$v=${!v}"); else echo "warning: $v unset/empty, skipped" >&2; fi
done
apply_secret dagster pipeline-env "${ARGS[@]}"
apply_secret dagster dagster-postgresql-secret "--from-literal=postgresql-password=$DB_PASSWORD"
apply_secret app api-env \
  "--from-literal=DATABASE_POOL_URL=${DATABASE_POOL_URL:?}" \
  "--from-literal=API_KEY=${API_KEY:?}" \
  "--from-literal=HONEYBADGER_API_KEY=${HONEYBADGER_API_KEY:-}"
