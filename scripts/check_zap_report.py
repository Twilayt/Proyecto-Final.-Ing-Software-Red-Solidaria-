"""Falla el pipeline si un reporte JSON de ZAP contiene alertas de riesgo alto."""

import json
import sys
from pathlib import Path


def high_risk_alerts(report_path: Path) -> list[dict]:
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    alerts: list[dict] = []
    for site in payload.get("site", []):
        for alert in site.get("alerts", []):
            risk_code = int(alert.get("riskcode", 0))
            if risk_code >= 3:
                alerts.append(alert)
    return alerts


def main(directory: str) -> int:
    report_dir = Path(directory)
    json_reports = sorted(report_dir.glob("*.json"))
    if not json_reports:
        print("No se encontraron reportes JSON de ZAP.")
        return 1

    findings: list[tuple[str, str]] = []
    for report in json_reports:
        for alert in high_risk_alerts(report):
            findings.append((report.name, alert.get("name", "Alerta sin nombre")))

    if findings:
        print("ZAP detectó alertas de riesgo alto:")
        for report_name, alert_name in findings:
            print(f"- {report_name}: {alert_name}")
        return 1

    print("Puerta ZAP aprobada: sin alertas de riesgo alto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))

