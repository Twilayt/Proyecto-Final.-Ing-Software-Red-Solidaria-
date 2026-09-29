# Resumen del escaneo OWASP ZAP

Este formato debe completarse con los valores del reporte generado por `security-zap.yml` o `scripts/run_zap_windows.ps1`. No se incluyen cifras ficticias.

| Campo | Resultado real |
|---|---|
| Fecha y hora | Pendiente de ejecución |
| Versión de ZAP | Pendiente de ejecución |
| Objetivo API | `http://127.0.0.1:8000/openapi.json` o URL equivalente |
| Objetivo web | `http://127.0.0.1:8000/docs` o URL equivalente |
| Alertas altas | Pendiente |
| Alertas medias | Pendiente |
| Alertas bajas | Pendiente |
| Informativas | Pendiente |
| Resultado XSS | Pendiente |
| Resultado SQLi | Pendiente |

## Hallazgos

| Alerta | Severidad | Ruta | Evidencia | Mitigación | Reprueba |
|---|---|---|---|---|---|
| Completar desde el reporte |  |  |  |  |  |

## Criterio de aceptación

- Cero alertas de riesgo alto abiertas.
- Toda alerta media revisada y clasificada como corregida, aceptada con justificación o falso positivo documentado.
- Resultado explícito para XSS y SQLi.
- Segundo escaneo realizado después de aplicar correcciones relevantes.

