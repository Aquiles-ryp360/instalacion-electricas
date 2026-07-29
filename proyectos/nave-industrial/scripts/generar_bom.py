#!/usr/bin/env python3
"""Genera BOM con precios de referencia para instalacion industrial 20x40m."""
import json, sys
from pathlib import Path
from datetime import date

PRECIOS = {
    "Cable N2XH 50 mm2": 22.00, "Cable N2XH 16 mm2": 8.50, "Cable N2XH 10 mm2": 5.50,
    "Cable N2XH 6 mm2": 3.80, "Cable N2XH 4 mm2": 2.80,
    "Bandeja portacables 200x50mm": 28.00, "Soporte suspensión bandeja": 12.00,
    "Tuberia PVC SAP 32 mm": 7.00, "Tuberia PVC SAP 25 mm": 5.50, "Tuberia PVC SAP 20 mm": 4.00,
    "Tablero general TGD 24 circuitos IP65": 480.00,
    "Tablero fuerza TF1 18 circuitos IP65": 380.00,
    "Tablero iluminacion TI1 12 circuitos IP65": 250.00,
    "ITM tripolar 100A": 250.00, "ITM tripolar 63A": 140.00,
    "ITM tripolar 40A": 65.00, "ITM tripolar 30A": 55.00,
    "ITM tripolar 25A": 50.00, "ITM tripolar 16A": 42.00,
    "ITM bipolar 25A": 28.00, "ITM bipolar 20A": 25.00, "ITM bipolar 16A": 22.00,
    "Diferencial 4P-63A-300mA sup.": 220.00, "Diferencial 4P-40A-300mA ret.": 180.00,
    "Diferencial 2P-25A-30mA": 65.00, "Diferencial 2P-20A-30mA": 55.00, "Diferencial 2P-16A-30mA": 48.00,
    "Guardamotor 14-20A": 95.00, "Guardamotor 20-25A": 105.00, "Guardamotor 63-80A": 160.00,
    "LED High-Bay 150W 5000K IP65": 135.00,
    "LED panel 60x60 40W 4000K": 55.00, "LED sobreponer 18W 4000K": 28.00,
    "Toma trifasica Stecker 32A 380V": 75.00,
    "Toma doble Shucko 16A 220V": 14.00,
    "Varilla copperweld 5/8'' x 2.4m": 45.00, "Cable Cu desnudo 35 mm2": 15.00,
    "Conector bimetalico": 8.00, "Caja registro PAT": 35.00,
    "Banco capacitores automatico 15kVAr 3 pasos": 680.00,
    "Contactor arranque estrella-delta 40A": 180.00,
    "Timer rele temporizador": 35.00,
}

MATERIALES = [
    ("Canalizacion y Bandejas", [
        ("Cable N2XH 50 mm2", "m", 60),
        ("Cable N2XH 16 mm2", "m", 40),
        ("Cable N2XH 10 mm2", "m", 30),
        ("Cable N2XH 6 mm2", "m", 80),
        ("Cable N2XH 4 mm2", "m", 100),
        ("Bandeja portacables 200x50mm", "m", 60),
        ("Soporte suspension bandeja", "und", 30),
        ("Tuberia PVC SAP 32 mm", "m", 30),
        ("Tuberia PVC SAP 25 mm", "m", 50),
        ("Tuberia PVC SAP 20 mm", "m", 60),
    ]),
    ("Tableros", [
        ("Tablero general TGD 24 circuitos IP65", "und", 1),
        ("Tablero fuerza TF1 18 circuitos IP65", "und", 1),
        ("Tablero iluminacion TI1 12 circuitos IP65", "und", 1),
    ]),
    ("Protecciones", [
        ("ITM tripolar 100A", "und", 1),
        ("ITM tripolar 63A", "und", 2),
        ("ITM tripolar 40A", "und", 1),
        ("ITM tripolar 30A", "und", 1),
        ("ITM tripolar 25A", "und", 1),
        ("ITM tripolar 16A", "und", 2),
        ("ITM bipolar 25A", "und", 1),
        ("ITM bipolar 20A", "und", 1),
        ("ITM bipolar 16A", "und", 1),
        ("Diferencial 4P-63A-300mA sup.", "und", 1),
        ("Diferencial 4P-40A-300mA ret.", "und", 1),
        ("Diferencial 2P-25A-30mA", "und", 2),
        ("Diferencial 2P-20A-30mA", "und", 1),
        ("Diferencial 2P-16A-30mA", "und", 1),
        ("Guardamotor 14-20A", "und", 1),
        ("Guardamotor 20-25A", "und", 1),
        ("Guardamotor 63-80A", "und", 1),
    ]),
    ("Arranque Estrella-Delta", [
        ("Contactor arranque estrella-delta 40A", "und", 1),
        ("Timer rele temporizador", "und", 1),
    ]),
    ("Iluminacion", [
        ("LED High-Bay 150W 5000K IP65", "und", 20),
        ("LED panel 60x60 40W 4000K", "und", 10),
        ("LED sobreponer 18W 4000K", "und", 4),
    ]),
    ("Tomacorrientes", [
        ("Toma trifasica Stecker 32A 380V", "und", 4),
        ("Toma doble Shucko 16A 220V", "und", 8),
    ]),
    ("Puesta a Tierra", [
        ("Varilla copperweld 5/8'' x 2.4m", "und", 6),
        ("Cable Cu desnudo 35 mm2", "m", 80),
        ("Conector bimetalico", "und", 12),
        ("Caja registro PAT", "und", 2),
    ]),
    ("Compensacion FP", [
        ("Banco capacitores automatico 15kVAr 3 pasos", "und", 1),
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

    bom = {"proyecto": "Instalaciones Electricas Industriales - Nave 20x40m",
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
             "## Resumen", "| Concepto | Monto (S/) |",
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
