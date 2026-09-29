$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path "reports/evidencias/owasp-zap" | Out-Null

docker run --rm --network host `
  -v "${PWD}/reports/evidencias/owasp-zap:/zap/wrk/:rw" `
  -t ghcr.io/zaproxy/zaproxy:stable `
  zap-api-scan.py `
  -t http://host.docker.internal:8000/openapi.json `
  -f openapi -I `
  -r zap-api-report.html `
  -J zap-api-report.json `
  -w zap-api-report.md

Write-Host "Reportes guardados en reports/evidencias/owasp-zap"

