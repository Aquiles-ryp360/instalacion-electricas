#!/usr/bin/env python3
import argparse
import csv
import json
import os

BOM_TEMPLATE = {
    "tuberias": [
        {"codigo": "TUB-01", "descripcion": "Tuberia PVC Liviana 3/4\" para alumbrado",
         "unidad": "m", "cantidad": 120, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "PVC liviano empotrado en techo"},
        {"codigo": "TUB-02", "descripcion": "Tuberia PVC Pesada 3/4\" para tomacorrientes",
         "unidad": "m", "cantidad": 150, "circuitos": ["C2", "C3", "C5", "C7", "C8"],
         "especificacion": "PVC pesado empotrado en muro"},
        {"codigo": "TUB-03", "descripcion": "Tuberia PVC Pesada 1\" para alimentador",
         "unidad": "m", "cantidad": 25, "circuitos": ["ALIM"],
         "especificacion": "Alimentador principal"},
    ],
    "conductores": [
        {"codigo": "CON-01", "descripcion": "Conductor LSOH 1.5 mm2 fase+neutro",
         "unidad": "m", "cantidad": 240, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "Cobre unipolar 1.5 mm2"},
        {"codigo": "CON-02", "descripcion": "Conductor LSOH 1.5 mm2 PE",
         "unidad": "m", "cantidad": 110, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "Cobre unipolar 1.5 mm2 verde/amarillo"},
        {"codigo": "CON-03", "descripcion": "Conductor LSOH 2.5 mm2 fase+neutro",
         "unidad": "m", "cantidad": 300, "circuitos": ["C2", "C3", "C5", "C7", "C8"],
         "especificacion": "Cobre unipolar 2.5 mm2"},
        {"codigo": "CON-04", "descripcion": "Conductor LSOH 2.5 mm2 PE",
         "unidad": "m", "cantidad": 150, "circuitos": ["C2", "C3", "C5", "C7", "C8"],
         "especificacion": "Cobre unipolar 2.5 mm2 verde/amarillo"},
        {"codigo": "CON-05", "descripcion": "Conductor LSOH 10 mm2 alimentador",
         "unidad": "m", "cantidad": 60, "circuitos": ["ALIM"],
         "especificacion": "Cobre unipolar 10 mm2"},
        {"codigo": "CON-06", "descripcion": "Conductor Cu desnudo 6 mm2 PT",
         "unidad": "m", "cantidad": 25, "circuitos": ["PT"],
         "especificacion": "Cobre desnudo 6 mm2"},
    ],
    "cajas": [
        {"codigo": "CAJ-01", "descripcion": "Caja octogonal FG 4\" x 2\"",
         "unidad": "pza", "cantidad": 19, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "Fierro galvanizado"},
        {"codigo": "CAJ-02", "descripcion": "Caja rectangular FG 4\" x 2\"",
         "unidad": "pza", "cantidad": 45, "circuitos": ["C1-C8"],
         "especificacion": "Fierro galvanizado"},
        {"codigo": "CAJ-03", "descripcion": "Caja de pase rectangular 4\" x 2\"",
         "unidad": "pza", "cantidad": 6, "circuitos": ["GEN"],
         "especificacion": "Fierro galvanizado"},
    ],
    "tableros": [
        {"codigo": "TAB-01", "descripcion": "Tablero General TG-01 12 polos",
         "unidad": "u", "cantidad": 1, "circuitos": ["TG-01"],
         "especificacion": "Metalico empotrable equipado"},
        {"codigo": "TAB-02", "descripcion": "Tablero Distribucion TD-01 8 polos",
         "unidad": "u", "cantidad": 1, "circuitos": ["TD-01"],
         "especificacion": "Metalico empotrable equipado"},
        {"codigo": "TAB-03", "descripcion": "Tablero Distribucion TD-02 8 polos",
         "unidad": "u", "cantidad": 1, "circuitos": ["TD-02"],
         "especificacion": "Metalico empotrable equipado"},
    ],
    "accesorios": [
        {"codigo": "ACC-01", "descripcion": "Interruptor simple unipolar",
         "unidad": "pza", "cantidad": 6, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "Placa completa"},
        {"codigo": "ACC-02", "descripcion": "Interruptor conmutador S3",
         "unidad": "pza", "cantidad": 4, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "3 vias, placa completa"},
        {"codigo": "ACC-03", "descripcion": "Tomacorriente doble c/tierra 15A",
         "unidad": "pza", "cantidad": 24, "circuitos": ["C2", "C3", "C5", "C7"],
         "especificacion": "15A-250V placa completa"},
        {"codigo": "ACC-04", "descripcion": "Tomacorriente GFCI 15A-30mA",
         "unidad": "pza", "cantidad": 2, "circuitos": ["C5", "C7"],
         "especificacion": "Protegido para banos"},
        {"codigo": "ACC-05", "descripcion": "Tomacorriente servicio pesado 20A",
         "unidad": "pza", "cantidad": 3, "circuitos": ["C8", "C9"],
         "especificacion": "20A-250V"},
    ],
    "protecciones": [
        {"codigo": "PRO-01", "descripcion": "Interruptor termomagnetico 2P-10A",
         "unidad": "pza", "cantidad": 3, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "Curva C"},
        {"codigo": "PRO-02", "descripcion": "Interruptor termomagnetico 2P-16A",
         "unidad": "pza", "cantidad": 5, "circuitos": ["C2", "C5", "C7", "C8", "C9"],
         "especificacion": "Curva C"},
        {"codigo": "PRO-03", "descripcion": "Interruptor termomagnetico 2P-20A",
         "unidad": "pza", "cantidad": 1, "circuitos": ["C3"],
         "especificacion": "Curva C"},
        {"codigo": "PRO-04", "descripcion": "Interruptor termomagnetico general 2P-40A",
         "unidad": "pza", "cantidad": 1, "circuitos": ["TG"],
         "especificacion": "Curva C"},
        {"codigo": "PRO-05", "descripcion": "Interruptor diferencial 2P-25A-30mA",
         "unidad": "pza", "cantidad": 1, "circuitos": ["TG"],
         "especificacion": "Proteccion de personas"},
    ],
    "luminarias": [
        {"codigo": "LUM-01", "descripcion": "Luminaria LED interior 12W",
         "unidad": "pza", "cantidad": 19, "circuitos": ["C1", "C4", "C6"],
         "especificacion": "Panel LED"},
    ],
    "puesta_a_tierra": [
        {"codigo": "PAT-01", "descripcion": "Kit puesta a tierra completo",
         "unidad": "jgo", "cantidad": 1, "circuitos": ["PT"],
         "especificacion": "Varilla 5/8\"x2.40m + accesorios"},
    ],
    "varios": [
        {"codigo": "VAR-01", "descripcion": "Accesorios de instalacion",
         "unidad": "glb", "cantidad": 1, "circuitos": ["GEN"],
         "especificacion": "Curvas, uniones, conectores, cinta"},
    ],
}

