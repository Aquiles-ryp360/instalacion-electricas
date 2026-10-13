# -*- coding: utf-8 -*-
"""
Genera planos DXF A3 para AutoCAD del alcance exclusivo de linea primaria.

El paquete toma el estilo de los proyectos con mejor CAD del repositorio:
- capas tecnicas separadas;
- simbologia DGE vectorial;
- rotulo A3 trazable;
- leyendas y planillas dentro del plano;
- ningun desarrollo de redes secundarias, acometidas ni AP.
"""

from __future__ import annotations

import math
import os
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment

from generar_planos_ejecutivos_lp_capachica import (
    CAMINO_CAPACHICA_CHIFRON,
    ESTRUCTURAS_LP,
    VANOS_LP,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "entregables" / "planos" / "autocad_lp"
ZIP_PATH = ROOT / "entregables" / "planos" / "planos_autocad_linea_primaria_capachica.zip"

A3_W = 420.0
A3_H = 297.0
MARGIN = 8.0


LAYER_DEFS = {
    "00_MARCO_ROTULO": (colors.WHITE, 35),
    "01_EJE_LP_MT_229KV": (colors.BLUE, 50),
    "02_SERVIDUMBRE_MT": (30, 18),
    "03_POSTES_CAC_MT": (colors.CYAN, 35),
    "04_SED_SAB1": (colors.YELLOW, 35),
    "05_RETENIDAS_R1": (colors.MAGENTA, 30),
    "06_PAT3_TIERRA": (colors.GREEN, 30),
    "07_VIAS_REFERENCIA": (8, 18),
    "08_COTAS_DIMENSIONES": (colors.WHITE, 18),
    "09_TEXTOS": (colors.WHITE, 18),
    "10_TABLAS_LEYENDAS": (colors.WHITE, 18),
    "11_EQUIPOS_MT": (colors.RED, 30),
    "12_CONDUCTOR_AAAC": (colors.BLUE, 30),
    "13_AISLADORES": (colors.GREEN, 18),
    "14_CIMENTACION": (colors.CYAN, 25),
    "15_CRITICO_REVISION": (colors.RED, 50),
}


PLANOS = [
    ("LP-01", "LP-01_PLANTA_LINEA_PRIMARIA_A3_AUTOCAD.dxf", "PLANTA DE LINEA PRIMARIA 22.9 kV", "Traza, servidumbre, estructuras, retenidas y PAT-3", "1 : 2000"),
    ("PL-01", "PL-01_PERFIL_LONGITUDINAL_A3_AUTOCAD.dxf", "PERFIL LONGITUDINAL DE LINEA PRIMARIA", "Spotting, catenaria y galibos CNE", "H 1:2000 / V 1:500"),
    ("U-01", "U-01_DIAGRAMA_UNIFILAR_MT_A3_AUTOCAD.dxf", "DIAGRAMA UNIFILAR DE MEDIA TENSION", "Protecciones 22.9 kV, SED SAB-1 y limite de alcance", "Indicada"),
    ("D-01", "D-01_ARMADOS_PS1_PA1_A3_AUTOCAD.dxf", "ARMADOS NORMALIZADOS DGE PS-1 Y PA-1", "Suspension, angulo y retenida R-1", "1 : 25"),
    ("D-02", "D-02_ARMADOS_PR1_SAB1_A3_AUTOCAD.dxf", "ARMADOS NORMALIZADOS DGE PR-1 Y SAB-1", "Retencion, seccionamiento y SED biposte 100 kVA", "1 : 25"),
    ("D-03", "D-03_CIMENTACION_RETENIDA_PAT3_A3_AUTOCAD.dxf", "CIMENTACION, RETENIDA R-1 Y PAT-3", "Sulzberger, anclaje mecanico y puesta a tierra", "1 : 20"),
]


def ensure_layer(doc: ezdxf.EzDxf, name: str, color: int, lineweight: int = 18) -> None:
    if name not in doc.layers:
        doc.layers.new(name=name, dxfattribs={"color": color, "lineweight": lineweight})
    else:
        layer = doc.layers.get(name)
        layer.dxf.color = color
        layer.dxf.lineweight = lineweight


def new_doc() -> ezdxf.EzDxf:
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4  # millimeters
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 1.0
    for name, (color, lw) in LAYER_DEFS.items():
        ensure_layer(doc, name, color, lw)
    define_blocks(doc)
    return doc


def text(msp, value, x, y, h=2.5, layer="09_TEXTOS", align=TextEntityAlignment.LEFT, rot=0, color=None):
    value = str(value).replace("\\n", "\n")
    if "\n" in value:
        lines = value.splitlines()
        step = h * 1.25
        start_y = y + step * (len(lines) - 1) / 2
        last = None
        for i, line_value in enumerate(lines):
            last = text(msp, line_value, x, start_y - i * step, h=h, layer=layer, align=align, rot=rot, color=color)
        return last
    attrs = {"layer": layer, "height": h, "rotation": rot}
    if color is not None:
        attrs["color"] = color
    ent = msp.add_text(str(value), dxfattribs=attrs)
    ent.set_placement((x, y), align=align)
    return ent


def mtext_lines(msp, lines, x, y, h=2.3, layer="09_TEXTOS", leading=1.28, align=TextEntityAlignment.LEFT):
    for i, line in enumerate(lines):
        text(msp, line, x, y - i * h * leading, h=h, layer=layer, align=align)


def box(msp, x, y, w, h, layer="00_MARCO_ROTULO", color=None):
    attrs = {"layer": layer}
    if color is not None:
        attrs["color"] = color
    return msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], dxfattribs=attrs)


