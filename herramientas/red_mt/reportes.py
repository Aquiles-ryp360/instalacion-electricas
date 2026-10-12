"""Generacion de reportes Excel (metrados) y LaTeX (memoria)."""
import json
from pathlib import Path

import pandas as pd


def generar_reportes(resultados_dss, formato="excel", ruta_salida="build/reportes",
                     diagnosticos=None):
    """Crea planilla Excel de metrados y/o fuente LaTeX de memoria.

    formato: 'excel', 'latex' o 'ambos'.
    Retorna lista de rutas generadas.
    """
    ruta = Path(ruta_salida)
    ruta.mkdir(parents=True, exist_ok=True)
    generados = []

    if formato in ("excel", "ambos"):
        with pd.ExcelWriter(ruta / "metrados_flujo_carga.xlsx",
                            engine="openpyxl") as xls:
            pd.DataFrame.from_dict(
                {b: v for b, v in resultados_dss["voltajes"].items()},
                orient="index").rename_axis("nodo").to_excel(
                    xls, sheet_name="voltajes_pu")
            if resultados_dss.get("corrientes_tramos"):
                pd.DataFrame.from_dict(
                    resultados_dss["corrientes_tramos"],
                    orient="index").rename_axis("tramo").to_excel(
                        xls, sheet_name="corrientes_tramos")
            pd.DataFrame([resultados_dss.get("perdidas", {})]).to_excel(
                xls, sheet_name="perdidas", index=False)
            if diagnosticos:
                pd.DataFrame(diagnosticos.get("nodos_criticos", [])).to_excel(
                    xls, sheet_name="nodos_criticos", index=False)
        generados.append(str(ruta / "metrados_flujo_carga.xlsx"))

    if formato in ("latex", "ambos"):
        tex = _memoria_latex(resultados_dss, diagnosticos)
        (ruta / "memoria_flujo_carga.tex").write_text(tex, encoding="utf-8")
        generados.append(str(ruta / "memoria_flujo_carga.tex"))

    return generados


def _memoria_latex(resultados_dss, diagnosticos):
    perdidas = resultados_dss.get("perdidas", {})
    lineas = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{amsmath,booktabs}",
        r"\title{Memoria de Calculo -- Flujo de Carga en Media Tension}",
        r"\begin{document}",
        r"\maketitle",
        r"\section{Resultados de la simulacion OpenDSS}",
        r"\subsection{Pérdidas}",
        f"Pérdidas totales: ${perdidas.get('kw')}$ kW, "
        f"${perdidas.get('kvar')}$ kvar.",
        r"\subsection{Voltajes de nodo (por unidad)}",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Nodo & Fase 1 & Fase 2 & Fase 3 \\" ,
        r"\midrule",
    ]
    for bus, fases in resultados_dss.get("voltajes", {}).items():
        vals = [fases.get(f"fase_{i}_pu") for i in range(1, 4)]
        fila = " & ".join(str(v) if v is not None else "--" for v in vals)
        lineas.append(f"{bus} & {fila} \\\\")
    lineas += [r"\bottomrule", r"\end{tabular}"]
    if diagnosticos:
        lineas.append(r"\section{Diagnostico de nodos criticos}")
        lineas.append(
            f"Cumplimiento del limite de caída de tensión: "
            f"{'SI' if diagnosticos['cumplimiento'] else 'NO'}. "
            f"Nodos críticos: {diagnosticos['resumen']['n_nodos_criticos']}.")
    lineas += [r"\end{document}"]
    return "\n".join(lineas)