def flatten_bom(bom):
    rows = []
    for category, items in bom.items():
        for item in items:
            rows.append({
                "categoria": category, "codigo": item["codigo"],
                "descripcion": item["descripcion"], "unidad": item["unidad"],
                "cantidad": item["cantidad"],
                "circuitos": ", ".join(item["circuitos"]),
                "especificacion": item["especificacion"],
            })
    return rows

def export_csv(rows, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["categoria","codigo","descripcion","unidad","cantidad","circuitos","especificacion"])
        writer.writeheader(); writer.writerows(rows)
    print(f"CSV: {filepath}")

def export_json(rows, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f"JSON: {filepath}")

def parse_args():
    p = argparse.ArgumentParser(description="Genera lista de materiales (BOM)")
    p.add_argument("--output-dir", default=".", help="Directorio de salida")
    p.add_argument("--format", choices=["json","csv","all"], default="all")
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    rows = flatten_bom(BOM_TEMPLATE)
    base = os.path.join(args.output_dir, "bom_instalacion_electrica")
    if args.format in ("json","all"): export_json(rows, base+".json")
    if args.format in ("csv","all"): export_csv(rows, base+".csv")
    print(f"BOM: {len(rows)} items en {len(BOM_TEMPLATE)} categorias")

if __name__ == "__main__":
    main()