def line(msp, p1, p2, layer="00_MARCO_ROTULO", color=None, width=None):
    attrs = {"layer": layer}
    if color is not None:
        attrs["color"] = color
    ent = msp.add_line(p1, p2, dxfattribs=attrs)
    if width is not None:
        ent.dxf.lineweight = int(width)
    return ent


def poly(msp, pts, layer, closed=False, width=None, color=None):
    attrs = {"layer": layer}
    if color is not None:
        attrs["color"] = color
    ent = msp.add_lwpolyline(pts, close=closed, dxfattribs=attrs)
    if width is not None:
        ent.dxf.const_width = width
    return ent


def circle(msp, center, radius, layer, color=None):
    attrs = {"layer": layer}
    if color is not None:
        attrs["color"] = color
    return msp.add_circle(center, radius, dxfattribs=attrs)


def define_blocks(doc: ezdxf.EzDxf) -> None:
    if "POSTE_CAC_PLANTA" not in doc.blocks:
        blk = doc.blocks.new("POSTE_CAC_PLANTA")
        blk.add_circle((0, 0), 1.15, dxfattribs={"layer": "03_POSTES_CAC_MT"})
        blk.add_lwpolyline([(-1.55, 0), (1.55, 0)], dxfattribs={"layer": "03_POSTES_CAC_MT"})
        blk.add_lwpolyline([(0, -1.55), (0, 1.55)], dxfattribs={"layer": "03_POSTES_CAC_MT"})
    if "PAT3_PLANTA" not in doc.blocks:
        blk = doc.blocks.new("PAT3_PLANTA")
        blk.add_lwpolyline([(-1.4, 0), (1.4, 0)], dxfattribs={"layer": "06_PAT3_TIERRA"})
        blk.add_lwpolyline([(-1.0, -0.7), (1.0, -0.7)], dxfattribs={"layer": "06_PAT3_TIERRA"})
        blk.add_lwpolyline([(-0.55, -1.35), (0.55, -1.35)], dxfattribs={"layer": "06_PAT3_TIERRA"})
    if "CUTOUT_27KV" not in doc.blocks:
        blk = doc.blocks.new("CUTOUT_27KV")
        blk.add_lwpolyline([(-2, -4), (2, -4), (2, 4), (-2, 4), (-2, -4)], dxfattribs={"layer": "11_EQUIPOS_MT"})
        blk.add_line((-1.7, -3.5), (1.7, 3.5), dxfattribs={"layer": "11_EQUIPOS_MT"})
    if "PARARRAYOS_ZNO" not in doc.blocks:
        blk = doc.blocks.new("PARARRAYOS_ZNO")
        blk.add_lwpolyline([(-2.0, 2.5), (2.0, 2.5), (2.0, -2.5), (-2.0, -2.5), (-2.0, 2.5)], dxfattribs={"layer": "11_EQUIPOS_MT"})
        blk.add_text("ZnO", dxfattribs={"layer": "11_EQUIPOS_MT", "height": 1.5}).set_placement((0, -0.5), align=TextEntityAlignment.MIDDLE_CENTER)
        blk.add_line((0, -2.5), (0, -6.0), dxfattribs={"layer": "06_PAT3_TIERRA"})
        blk.add_line((-1.7, -6.0), (1.7, -6.0), dxfattribs={"layer": "06_PAT3_TIERRA"})
        blk.add_line((-1.2, -7.0), (1.2, -7.0), dxfattribs={"layer": "06_PAT3_TIERRA"})
    if "TRANSFORMADOR_DYN5" not in doc.blocks:
        blk = doc.blocks.new("TRANSFORMADOR_DYN5")
        blk.add_circle((-3, 0), 4, dxfattribs={"layer": "11_EQUIPOS_MT"})
        blk.add_circle((3, 0), 4, dxfattribs={"layer": "11_EQUIPOS_MT"})
        blk.add_text("D", dxfattribs={"layer": "11_EQUIPOS_MT", "height": 1.8}).set_placement((-3, 4.8), align=TextEntityAlignment.MIDDLE_CENTER)
        blk.add_text("Y", dxfattribs={"layer": "11_EQUIPOS_MT", "height": 1.8}).set_placement((3, -6.2), align=TextEntityAlignment.MIDDLE_CENTER)


