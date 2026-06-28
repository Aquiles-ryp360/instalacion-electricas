#!/usr/bin/env python3
"""Regenera los capitulos de metrado y presupuesto del Proyecto Renzo.

La fuente primaria para conteos de puntos es
``diseno-electrico/datos/modelo-electrico.json``. Los precios y codigos se
mantienen alineados con el cuadro de insumos validado contra catalogo.win.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
CAPITULOS_DIR = PROJECT_DIR / "expediente" / "capitulos"
MODELO_PATH = PROJECT_DIR / "diseno-electrico" / "datos" / "modelo-electrico.json"
METRADO_PATH = CAPITULOS_DIR / "06-metrado.tex"
PRESUPUESTO_PATH = CAPITULOS_DIR / "09-presupuesto.tex"


INSUMOS = [
    ("01.01", "Tuberia PVC SAP electrica D=20 mm (3/4 in) L=3 m para alumbrado", "und", 40, 6.75, "969800030540"),
    ("01.02", "Tuberia PVC SAP electrica D=20 mm (3/4 in) L=3 m para tomacorrientes", "und", 50, 6.75, "969800030540"),
    ("01.03", "Tuberia PVC SAP electrica D=25 mm (1 in) L=3 m para alimentador", "und", 9, 19.50, "969800031384"),
    ("02.01", "Conductor de cobre aislado LSOH 450/750 V 1.5 mm2", "m", 350, 1.65, "281600450640"),
    ("02.02", "Conductor de cobre aislado LSOH 450/750 V 2.5 mm2", "m", 480, 2.55, "281600450641"),
    ("02.03", "Conductor de cobre aislado LSOH 0.6/1 kV 10 mm2", "m", 30, 14.50, "281600450644"),
    ("03.01", "Caja octogonal galvanizada 4 x 2 in para salida de luz", "und", 19, 3.50, "283400010796"),
    ("03.02", "Caja rectangular galvanizada 4 x 2 in para interruptor y tomacorriente", "und", 40, 3.50, "283400010161"),
    ("04.01", "Tablero general metalico TG-01 12 polos equipado", "und", 1, 450.00, "462290890071"),
    ("04.02", "Tablero de distribucion metalico TD 8 polos equipado", "und", 2, 320.00, "952281740043"),
    ("05.01", "Interruptor termomagnetico 2P 40 A curva C 6 kA o superior", "und", 1, 42.90, "285000180299"),
    ("05.02", "Interruptor termomagnetico 2P 10 A para alumbrado", "und", 3, 38.50, "285000180309"),
    ("05.03", "Interruptor termomagnetico 2P 16 A para tomacorrientes", "und", 3, 39.00, "285000180297"),
    ("05.04", "Interruptor termomagnetico 2P 20 A para cocina", "und", 1, 39.90, "285000180298"),
    ("05.05", "Interruptor diferencial 2P 40 A 30 mA tipo AC", "und", 1, 160.60, "285000061084"),
    ("05.06", "Interruptor diferencial 2P 25 A 30 mA tipo AC", "und", 4, 145.00, "285000060817"),
    ("05.07", "Interruptor simple empotrable con placa", "und", 11, 12.00, "285000060186"),
    ("05.08", "Interruptor conmutado de 3 vias empotrable con placa", "und", 5, 15.00, "285000060010"),
    ("05.09", "Tomacorriente doble con puesta a tierra empotrable", "und", 22, 14.50, "285000100015"),
    ("05.10", "Tomacorriente protegido tipo GFCI / diferencial para bano", "und", 2, 45.00, "por verificar"),
    ("06.01", "Luminaria LED interior tipo panel / sobreponer 18 W aprox.", "und", 19, 28.00, "285400320060"),
    ("07.01", "Kit de pozo de puesta a tierra completo", "jgo", 1, 135.00, "por desagregar"),
    ("08.01", "Cinta aislante electrica PVC 19 mm x 18 m aprox.", "und", 5, 7.50, "070400190001"),
]


PARTIDAS = {
    "01": "TUBERIAS Y CANALIZACIONES",
    "02": "CONDUCTORES ELECTRICOS",
    "03": "CAJAS",
    "04": "TABLEROS",
    "05": "ACCESORIOS Y PROTECCIONES",
    "06": "LUMINARIAS",
    "07": "PUESTA A TIERRA",
    "08": "CONSUMIBLES",
}


def load_model() -> dict:
    return json.loads(MODELO_PATH.read_text(encoding="utf-8"))


def circuit_counts(model: dict) -> dict[str, dict[str, int | float | str]]:
    result = {
        c["id"]: {
            "uso": c["uso"],
            "luminarias": 0,
            "tomacorrientes": 0,
            "interruptores": 0,
            "longitud_m": 0.0,
        }
        for c in model["circuitos"]
    }
    for floor in model["floors"]:
        for key, target in (
            ("luminarias", "luminarias"),
            ("tomacorrientes", "tomacorrientes"),
            ("interruptores", "interruptores"),
        ):
            for item in floor.get(key, []):
                result[item["circuito"]][target] += 1
        for canalizacion in floor.get("canalizaciones", []):
            points = canalizacion["puntos"]
            length = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
            result[canalizacion["circuito"]]["longitud_m"] = round(length)
    return result


def model_totals(model: dict) -> dict[str, int | float]:
    totals = {"luminarias": 0, "interruptores": 0, "tomacorrientes": 0, "tableros": 0}
    for floor in model["floors"]:
        for key in totals:
            totals[key] += len(floor.get(key, []))
    totals.update(model["resumen"])
    return totals


def money(value: float) -> str:
    return f"{value:,.2f}"


def render_circuit_rows(counts: dict[str, dict[str, int | float | str]]) -> str:
    rows = []
    for circuit, data in counts.items():
        rows.append(
            f'{circuit} & {data["uso"]} & {data["luminarias"] or "--"} & '
            f'{data["tomacorrientes"] or "--"} & {data["interruptores"] or "--"} & '
            f'{data["longitud_m"]} \\\\'
        )
    totals = {
        "luminarias": sum(int(d["luminarias"]) for d in counts.values()),
        "tomacorrientes": sum(int(d["tomacorrientes"]) for d in counts.values()),
        "interruptores": sum(int(d["interruptores"]) for d in counts.values()),
        "longitud_m": sum(float(d["longitud_m"]) for d in counts.values()),
    }
    rows.append(
        "\\midrule\n"
        f'\\textbf{{Total}} & & \\textbf{{{totals["luminarias"]}}} & '
        f'\\textbf{{{totals["tomacorrientes"]}}} & '
        f'\\textbf{{{totals["interruptores"]}}} & '
        f'\\textbf{{{int(totals["longitud_m"])}}} \\\\'
    )
    return "\n".join(rows)


def render_insumo_rows(include_code: bool = False) -> str:
    rows = []
    for item, desc, unit, qty, price, code in INSUMOS:
        partial = qty * price
        if include_code:
            rows.append(
                f"{item} & {desc} & {unit} & {qty:g} & {money(price)} & "
                f"{money(partial)} & {code} \\\\"
            )
        else:
            rows.append(f"{item} & {desc} & {unit} & {qty:g} & {code} \\\\")
    return "\n".join(rows)


def render_budget_rows() -> str:
    rows = []
    current = None
    subtotal = 0.0
    for item, desc, unit, qty, price, _code in INSUMOS:
        partida = item.split(".")[0]
        if current != partida:
            if current is not None:
                rows.append(
                    f" & & & & & \\textbf{{Subtotal {current}}} & \\textbf{{{money(subtotal)}}} \\\\"
                )
                rows.append("\\midrule")
            current = partida
            subtotal = 0.0
            rows.append(f"\\multicolumn{{7}}{{l}}{{\\textbf{{{partida}.00 {PARTIDAS[partida]}}}}} \\\\")
        partial = qty * price
        subtotal += partial
        rows.append(
            f"{item} & {desc} & {unit} & {qty:g} & {money(price)} & {money(partial)} & \\\\"
        )
    rows.append(f" & & & & & \\textbf{{Subtotal {current}}} & \\textbf{{{money(subtotal)}}} \\\\")
    return "\n".join(rows)


def render_metrado(model: dict) -> str:
    counts = circuit_counts(model)
    totals = model_totals(model)
    circuit_rows = render_circuit_rows(counts)
    insumo_rows = render_insumo_rows()
    return rf"""\chapter{{METRADO}}

