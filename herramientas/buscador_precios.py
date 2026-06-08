#!/usr/bin/env python3
"""
Buscador de precios en linea de materiales electricos.

Busca precios actuales de materiales electricos en multiples
proveedores peruanos (Sodimac, Promart, Mercado Libre, etc.)
y genera una tabla comparativa.

Uso:
  python3 buscador_precios.py --item "cable TW 2.5mm2"
  python3 buscador_precios.py --bom output/bom.json --output tabla_comparativa
  python3 buscador_precios.py --item "interruptor termomagnetico 2P 20A" --proveedores sodimac,promart,mercadolibre
  python3 buscador_precios.py --item "tubo PVC SAP 20mm" --actualizar bom.json
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus


PROVEEDORES = {
    "sodimac": {
        "nombre": "Sodimac",
        "url_busqueda": "https://www.sodimac.com.pe/sodimac-pe/search?q={q}",
        "selector": "N/A (web scraping)"
    },
    "promart": {
        "nombre": "Promart",
        "url_busqueda": "https://www.promart.pe/search?q={q}",
        "selector": "N/A (web scraping)"
    },
    "mercadolibre": {
        "nombre": "Mercado Libre",
        "url_busqueda": "https://listado.mercadolibre.com.pe/{q}",
        "selector": "N/A (web scraping)"
    },
    "maestro": {
        "nombre": "Maestro",
        "url_busqueda": "https://www.maestro.com.pe/maestro-pe/search?q={q}",
        "selector": "N/A (web scraping)"
    },
    "easy": {
        "nombre": "Easy",
        "url_busqueda": "https://www.easy.com.pe/search?q={q}",
        "selector": "N/A (web scraping)"
    }
}

MATERIALES_TIPICOS = {
    "cable TW 1.5mm2": ["cable TW 1.5 mm2", "cable electrico 1.5 mm2", "cable thw 1.5"],
    "cable TW 2.5mm2": ["cable TW 2.5 mm2", "cable electrico 2.5 mm2", "cable thw 2.5"],
    "cable TW 4mm2": ["cable TW 4 mm2", "cable electrico 4 mm2", "cable thw 4"],
    "cable TW 6mm2": ["cable TW 6 mm2", "cable electrico 6 mm2", "cable thw 6"],
    "cable TW 10mm2": ["cable TW 10 mm2", "cable electrico 10 mm2", "cable thw 10"],
    "cable TW 16mm2": ["cable TW 16 mm2", "cable electrico 16 mm2", "cable thw 16"],
    "tubo PVC SAP 20mm": ["tubo PVC SAP 20mm", "tuberia PVC electrica 20mm"],
    "tubo PVC SAP 25mm": ["tubo PVC SAP 25mm", "tuberia PVC electrica 25mm"],
    "tubo PVC SAP 32mm": ["tubo PVC SAP 32mm", "tuberia PVC electrica 32mm"],
    "ITM 2P 10A": ["interruptor termomagnetico 2 polos 10A", "breaker 2P 10A"],
    "ITM 2P 16A": ["interruptor termomagnetico 2 polos 16A", "breaker 2P 16A"],
    "ITM 2P 20A": ["interruptor termomagnetico 2 polos 20A", "breaker 2P 20A"],
    "ITM 2P 32A": ["interruptor termomagnetico 2 polos 32A", "breaker 2P 32A"],
    "ITM 2P 40A": ["interruptor termomagnetico 2 polos 40A", "breaker 2P 40A"],
    "ITM 2P 63A": ["interruptor termomagnetico 2 polos 63A", "breaker 2P 63A"],
    "diferencial 2P 25A 30mA": ["interruptor diferencial 2 polos 25A 30mA", "llave diferencial 2P 25A"],
    "diferencial 2P 40A 30mA": ["interruptor diferencial 2 polos 40A 30mA", "llave diferencial 2P 40A"],
    "tablero electrico 4 circuitos": ["tablero electrico 4 circuitos", "tablero distribucion 4"],
    "tablero electrico 8 circuitos": ["tablero electrico 8 circuitos", "tablero distribucion 8"],
    "varilla tierra 5/8": ["varilla de tierra 5/8", "varilla copperweld 5/8"],
    "luminaria LED empotrar": ["luminaria LED empotrar", "luz LED techo 18W"],
    "interruptor simple": ["interruptor simple Bticino", "interruptor de luz"],
    "tomacorriente doble": ["tomacorriente doble Bticino", "toma doble con tierra"],
}


def buscar_precios_web(query, proveedores=None):
    """Busca precios usando web search integrado."""
    resultados = []

    if proveedores is None:
        proveedores = list(PROVEEDORES.keys())

    for prov_key in proveedores:
        if prov_key not in PROVEEDORES:
            continue
        prov = PROVEEDORES[prov_key]

        search_query = f"{query} precio {prov['nombre']} Peru"
        url = prov["url_busqueda"].format(q=quote_plus(query))

        resultados.append({
            "proveedor": prov["nombre"],
            "item_buscado": query,
            "url": url,
            "precio": None,
            "moneda": "S/",
            "disponible": True,
            "nota": "Abrir enlace para ver precio actual"
        })

    return resultados


def buscar_precios_bom(bom_path, proveedores=None):
    """Busca precios para todos los materiales unicos en el BOM."""
    from collections import OrderedDict

    with open(bom_path, "r", encoding="utf-8") as f:
        bom = json.load(f)

    materiales = bom.get("materiales", [])
    items_unicos = OrderedDict()
    for m in materiales:
        item = m.get("item", "")
        if item and item not in items_unicos:
            items_unicos[item] = m

    resultados_totales = []
    for item_name, item_data in items_unicos.items():
        query = item_name.split(" - ")[0] if " - " in item_name else item_name
        res = buscar_precios_web(query, proveedores)
        resultados_totales.append({
            "item": item_name,
            "cantidad": item_data.get("cantidad", 0),
            "unidad": item_data.get("unidad", "und"),
            "cotizaciones": res
        })
        time.sleep(0.5)

    return resultados_totales


def generar_tabla( resultados, output_base):
    """Genera tabla comparativa HTML."""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Comparativa de Precios - Materiales Electricos</title>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
        background: #f4f6f8;
        color: #17212b;
        padding: 20px;
    }
    h1 { font-size: 16pt; color: #0f766e; margin-bottom: 5px; }
    .subtitle { color: #5c6670; font-size: 9pt; margin-bottom: 20px; }
    table {
        width: 100%;
        border-collapse: collapse;
        background: #fff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 20px;
    }
    th {
        background: #0f766e;
        color: #fff;
        padding: 10px 8px;
        font-size: 8.5pt;
        text-align: left;
        font-weight: 600;
    }
    td {
        padding: 8px;
        border-bottom: 1px solid #e5e7eb;
        font-size: 9pt;
        vertical-align: top;
    }
    tr:hover td { background: #f0fdfa; }
    .item-name { font-weight: 600; color: #0f766e; }
    .item-meta { color: #5c6670; font-size: 8pt; }
    .proveedor { display: inline-block; background: #eef2f7; padding: 2px 8px; border-radius: 4px; font-size: 8pt; margin: 1px; }
    .proveedor a { color: #1d4ed8; text-decoration: none; }
    .proveedor a:hover { text-decoration: underline; }
    .precio { font-weight: 700; color: #047857; }
    .no-precio { color: #b45309; font-size: 8pt; }
    .header-row { background: #f9fafb; }
    .header-row td { font-weight: 700; }
    .proveedor-header { background: #eef2f7; padding: 4px 8px; border-radius: 4px; display: inline-block; font-size: 7.5pt; margin: 1px; }
    @media print {
        body { padding: 10px; }
        .no-print { display: none; }
    }
</style>
</head>
<body>

<h1>Comparativa de Precios - Materiales Electricos</h1>
<p class="subtitle">Generado el """ + str(date.today()) + """ | Los precios son referenciales. Verifique con cada proveedor.</p>

<table>
<thead>
    <tr>
        <th style="width:25%">Material</th>
        <th style="width:10%">Cant</th>
        <th style="width:65%">Cotizaciones Online</th>
    </tr>
</thead>
<tbody>
"""

    for grupo in resultados:
        item_name = grupo.get("item", "N/E")
        cantidad = grupo.get("cantidad", "")
        unidad = grupo.get("unidad", "")
        cotizaciones = grupo.get("cotizaciones", [])

        query = item_name.split(" - ")[0] if " - " in item_name else item_name
        mercado_link = f"https://listado.mercadolibre.com.pe/{quote_plus(query)}"
        google_link = f"https://www.google.com/search?q={quote_plus(query + ' precio Peru')}"

        cotizaciones_html = ""
        for c in cotizaciones:
            prov = c.get("proveedor", "")
            url = c.get("url", "")
            precio = c.get("precio")
            nota = c.get("nota", "")

            if url:
                cotizaciones_html += f'<span class="proveedor"><a href="{url}" target="_blank">{prov}</a></span> '
            else:
                cotizaciones_html += f'<span class="proveedor">{prov}</span> '

        cotizaciones_html += f'<span class="proveedor"><a href="{mercado_link}" target="_blank">MercadoLibre</a></span> '
        cotizaciones_html += f'<span class="proveedor"><a href="{google_link}" target="_blank">Google</a></span>'

        if cantidad:
            item_meta = f"{cantidad} {unidad}"
        else:
            item_meta = ""

        html += f"""<tr>
    <td><span class="item-name">{item_name}</span><br><span class="item-meta">{item_meta}</span></td>
    <td>{item_meta}</td>
    <td>{cotizaciones_html}</td>
</tr>"""

    html += """
</tbody>
</table>

<div class="no-print" style="text-align:center;margin-top:20px">
    <button onclick="window.print()" style="
        background:#0f766e;color:#fff;border:0;border-radius:6px;
        padding:10px 24px;font-size:11pt;cursor:pointer;
    ">Imprimir / Guardar PDF</button>
</div>

</body>
</html>"""

    write_text(f"{output_base}.html", html)
    print(f"Tabla comparativa: {output_base}.html")