def draw_sheet(msp, code: str, title1: str, title2: str, scale: str) -> None:
    box(msp, 0, 0, A3_W, A3_H, "00_MARCO_ROTULO")
    box(msp, MARGIN, MARGIN, A3_W - 2 * MARGIN, A3_H - 2 * MARGIN, "00_MARCO_ROTULO")
    box(msp, MARGIN, A3_H - 22, A3_W - 2 * MARGIN, 14, "00_MARCO_ROTULO")
    text(msp, "PROYECTO DE INGENIERIA DE DETALLE - LINEA PRIMARIA 22.9 kV CAPACHICA A CHIFRON",
         A3_W / 2, A3_H - 13.5, 3.1, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, title1, A3_W / 2, A3_H - 18.0, 2.35, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)

    x, y, w, h = 270, 12, 140, 55
    box(msp, x, y, w, h, "00_MARCO_ROTULO")
    for yy in [y + 10, y + 20, y + 32, y + 43]:
        line(msp, (x, yy), (x + w, yy), "00_MARCO_ROTULO")
    for xx in [x + 45, x + 92]:
        line(msp, (xx, y), (xx, y + 10), "00_MARCO_ROTULO")

    text(msp, "UNIVERSIDAD NACIONAL DEL ALTIPLANO - PUNO", x + w / 2, y + 50.0, 2.1, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "FACULTAD DE INGENIERIA MECANICA ELECTRICA, ELECTRONICA Y SISTEMAS", x + w / 2, y + 46.2, 1.55, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "ESCUELA PROFESIONAL DE INGENIERIA MECANICA ELECTRICA", x + w / 2, y + 37.3, 1.9, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "PROYECTO: LINEA PRIMARIA 22.9 kV Y SUBESTACION SAB-1 100 kVA", x + w / 2, y + 27.5, 1.55, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "SECTOR CHIFRON - DISTRITO DE CAPACHICA - PUNO", x + w / 2, y + 23.8, 1.4, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, f"PLANO: {title1}", x + w / 2, y + 16.2, 1.65, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, title2, x + w / 2, y + 12.5, 1.45, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "FECHA", x + 22.5, y + 6.6, 1.45, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "Octubre 2026", x + 22.5, y + 2.8, 1.45, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "ESCALA", x + 68.5, y + 6.6, 1.45, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, scale, x + 68.5, y + 2.8, 1.35, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "LAMINA", x + 116, y + 6.6, 1.45, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, code, x + 116, y + 2.7, 2.25, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "PROYECTISTA: Br. Renzo Gabriel Mamani Galindo (Cod. 228447)", 18, 14.5, 1.8, "09_TEXTOS")
    text(msp, "DOCENTES: Ing. Leonidas Vilca Callata / Ing. Marcos Jose Villanueva Cornejo", 18, 10.8, 1.8, "09_TEXTOS")


def fit_transform(points, box_xywh):
    x0, y0, w, h = box_xywh
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    sx = w / (maxx - minx or 1)
    sy = h / (maxy - miny or 1)
    s = min(sx, sy)
    pad_x = (w - (maxx - minx) * s) / 2
    pad_y = (h - (maxy - miny) * s) / 2

    def tr(pt):
        return (x0 + pad_x + (pt[0] - minx) * s, y0 + pad_y + (pt[1] - miny) * s)

    return tr, s


def rotated_offset(angle_deg, length=14.0):
    a = math.radians(angle_deg)
    return (math.cos(a) * length, math.sin(a) * length)


def draw_retenida_symbol(msp, p0, angle_deg, label):
    dx, dy = rotated_offset(angle_deg, 18.0)
    p1 = (p0[0] + dx, p0[1] + dy)
    poly(msp, [p0, p1], "05_RETENIDAS_R1", width=0.35)
    ux, uy = dx / 18.0, dy / 18.0
    vx, vy = -uy, ux
    iso = (p0[0] + 0.55 * dx, p0[1] + 0.55 * dy)
    r = 1.4
    poly(msp, [
        (iso[0] + ux * r, iso[1] + uy * r),
        (iso[0] + vx * r, iso[1] + vy * r),
        (iso[0] - ux * r, iso[1] - uy * r),
        (iso[0] - vx * r, iso[1] - vy * r),
    ], "05_RETENIDAS_R1", closed=True)
    box(msp, p1[0] - 1.7, p1[1] - 1.2, 3.4, 2.4, "05_RETENIDAS_R1")
    text(msp, label, p1[0] + vx * 4, p1[1] + vy * 4, 1.8, "05_RETENIDAS_R1", TextEntityAlignment.MIDDLE_CENTER)