\section{{Alcance}}

El presente metrado cuantifica los materiales necesarios para la instalacion electrica interior de la vivienda unifamiliar de tres niveles, conforme a la sectorizacion de siete circuitos (C1 a C7) definida para el proyecto de Renzo Gabriel Mamani Galindo. Los puntos proceden del modelo electrico canonico y las cantidades de compra se mantienen alineadas con el cuadro de insumos validado.

Los metrados se agrupan por tuberias, conductores, cajas, tableros, accesorios, protecciones, luminarias y sistema de puesta a tierra.

\section{{Resumen de puntos electricos por circuito}}

\begin{{table}}[H]
\centering
\small
\caption{{Puntos electricos por circuito (Proyecto de Renzo)}}
\label{{tab:puntos-por-circuito}}
\begin{{tabularx}}{{\textwidth}}{{c L{{5.0cm}} c c c c}}
\toprule
\textbf{{Cto.}} & \textbf{{Uso}} & \textbf{{Luminarias}} & \textbf{{TCs}} & \textbf{{Interruptores}} & \textbf{{Long. modelo (m)}} \\
\midrule
{circuit_rows}
\bottomrule
\end{{tabularx}}
\end{{table}}

\section{{Metrado consolidado de insumos}}

\begin{{landscape}}
\begin{{longtable}}{{c L{{6.8cm}} c r L{{3.0cm}}}}
\caption{{Metrado consolidado de insumos electricos}}\label{{tab:resumen-metrados}}\\
\toprule
\textbf{{Item}} & \textbf{{Descripcion}} & \textbf{{Und.}} & \textbf{{Cant.}} & \textbf{{Codigo SIGA / catalogo.win}} \\
\midrule
\endfirsthead
\toprule
\textbf{{Item}} & \textbf{{Descripcion}} & \textbf{{Und.}} & \textbf{{Cant.}} & \textbf{{Codigo SIGA / catalogo.win}} \\
\midrule
\endhead
{insumo_rows}
\bottomrule
\end{{longtable}}
\end{{landscape}}

