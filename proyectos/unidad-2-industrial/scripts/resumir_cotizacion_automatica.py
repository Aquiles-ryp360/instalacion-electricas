#!/usr/bin/env python3
"""Resume la salida JSON del cotizador v1 en formatos legibles por IA/humano."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def latex_escape(value: Any) -> str:
    text = ("" if value is None else str(value)).replace("¨", " pulg")
    for old, new in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("$", r"\$")):
        text = text.replace(old, new)
    return text


def main() -> int:
    root = repository_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=root / "build/unidad-2-industrial/cotizaciones/promelsa.json")
    parser.add_argument("--output", type=Path, default=root / "build/unidad-2-industrial/cotizaciones")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    items = data.get("materiales", [])
    if not isinstance(items, list):
        raise SystemExit("La salida no contiene una lista 'materiales'")

    rows: list[dict[str, Any]] = []
    states: Counter[str] = Counter()
    for item in items:
        quote = item.get("cotizacion_promelsa") or {}
        state = str(quote.get("estado") or "SIN_EJECUTAR")
        states[state] += 1
        product = quote.get("producto") or {}
        selection = quote.get("seleccion") or {}
        rows.append({
            "codigo": item.get("codigo"),
            "consulta": item.get("item"),
            "estado": state,
            "producto": product.get("nombre"),
            "sku": product.get("sku"),
            "precio_soles": product.get("precio_soles"),
            "url": product.get("url"),
            "decision": selection.get("decision"),
            "requiere_revision": quote.get("requiere_revision", selection.get("requiere_revision", True)),
            "fecha_consulta": quote.get("fecha_consulta"),
            "mensaje": quote.get("mensaje"),
        })

    args.output.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0]) if rows else ["codigo", "estado"]
    with (args.output / "cotizacion-automatica-resumen.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Cotización automática trazable - Promelsa",
        "",
        "> Evidencia comercial de consulta. No es orden de compra ni reemplaza el precio instalado del presupuesto.",
        "",
        "## Estados",
        "",
    ]
    lines.extend(f"- {state}: {count}" for state, count in sorted(states.items()))
    lines.extend([
        "",
        "## Resultados",
        "",
        "| Código | Estado | Producto / mensaje | Precio visible | Revisión | URL |",
        "|---|---|---|---:|---|---|",
    ])
    for row in rows:
        product = row["producto"] or row["mensaje"] or "Sin selección"
        price = f"S/ {float(row['precio_soles']):,.2f}" if row["precio_soles"] is not None else "--"
        url = f"[ficha]({row['url']})" if row["url"] else "--"
        lines.append(f"| {row['codigo']} | {row['estado']} | {product} | {price} | {'sí' if row['requiere_revision'] else 'no'} | {url} |")
    lines.extend([
        "",
        "## Comando reproducible",
        "",
        "```bash",
        ".venv/bin/python herramientas/cotizacion/v1/cli/cotizar.py \\",
        "  --input build/unidad-2-industrial/cotizaciones/bom-cotizable.json \\",
        "  --output build/unidad-2-industrial/cotizaciones/promelsa.json \\",
        "  --modo heuristico --key item --no-actualizar-precio --workers 4",
        ".venv/bin/python proyectos/unidad-2-industrial/scripts/revalidar_cotizacion_automatica.py",
        ".venv/bin/python proyectos/unidad-2-industrial/scripts/resumir_cotizacion_automatica.py",
        "```",
    ])
    (args.output / "cotizacion-automatica-resumen.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    accepted = [row for row in rows if row["estado"] == "OK"]
    tex = [
        r"\section{Consulta automatica de mercado}",
        (
            f"El cotizador reproducible de Promelsa proceso {len(rows)} partidas de suministro: "
            f"{states.get('OK', 0)} quedaron con coincidencia trazable, "
            f"{states.get('SIN_SELECCION', 0)} sin seleccion segura y "
            f"{states.get('NO_ENCONTRADO', 0)} sin resultados. "
            "Las coincidencias mantienen revision humana y no sustituyen precios de partidas instaladas."
        ),
        "",
        r"\begin{tabularx}{\textwidth}{@{}p{1.45cm}Xr@{}}",
        r"\toprule",
        r"Codigo & Suministro comparable & Precio visible \\",
        r"\midrule",
    ]
    for row in accepted:
        tex.append(rf"{latex_escape(row['codigo'])} & {latex_escape(row['producto'])} & S/ {float(row['precio_soles']):,.2f} \\")
    tex.extend([
        r"\bottomrule",
        r"\end{tabularx}",
        "",
        r"\textit{Fuente: consulta automatica Promelsa registrada en JSON con URL, SKU, fecha, candidatos y criterios. Verificar vigencia, unidad comercial, flete y equivalencia antes de cotizar una compra.}",
        "",
    ])
    (args.output / "cotizacion-automatica.tex").write_text("\n".join(tex), encoding="utf-8")
    print(json.dumps({"status": "PASS", "items": len(rows), "states": states}, ensure_ascii=False, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
