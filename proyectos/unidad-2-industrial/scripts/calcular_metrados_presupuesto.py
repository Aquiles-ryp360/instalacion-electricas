#!/usr/bin/env python3
"""Genera metrados y presupuesto academico desde cargas y partidas canonicas."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def merged_circuits(loads: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = loads.get("profiles", {})
    rows: list[dict[str, Any]] = []
    for raw in loads["circuits"]:
        row = dict(profiles.get(raw.get("profile"), {}))
        row.update(raw)
        rows.append(row)
    return rows


def conduit_id(*, method: str, supply: str, size: float) -> str:
    if method == "D":
        return "COND-32-D" if supply == "3P" or size > 4 else "COND-25-D"
    if supply == "3P":
        return "COND-32-I"
    return "COND-25-I"


def feeder_conduit_id(size: float) -> str:
    if size <= 4:
        return "COND-32-I"
    if size <= 6:
        return "COND-40-I"
    return "COND-50-I"


def calculate(loads: dict[str, Any], budget: dict[str, Any]) -> dict[str, Any]:
    factors = budget["factores"]
    route_factor = float(factors["holgura_rutas"])
    cable_factor = float(factors["holgura_conductores"])
    catalog = budget["catalogo"]
    circuits = merged_circuits(loads)

    routes: defaultdict[str, float] = defaultdict(float)
    cables: defaultdict[str, float] = defaultdict(float)
    for circuit in circuits:
        length = float(circuit["length_m"])
        size = float(circuit["conductor_mm2"])
        routes[conduit_id(method=str(circuit["method"]), supply=str(circuit["supply"]), size=size)] += length * route_factor
        active_count = 2 if circuit["supply"] == "1P" else 3
        cables[f"CAB-{size:g}"] += length * active_count * cable_factor
        cables[f"CAB-{float(circuit['pe_mm2']):g}"] += length * cable_factor

    for feeder in loads["feeders"]:
        length = float(feeder["length_m"])
        phase_size = float(feeder["phase_mm2"])
        pe_size = float(feeder["pe_mm2"])
        routes[feeder_conduit_id(phase_size)] += length * route_factor
        cables[f"CAB-{phase_size:g}"] += length * 4 * cable_factor
        cables[f"CAB-{pe_size:g}"] += length * cable_factor

    system = loads["system"]
    main_length = float(system["main_feeder_length_m"])
    routes["COND-75-D"] += main_length * route_factor
    cables[f"CAB-{float(system['main_feeder_phase_mm2']):g}"] += main_length * 4 * cable_factor
    cables[f"CAB-{float(system['main_feeder_pe_mm2']):g}"] += main_length * cable_factor

    model_counts = Counter()
    for circuit in circuits:
        poles = int(circuit["breaker_poles"])
        breaker = int(circuit["breaker_a"])
        if poles == 2:
            model_counts[f"rcbo_2p_{breaker}"] += 1
        if poles == 3:
            model_counts["proteccion_motor_3p"] += 1

    items: list[dict[str, Any]] = []
    counter = 1

    def add_item(group: str, item_id: str, description: str, unit: str, quantity: float, price: float, price_type: str, source: str = "") -> None:
        nonlocal counter
        quantity = round(float(quantity), 2)
        subtotal = round(quantity * float(price), 2)
        items.append({
            "orden": counter,
            "grupo": group,
            "id": item_id,
            "descripcion": description,
            "unidad": unit,
            "cantidad": quantity,
            "precio_unitario": round(float(price), 2),
            "subtotal": subtotal,
            "tipo_precio": price_type,
            "fuente": source,
        })
        counter += 1

    for item_id, quantity in sorted(routes.items()):
        row = catalog[item_id]
        add_item("02 Canalizaciones", item_id, row["descripcion"], row["unidad"], quantity, row["precio_unitario"], row["tipo_precio"], row.get("fuente", ""))
    for item_id, quantity in sorted(cables.items(), key=lambda pair: float(pair[0].split("-")[1])):
        row = catalog[item_id]
        add_item("03 Conductores", item_id, row["descripcion"], row["unidad"], quantity, row["precio_unitario"], row["tipo_precio"], row.get("fuente", ""))
    for raw in budget["partidas_fijas"]:
        quantity = raw.get("cantidad")
        if quantity is None:
            quantity = model_counts[str(raw["cantidad_desde_modelo"])]
        add_item(raw["grupo"], raw["id"], raw["descripcion"], raw["unidad"], quantity, raw["precio_unitario"], raw["tipo_precio"], raw.get("fuente", ""))

    items.sort(key=lambda row: (row["grupo"], row["orden"]))
    direct_cost = round(sum(row["subtotal"] for row in items), 2)
    general_cost = round(direct_cost * float(factors["gastos_generales_pct"]) / 100.0, 2)
    utility = round(direct_cost * float(factors["utilidad_pct"]) / 100.0, 2)
    subtotal_before_tax = round(direct_cost + general_cost + utility, 2)
    igv = round(subtotal_before_tax * float(factors["igv_pct"]) / 100.0, 2)
    total = round(subtotal_before_tax + igv, 2)
    by_group: defaultdict[str, float] = defaultdict(float)
    for row in items:
        by_group[row["grupo"]] += row["subtotal"]

    return {
        "schema_version": 1,
        "status": "PASS" if items and direct_cost > 0 else "FAIL",
        "fecha_base": budget["fecha_base"],
        "moneda": budget["moneda"],
        "estado": budget["estado"],
        "scope": budget["alcance"],
        "assumptions": {
            "route_factor": route_factor,
            "cable_factor": cable_factor,
            "circuits_count": len(circuits),
            "design_route_length_m": sum(float(c["length_m"]) for c in circuits),
            "feeders_route_length_m": sum(float(f["length_m"]) for f in loads["feeders"]),
        },
        "model_counts": dict(model_counts),
        "items": items,
        "summary_by_group": {key: round(value, 2) for key, value in sorted(by_group.items())},
        "totals": {
            "direct_cost": direct_cost,
            "general_cost_pct": float(factors["gastos_generales_pct"]),
            "general_cost": general_cost,
            "utility_pct": float(factors["utilidad_pct"]),
            "utility": utility,
            "subtotal_before_tax": subtotal_before_tax,
            "igv_pct": float(factors["igv_pct"]),
            "igv": igv,
            "total": total,
        },
        "web_sources": budget.get("fuentes_web", []),
    }


def write_outputs(result: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "resumen-metrados-presupuesto.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    columns = ["grupo", "id", "descripcion", "unidad", "cantidad", "precio_unitario", "subtotal", "tipo_precio", "fuente"]
    with (output / "metrados-presupuesto.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(result["items"])

    totals = result["totals"]
    lines = [
        "# Metrados y presupuesto referencial", "",
        f"Estado: **{result['status']}**. Fecha base: {result['fecha_base']}. Moneda: {result['moneda']}.", "",
        "> Es un presupuesto academico de anteproyecto, no una cotizacion ni una autorizacion de compra.", "",
        "| Grupo | Parcial (S/) |", "|---|---:|",
    ]
    lines.extend(f"| {group} | {value:,.2f} |" for group, value in result["summary_by_group"].items())
    lines.extend([
        "", "## Resumen", "",
        f"- Costo directo: S/ {totals['direct_cost']:,.2f}",
        f"- Gastos generales ({totals['general_cost_pct']:.0f}%): S/ {totals['general_cost']:,.2f}",
        f"- Utilidad ({totals['utility_pct']:.0f}%): S/ {totals['utility']:,.2f}",
        f"- IGV ({totals['igv_pct']:.0f}%): S/ {totals['igv']:,.2f}",
        f"- **Total referencial: S/ {totals['total']:,.2f}**", "",
        "## Alcance y limites", "",
        f"Incluye: {result['scope']['incluye']}.", "",
    ])
    lines.extend(f"- Excluye: {item}." for item in result["scope"]["excluye"])
    (output / "memoria-metrados-presupuesto.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    root = repository_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loads", type=Path, default=root / "proyectos/unidad-2-industrial/diseno-electrico/datos/cargas.yaml")
    parser.add_argument("--budget", type=Path, default=root / "proyectos/unidad-2-industrial/presupuesto/datos/partidas.yaml")
    parser.add_argument("--output", type=Path, default=root / "build/unidad-2-industrial/presupuesto")
    args = parser.parse_args()
    loads = yaml.safe_load(args.loads.read_text(encoding="utf-8"))
    budget = yaml.safe_load(args.budget.read_text(encoding="utf-8"))
    result = calculate(loads, budget)
    if result["status"] != "PASS":
        raise SystemExit("No se pudo cerrar metrados/presupuesto")
    write_outputs(result, args.output.resolve())
    print(f"Metrados y presupuesto generados en {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