\section{{Resumen de cantidades fisicas}}

\begin{{table}}[H]
\centering
\small
\caption{{Resumen de puntos y equipos segun modelo canonico}}
\label{{tab:resumen-puntos-metrado}}
\begin{{tabularx}}{{\textwidth}}{{L{{5.0cm}} c Y}}
\toprule
\textbf{{Concepto}} & \textbf{{Cantidad}} & \textbf{{Fuente}} \\
\midrule
Luminarias & {totals["luminarias"]} & Modelo electrico canonico \\
Interruptores & {totals["interruptores"]} & Modelo electrico canonico \\
Tomacorrientes totales & {totals["tomacorrientes"]} & Modelo electrico canonico; incluye 2 tomacorrientes protegidos en banos \\
Tableros & {totals["tableros"]} & TG-01, TD-02 y TD-03 \\
Potencia instalada & {totals["potencia_instalada_w"] / 1000:.2f} kW & Cuadro de cargas canonico \\
Demanda maxima & {totals["demanda_maxima_w"] / 1000:.2f} kW & Cuadro de cargas canonico \\
\bottomrule
\end{{tabularx}}
\end{{table}}

\section{{Nota tecnica}}

Los metrados presentados son referenciales para expediente academico. Antes de compra o ejecucion deben verificarse recorridos reales, alturas de montaje, disponibilidad comercial y los dos items aun pendientes de decision formal en catalogo.win: tomacorriente protegido tipo GFCI y kit de pozo de puesta a tierra.
"""


def render_presupuesto(model: dict) -> str:
    material_total = sum(qty * price for _, _, _, qty, price, _ in INSUMOS)
    labor = round(material_total * 0.40, 2)
    subtotal = round(material_total + labor, 2)
    tax = round(subtotal * 0.18, 2)
    total = round(subtotal + tax, 2)
    budget_rows = render_budget_rows()
    price_rows = render_insumo_rows(include_code=True)

    return rf"""\chapter{{PRESUPUESTO ESTIMADO}}

