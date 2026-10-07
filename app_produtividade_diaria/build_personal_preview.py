"""Build an offline personal dashboard without publishing private data to GitHub."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
TEMPLATE = PACKAGE / "site" / "painel.template.html"
TOKEN = "__EMBEDDED_DASHBOARD_JSON__"


def build(data_path: Path, output_path: Path) -> None:
    payload = json.loads(Path(data_path).read_text(encoding="utf-8"))
    months = payload.get("monthly", [])
    if len(months) < 2 or not all(row.get("period") for row in months):
        raise ValueError("A série mensal precisa de pelo menos dois meses identificados.")
    if [row["period"] for row in months] != sorted(row["period"] for row in months):
        raise ValueError("A série mensal deve estar em ordem cronológica.")
    activities = payload.get("dailyActivities", [])
    relations = payload.get("relationships", [])
    if not isinstance(activities, list) or not isinstance(relations, list):
        raise ValueError("Atividades e relações devem ser listas.")
    for index, row in enumerate(activities, start=1):
        if not isinstance(row, dict) or not row.get("activityDate") or not str(row.get("description", "")).strip():
            raise ValueError(f"Atividade {index}: data e descrição são obrigatórias.")
        try:
            date.fromisoformat(row["activityDate"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Atividade {index}: data inválida.") from exc
        if not isinstance(row.get("processIds", []), list):
            raise ValueError(f"Atividade {index}: processos devem ser uma lista.")
        row.setdefault("processIds", [])
    for index, row in enumerate(relations, start=1):
        if not isinstance(row, dict) or not row.get("processA") or not row.get("processB"):
            raise ValueError(f"Relação {index}: os dois processos são obrigatórios.")
        if row.get("confirmationState") == "confirmed" and (
            not str(row.get("evidence", "")).strip()
            or not str(row.get("evidenceReference", "")).strip()
        ):
            raise ValueError(f"Relação {index}: confirmação exige evidência e referência.")
    payload["dailyActivities"] = activities
    payload["relationships"] = relations
    markup = TEMPLATE.read_text(encoding="utf-8")
    if markup.count(TOKEN) != 1:
        raise ValueError("O template deve conter exatamente um marcador de dados.")
    safe_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    safe_json = safe_json.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markup.replace(TOKEN, safe_json), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.data, args.output)