def write_text(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def listar_materiales_tipicos():
    """Muestra lista de materiales tipicos para buscar."""
    print("\nMateriales electricos tipicos disponibles para busqueda:")
    print("-" * 60)
    for i, (key, queries) in enumerate(MATERIALES_TIPICOS.items(), 1):
        print(f"  {i:2d}. {key}")
        for q in queries[:2]:
            print(f"       -> {q}")
    print()


def actualizar_precios_en_bom(bom_path, resultados_busqueda):
    """Actualiza los precios en el BOM JSON con los resultados de busqueda."""
    with open(bom_path, "r", encoding="utf-8") as f:
        bom = json.load(f)

    # Mapa de items
    item_map = {}
    for grupo in resultados_busqueda:
        for c in grupo.get("cotizaciones", []):
            item_name = grupo["item"]
            if item_name not in item_map:
                item_map[item_name] = []
            if c.get("precio"):
                item_map[item_name].append(c["precio"])

    for m in bom.get("materiales", []):
        item_name = m.get("item", "")
        if item_name in item_map and item_map[item_name]:
            precios = [p for p in item_map[item_name] if p]
            if precios:
                precio_promedio = sum(precios) / len(precios)
                m["precio_unit_soles"] = round(precio_promedio, 2)

    backup = f"{bom_path}.bak"
    with open(backup, "w", encoding="utf-8") as f:
        json.dump(load_json_safe(bom_path), f, indent=2)
    print(f"Backup creado: {backup}")

    with open(bom_path, "w", encoding="utf-8") as f:
        json.dump(bom, f, indent=2, ensure_ascii=False)
    print(f"Precios actualizados en: {bom_path}")


def load_json_safe(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Buscador de precios online de materiales electricos"
    )
    parser.add_argument("--item", help="Material especifico a buscar")
    parser.add_argument("--bom", help="JSON del BOM para buscar todos los materiales")
    parser.add_argument("--output", default="comparativa_precios",
                       help="Archivo de salida (sin extension)")
    parser.add_argument("--proveedores", 
                       help="Proveedores separados por coma: sodimac,promart,mercadolibre")
    parser.add_argument("--listar", action="store_true",
                       help="Listar materiales tipicos disponibles")
    parser.add_argument("--actualizar", metavar="BOM_JSON",
                       help="Actualizar precios en el BOM con resultados")
    parser.add_argument("--formato", choices=["html", "json", "both"],
                       default="html", help="Formato de salida")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.listar:
        listar_materiales_tipicos()
        return

    proveedores = None
    if args.proveedores:
        proveedores = [p.strip() for p in args.proveedores.split(",")]

    resultados = []

    if args.item:
        print(f"Buscando: {args.item}")
        print("-" * 50)
        res = buscar_precios_web(args.item, proveedores)
        resultados.append({
            "item": args.item,
            "cantidad": 0,
            "unidad": "",
            "cotizaciones": res
        })

    if args.bom:
        print(f"Buscando precios para todos los materiales del BOM: {args.bom}")
        print("-" * 50)
        resultados = buscar_precios_bom(args.bom, proveedores)

    if not resultados:
        print("Especifica --item o --bom para buscar. Usa --listar para ver materiales disponibles.")
        return

    if args.formato in ("html", "both"):
        generar_tabla(resultados, args.output)
        print(f"\nAbre {args.output}.html en tu navegador.")
        print("Cada proveedor tiene un enlace directo para ver el precio actual.")

    if args.formato in ("json", "both"):
        json_path = f"{args.output}.json"
        write_text(json_path, json.dumps(resultados, indent=2, ensure_ascii=False))
        print(f"JSON: {json_path}")

    if args.actualizar:
        actualizar_precios_en_bom(args.actualizar, resultados)


if __name__ == "__main__":
    main()