\section{{Alcance}}

El presente presupuesto estima el costo referencial de los materiales, mano de obra e impuestos para la instalacion electrica interior de la vivienda unifamiliar de tres niveles. Los precios unitarios se alinean con el cuadro de insumos del requerimiento y con la validacion de codigos catalogo.win realizada el 2026-06-28.

\section{{Precios unitarios referenciales}}

\begin{{landscape}}
\begin{{longtable}}{{c L{{6.2cm}} c r R{{1.8cm}} R{{1.8cm}} L{{2.8cm}}}}
\caption{{Precios unitarios referenciales de materiales (Proyecto Renzo)}}\label{{tab:precios-unitarios}}\\
\toprule
\textbf{{Item}} & \textbf{{Descripcion}} & \textbf{{Und.}} & \textbf{{Cant.}} & \textbf{{P. Unit. (S/)}} & \textbf{{Parcial (S/)}} & \textbf{{Codigo}} \\
\midrule
\endfirsthead
\toprule
\textbf{{Item}} & \textbf{{Descripcion}} & \textbf{{Und.}} & \textbf{{Cant.}} & \textbf{{P. Unit. (S/)}} & \textbf{{Parcial (S/)}} & \textbf{{Codigo}} \\
\midrule
\endhead
{price_rows}
\bottomrule
\end{{longtable}}
\end{{landscape}}

\clearpage

\section{{Presupuesto general}}

\begin{{landscape}}
\begin{{longtable}}{{c L{{6.0cm}} c r R{{1.8cm}} R{{1.8cm}} R{{1.8cm}}}}
\caption{{Presupuesto general estimado (Proyecto Renzo)}}\label{{tab:presupuesto-general}}\\
\toprule
\textbf{{Item}} & \textbf{{Descripcion de partida / material}} & \textbf{{Und.}} & \textbf{{Cant.}} & \textbf{{P. Unit. (S/)}} & \textbf{{Parcial (S/)}} & \textbf{{Subtotal (S/)}} \\
\midrule
\endfirsthead
\toprule
\textbf{{Item}} & \textbf{{Descripcion de partida / material}} & \textbf{{Und.}} & \textbf{{Cant.}} & \textbf{{P. Unit. (S/)}} & \textbf{{Parcial (S/)}} & \textbf{{Subtotal (S/)}} \\
\midrule
\endhead
{budget_rows}
\midrule
\multicolumn{{6}}{{r}}{{\textbf{{VALOR TOTAL DE MATERIALES}}}} & \textbf{{{money(material_total)}}} \\
\multicolumn{{6}}{{r}}{{Mano de Obra (40\%)}} & \textbf{{{money(labor)}}} \\
\multicolumn{{6}}{{r}}{{\textbf{{SUBTOTAL GENERAL}}}} & \textbf{{{money(subtotal)}}} \\
\multicolumn{{6}}{{r}}{{Impuesto General a las Ventas (IGV 18\%)}} & \textbf{{{money(tax)}}} \\
\multicolumn{{6}}{{r}}{{\textbf{{PRESUPUESTO TOTAL GENERAL}}}} & \textbf{{{money(total)}}} \\
\bottomrule
\end{{longtable}}
\end{{landscape}}

\section{{Nota tecnica}}

Los costos presentados son referenciales. El tomacorriente protegido tipo GFCI y el kit de pozo de puesta a tierra mantienen estado de verificacion/desagregacion en catalogo.win, por lo que su compra requiere decision humana y cotizacion vigente.
"""


def main() -> None:
    model = load_model()
    METRADO_PATH.write_text(render_metrado(model), encoding="utf-8")
    PRESUPUESTO_PATH.write_text(render_presupuesto(model), encoding="utf-8")
    print(f"Updated: {METRADO_PATH}")
    print(f"Updated: {PRESUPUESTO_PATH}")


if __name__ == "__main__":
    main()
