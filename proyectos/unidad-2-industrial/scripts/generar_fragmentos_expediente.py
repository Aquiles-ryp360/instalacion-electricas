#!/usr/bin/env python3
"""Genera fragmentos LaTeX del expediente desde los calculos canonicos."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def tex(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def command(name: str, value: Any, digits: int | None = None) -> str:
    if isinstance(value, float) and digits is not None:
        rendered = f"{value:.{digits}f}"
    else:
        rendered = str(value)
    return rf"\newcommand{{\{name}}}{{{tex(rendered)}}}"


def generate(calculation: dict[str, Any], lighting: dict[str, Any], budget: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    s = calculation["summary"]
    g = calculation["generator"]
    macros = [
        command("PotenciaInstaladaKW", s["installed_kw"], 2),
        command("PotenciaInstaladaKVA", s["installed_kva"], 2),
        command("MaximaDemandaKW", s["maximum_demand_kw"], 2),
        command("MaximaDemandaKVA", s["maximum_demand_kva"], 2),
        command("DemandaReservaKVA", s["service_design_kva_with_reserve"], 2),
        command("CorrienteMaximaA", s["maximum_phase_current_with_reserve_a"], 2),
        command("DesbalanceFases", s["phase_unbalance_percent"], 2),
        command("CaidaPrincipal", s["main_voltage_drop_percent"], 2),
        command("GrupoSeleccionadoKVA", g["selected_nameplate_kva"], 1),
        command("GrupoDisponibleKVA", g["available_standby_kva_at_site"], 2),
        command("GrupoArranqueKVA", g["starting_with_margin_kva"], 2),
        command("FactorAltitud", g["altitude_factor"], 4),
        command("EstadoCalculo", calculation["status"]),
        command("EstadoAlumbrado", lighting["status"]),
        command("EstadoPresupuesto", budget["status"]),
        command("CostoDirecto", f"{budget['totals']['direct_cost']:,.2f}"),
        command("PresupuestoTotal", f"{budget['totals']['total']:,.2f}"),
    ]
    (output / "datos.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")

    circuit_lines = [
        r"\begin{longtable}{@{}p{0.72cm}p{4.8cm}p{1.25cm}c r r r r@{}}",
        r"\toprule",
        r"ID & Descripcion & Tablero & Fase & MD kVA & ITM A & Cu/PE & $\Delta V$ total \\",
        r"\midrule\endfirsthead",
        r"\toprule ID & Descripcion & Tablero & Fase & MD kVA & ITM A & Cu/PE & $\Delta V$ total \\",
        r"\midrule\endhead",
    ]
    for row in calculation["circuits"]:
        circuit_lines.append(
            f"{tex(row['id'])} & {tex(row['description'])} & {tex(row['panel'])} & {tex(row['phase'])} & "
            f"{row['demand_kva']:.2f} & {float(row['breaker_a']):.0f} & "
            f"{float(row['conductor_mm2']):g}/{float(row['pe_mm2']):g} & {row['total_voltage_drop_percent']:.2f}\\% \\\\"
        )
    circuit_lines.extend([r"\bottomrule", r"\end{longtable}"])
    (output / "circuitos.tex").write_text("\n".join(circuit_lines) + "\n", encoding="utf-8")

    feeder_lines = [
        r"\begin{tabularx}{\textwidth}{@{}L r r r r@{}}",
        r"\toprule Alimentador & Ib (A) & ITM (A) & Iz corregida (A) & $\Delta V$ (\%) \\",
        r"\midrule",
    ]
    for row in calculation["feeders"]:
        feeder_lines.append(
            f"{tex(row['id'])} & {row['max_phase_current_a']:.2f} & {float(row['breaker_a']):.0f} & "
            f"{row['corrected_ampacity_a']:.2f} & {row['voltage_drop_percent']:.2f} \\\\"
        )
    feeder_lines.extend([r"\bottomrule", r"\end{tabularx}"])
    (output / "alimentadores.tex").write_text("\n".join(feeder_lines) + "\n", encoding="utf-8")

    lighting_lines = [
        r"\begin{tabularx}{\textwidth}{@{}p{1.6cm}L r r r@{}}",
        r"\toprule Zona & Descripcion & Objetivo (lx) & Calculado (lx) & Estado \\",
        r"\midrule",
    ]
    for zone in lighting["zones"]:
        lighting_lines.append(
            f"{tex(zone['id'])} & {tex(zone['description'])} & {float(zone['target_lux']):.0f} & "
            f"{zone['average_lux']:.1f} & {'CUMPLE' if zone['pass'] else 'NO CUMPLE'} \\\\"
        )
    lighting_lines.extend([r"\bottomrule", r"\end{tabularx}"])
    (output / "alumbrado.tex").write_text("\n".join(lighting_lines) + "\n", encoding="utf-8")

    budget_lines = [
        r"\begin{longtable}{@{}p{1.15cm}p{7.0cm}p{0.85cm}r r r@{}}",
        r"\toprule",
        r"Item & Descripcion & Und. & Cantidad & P.U. S/ & Parcial S/ \\",
        r"\midrule\endfirsthead",
        r"\toprule Item & Descripcion & Und. & Cantidad & P.U. S/ & Parcial S/ \\",
        r"\midrule\endhead",
    ]
    current_group = None
    for row in budget["items"]:
        if row["grupo"] != current_group:
            current_group = row["grupo"]
            budget_lines.append(rf"\multicolumn{{6}}{{l}}{{\textbf{{{tex(current_group)}}}}} \\")
        budget_lines.append(
            f"{tex(row['id'])} & {tex(row['descripcion'])} & {tex(row['unidad'])} & "
            f"{row['cantidad']:,.2f} & {row['precio_unitario']:,.2f} & {row['subtotal']:,.2f} \\\\"
        )
    totals = budget["totals"]
    budget_lines.extend([
        r"\midrule",
        rf"\multicolumn{{5}}{{r}}{{Costo directo}} & {totals['direct_cost']:,.2f} \\",
        rf"\multicolumn{{5}}{{r}}{{Gastos generales ({totals['general_cost_pct']:.0f}\%)}} & {totals['general_cost']:,.2f} \\",
        rf"\multicolumn{{5}}{{r}}{{Utilidad ({totals['utility_pct']:.0f}\%)}} & {totals['utility']:,.2f} \\",
        rf"\multicolumn{{5}}{{r}}{{IGV ({totals['igv_pct']:.0f}\%)}} & {totals['igv']:,.2f} \\",
        rf"\multicolumn{{5}}{{r}}{{\textbf{{TOTAL REFERENCIAL}}}} & \textbf{{{totals['total']:,.2f}}} \\",
        r"\bottomrule",
        r"\end{longtable}",
    ])
    (output / "metrados-presupuesto.tex").write_text("\n".join(budget_lines) + "\n", encoding="utf-8")


def main() -> int:
    root = repository_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calculation", type=Path, default=root / "build/unidad-2-industrial/calculos/resumen-calculos.json")
    parser.add_argument("--lighting", type=Path, default=root / "build/unidad-2-industrial/calculos/resumen-alumbrado.json")
    parser.add_argument("--budget", type=Path, default=root / "build/unidad-2-industrial/presupuesto/resumen-metrados-presupuesto.json")
    parser.add_argument("--output", type=Path, default=root / "build/unidad-2-industrial/expediente/generated")
    args = parser.parse_args()
    calculation = json.loads(args.calculation.read_text(encoding="utf-8"))
    lighting = json.loads(args.lighting.read_text(encoding="utf-8"))
    budget = json.loads(args.budget.read_text(encoding="utf-8"))
    if calculation["status"] != "PASS" or lighting["status"] != "PASS" or budget["status"] != "PASS":
        raise SystemExit("Los calculos y el presupuesto deben estar en PASS antes de generar el expediente")
    generate(calculation, lighting, budget, args.output.resolve())
    print(f"Fragmentos generados en {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
