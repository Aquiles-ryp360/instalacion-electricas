"""Colocación automática de postes aprobados en el corredor Capachica-Llachón.

Insume `datos/estructuras_aprobadas.csv`: lista de estructuras con diseño
aprobado, verificada en campo y autorizada por Electro Puno. Las PC/PN de
gabinete NO son insumo; usarlas inventaría datos de obra.

Esquema del CSV (encabezados exactos, coordenadas UTM EPSG:32719 en metros):

    id,codigo_gisem,segmento,progresiva_m,este_m,norte_m,utm,tipo_poste,armado,angulo_deflexion_grados,retenida,pat,observaciones

Convenciones de campos:
  - segmento: 1 a 4 (trazos del KML manual); progresiva_m monótona dentro
    de cada segmento.
  - tipo_poste: "CAC 12/300", "CAC 12/400", "CAC 13/400 BIPOSTE", ...
    Un registro con "BIPOSTE" o armado "SAB-1" dibuja el bloque SED_BIPOSTE.
  - retenida / pat: "R-1", "PAT-3", ... o "NINGUNA"/"NINGUNO" para omitir.

Salidas en `build/renzo-linea-primaria-capachica-llachon/colocacion_postes/`:
DXF con modelo georreferenciado en metros UTM (bloques a escala real) más
lámina A3 con símbolos a escala fija de legibilidad, y reporte JSON con
SHA-256 del CSV fuente. El script rehúsa sobrescribir salidas existentes.

Uso:
    python scripts/colocar_postes_automatico.py
    python scripts/colocar_postes_automatico.py --csv datos/estructuras_aprobadas.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import LineString, Point

from generar_entrega_rev4 import read_inputs

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = ROOT / "datos" / "estructuras_aprobadas.csv"
TEMPLATE_CSV = ROOT / "datos" / "estructuras_aprobadas_plantilla.csv"
OUT_DIR = ROOT / "build" / "renzo-linea-primaria-capachica-llachon" / "colocacion_postes"
DXF_NAME = "CL-01_POSTES_UTM19S_A3.dxf"
REPORT_NAME = "reporte_colocacion_postes.json"

REQUIRED_FIELDS = [
    "id", "codigo_gisem", "segmento", "progresiva_m", "este_m", "norte_m",
    "utm", "tipo_poste", "armado", "angulo_deflexion_grados", "retenida",
    "pat", "observaciones",
]
UTM_EAST_RANGE = (150_000.0, 850_000.0)
UTM_NORTH_RANGE = (7_500_000.0, 9_500_000.0)
EMPTY_VALUES = {"", "NINGUNA", "NINGUNO", "-", "N/A"}

LAYERS = [
    ("EJE_KML", 5), ("POSTES_APROBADOS", 1), ("PAT_TIERRA", 3),
    ("RETENIDAS_R1", 6), ("EQUIPOS_MT", 2), ("MARCO", 7), ("TEXT", 7),
]

PAPER_SYMBOL_SCALE = {
    "POSTE_CAC_PLANTA": 0.52,
    "PAT3_PLANTA": 0.50,
    "RETENIDA_R1": 0.35,
    "SED_BIPOSTE": 0.28,
}

MAP_X, MAP_Y, MAP_W, MAP_H = 14.0, 62.0, 258.0, 192.0
TABLE_X, TABLE_Y = 280.0, 254.0
ROW_STEP = 6.8
MAX_TABLE_ROWS = 30
MM = 72 / 25.4


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_estructuras(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(
            f"Falta la lista aprobada {path}. Copie {TEMPLATE_CSV} y completela "
            "con las estructuras validadas en campo y autorizadas por Electro Puno."
        )
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        faltantes = sorted(set(REQUIRED_FIELDS) - set(reader.fieldnames or []))
        if faltantes:
            raise ValueError(f"CSV incompleto; faltan columnas: {', '.join(faltantes)}")
        rows = list(reader)
    if not rows:
        raise ValueError("El CSV de estructuras aprobadas está vacío")
    vistos = set()
    for row in rows:
        identificador = row["id"].strip()
        if identificador in vistos:
            raise ValueError(f"ID duplicado: {identificador}")
        vistos.add(identificador)
        for columna in ("segmento", "progresiva_m", "este_m", "norte_m",
                        "angulo_deflexion_grados"):
            float(row[columna])
        if int(row["segmento"]) not in (1, 2, 3, 4):
            raise ValueError(f"Segmento fuera de 1-4 en {identificador}")
        este, norte = float(row["este_m"]), float(row["norte_m"])
        if not UTM_EAST_RANGE[0] <= este <= UTM_EAST_RANGE[1]:
            raise ValueError(f"Este fuera de rango UTM 19S en {identificador}: {este}")
        if not UTM_NORTH_RANGE[0] <= norte <= UTM_NORTH_RANGE[1]:
            raise ValueError(f"Norte fuera de rango UTM 19S en {identificador}: {norte}")
        if row["utm"].strip().upper() != "EPSG:32719":
            raise ValueError(f"utm debe ser EPSG:32719 en {identificador}")
        if not row["tipo_poste"].strip() or not row["armado"].strip():
            raise ValueError(f"tipo_poste y armado obligatorios en {identificador}")
        if not -180.0 <= float(row["angulo_deflexion_grados"]) <= 180.0:
            raise ValueError(f"Deflexión fuera de ±180° en {identificador}")
    por_segmento: dict[int, list[float]] = {}
    for row in rows:
        por_segmento.setdefault(int(row["segmento"]), []).append(float(row["progresiva_m"]))
    for segmento, progresivas in por_segmento.items():
        if progresivas != sorted(progresivas):
            raise ValueError(f"Progresivas no monótonas en el segmento {segmento}")
    return rows


def define_blocks(doc: ezdxf.EzDxf) -> None:
    if "POSTE_CAC_PLANTA" not in doc.blocks:
        blk = doc.blocks.new("POSTE_CAC_PLANTA")
        blk.add_circle((0, 0), 1.15, dxfattribs={"layer": "POSTES_APROBADOS"})
        blk.add_lwpolyline([(-1.55, 0), (1.55, 0)], dxfattribs={"layer": "POSTES_APROBADOS"})
        blk.add_lwpolyline([(0, -1.55), (0, 1.55)], dxfattribs={"layer": "POSTES_APROBADOS"})
    if "PAT3_PLANTA" not in doc.blocks:
        blk = doc.blocks.new("PAT3_PLANTA")
        for y, semi in ((0.0, 1.4), (-0.7, 1.0), (-1.35, 0.55)):
            blk.add_lwpolyline([(-semi, y), (semi, y)], dxfattribs={"layer": "PAT_TIERRA"})
    if "RETENIDA_R1" not in doc.blocks:
        blk = doc.blocks.new("RETENIDA_R1")
        blk.add_line((0, 0), (12.0, 12.0), dxfattribs={"layer": "RETENIDAS_R1"})
        blk.add_lwpolyline([(6.0, 7.4), (7.4, 6.0), (6.0, 4.6), (4.6, 6.0), (6.0, 7.4)],
                           dxfattribs={"layer": "RETENIDAS_R1"})
        blk.add_lwpolyline([(10.3, 10.3), (13.7, 10.3), (13.7, 13.7), (10.3, 13.7), (10.3, 10.3)],
                           dxfattribs={"layer": "RETENIDAS_R1"})
    if "SED_BIPOSTE" not in doc.blocks:
        blk = doc.blocks.new("SED_BIPOSTE")
        for x in (-2.5, 2.5):
            blk.add_circle((x, 0), 1.15, dxfattribs={"layer": "POSTES_APROBADOS"})
            blk.add_lwpolyline([(x - 1.55, 0), (x + 1.55, 0)], dxfattribs={"layer": "POSTES_APROBADOS"})
            blk.add_lwpolyline([(x, -1.55), (x, 1.55)], dxfattribs={"layer": "POSTES_APROBADOS"})
        for x in (-7.0, 7.0):
            blk.add_circle((x, 0), 3.5, dxfattribs={"layer": "EQUIPOS_MT"})
        blk.add_text("D", dxfattribs={"layer": "EQUIPOS_MT", "height": 1.8}).set_placement(
            (-7.0, 4.2), align=TextEntityAlignment.MIDDLE_CENTER)
        blk.add_text("Y", dxfattribs={"layer": "EQUIPOS_MT", "height": 1.8}).set_placement(
            (7.0, -5.4), align=TextEntityAlignment.MIDDLE_CENTER)


def bloques_para(row: dict) -> list[tuple[str, tuple[float, float], str]]:
    este, norte = float(row["este_m"]), float(row["norte_m"])
    salida: list[tuple[str, tuple[float, float], str]] = []
    if "BIPOSTE" in row["tipo_poste"].upper() or row["armado"].strip().upper() == "SAB-1":
        salida.append(("SED_BIPOSTE", (este, norte), "EQUIPOS_MT"))
    else:
        salida.append(("POSTE_CAC_PLANTA", (este, norte), "POSTES_APROBADOS"))
    if row["pat"].strip().upper() not in EMPTY_VALUES:
        salida.append(("PAT3_PLANTA", (este + 3.8, norte - 4.2), "PAT_TIERRA"))
    if row["retenida"].strip().upper() not in EMPTY_VALUES:
        salida.append(("RETENIDA_R1", (este, norte), "RETENIDAS_R1"))
    return salida


def _text(layout, x: float, y: float, value, height: float = 2.0, layer: str = "TEXT") -> None:
    layout.add_text(str(value), dxfattribs={"height": height, "layer": layer}).set_placement((x, y))


def _map_transform(points: list[tuple[float, float]]):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    dx, dy = max(xmax - xmin, 1.0), max(ymax - ymin, 1.0)
    scale = min((MAP_W - 16.0) / dx, (MAP_H - 16.0) / dy)
    ox = MAP_X + (MAP_W - dx * scale) / 2.0
    oy = MAP_Y + (MAP_H - dy * scale) / 2.0
    return lambda p: (ox + (p[0] - xmin) * scale, oy + (p[1] - ymin) * scale), scale, (xmin, xmax, ymin, ymax)


def _draw_paper(layout, estructuras: list[dict], lineas: list[list[tuple[float, float]]]) -> None:
    frame = [(8, 8), (412, 8), (412, 289), (8, 289), (8, 8)]
    layout.add_lwpolyline(frame, dxfattribs={"layer": "MARCO"})
    _text(layout, 14, 281, "CL-01-POST | Colocación automática de postes aprobados", 4.0)
    _text(layout, 14, 271,
          f"Fuente: datos/estructuras_aprobadas.csv | {len(estructuras)} estructuras | "
          "Modelo DXF en metros UTM EPSG:32719", 2.0)
    _text(layout, 14, 28, "ANTEPROYECTO ACADEMICO - VERIFICAR FIRMA DE INGENIERIA RESPONSABLE", 2.2)
    layout.add_lwpolyline([(MAP_X, MAP_Y), (MAP_X + MAP_W, MAP_Y), (MAP_X + MAP_W, MAP_Y + MAP_H),
                           (MAP_X, MAP_Y + MAP_H), (MAP_X, MAP_Y)], dxfattribs={"layer": "MARCO"})
    puntos = [p for linea in lineas for p in linea] + [
        (float(r["este_m"]), float(r["norte_m"])) for r in estructuras]
    transform, scale, limites = _map_transform(puntos)
    for linea in lineas:
        layout.add_lwpolyline([transform(p) for p in linea], dxfattribs={"layer": "EJE_KML"})
    colocados: list[tuple[float, float]] = []
    for row in estructuras:
        for nombre, punto, capa in bloques_para(row):
            px, py = transform(punto)
            layout.add_blockref(nombre, (px, py), dxfattribs={
                "layer": capa, "xscale": PAPER_SYMBOL_SCALE[nombre],
                "yscale": PAPER_SYMBOL_SCALE[nombre]})
        px, py = transform((float(row["este_m"]), float(row["norte_m"])))
        if all(((px - qx) ** 2 + (py - qy) ** 2) ** 0.5 > 13.0 for qx, qy in colocados):
            _text(layout, px + 1.4, py + 1.0, row["id"], 1.5)
            colocados.append((px, py))
    _text(layout, MAP_X + MAP_W - 13, MAP_Y + MAP_H - 10, "N", 3.0)
    layout.add_line((MAP_X + MAP_W - 10, MAP_Y + MAP_H - 13),
                    (MAP_X + MAP_W - 10, MAP_Y + MAP_H - 22), dxfattribs={"layer": "MARCO"})
    layout.add_line((MAP_X + MAP_W - 10, MAP_Y + MAP_H - 13),
                    (MAP_X + MAP_W - 12, MAP_Y + MAP_H - 17), dxfattribs={"layer": "MARCO"})
    layout.add_line((MAP_X + MAP_W - 10, MAP_Y + MAP_H - 13),
                    (MAP_X + MAP_W - 8, MAP_Y + MAP_H - 17), dxfattribs={"layer": "MARCO"})
    extent = max(limites[1] - limites[0], limites[3] - limites[2])
    objetivo = extent / 5.0
    exponente = 10 ** math.floor(math.log10(objetivo))
    longitud = max(exponente, round(objetivo / exponente) * exponente)
    barra = longitud * scale
    if barra > MAP_W * 0.35:
        longitud /= 2.0
        barra = longitud * scale
    bx, by = MAP_X + 8.0, MAP_Y + 8.0
    layout.add_line((bx, by), (bx + barra, by), dxfattribs={"layer": "MARCO"})
    _text(layout, bx, by + 2.0, f"{longitud:g} m", 1.6)
    _text(layout, MAP_X + 3, MAP_Y + 2.0,
          f"E {limites[0]:.0f}-{limites[1]:.0f} m | N {limites[2]:.0f}-{limites[3]:.0f} m", 1.5)
    _text(layout, MAP_X + 3, MAP_Y + MAP_H - 7.0,
          "Símbolos a escala fija; eje a escala de corredor", 1.5)
    for j, (etiqueta, bloque) in enumerate([
            ("POSTE", "POSTE_CAC_PLANTA"), ("PAT", "PAT3_PLANTA"),
            ("RETENIDA", "RETENIDA_R1"), ("SED", "SED_BIPOSTE")]):
        lx, ly = MAP_X + 6.0 + j * 44.0, MAP_Y + MAP_H - 14.0
        _text(layout, lx, ly, etiqueta, 1.6)
        layout.add_blockref(bloque, (lx + 14.0, ly + 0.7), dxfattribs={
            "layer": "TEXT", "xscale": PAPER_SYMBOL_SCALE[bloque],
            "yscale": PAPER_SYMBOL_SCALE[bloque]})
    _text(layout, TABLE_X, TABLE_Y, "CUADRO DE ESTRUCTURAS APROBADAS", 2.4)
    yy = TABLE_Y - 5.0
    for etiqueta, dx in (("ID", 0), ("PK m", 34), ("E", 62), ("N", 88)):
        _text(layout, TABLE_X + dx, yy, etiqueta, 1.6)
    yy -= 4.0
    for row in estructuras[:MAX_TABLE_ROWS]:
        _text(layout, TABLE_X, yy, row["id"], 1.6)
        _text(layout, TABLE_X + 34, yy, f"{float(row['progresiva_m']):.0f}", 1.6)
        _text(layout, TABLE_X + 62, yy, f"{float(row['este_m']):.0f}", 1.6)
        _text(layout, TABLE_X + 88, yy, f"{float(row['norte_m']):.0f}", 1.6)
        _text(layout, TABLE_X, yy - 3.0,
              f"{row['tipo_poste']} | armado {row['armado']} | seg {int(row['segmento'])}", 1.3)
        yy -= ROW_STEP
    if len(estructuras) > MAX_TABLE_ROWS:
        _text(layout, TABLE_X, yy, f"+{len(estructuras) - MAX_TABLE_ROWS} registros más en el CSV", 1.4)
    _text(layout, TABLE_X, 40.0, "Coordenadas UTM EPSG:32719; PK por segmento KML.", 1.4)
    _text(layout, TABLE_X, 34.0, "Bloques reutilizables: INSERT editables en AutoCAD.", 1.4)


def generate(source_csv: Path, output: Path) -> dict:
    if (output / DXF_NAME).exists():
        raise FileExistsError(f"Ya existe {output / DXF_NAME}; archive antes de regenerar")
    estructuras = read_estructuras(source_csv)
    lineas = read_inputs()[0]
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    for nombre, aci in LAYERS:
        doc.layers.new(nombre, dxfattribs={"color": aci})
    define_blocks(doc)
    msp = doc.modelspace()
    for linea in lineas:
        msp.add_lwpolyline(linea, dxfattribs={"layer": "EJE_KML"})
    ejes = [LineString(linea) for linea in lineas]
    alertas = []
    for row in estructuras:
        este, norte = float(row["este_m"]), float(row["norte_m"])
        distancia = min(eje.distance(Point(este, norte)) for eje in ejes)
        if distancia > 50.0:
            alertas.append({"id": row["id"], "distancia_eje_m": round(distancia, 2)})
        for nombre, punto, capa in bloques_para(row):
            msp.add_blockref(nombre, punto, dxfattribs={"layer": capa})
    layout = doc.layouts.new("CL-01_POSTES_A3")
    layout.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
    _draw_paper(layout, estructuras, lineas)
    output.mkdir(parents=True, exist_ok=False)
    doc.saveas(output / DXF_NAME)
    usados: dict[str, int] = {}
    for row in estructuras:
        for nombre, _, _ in bloques_para(row):
            usados[nombre] = usados.get(nombre, 0) + 1
    este = [float(r["este_m"]) for r in estructuras]
    norte = [float(r["norte_m"]) for r in estructuras]
    reporte = {
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "csv_fuente": str(source_csv),
        "csv_sha256": sha(source_csv),
        "total_estructuras": len(estructuras),
        "por_segmento": {str(s): sum(1 for r in estructuras if int(r["segmento"]) == s)
                         for s in sorted({int(r["segmento"]) for r in estructuras})},
        "bloques_usados": usados,
        "con_pat": sum(1 for r in estructuras if r["pat"].strip().upper() not in EMPTY_VALUES),
        "con_retenida": sum(1 for r in estructuras
                            if r["retenida"].strip().upper() not in EMPTY_VALUES),
        "bbox_este_m": [min(este), max(este)],
        "bbox_norte_m": [min(norte), max(norte)],
        "alertas_lejanas_eje": alertas,
        "dxf": DXF_NAME,
        "advertencia": "Colocación automática de software; no sustituye revisión de ingeniería ni aprobación de obra",
    }
    (output / REPORT_NAME).write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")
    return reporte


def verify(output: Path, source_csv: Path) -> dict:
    doc = ezdxf.readfile(output / DXF_NAME)
    if doc.audit().has_errors or doc.header["$INSUNITS"] != 6:
        raise ValueError("DXF inválido: auditoría con errores o unidades incorrectas")
    if "CL-01_POSTES_A3" not in doc.layouts:
        raise ValueError("Falta la lámina A3 en el DXF")
    msp = doc.modelspace()
    eje = [e for e in msp if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "EJE_KML"]
    if len(eje) != 4:
        raise ValueError(f"Eje KML incompleto: {len(eje)} segmentos")
    estructuras = read_estructuras(source_csv)
    esperados: dict[str, list[tuple[float, float]]] = {}
    for row in estructuras:
        for nombre, punto, _ in bloques_para(row):
            esperados.setdefault(nombre, []).append(punto)
    inserts = [e for e in msp if e.dxftype() == "INSERT"]
    por_bloque: dict[str, list[tuple[float, float]]] = {}
    for entity in inserts:
        por_bloque.setdefault(entity.dxf.name, []).append(
            (round(entity.dxf.insert.x, 3), round(entity.dxf.insert.y, 3)))
    for nombre, puntos in esperados.items():
        actual = sorted(por_bloque.get(nombre, []))
        if actual != sorted((round(x, 3), round(y, 3)) for x, y in puntos):
            raise ValueError(f"Bloque {nombre}: coordenadas o conteo distinto del CSV")
    reporte = json.loads((output / REPORT_NAME).read_text(encoding="utf-8"))
    if reporte["csv_sha256"] != sha(source_csv) or reporte["total_estructuras"] != len(estructuras):
        raise ValueError("El reporte no coincide con el CSV fuente")
    return reporte


def main() -> None:
    parser = argparse.ArgumentParser(description="Coloca postes aprobados en DXF UTM 19S + lámina A3")
    parser.add_argument("--csv", type=Path, default=SOURCE_CSV,
                        help="CSV de estructuras aprobadas (esquema de la plantilla)")
    args = parser.parse_args()
    try:
        reporte = generate(args.csv, OUT_DIR)
    except (FileNotFoundError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"DXF: {OUT_DIR / DXF_NAME}")
    print(f"Estructuras colocadas: {reporte['total_estructuras']} | "
          f"bloques: {reporte['bloques_usados']}")
    if reporte["alertas_lejanas_eje"]:
        print(f"Alerta: {len(reporte['alertas_lejanas_eje'])} estructuras a >50 m del eje KML")


if __name__ == "__main__":
    main()