def table(msp, x, y, headers, rows, col_w, row_h=7.0, h_text=1.8, layer="10_TABLAS_LEYENDAS"):
    total_w = sum(col_w)
    total_h = row_h * (len(rows) + 1)
    box(msp, x, y - total_h, total_w, total_h, layer)
    y_head = y - row_h
    line(msp, (x, y_head), (x + total_w, y_head), layer)
    xx = x
    for w in col_w[:-1]:
        xx += w
        line(msp, (xx, y), (xx, y - total_h), layer)
    xx = x
    for header, w in zip(headers, col_w):
        text(msp, header, xx + w / 2, y - row_h * 0.65, h_text, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
        xx += w
    for ri, row in enumerate(rows):
        yy = y - row_h * (ri + 1.65)
        if ri > 0:
            line(msp, (x, y - row_h * (ri + 1)), (x + total_w, y - row_h * (ri + 1)), layer)
        xx = x
        for value, w in zip(row, col_w):
            text(msp, value, xx + 1.2, yy, h_text, "09_TEXTOS")
            xx += w


def save_doc(doc, path: Path):
    doc.saveas(path)
    if path.stat().st_size < 12000:
        raise RuntimeError(f"DXF demasiado pequeno o incompleto: {path}")


def generate_lp01(path: Path) -> None:
    doc = new_doc()
    msp = doc.modelspace()
    draw_sheet(msp, "LP-01", "PLANTA DE LINEA PRIMARIA 22.9 kV", "TRAZA, SERVIDUMBRE Y ESTRUCTURAS MT", "1 : 2000")

    content = (18, 42, 242, 222)
    pts_utm = [(p["este"], p["norte"]) for p in ESTRUCTURAS_LP] + CAMINO_CAPACHICA_CHIFRON
    tr, _ = fit_transform(pts_utm, content)
    line_pts = [tr((p["este"], p["norte"])) for p in ESTRUCTURAS_LP]
    road_pts = [tr(p) for p in CAMINO_CAPACHICA_CHIFRON]

    poly(msp, road_pts, "07_VIAS_REFERENCIA", width=0.55, color=8)
    poly(msp, line_pts, "02_SERVIDUMBRE_MT", width=5.0, color=30)
    poly(msp, line_pts, "01_EJE_LP_MT_229KV", width=0.85)

    # Vano critico E-05 a E-06
    e05 = next(p for p in ESTRUCTURAS_LP if p["id"] == "E-05")
    e06 = next(p for p in ESTRUCTURAS_LP if p["id"] == "E-06")
    p05 = tr((e05["este"], e05["norte"]))
    p06 = tr((e06["este"], e06["norte"]))
    poly(msp, [p05, p06], "15_CRITICO_REVISION", width=1.35)
    mid = ((p05[0] + p06[0]) / 2, (p05[1] + p06[1]) / 2)
    box(msp, mid[0] + 4, mid[1] + 2, 33, 14, "15_CRITICO_REVISION")
    mtext_lines(msp, ["VANO CRITICO", "E-05 - E-06", "115.59 m"], mid[0] + 6, mid[1] + 13, 2.0, "15_CRITICO_REVISION")

    retenida_angles = {
        "E-01": 225, "E-04": 130, "E-05": 250, "E-06": 35, "E-08": 35, "E-09": 90,
    }
    for p in ESTRUCTURAS_LP:
        q = tr((p["este"], p["norte"]))
        if p["armado"] == "SAB-1":
            box(msp, q[0] - 2.6, q[1] - 2.0, 5.2, 4.0, "04_SED_SAB1")
            text(msp, "SED", q[0], q[1] - 0.7, 1.7, "04_SED_SAB1", TextEntityAlignment.MIDDLE_CENTER)
        else:
            msp.add_blockref("POSTE_CAC_PLANTA", q, dxfattribs={"layer": "03_POSTES_CAC_MT"})
        if p["pat"]:
            msp.add_blockref("PAT3_PLANTA", (q[0] + 3.8, q[1] - 4.2), dxfattribs={"layer": "06_PAT3_TIERRA"})
        if p["id"] in retenida_angles:
            draw_retenida_symbol(msp, q, retenida_angles[p["id"]], p["ret"].split()[0])
        text(msp, f"{p['id']}\\n{p['armado']}", q[0] + 3.5, q[1] + 4.6, 1.8, "09_TEXTOS")

    # Norte, escala grafica y notas
    line(msp, (34, 240), (34, 259), "09_TEXTOS")
    poly(msp, [(34, 264), (30.8, 256), (37.2, 256)], "09_TEXTOS", closed=True)
    text(msp, "N", 34, 267, 3.0, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    line(msp, (33, 37), (83, 37), "08_COTAS_DIMENSIONES")
    for x in [33, 58, 83]:
        line(msp, (x, 35), (x, 39), "08_COTAS_DIMENSIONES")
    text(msp, "0", 33, 32.5, 1.8, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "50 m", 58, 32.5, 1.8, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "100 m", 83, 32.5, 1.8, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)

    rows = [[p["id"], f"{p['prog']:.2f}", p["poste"].replace("C.A.C. ", ""), p["armado"], f"{p['ang']:.1f}", p["pat"] or "-"] for p in ESTRUCTURAS_LP]
    table(msp, 272, 262, ["ID", "Prog", "Poste", "Arm", "Ang", "PAT"], rows, [15, 21, 31, 17, 18, 16], row_h=7.2, h_text=1.55)
    mtext_lines(msp, [
        "LEYENDA DGE:",
        "Azul: eje LP 22.9 kV AAAC 35 mm2",
        "Amarillo: faja de servidumbre referencial 6 m",
        "Cian: poste CAC MT",
        "Magenta: retenida mecanica R-1",
        "Verde: puesta a tierra PAT-3",
        "Rojo: vano critico de verificacion mecanica",
    ], 273, 110, 2.05, "09_TEXTOS")
    save_doc(doc, path)


def generate_pl01(path: Path) -> None:
    doc = new_doc()
    msp = doc.modelspace()
    draw_sheet(msp, "PL-01", "PERFIL LONGITUDINAL DE LINEA PRIMARIA", "SPOTTING, CATENARIA Y GALIBOS CNE", "H 1:2000 / V 1:500")
    x0, y0, w, h = 22, 62, 355, 190
    min_prog, max_prog = 0, ESTRUCTURAS_LP[-1]["prog"]
    min_cota = min(p["cota"] for p in ESTRUCTURAS_LP) - 12
    max_cota = max(p["cota"] for p in ESTRUCTURAS_LP) + 12

    def tr(prog, cota):
        return (x0 + (prog - min_prog) / (max_prog - min_prog) * w, y0 + (cota - min_cota) / (max_cota - min_cota) * h)

    # Grilla
    for i in range(0, 9):
        xx = x0 + w * i / 8
        line(msp, (xx, y0), (xx, y0 + h), "08_COTAS_DIMENSIONES", color=8)
    for i in range(0, 7):
        yy = y0 + h * i / 6
        line(msp, (x0, yy), (x0 + w, yy), "08_COTAS_DIMENSIONES", color=8)
    box(msp, x0, y0, w, h, "00_MARCO_ROTULO")

    terr = [tr(p["prog"], p["cota"]) for p in ESTRUCTURAS_LP]
    poly(msp, terr, "07_VIAS_REFERENCIA", width=0.7, color=30)
    for p in ESTRUCTURAS_LP:
        base = tr(p["prog"], p["cota"])
        top = tr(p["prog"], p["cota"] + p["h_total"] - p["empot"])
        line(msp, base, top, "03_POSTES_CAC_MT", width=50)
        text(msp, p["id"], top[0], top[1] + 4, 2.0, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
        text(msp, p["armado"], top[0], top[1] + 1, 1.6, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)

    for vano in VANOS_LP:
        pa = next(p for p in ESTRUCTURAS_LP if p["id"] == vano["de"])
        pb = next(p for p in ESTRUCTURAS_LP if p["id"] == vano["a"])
        pts = []
        for i in range(21):
            t = i / 20
            prog = pa["prog"] + (pb["prog"] - pa["prog"]) * t
            cota_line = (pa["cota"] + pa["h_total"] - pa["empot"]) * (1 - t) + (pb["cota"] + pb["h_total"] - pb["empot"]) * t
            cota = cota_line - vano["flecha_max"] * 4 * t * (1 - t)
            pts.append(tr(prog, cota))
        poly(msp, pts, "12_CONDUCTOR_AAAC", width=0.55)
        mid = pts[len(pts) // 2]
        text(msp, f"V{vano['num']} {vano['long']:.2f}m", mid[0], mid[1] + 4, 1.45, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)

    text(msp, "PROGRESIVA (m)", x0 + w / 2, y0 - 13, 2.1, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "COTA (msnm)", x0 - 11, y0 + h / 2, 2.1, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER, rot=90)
    rows = [[f"V{v['num']}", f"{v['de']}-{v['a']}", f"{v['long']:.2f}", f"{v['flecha_max']:.3f}", f"{v['galibo']:.2f}"] for v in VANOS_LP]
    table(msp, 48, 51, ["Vano", "Tramo", "Long", "Flecha", "Galibo"], rows, [22, 35, 28, 28, 28], row_h=5.8, h_text=1.35)
    save_doc(doc, path)


def generate_u01(path: Path) -> None:
    doc = new_doc()
    msp = doc.modelspace()
    draw_sheet(msp, "U-01", "DIAGRAMA UNIFILAR DE MEDIA TENSION", "PROTECCIONES 22.9 kV Y LIMITE DE ALCANCE", "Indicada")
    x = 180
    y_top = 248
    line(msp, (65, y_top), (310, y_top), "01_EJE_LP_MT_229KV", width=50)
    text(msp, "RED TRONCAL MT 22.9 kV - ELECTRO PUNO", 187, y_top + 8, 2.4, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    line(msp, (x, y_top), (x, 78), "01_EJE_LP_MT_229KV", width=50)
    msp.add_blockref("CUTOUT_27KV", (x, 220), dxfattribs={"layer": "11_EQUIPOS_MT"})
    text(msp, "03 CUT-OUT 27 kV / 100 A\\nFusible K 4 A", x + 18, 223, 2.0, "11_EQUIPOS_MT")
    line(msp, (x - 42, 210), (x - 42, 173), "01_EJE_LP_MT_229KV")
    msp.add_blockref("PARARRAYOS_ZNO", (x - 42, 186), dxfattribs={"layer": "11_EQUIPOS_MT"})
    text(msp, "03 Pararrayos ZnO 21 kV\\n10 kA - PAT-3 R <= 10 ohm", x - 72, 185, 1.75, "06_PAT3_TIERRA", TextEntityAlignment.RIGHT)
    msp.add_blockref("CUTOUT_27KV", (x, 140), dxfattribs={"layer": "11_EQUIPOS_MT"})
    text(msp, "Seccionamiento cabecera SED", x + 18, 142, 2.0, "11_EQUIPOS_MT")
    msp.add_blockref("TRANSFORMADOR_DYN5", (x, 86), dxfattribs={"layer": "11_EQUIPOS_MT"})
    mtext_lines(msp, [
        "TRANSFORMADOR TRIFASICO",
        "100 kVA - 22.9/0.38-0.22 kV",
        "Dyn5 - ONAN - 3850 msnm",
    ], x + 17, 93, 1.75, "11_EQUIPOS_MT")
    line(msp, (x, 78), (x, 62), "01_EJE_LP_MT_229KV")
    box(msp, x - 35, 47, 70, 13, "01_EJE_LP_MT_229KV")
    mtext_lines(msp, ["LIMITE DE ALCANCE", "SOLO LINEA PRIMARIA 22.9 kV", "Sin red secundaria"], x, 57, 1.75, "09_TEXTOS", align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_blockref("PAT3_PLANTA", (x - 42, 65), dxfattribs={"layer": "06_PAT3_TIERRA"})
    text(msp, "PAT-3 Neutro y masa\\nR <= 10 ohm", x - 52, 62, 1.75, "06_PAT3_TIERRA", TextEntityAlignment.RIGHT)

    box(msp, 288, 86, 112, 160, "10_TABLAS_LEYENDAS")
    mtext_lines(msp, [
        "ESPECIFICACIONES MT",
        "",
        "Sistema: 22.9 kV, 3 hilos, 60 Hz",
        "Conductor: AAAC 35 mm2",
        "Estructuras: E-01 a E-09",
        "Cut-Out: 27 kV, 100 A, BIL 150 kV",
        "Pararrayos: ZnO 21 kV, 10 kA",
        "Transformador: 100 kVA, Dyn5",
        "Puesta a tierra: PAT-3, R <= 10 ohm",
        "",
        "Nota: plano exclusivo de media tension.",
    ], 294, 236, 2.0, "09_TEXTOS")
    save_doc(doc, path)


def draw_post_detail(msp, x, y, height=120, label="PS-1", retenida=False, biposte=False, trafo=False):
    if biposte:
        line(msp, (x - 14, y), (x - 11, y + height), "03_POSTES_CAC_MT", width=50)
        line(msp, (x + 14, y), (x + 11, y + height), "03_POSTES_CAC_MT", width=50)
    else:
        line(msp, (x, y), (x, y + height), "03_POSTES_CAC_MT", width=50)
    line(msp, (x - 32, y + height - 15), (x + 32, y + height - 15), "12_CONDUCTOR_AAAC", width=30)
    for dx in [-25, 0, 25]:
        circle(msp, (x + dx, y + height - 24), 2.2, "13_AISLADORES")
        line(msp, (x + dx, y + height - 24), (x + dx, y + height - 16), "13_AISLADORES")
    if retenida:
        line(msp, (x, y + height - 18), (x - 48, y + 24), "05_RETENIDAS_R1", width=30)
        box(msp, x - 53, y + 18, 10, 7, "05_RETENIDAS_R1")
    if trafo:
        box(msp, x - 18, y + 50, 36, 28, "11_EQUIPOS_MT")
        text(msp, "TRAFO\\n100 kVA", x, y + 61, 2.2, "11_EQUIPOS_MT", TextEntityAlignment.MIDDLE_CENTER)
        line(msp, (x - 24, y + 47), (x + 24, y + 47), "11_EQUIPOS_MT", width=35)
    text(msp, label, x, y + height + 7, 3.0, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)


def generate_d01(path: Path) -> None:
    doc = new_doc()
    msp = doc.modelspace()
    draw_sheet(msp, "D-01", "ARMADOS NORMALIZADOS DGE PS-1 Y PA-1", "SUSPENSION, ANGULO Y RETENIDA R-1", "1 : 25")
    box(msp, 18, 48, 170, 210, "10_TABLAS_LEYENDAS")
    box(msp, 202, 48, 170, 210, "10_TABLAS_LEYENDAS")
    draw_post_detail(msp, 103, 72, 145, "DGE PS-1 - SUSPENSION", retenida=False)
    draw_post_detail(msp, 287, 72, 145, "DGE PA-1 - ANGULO", retenida=True)
    mtext_lines(msp, [
        "PS-1: poste CAC 12/300 daN",
        "Cruceta F G L 75x75x6.4 mm x 1.50 m",
        "03 aisladores tipo pin ANSI 56-3",
        "Conductor AAAC 35 mm2",
    ], 25, 242, 2.1, "09_TEXTOS")
    mtext_lines(msp, [
        "PA-1: poste CAC 12/400 daN",
        "Cadena polimerica 25 kV BIL 150 kV",
        "Retenida R-1 segun resultante de angulo",
        "Cable Siemens-Martin 3/8 pulg",
    ], 209, 242, 2.1, "09_TEXTOS")
    save_doc(doc, path)


def generate_d02(path: Path) -> None:
    doc = new_doc()
    msp = doc.modelspace()
    draw_sheet(msp, "D-02", "ARMADOS NORMALIZADOS DGE PR-1 Y SAB-1", "RETENCION, SECCIONAMIENTO Y SED BIPOSTE", "1 : 25")
    box(msp, 18, 48, 170, 210, "10_TABLAS_LEYENDAS")
    box(msp, 202, 48, 170, 210, "10_TABLAS_LEYENDAS")
    draw_post_detail(msp, 103, 70, 145, "DGE PR-1 - RETENCION", retenida=True)
    msp.add_blockref("CUTOUT_27KV", (118, 197), dxfattribs={"layer": "11_EQUIPOS_MT"})
    msp.add_blockref("PARARRAYOS_ZNO", (72, 190), dxfattribs={"layer": "11_EQUIPOS_MT"})
    draw_post_detail(msp, 287, 70, 155, "DGE SAB-1 - BIPOSTE", biposte=True, trafo=True)
    mtext_lines(msp, [
        "PR-1: retencion terminal o derivacion",
        "03 Cut-Out 27 kV / 100 A",
        "03 Pararrayos ZnO 21 kV / 10 kA",
        "PAT-3: R <= 10 ohm",
    ], 25, 242, 2.1, "09_TEXTOS")
    mtext_lines(msp, [
        "SAB-1: 02 postes CAC 13/400 daN",
        "Transformador 100 kVA Dyn5 ONAN",
        "Plataforma F G UPN-120",
        "Alcance del plano: media tension y SED",
    ], 209, 242, 2.1, "09_TEXTOS")
    save_doc(doc, path)


def generate_d03(path: Path) -> None:
    doc = new_doc()
    msp = doc.modelspace()
    draw_sheet(msp, "D-03", "CIMENTACION, RETENIDA R-1 Y PAT-3", "SULZBERGER, ANCLAJE MECANICO Y PUESTA A TIERRA", "1 : 20")
    # Cimentacion
    box(msp, 18, 58, 112, 198, "10_TABLAS_LEYENDAS")
    line(msp, (40, 172), (108, 172), "14_CIMENTACION", width=30)
    box(msp, 55, 80, 38, 92, "14_CIMENTACION")
    line(msp, (74, 80), (79, 232), "03_POSTES_CAC_MT", width=50)
    text(msp, "CIMENTACION SULZBERGER", 74, 244, 2.6, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "t=1.40 m (12m) / 1.50 m (13m)", 74, 68, 1.8, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)

    # Retenida
    box(msp, 142, 58, 112, 198, "10_TABLAS_LEYENDAS")
    line(msp, (172, 105), (172, 232), "03_POSTES_CAC_MT", width=50)
    line(msp, (172, 210), (228, 82), "05_RETENIDAS_R1", width=35)
    box(msp, 220, 72, 18, 12, "05_RETENIDAS_R1")
    circle(msp, (194, 159), 3, "05_RETENIDAS_R1")
    text(msp, "RETENIDA R-1 A TIERRA 45 GRADOS", 198, 244, 2.5, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "Cable SM 3/8 pulg - bloque 0.40x0.40x0.20 m", 198, 65, 1.7, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)

    # PAT
    box(msp, 266, 58, 112, 198, "10_TABLAS_LEYENDAS")
    text(msp, "PUESTA A TIERRA PAT-3", 322, 244, 2.6, "09_TEXTOS", TextEntityAlignment.MIDDLE_CENTER)
    for ang in [90, 210, 330]:
        rad = math.radians(ang)
        x = 322 + math.cos(rad) * 24
        y = 154 + math.sin(rad) * 24
        circle(msp, (x, y), 3, "06_PAT3_TIERRA")
        line(msp, (322, 154), (x, y), "06_PAT3_TIERRA", width=25)
    circle(msp, (322, 154), 3, "06_PAT3_TIERRA")
    mtext_lines(msp, [
        "03 electrodos Cu 5/8 x 2.40 m",
        "Separacion triangular S=4.80 m",
        "Cable Cu desnudo 35 mm2",
        "R equivalente calculada: 6.80 ohm <= 10 ohm",
    ], 282, 94, 1.85, "09_TEXTOS")
    save_doc(doc, path)


def write_readme(paths: list[Path]) -> Path:
    readme = OUT_DIR / "README_AUTOCAD_LP.md"
    lines = [
        "# Paquete AutoCAD - Línea Primaria 22.9 kV",
        "",
        "Alcance exclusivo: línea primaria MT 22.9 kV, SED SAB-1 100 kVA, protecciones, retenidas, cimentaciones y PAT-3.",
        "",
        "## Archivos DXF A3 Generados",
        "",
        "| Lámina | Archivo | Contenido |",
        "| --- | --- | --- |",
        "| LP-01 | `LP-01_PLANTA_LINEA_PRIMARIA_A3_AUTOCAD.dxf` | Planta, trazo, servidumbre, estructuras, retenidas y PAT-3. |",
        "| PL-01 | `PL-01_PERFIL_LONGITUDINAL_A3_AUTOCAD.dxf` | Perfil longitudinal, spotting, catenaria y gálibos. |",
        "| U-01 | `U-01_DIAGRAMA_UNIFILAR_MT_A3_AUTOCAD.dxf` | Unifilar de media tensión y límite de alcance. |",
        "| D-01 | `D-01_ARMADOS_PS1_PA1_A3_AUTOCAD.dxf` | Armados DGE PS-1 y PA-1. |",
        "| D-02 | `D-02_ARMADOS_PR1_SAB1_A3_AUTOCAD.dxf` | Armados DGE PR-1 y SAB-1. |",
        "| D-03 | `D-03_CIMENTACION_RETENIDA_PAT3_A3_AUTOCAD.dxf` | Cimentación Sulzberger, retenida R-1 y PAT-3. |",
        "",
        "## Recomendación AutoCAD",
        "",
        "1. Abrir cada DXF en AutoCAD.",
        "2. Ejecutar `ZOOM EXTENTS`.",
        "3. Configurar papel A3 horizontal.",
        "4. Plotear con CTB monocromo o por color, según indique el docente.",
        "5. Si se requiere DWG, guardar cada DXF como DWG desde AutoCAD.",
        "",
        "## Capas Principales",
        "",
        "- `00_MARCO_ROTULO`",
        "- `01_EJE_LP_MT_229KV`",
        "- `02_SERVIDUMBRE_MT`",
        "- `03_POSTES_CAC_MT`",
        "- `04_SED_SAB1`",
        "- `05_RETENIDAS_R1`",
        "- `06_PAT3_TIERRA`",
        "- `11_EQUIPOS_MT`",
        "- `15_CRITICO_REVISION`",
        "",
        "## Advertencia de Alcance",
        "",
        "No usar estos planos para redes secundarias, acometidas domiciliarias ni alumbrado público. Este paquete fue cerrado únicamente para línea primaria 22.9 kV.",
    ]
    readme.write_text("\n".join(lines), encoding="utf-8")
    return readme


def create_zip(files: list[Path]) -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with ZipFile(ZIP_PATH, "w", compression=ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(file, arcname=file.relative_to(OUT_DIR.parent))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generators = [generate_lp01, generate_pl01, generate_u01, generate_d01, generate_d02, generate_d03]
    out_files: list[Path] = []
    for (_, filename, *_), generator in zip(PLANOS, generators):
        target = OUT_DIR / filename
        generator(target)
        out_files.append(target)
        print(f"[OK] {target}")
    readme = write_readme(out_files)
    out_files.append(readme)
    create_zip(out_files)
    print(f"[OK ZIP] {ZIP_PATH}")


if __name__ == "__main__":
    main()
