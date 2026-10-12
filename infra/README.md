# city-records infra (GKE Autopilot, us-east1)
1. Create cluster + registry: `bash infra/create-cluster.sh`
2. Deploy everything: `bash infra/deploy.sh` (add `--skip-build` to reuse pushed images)
   - builds/pushes `pipeline` and `api` (linux/amd64), applies secrets from `.env`,
     installs Dagster via Helm (`infra/dagster-values.yaml`), applies `infra/k8s`.
3. Secrets only: `bash infra/secrets.sh`
4. Dagster UI: `kubectl -n dagster port-forward svc/dagster-dagster-webserver 3000:80`
   (check `kubectl -n dagster get svc` for the exact webserver service name)
5. API external IP: `kubectl -n app get svc api -w` (EXTERNAL-IP column)
6. Logs: `kubectl -n app logs deploy/api`, `kubectl -n dagster logs deploy/dagster-daemon`
7. Teardown: `gcloud container clusters delete city-records --region us-east1 --project city-records-511405`
8. Registry cleanup: `gcloud artifacts repositories delete city-records --location us-east1`
