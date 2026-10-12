#!/usr/bin/env bash
# Creates the GKE Autopilot cluster and the Artifact Registry repository.
# Idempotent: safe to re-run.
set -euo pipefail
PROJECT="${GCP_PROJECT_ID:-city-records-511405}"
REGION="${GCP_REGION:-us-east1}"
CLUSTER="${CLUSTER_NAME:-city-records}"

gcloud services enable container.googleapis.com artifactregistry.googleapis.com --project "$PROJECT"

if ! gcloud artifacts repositories describe city-records --location "$REGION" --project "$PROJECT" >/dev/null 2>&1; then
  gcloud artifacts repositories create city-records --repository-format docker \
    --location "$REGION" --project "$PROJECT" --description "city-records images"
fi

if ! gcloud container clusters describe "$CLUSTER" --region "$REGION" --project "$PROJECT" >/dev/null 2>&1; then
  gcloud container clusters create-auto "$CLUSTER" --region "$REGION" --project "$PROJECT" --release-channel regular
fi

gcloud container clusters get-credentials "$CLUSTER" --region "$REGION" --project "$PROJECT"
echo "Registry: ${REGION}-docker.pkg.dev/${PROJECT}/city-records"
