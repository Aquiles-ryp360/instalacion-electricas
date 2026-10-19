#!/usr/bin/env python3
"""Control reproducible M01 + decisión R03 22,9 kV.

La fase R03 NO está validada para construcción. Esta herramienta verifica
cantidades canónicas, clasificación de apoyos, 3 escenarios eléctricos y
escribe un informe en carpeta NUEVA; nunca reescribe los entregables M01.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[2]
ROOT = P.parents[1]
sys.path.insert(0, str(P / "scripts/lp_r02"))
from metrados_componentes import medir

def obtener():
    r02 = json.loads((P / "revisiones/lp-r02/03-calculos/resultados.json").read_text(encoding="utf-8"))
    met = medir(r02)
    cfg = json.loads((P / "datos/lp-r03-229kv/escenario.json").read_text(encoding="utf-8"))
    datos = json.loads((P / "datos/lp-r03-229kv/resultados_referenciales_229kv.json").read_text(encoding="utf-8"))
    matriz_path = P / "documentacion/lp-r03-229kv/MATRIZ_111_ARMADOS_CAC_229KV.csv"
    with matriz_path.open(encoding="utf-8-sig", newline="") as f:
        matrix = list(csv.DictReader(f))
    return r02, met, cfg, datos, matrix

def validar():
    r02, m, cfg, datos, matrix = obtener()
    checks = []
    def check(key, observed, expected, tolerance=0):
        ok = (abs(observed-expected)<=tolerance if isinstance(observed,(int,float)) and
              isinstance(expected,(int,float)) else observed==expected)
        checks.append({"control":key, "observado":observed, "esperado":expected, "ok":bool(ok)})
    z = m["conductor"]
    check("tension_nominal_adoptada_kv", cfg.get("tension_nominal_linea_kv"), 22.9)
    check("aprobado_para_construccion", cfg.get("aprobado_para_construccion"), False)
    check("postes_m01", m["postes"], 111)
    check("vanos_r02", len(r02["vanos"]), 110)
    check("ramales_m01", m["ramales"], 160)
    check("tendido_terna_m", z["tendido_terna_m"], 20274.360891, 0.01)
    check("puentes_y_colas_m", z["puentes_provision_m"], 240)
    check("reserva_m", z["reserva_m"], 616)
    check("total_suministro_m", z["total_compra_estudio_m"], 21131)
    check("armados_m01_S", m["cuenta_armados"].get("CAC-S"), 30)
    check("armados_m01_A", m["cuenta_armados"].get("CAC-A"), 41)
    check("armados_m01_R", m["cuenta_armados"].get("CAC-R"), 38)
    check("armados_m01_T", m["cuenta_armados"].get("CAC-T"), 2)
    check("111_fichas_matriz", len(matrix), 111)
    check("IDs_matriz_unicos", len({p["poste"] for p in matrix}), 111)
    check("armados_matriz", dict(Counter(p["armado_m01"] for p in matrix)),
          {"CAC-S":30,"CAC-A":41,"CAC-R":38,"CAC-T":2})
    check("casos_22_9kv", len(datos["casos"]), 3)
    with (P/"revisiones/lp-r02/03-calculos/comparacion_tensiones.csv").open(
            encoding="utf-8-sig", newline="") as f:
        ref = [r for r in csv.DictReader(f) if abs(float(r["kV"])-22.9)<1e-9]
    check("referencia_electrica_22_9kv", len(ref), 3)
    for row in datos["casos"]:
        origin = next((x for x in ref if abs(float(x["toma_pu"])-row["fuente_pu"])<1e-9),None)
        if origin is None:
            checks.append({"control":"comparacion_r02","ok":False,"observado":"sin escenario", "esperado":row["fuente_pu"]})
            continue
        for field,prior in (("bt_v","BT_llegada_V"),("perdida_linea_kw","perdida_linea_kW"),
                             ("fuente_kw","P_generacion_kW")):
            check(f"{field}_{row['fuente_pu']}", float(row[field]),float(origin[prior]),0.00001)
    report = {
        "revision":"LP-R03-229KV",
        "base":"M01 de ga elrenzo/instalacion-electricas, commit f7c29c2".replace("ga elrenzo","gaelrenzo"),
        "modelo":"Sistema aislado, revisión académica",
        "aprobacion_ingenieria":False,
        "total_controles":len(checks),
        "controles_correctos":sum(c["ok"] for c in checks),
        "ok_cantidades_y_comparacion":all(c["ok"] for c in checks),
        "controles":checks,
        "advertencias":[
            "Los precios, transformadores y datos de campo siguen siendo hipótesis.",
            "R03 no dispone aún de armados CAC 22,9 kV certificados, protección y topografía verificados.",
            "No sustituir con una portada 22,9 kV las páginas históricas del expediente M01 a 10 kV.",
            "Las validaciones numéricas no son aprobación de ingeniería ni verificación visual de DWG."
        ]
    }
    return report

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--salida",required=True,type=Path)
    args=a.parse_args()
    target=args.salida.resolve()
    if target.exists(): raise FileExistsError(f"Utilizar carpeta nueva: {target}")
    report=validar()
    target.mkdir(parents=True)
    (target/"control_m01_r03.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Control cruzado M01 / R03 — 22,9 kV","",
        f"Controles: **{report['controles_correctos']} / {report['total_controles']}**.","",
        "| Control | Observado | ¿Conforme? |","| --- | --- | --- |"]
    for x in report["controles"]:
        lines.append(f"| {x['control']} | {x['observado']} | {'SÍ' if x['ok'] else 'NO'} |")
    lines += ["", "## Observaciones abiertas",""] + [f"- {x}" for x in report["advertencias"]]
    (target/"control_m01_r03.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"salida":str(target),"correctos":report["controles_correctos"],
                      "total":report["total_controles"],"ok":report["ok_cantidades_y_comparacion"]}))
    raise SystemExit(0 if report["ok_cantidades_y_comparacion"] else 1)
if __name__=="__main__":main()
