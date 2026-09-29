$ErrorActionPreference = "Stop"

docker compose -f docker-compose.sonar.yml up -d
Write-Host "Espera a que SonarQube esté disponible en http://localhost:9000"
Write-Host "Genera un token y ejecuta el escáner siguiendo GUIA_EJECUCION.md"

