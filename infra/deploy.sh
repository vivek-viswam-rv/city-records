#!/usr/bin/env bash
# Build, push and deploy pipeline (Dagster Helm) and API (kustomize). Usage: infra/deploy.sh [--skip-build]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
REGISTRY=us-east1-docker.pkg.dev/city-records-511405/city-records
SKIP_BUILD=0
for a in "$@"; do case "$a" in --skip-build) SKIP_BUILD=1 ;; *) echo "unknown flag $a" >&2; exit 2 ;; esac; done
TAG="$(git rev-parse --short HEAD)"

if [ "$SKIP_BUILD" = 0 ]; then
  gcloud auth configure-docker us-east1-docker.pkg.dev --quiet
  docker buildx build --platform linux/amd64 -f pipeline/Dockerfile -t "$REGISTRY/pipeline:$TAG" -t "$REGISTRY/pipeline:latest" --push pipeline
  docker buildx build --platform linux/amd64 -f api/Dockerfile -t "$REGISTRY/api:$TAG" -t "$REGISTRY/api:latest" --push .
fi

bash infra/secrets.sh

helm repo add dagster https://dagster-io.github.io/helm >/dev/null 2>&1 || true
helm repo update >/dev/null
helm upgrade --install dagster dagster/dagster -n dagster --create-namespace \
  -f infra/dagster-values.yaml \
  --set "dagster-user-deployments.deployments[0].image.tag=$TAG"

kubectl apply -k infra/k8s
kubectl -n app set image deployment/api api="$REGISTRY/api:$TAG"

kubectl -n dagster rollout status deployment --timeout=300s
kubectl -n app rollout status deployment/api --timeout=300s
echo "deployed $TAG"
