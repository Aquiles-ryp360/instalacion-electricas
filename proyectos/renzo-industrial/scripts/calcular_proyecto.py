#!/usr/bin/env python3
"""Calcula cargas, fases, conductores, caidas y respaldo del grifo."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


# CNE-U Tabla 2, cobre XLPE/EPR 90 C, tres conductores cargados.
AMPACITY_A = {
    "B1": {1.5: 20, 2.5: 28, 4.0: 37, 6.0: 48, 10.0: 68, 16.0: 88, 25.0: 117, 35.0: 144, 50.0: 175},
    "D": {1.5: 22, 2.5: 29, 4.0: 37, 6.0: 46, 10.0: 61, 16.0: 79, 25.0: 101, 35.0: 122, 50.0: 144},
}

# CNE-U Tabla 16: maxima proteccion -> PE minimo de cobre.
PE_TABLE = [(20, 2.5), (30, 4.0), (40, 6.0), (60, 6.0), (100, 10.0), (200, 16.0), (300, 25.0)]

FEEDER_GROUPS = {
    "TDF": {"TDF"},
    "TD-A1": {"TD-A1"},
    "TDE": {"TDE", "UPS-FUEL", "UPS-IT"},
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pe_minimum(breaker_a: float) -> float:
    for limit, size in PE_TABLE:
        if breaker_a <= limit:
            return size
    raise ValueError(f"proteccion fuera del rango de Tabla 16: {breaker_a} A")


def merge_profiles(data: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = data.get("profiles", {})
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in data["circuits"]:
        profile_name = raw.get("profile")
        base = dict(profiles.get(profile_name, {}))
        base.update(raw)
        base.pop("profile", None)
        circuit_id = str(base["id"])
        if circuit_id in seen:
            raise ValueError(f"circuito duplicado: {circuit_id}")
        seen.add(circuit_id)
        result.append(base)
    return result


def apparent_power(circuit: dict[str, Any]) -> tuple[float, float]:
    pf = float(circuit["power_factor"])
    if not (0 < pf <= 1):
        raise ValueError(f"{circuit['id']}: factor de potencia invalido")
    if "installed_kva" in circuit:
        kva = float(circuit["installed_kva"])
        kw = kva * pf
    elif "installed_kw" in circuit:
        kw = float(circuit["installed_kw"])
        kva = kw / pf
    else:
        raise ValueError(f"{circuit['id']}: falta installed_kva o installed_kw")
    return kva, kw


def voltage_drop_percent(
    *, supply: str, voltage: float, current_a: float, pf: float, length_m: float, size_mm2: float, rho: float, x_ohm_km: float
) -> float:
    r_ohm_m = rho / size_mm2
    x_ohm_m = x_ohm_km / 1000.0
    sin_phi = math.sqrt(max(0.0, 1.0 - pf**2))
    impedance = r_ohm_m * pf + x_ohm_m * sin_phi
    factor = 2.0 if supply == "1P" else math.sqrt(3.0)
    drop_v = factor * length_m * current_a * impedance
    return 100.0 * drop_v / voltage


def phase_values(circuits: list[dict[str, Any]], *, demand: bool, panels: set[str] | None = None) -> dict[str, float]:
    phases = {"R": 0.0, "S": 0.0, "T": 0.0}
    for c in circuits:
        if panels is not None and c["panel"] not in panels:
            continue
        value = c["demand_kva"] if demand else c["installed_kva_calc"]
        if c["supply"] == "3P":
            for phase in phases:
                phases[phase] += value / 3.0
        else:
            phases[c["phase"]] += value
    return phases


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    system = data["system"]
    rules = data["calculation"]
    vll = float(system["line_to_line_v"])
    vln = float(system["line_to_neutral_v"])
    rho = float(rules["copper_resistivity_ohm_mm2_per_m_at_operating_temperature"])
    x_ohm_km = float(rules["cable_reactance_ohm_per_km"])
    branch_limit = float(rules["cne_voltage_drop_branch_percent_max"])
    total_limit = float(rules["cne_voltage_drop_total_percent_max"])
    minimum_size = float(rules["minimum_power_and_lighting_conductor_mm2"])

    circuits = merge_profiles(data)
    failures: list[str] = []
    warnings: list[str] = []

    for c in circuits:
        kva, kw = apparent_power(c)
        demand_factor = float(c["demand_factor"])
        if not (0 < demand_factor <= 1):
            failures.append(f"{c['id']}: factor de demanda fuera de 0..1")
        c["installed_kva_calc"] = kva
        c["installed_kw_calc"] = kw
        c["demand_kva"] = kva * demand_factor
        c["demand_kw"] = kw * demand_factor
        voltage = vln if c["supply"] == "1P" else vll
        connected_current = kva * 1000.0 / voltage
        if c["supply"] == "3P":
            connected_current /= math.sqrt(3.0)
        rated_current = float(c.get("rated_current_a", connected_current))
        conductor_factor = float(c.get("conductor_factor", 1.0))
        design_current = max(connected_current, rated_current) * conductor_factor
        c["connected_current_a"] = connected_current
        c["design_current_a"] = design_current

        method = str(c["method"])
        size = float(c["conductor_mm2"])
        derating = float(c["derating_factor"])
        if method not in AMPACITY_A or size not in AMPACITY_A[method]:
            failures.append(f"{c['id']}: falta capacidad CNE para {method}/{size} mm2")
            corrected_ampacity = 0.0
        else:
            corrected_ampacity = AMPACITY_A[method][size] * derating
        c["corrected_ampacity_a"] = corrected_ampacity

        if size < minimum_size:
            failures.append(f"{c['id']}: conductor {size} mm2 menor al minimo CNE {minimum_size} mm2")
        if design_current > corrected_ampacity + 1e-9:
            failures.append(f"{c['id']}: Ib diseno {design_current:.2f} A excede Iz corregida {corrected_ampacity:.2f} A")
        if float(c["breaker_a"]) > corrected_ampacity + 1e-9:
            failures.append(f"{c['id']}: interruptor {c['breaker_a']} A excede Iz corregida {corrected_ampacity:.2f} A")
        if float(c["breaker_a"]) + 1e-9 < design_current:
            failures.append(f"{c['id']}: interruptor {c['breaker_a']} A menor que Ib diseno {design_current:.2f} A")

        required_pe = pe_minimum(float(c["breaker_a"]))
        c["required_pe_mm2"] = required_pe
        if float(c["pe_mm2"]) + 1e-9 < required_pe:
            failures.append(f"{c['id']}: PE {c['pe_mm2']} mm2 menor que Tabla 16 ({required_pe} mm2)")

        vd = voltage_drop_percent(
            supply=c["supply"], voltage=voltage, current_a=connected_current,
            pf=float(c["power_factor"]), length_m=float(c["length_m"]),
            size_mm2=size, rho=rho, x_ohm_km=x_ohm_km,
        )
        c["branch_voltage_drop_percent"] = vd
        if vd > branch_limit + 1e-9:
            failures.append(f"{c['id']}: caida derivada {vd:.2f}% > {branch_limit:.2f}%")
        if int(c.get("rcd_ma", 0)) > 30 or int(c.get("rcd_ma", 0)) <= 0:
            failures.append(f"{c['id']}: proteccion diferencial no cumple umbral de 30 mA")

    installed_phases = phase_values(circuits, demand=False)
    demand_phases = phase_values(circuits, demand=True)
    installed_kva = sum(c["installed_kva_calc"] for c in circuits)
    demand_kva = sum(c["demand_kva"] for c in circuits)
    installed_kw = sum(c["installed_kw_calc"] for c in circuits)
    demand_kw = sum(c["demand_kw"] for c in circuits)
    average_phase = sum(demand_phases.values()) / 3.0
    phase_unbalance = 100.0 * (max(demand_phases.values()) - min(demand_phases.values())) / average_phase
    if phase_unbalance > float(rules["phase_unbalance_target_percent"]):
        failures.append(f"desbalance de fases {phase_unbalance:.2f}% supera objetivo")

    reserve_factor = float(system["reserve_factor"])
    service_design_kva = demand_kva * reserve_factor
    service_phase_current = max(demand_phases.values()) * reserve_factor * 1000.0 / vln
    if service_design_kva > float(system["service_capacity_kva"]) + 1e-9:
        failures.append("demanda con reserva excede capacidad de servicio propuesta")
    if service_phase_current > float(system["main_breaker_a"]) + 1e-9:
        failures.append("corriente de fase con reserva excede interruptor principal")

    main_size = float(system["main_feeder_phase_mm2"])
    main_ampacity = AMPACITY_A["D"][main_size] * float(rules["default_derating_factor"])
    if float(system["main_breaker_a"]) > main_ampacity:
        failures.append("interruptor principal excede ampacidad corregida del alimentador")
    main_vd = voltage_drop_percent(
        supply="1P", voltage=vln, current_a=service_phase_current, pf=0.90,
        length_m=float(system["main_feeder_length_m"]), size_mm2=main_size,
        rho=rho, x_ohm_km=x_ohm_km,
    )

    feeder_results: list[dict[str, Any]] = []
    feeder_drop_by_panel: dict[str, float] = {}
    for feeder in data["feeders"]:
        panel = feeder["panel"]
        panels = FEEDER_GROUPS[panel]
        phases = phase_values(circuits, demand=True, panels=panels)
        max_current = max(phases.values()) * 1000.0 / vln
        method = feeder["method"]
        size = float(feeder["phase_mm2"])
        ampacity = AMPACITY_A[method][size] * float(feeder["derating_factor"])
        breaker = float(feeder["breaker_a"])
        if max_current > breaker + 1e-9:
            failures.append(f"{feeder['id']}: corriente {max_current:.2f} A excede interruptor {breaker:.0f} A")
        if breaker > ampacity + 1e-9:
            failures.append(f"{feeder['id']}: interruptor excede Iz {ampacity:.2f} A")
        required_pe = pe_minimum(breaker)
        if float(feeder["pe_mm2"]) < required_pe:
            failures.append(f"{feeder['id']}: PE menor que Tabla 16")
        vd = voltage_drop_percent(
            supply="1P", voltage=vln, current_a=max_current, pf=0.90,
            length_m=float(feeder["length_m"]), size_mm2=size,
            rho=rho, x_ohm_km=x_ohm_km,
        )
        feeder_drop_by_panel[panel] = vd
        feeder_results.append({**feeder, "phase_demand_kva": phases, "max_phase_current_a": max_current, "corrected_ampacity_a": ampacity, "voltage_drop_percent": vd})

    panel_alias = {"UPS-FUEL": "TDE", "UPS-IT": "TDE"}
    for c in circuits:
        feeder_panel = panel_alias.get(c["panel"], c["panel"])
        total_vd = main_vd + feeder_drop_by_panel.get(feeder_panel, 0.0) + c["branch_voltage_drop_percent"]
        c["total_voltage_drop_percent"] = total_vd
        if total_vd > total_limit + 1e-9:
            failures.append(f"{c['id']}: caida total {total_vd:.2f}% > {total_limit:.2f}%")

    emergency = [c for c in circuits if bool(c["emergency"])]
    emergency_phases = phase_values(emergency, demand=True)
    emergency_running_kva = sum(c["demand_kva"] for c in emergency)
    emergency_motors = [c for c in emergency if bool(c.get("motor"))]
    largest_motor = max(emergency_motors, key=lambda c: c["installed_kva_calc"])
    generator = data["generator"]
    start_multiplier = float(generator["starting_multiplier_largest_STP"])
    starting_kva = emergency_running_kva - largest_motor["demand_kva"] + largest_motor["installed_kva_calc"] * start_multiplier
    starting_with_margin_kva = starting_kva * float(generator["design_margin"])
    altitude = float(generator["site_altitude_m"])
    start_altitude = float(generator["derating_start_altitude_m"])
    loss = max(0.0, (altitude - start_altitude) / 500.0 * float(generator["derating_percent_per_500m"]) / 100.0)
    altitude_factor = 1.0 - loss
    available_site_kva = float(generator["standby_kva_nameplate"]) * altitude_factor
    required_nameplate_kva = starting_with_margin_kva / altitude_factor
    generator_pass = available_site_kva + 1e-9 >= starting_with_margin_kva
    if not generator_pass:
        failures.append("grupo electrogeno no cubre arranque con margen y correccion de altitud")
    if (max(emergency_phases.values()) - min(emergency_phases.values())) / (sum(emergency_phases.values()) / 3.0) * 100.0 > 10.0:
        warnings.append("desbalance de cargas permanentes del grupo supera 10%; revisar reparto final")

    for ups in data["ups"]:
        kva = sum(c["installed_kva_calc"] for c in circuits if c["panel"] == ups["id"])
        if kva > float(ups["rating_kva"]):
            failures.append(f"{ups['id']}: carga {kva:.2f} kVA excede potencia UPS")

    return {
        "schema_version": 1,
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "installed_kw": installed_kw,
            "installed_kva": installed_kva,
            "maximum_demand_kw": demand_kw,
            "maximum_demand_kva": demand_kva,
            "service_design_kva_with_reserve": service_design_kva,
            "service_capacity_kva": float(system["service_capacity_kva"]),
            "phase_installed_kva": installed_phases,
            "phase_demand_kva": demand_phases,
            "phase_unbalance_percent": phase_unbalance,
            "maximum_phase_current_with_reserve_a": service_phase_current,
            "main_breaker_a": float(system["main_breaker_a"]),
            "main_corrected_ampacity_a": main_ampacity,
            "main_voltage_drop_percent": main_vd,
        },
        "generator": {
            "model_reference": generator["model_reference"],
            "emergency_running_kva": emergency_running_kva,
            "emergency_phase_kva": emergency_phases,
            "largest_starting_motor": largest_motor["id"],
            "starting_scenario_kva": starting_kva,
            "starting_with_margin_kva": starting_with_margin_kva,
            "altitude_factor": altitude_factor,
            "available_standby_kva_at_site": available_site_kva,
            "required_nameplate_kva": required_nameplate_kva,
            "selected_nameplate_kva": float(generator["standby_kva_nameplate"]),
            "pass": generator_pass,
        },
        "feeders": feeder_results,
        "circuits": circuits,
        "warnings": warnings,
        "failures": failures,
    }


def fmt(value: float) -> str:
    return f"{value:.2f}"


def write_outputs(result: dict[str, Any], source: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    payload = {"source": str(source), "source_sha256": sha256(source), **result}
    (output / "resumen-calculos.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    columns = ["id", "description", "panel", "phase", "supply", "installed_kw_calc", "installed_kva_calc", "demand_kva", "connected_current_a", "design_current_a", "breaker_a", "conductor_mm2", "pe_mm2", "corrected_ampacity_a", "branch_voltage_drop_percent", "total_voltage_drop_percent", "emergency", "source_state"]
    with (output / "cuadro-cargas.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(result["circuits"])

    s = result["summary"]
    g = result["generator"]
    lines = [
        "# Memoria de calculo reproducible", "",
        f"Estado automatico: **{result['status']}**.", "",
        "## Resumen de demanda", "",
        "| Magnitud | Resultado |", "|---|---:|",
        f"| Potencia instalada | {fmt(s['installed_kw'])} kW / {fmt(s['installed_kva'])} kVA |",
        f"| Maxima demanda | {fmt(s['maximum_demand_kw'])} kW / {fmt(s['maximum_demand_kva'])} kVA |",
        f"| Demanda con 20 % de reserva | {fmt(s['service_design_kva_with_reserve'])} kVA |",
        f"| Suministro propuesto | {fmt(s['service_capacity_kva'])} kVA |",
        f"| Corriente maxima de fase con reserva | {fmt(s['maximum_phase_current_with_reserve_a'])} A |",
        f"| Interruptor principal | {fmt(s['main_breaker_a'])} A, 4P |",
        f"| Desbalance de fases | {fmt(s['phase_unbalance_percent'])} % |",
        f"| Caida del alimentador principal | {fmt(s['main_voltage_drop_percent'])} % |", "",
        "## Grupo electrogeno", "",
        "| Magnitud | Resultado |", "|---|---:|",
        f"| Carga critica permanente | {fmt(g['emergency_running_kva'])} kVA |",
        f"| Escenario con arranque secuencial | {fmt(g['starting_scenario_kva'])} kVA |",
        f"| Escenario con margen | {fmt(g['starting_with_margin_kva'])} kVA |",
        f"| Factor de altitud adoptado | {fmt(g['altitude_factor'])} |",
        f"| Capacidad disponible a la altitud | {fmt(g['available_standby_kva_at_site'])} kVA |",
        f"| Grupo seleccionado | {fmt(g['selected_nameplate_kva'])} kVA standby |",
        f"| Verificacion | {'CUMPLE' if g['pass'] else 'NO CUMPLE'} |", "",
        "## Circuitos", "",
        "| ID | Tablero | Fase | kVA inst. | kVA MD | Ib diseno (A) | ITM (A) | Cu/PE (mm2) | dV ramal / total |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for c in result["circuits"]:
        lines.append(
            f"| {c['id']} | {c['panel']} | {c['phase']} | {fmt(c['installed_kva_calc'])} | {fmt(c['demand_kva'])} | {fmt(c['design_current_a'])} | {c['breaker_a']} | {c['conductor_mm2']}/{c['pe_mm2']} | {fmt(c['branch_voltage_drop_percent'])}% / {fmt(c['total_voltage_drop_percent'])}% |"
        )
    if result["warnings"]:
        lines.extend(["", "## Advertencias", ""] + [f"- {item}" for item in result["warnings"]])
    if result["failures"]:
        lines.extend(["", "## Fallas", ""] + [f"- {item}" for item in result["failures"]])
    lines.extend(["", "Los valores de catalogo deben sustituirse por placas antes de construir. La corriente de cortocircuito depende de la factibilidad de Electro Puno.", ""])
    (output / "memoria-calculo.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=root / "proyectos/renzo-industrial/diseno-electrico/datos/cargas.yaml")
    parser.add_argument("--output", type=Path, default=root / "build/renzo-industrial/calculos")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    try:
        result = calculate(data)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"ERROR DE ENTRADA: {exc}", file=sys.stderr)
        return 2
    write_outputs(result, args.input.resolve(), args.output.resolve())
    print(json.dumps({"status": result["status"], "summary": result["summary"], "generator": result["generator"], "failures": result["failures"]}, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
