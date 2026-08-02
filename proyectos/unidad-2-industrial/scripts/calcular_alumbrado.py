#!/usr/bin/env python3
"""Verifica por metodo de lumenes las zonas de alumbrado del grifo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for zone in data["zones"]:
        area = float(zone["area_m2"])
        fixtures = int(zone["fixtures"])
        flux = float(zone["fixture_flux_lm"])
        cu = float(zone["utilization_factor"])
        fm = float(zone["maintenance_factor"])
        target = float(zone["target_lux"])
        if min(area, fixtures, flux, cu, fm, target) <= 0:
            failures.append(f"{zone['id']}: parametro no positivo")
            continue
        average_lux = fixtures * flux * cu * fm / area
        installed_kw = fixtures * float(zone["fixture_power_w"]) / 1000.0
        passed = average_lux + 1e-9 >= target
        if not passed:
            failures.append(f"{zone['id']}: {average_lux:.1f} lux < {target:.1f} lux")
        rows.append({**zone, "average_lux": average_lux, "installed_kw": installed_kw, "pass": passed})
    return {"schema_version": 1, "status": "PASS" if not failures else "FAIL", "zones": rows, "failures": failures, "limitations": data.get("limitations", [])}


def write_outputs(result: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "resumen-alumbrado.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Calculo de alumbrado por metodo de lumenes", "", f"Estado: **{result['status']}**.", "", "| Zona | Objetivo | Calculado | Potencia | Estado |", "|---|---:|---:|---:|---|"]
    for zone in result["zones"]:
        lines.append(f"| {zone['id']} — {zone['description']} | {zone['target_lux']:.0f} lx | {zone['average_lux']:.1f} lx | {zone['installed_kw']:.2f} kW | {'CUMPLE' if zone['pass'] else 'NO CUMPLE'} |")
    lines.extend(["", "## Limitaciones", ""] + [f"- {item}" for item in result["limitations"]] + [""])
    (output / "memoria-alumbrado.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = repository_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=root / "proyectos/unidad-2-industrial/diseno-electrico/datos/alumbrado.yaml")
    parser.add_argument("--output", type=Path, default=root / "build/unidad-2-industrial/calculos")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    result = calculate(data)
    write_outputs(result, args.output.resolve())
    print(json.dumps({"status": result["status"], "zones": [{"id": z["id"], "lux": round(z["average_lux"], 1)} for z in result["zones"]], "failures": result["failures"]}, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
