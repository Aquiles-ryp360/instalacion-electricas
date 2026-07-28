#!/usr/bin/env python3
"""Genera BOM con precios de referencia para instalacion industrial."""
import json, sys
from pathlib import Path
from datetime import date

PRECIOS = {
    "Cable THW 50 mm2": 18.50, "Cable THW 10 mm2": 4.80, "Cable THW 6 mm2": 3.20,
    "Cable THW 4 mm2": 2.40, "Tuberia PVC SAP 65 mm": 12.00, "Tuberia PVC SAP 25 mm": 5.50,
    "Tuberia PVC SAP 20 mm": 4.00, "Tablero general 24 circuitos": 350.00,
    "Tablero fuerza 12 circuitos": 280.00, "Tablero iluminacion 8 circuitos": 180.00,
    "ITM tripolar 160A": 320.00, "ITM tripolar 100A": 210.00, "ITM tripolar 40A": 65.00,
    "ITM tripolar 30A": 55.00, "ITM tripolar 20A": 45.00, "ITM tripolar 16A": 42.00,
    "ITM bipolar 25A": 28.00, "ITM bipolar 20A": 25.00, "ITM bipolar 16A": 22.00,
    "Diferencial 4P-63A-300mA": 180.00, "Reles termicos": 45.00,
    "LED industrial 100W IP65": 85.00, "LED industrial 80W IP65": 72.00,
    "LED panel 60x60 40W": 55.00, "LED sobreponer 18W": 28.00,
    "Toma trifasica interlock 32A": 65.00, "Toma trifasica interlock 16A": 52.00,
    "Toma doble 16A + T": 12.00,
    "Varilla copperweld 5/8'' x 2.4m": 45.00, "Cable Cu desnudo 35 mm2": 15.00,
    "Conector bimetalico": 8.00, "Banco capacitores automatico 25kVAr": 850.00,
}

MATERIALES = [
    ("Canalizacion", [
        ("Cable THW 50 mm2", "m", 50), ("Cable THW 10 mm2", "m", 40),
        ("Cable THW 6 mm2", "m", 60), ("Cable THW 4 mm2", "m", 80),
        ("Tuberia PVC SAP 65 mm", "m", 20), ("Tuberia PVC SAP 25 mm", "m", 60),
        ("Tuberia PVC SAP 20 mm", "m", 40),
    ]),
    ("Tableros", [
        ("Tablero general 24 circuitos", "und", 1),
        ("Tablero fuerza 12 circuitos", "und", 1),
        ("Tablero iluminacion 8 circuitos", "und", 1),
    ]),
    ("Protecciones", [
        ("ITM tripolar 160A", "und", 1), ("ITM tripolar 100A", "und", 1),
        ("ITM tripolar 40A", "und", 1), ("ITM tripolar 30A", "und", 1),
        ("ITM tripolar 20A", "und", 1), ("ITM tripolar 16A", "und", 1),
        ("ITM bipolar 25A", "und", 1), ("ITM bipolar 20A", "und", 1),
        ("ITM bipolar 16A", "und", 1), ("Diferencial 4P-63A-300mA", "und", 1),
        ("Reles termicos", "und", 4),
    ]),
    ("Iluminacion", [
        ("LED industrial 100W IP65", "und", 16), ("LED industrial 80W IP65", "und", 8),
        ("LED panel 60x60 40W", "und", 8), ("LED sobreponer 18W", "und", 4),
    ]),
    ("Tomacorrientes", [
        ("Toma trifasica interlock 32A", "und", 1),
        ("Toma trifasica interlock 16A", "und", 1),
        ("Toma doble 16A + T", "und", 4),
    ]),
    ("Puesta a Tierra", [
        ("Varilla copperweld 5/8'' x 2.4m", "und", 4),
        ("Cable Cu desnudo 35 mm2", "m", 50), ("Conector bimetalico", "und", 8),
    ]),
    ("Compensacion FP", [
        ("Banco capacitores automatico 25kVAr", "und", 1),
    ]),
]

def main():
    total_general = 0
    items = []
    for categoria, mats in MATERIALES:
        subtotal = 0
        for nombre, unidad, cantidad in mats:
            pu = PRECIOS.get(nombre, 0)
            pt = pu * cantidad
            items.append({"categoria": categoria, "item": nombre, "unidad": unidad,
                          "cantidad": cantidad, "pu_soles": pu, "parcial_soles": pt})
            subtotal += pt
        total_general += subtotal

    bom = {"proyecto": "Instalaciones Electricas Industriales - Nave Industrial",
           "fecha": str(date.today()), "moneda": "Soles (PEN)",
           "estado": "ESTIMADO - VERIFICAR CON INGENIERO",
           "resumen": {"categorias": len(set(i["categoria"] for i in items)),
                       "items": len(items), "materiales": total_general,
                       "mano_obra": round(total_general * 0.35),
                       "total_estimado": round(total_general * 1.35)},
           "materiales": items}

    Path("build/nave-industrial/bom").mkdir(parents=True, exist_ok=True)

    with open("build/nave-industrial/bom/bom.json", "w") as f:
        json.dump(bom, f, indent=2, ensure_ascii=False)

    lines = [f"# BOM - {bom['proyecto']}", f"**Fecha:** {bom['fecha']}",
             f"**Estado:** {bom['estado']}", f"**Moneda:** {bom['moneda']}", "",
             "## Resumen", f"| Concepto | Monto (S/) |",
             "|---|---|", f"| Materiales | {total_general:,.0f} |",
             f"| Mano de obra (35%) | {round(total_general*0.35):,.0f} |",
             f"| **Total estimado** | **{round(total_general*1.35):,.0f}** |", "",
             "## Detalle", "", "| Categoria | Item | Und | Cant | P.U. (S/) | Parcial (S/) |",
             "|---|---|---:|---:|---:|---:|"]
    for i in items:
        lines.append(f"| {i['categoria']} | {i['item']} | {i['unidad']} | {i['cantidad']} | {i['pu_soles']:.0f} | {i['parcial_soles']:.0f} |")

    with open("build/nave-industrial/bom/bom.md", "w") as f:
        f.write("\n".join(lines))

    print(f"BOM generado en build/nave-industrial/bom/")
    print(f"  Materiales: S/ {total_general:,.0f}")
    print(f"  Total estimado: S/ {round(total_general*1.35):,.0f}")

if __name__ == "__main__":
    main()
