"""Plano de planta con imagen satelital georreferenciada y expediente Capachica-Llachón.

Genera en `build/renzo-linea-primaria-capachica-llachon/planta_satelital/`:

  - imagen_satelital_corredor.png/.pgw/.prj  mosaico ESRI World Imagery reproyectado a UTM 19S
  - CL-01_PLANTA_SATELITAL_A3.dxf           modelo UTM con IMAGE + insercion de bloques PC
  - plancha_satelital_CL-01.pdf             lamina A3 con la imagen satelital y superposiciones
  - plancha_planta_CL-01.pdf                lamina A3 simbolica de planta
  - EXPEDIENTE_CON_IMAGEN_SATELITAL.pdf     expediente A4 (8 paginas) + las dos laminas A3
  - reporte_planta_satelital.json           trazabilidad: teselas, SHA-256, conteos
  - tiles_satelitales/                      teselas JPEG descargadas con manifiesto SHA-256

Colocacion de postes: las 40 PC (estructuras GIS GISEM a <=25 m del KML) se
insertan automaticamente como bloques reutilizables POSTE_CAC_PLANTA en su
coordenada UTM 19S. Son referencias GIS pendientes de verificacion en campo,
NO postes aprobados; PN (27) son circulos de sitio de gabinete y CV (44) cruces
OSM. Ninguno representa una estructura aprobada.

Limites: la imagen satelital es contexto (~2.3 m/px en zoom 16), no sustituye
topografia de diseno. Borrador academico no apto para construccion.

Fuentes: ESRI World Imagery (ArcGIS REST, teselas raster, consultado en fecha
del reporte); geometria de `sources/ruta topografica capachica llachon.kml`,
`datos/ubicaciones_postes_preliminares.csv`, `datos/candidatos_nuevos_replanteo_rev3.csv`,
`datos/cruces_viales_rev3.csv` (inalteradas).

Uso:
    python scripts/generar_planta_satelital.py
    python scripts/generar_planta_satelital.py --zoom 15 --salida <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import textwrap
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import ezdxf
import numpy as np
from PIL import Image
from pyproj import CRS, Transformer
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A3, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from colocar_postes_automatico import PAPER_SYMBOL_SCALE, define_blocks
from generar_entrega_rev4 import read_inputs

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "renzo-linea-primaria-capachica-llachon" / "planta_satelital"
DXF_NAME = "CL-01_PLANTA_SATELITAL_A3.dxf"
PNG_NAME = "imagen_satelital_corredor.png"
JPEG_NAME = "imagen_satelital_plancha.jpg"
PGW_NAME = "imagen_satelital_corredor.pgw"
PRJ_NAME = "imagen_satelital_corredor.prj"
PLANCHA_SAT_PDF = "plancha_satelital_CL-01.pdf"
PLANCHA_PLANTA_PDF = "plancha_planta_CL-01.pdf"
EXPEDIENTE_PDF = "EXPEDIENTE_CON_IMAGEN_SATELITAL.pdf"
REPORT_NAME = "reporte_planta_satelital.json"
TILES_DIR = "tiles_satelitales"

ESRI_TILE_URL = ("https://services.arcgisonline.com/ArcGIS/rest/services/"
                 "World_Imagery/MapServer/tile/{z}/{y}/{x}")
WM_R = 6378137.0
ZOOM = 16
MARGIN_M = 150.0
MAX_TILES = 400
CHUNK_ROWS = 256

MM = 72 / 25.4
BLUE = HexColor("#245b91")
RED = HexColor("#c63434")
CYAN = HexColor("#157899")
AMBER = HexColor("#cd7a19")
INK = HexColor("#24313f")

MAP_X, MAP_Y, MAP_W, MAP_H = 14.0, 62.0, 258.0, 192.0
TABLE_X, TABLE_Y = 280.0, 254.0
ROW_STEP = 4.6
PAPER_PC = ("PC_GISEM", 1)
PAPER_PN = ("PN_CANDIDATO", 4)
PAPER_CV = ("CV_OSM", 30)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calcular_bbox(lineas, pc, pn, cv, margen: float) -> tuple[float, float, float, float]:
    puntos = [p for linea in lineas for p in linea]
    puntos += [(float(r["este_m"]), float(r["norte_m"])) for r in pc]
    puntos += [(float(r["este_utm19s_m"]), float(r["norte_utm19s_m"])) for r in pn + cv]
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    return (min(xs) - margen, min(ys) - margen, max(xs) + margen, max(ys) + margen)


def cobertura_tiles(bbox_utm, zoom: int) -> tuple[int, int, int, int]:
    if not 0 <= zoom <= 19:
        raise ValueError(f"Zoom fuera de rango 0-19: {zoom}")
    t = Transformer.from_crs(32719, 3857, always_xy=True)
    x0, y0, x1, y1 = bbox_utm
    esquinas = [(x0, y0), (x0, y1), (x1, y0), (x1, y1)]
    wm = [t.transform(px, py) for px, py in esquinas]
    wx = [p[0] for p in wm]
    wy = [p[1] for p in wm]
    n = 2 ** zoom
    paso = 2 * math.pi * WM_R / n
    tx0 = math.floor((min(wx) + math.pi * WM_R) / paso)
    tx1 = math.floor((max(wx) + math.pi * WM_R) / paso)
    ty0 = math.floor((math.pi * WM_R - max(wy)) / paso)
    ty1 = math.floor((math.pi * WM_R - min(wy)) / paso)
    total = (tx1 - tx0 + 1) * (ty1 - ty0 + 1)
    if total > MAX_TILES:
        raise ValueError(f"Rango de teselas demasiado grande ({total} > {MAX_TILES}); use menor zoom")
    if total <= 0 or tx1 < tx0 or ty1 < ty0:
        raise ValueError("Cobertura de teselas vacia")
    return int(tx0), int(tx1), int(ty0), int(ty1)


def _leer_tesela(path: Path) -> np.ndarray:
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"))


def descargar_mosaico(dir_tiles: Path, zoom: int, rango) -> tuple[np.ndarray, dict, dict]:
    tx0, tx1, ty0, ty1 = rango
    wm_res = 2 * math.pi * WM_R / (2 ** zoom) / 256.0
    wm_x0 = -math.pi * WM_R + tx0 * wm_res * 256.0
    wm_y0 = math.pi * WM_R - ty0 * wm_res * 256.0
    ancho = (tx1 - tx0 + 1) * 256
    alto = (ty1 - ty0 + 1) * 256
    mosaico = np.zeros((alto, ancho, 3), dtype=np.uint8)
    dir_tiles.mkdir(parents=True, exist_ok=True)
    manifiesto: dict[str, str] = {}
    faltantes = [(x, y) for x in range(tx0, tx1 + 1) for y in range(ty0, ty1 + 1)
                 if not (dir_tiles / f"z{zoom}_{x}_{y}.jpg").is_file()]
    if faltantes:
        print(f"Descargando {len(faltantes)} teselas ESRI World Imagery (z{zoom})...")
    for x, y in ((x, y) for x in range(tx0, tx1 + 1) for y in range(ty0, ty1 + 1)):
        destino = dir_tiles / f"z{zoom}_{x}_{y}.jpg"
        if not destino.is_file():
            url = ESRI_TILE_URL.format(z=zoom, y=y, x=x)
            ultimo = None
            for intento in range(3):
                try:
                    with urllib.request.urlopen(url, timeout=25) as respuesta:
                        datos = respuesta.read()
                    if len(datos) < 500:
                        raise RuntimeError(f"tesela incompleta ({len(datos)} bytes)")
                    destino.write_bytes(datos)
                    break
                except (urllib.error.URLError, RuntimeError, TimeoutError) as error:
                    ultimo = error
                    time.sleep(1.5 * (intento + 1))
            else:
                raise RuntimeError(f"No se pudo descargar {url}: {ultimo}")
        datos = destino.read_bytes()
        manifiesto[destino.name] = hashlib.sha256(datos).hexdigest()
        imagen = Image.open(io.BytesIO(datos)).convert("RGB")
        fila0, col0 = (y - ty0) * 256, (x - tx0) * 256
        mosaico[fila0:fila0 + 256, col0:col0 + 256] = np.asarray(imagen)
    meta = {"wm_x0": wm_x0, "wm_y0": wm_y0, "wm_res": wm_res,
            "ancho_px": ancho, "alto_px": alto}
    return mosaico, meta, manifiesto


def _bilineal(mosaico: np.ndarray, mx: np.ndarray, my: np.ndarray) -> np.ndarray:
    alto, ancho = mosaico.shape[:2]
    fx = np.clip(mx - 0.5, 0.0, ancho - 1.000001)
    fy = np.clip(my - 0.5, 0.0, alto - 1.000001)
    j0 = fx.astype(np.int32)
    i0 = fy.astype(np.int32)
    j1 = np.minimum(j0 + 1, ancho - 1)
    i1 = np.minimum(i0 + 1, alto - 1)
    wx = (fx - j0)[..., None]
    wy = (fy - i0)[..., None]
    a = mosaico[i0, j0]
    b = mosaico[i0, j1]
    c = mosaico[i1, j0]
    d = mosaico[i1, j1]
    valor = (a * (1.0 - wx) * (1.0 - wy) + b * wx * (1.0 - wy)
             + c * (1.0 - wx) * wy + d * wx * wy)
    return valor.astype(np.uint8)


def reproyectar_utm(mosaico: np.ndarray, wm: dict, bbox_utm, zoom: int):
    x0, y0, x1, y1 = bbox_utm
    t_ll = Transformer.from_crs(32719, 4326, always_xy=True)
    _, lat_c = t_ll.transform((x0 + x1) / 2.0, (y0 + y1) / 2.0)
    res = (2 * math.pi * WM_R / (2 ** zoom) / 256.0) * math.cos(math.radians(lat_c))
    res = max(res, 0.5)
    xs = np.arange(x0 + res / 2.0, x1, res)
    ys = np.arange(y1 - res / 2.0, y0, -res)
    if len(xs) < 2 or len(ys) < 2:
        raise ValueError("Rejilla de salida vacia")
    salida = np.empty((len(ys), len(xs), 3), dtype=np.uint8)
    t = Transformer.from_crs(32719, 3857, always_xy=True)
    for r0 in range(0, len(ys), CHUNK_ROWS):
        fila_y, col_x = np.meshgrid(ys[r0:r0 + CHUNK_ROWS], xs, indexing="ij")
        wmx, wmy = t.transform(col_x, fila_y)
        mx = (wmx - wm["wm_x0"]) / wm["wm_res"]
        my = (wm["wm_y0"] - wmy) / wm["wm_res"]
        salida[r0:r0 + CHUNK_ROWS] = _bilineal(mosaico, mx, my)
    return salida, x0, y1, res


def guardar_georeferenciado(png_path: Path, rgb: np.ndarray, xmin: float,
                            ymax: float, res: float) -> None:
    Image.fromarray(rgb, "RGB").save(png_path)
    png_path.with_suffix(".pgw").write_text(
        f"{res:.12g}\n0\n0\n{-res:.12g}\n{xmin + res / 2.0:.12g}\n{ymax - res / 2.0:.12g}\n",
        encoding="utf-8")
    png_path.with_suffix(".prj").write_text(CRS.from_epsg(32719).to_wkt(), encoding="utf-8")


def crear_jpeg_plancha(png_path: Path, destino: Path) -> Path:
    with Image.open(png_path) as im:
        im = im.convert("RGB")
        if im.width > 3400:
            im = im.resize((3400, round(im.height * 3400 / im.width)), Image.LANCZOS)
        im.save(destino, "JPEG", quality=88, optimize=True)
    return destino


def mapa_transform(puntos, x: float, y: float, w: float, h: float):
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    dx, dy = max(xmax - xmin, 1.0), max(ymax - ymin, 1.0)
    escala = min((w - 16.0) / dx, (h - 16.0) / dy)
    ox = x + (w - dx * escala) / 2.0
    oy = y + (h - dy * escala) / 2.0
    return (lambda p: (ox + (p[0] - xmin) * escala, oy + (p[1] - ymin) * escala),
            escala, (xmin, xmax, ymin, ymax))


def puntos_con_imagen(lineas, pc, pn, cv, img_bbox):
    puntos = [p for linea in lineas for p in linea]
    puntos += [(float(r["este_m"]), float(r["norte_m"])) for r in pc]
    puntos += [(float(r["este_utm19s_m"]), float(r["norte_utm19s_m"])) for r in pn + cv]
    x0, y0, x1, y1 = img_bbox
    puntos += [(x0, y0), (x0, y1), (x1, y0), (x1, y1)]
    return puntos


def _escala_barra(transform, escala, limites, mapa_w: float):
    extent = max(limites[1] - limites[0], limites[3] - limites[2])
    objetivo = extent / 5.0
    exponente = 10 ** math.floor(math.log10(objetivo)) if objetivo > 0 else 1
    longitud = max(exponente, round(objetivo / exponente) * exponente)
    barra = longitud * escala
    if barra > mapa_w * 0.35:
        longitud /= 2.0
        barra = longitud * escala
    return longitud, barra


def construir_dxf(salida_dxf: Path, nombre_png: str, img_bbox, img_px,
                  lineas, pc, pn, cv) -> dict:
    if salida_dxf.exists():
        raise FileExistsError(f"Ya existe {salida_dxf}; archive antes de regenerar")
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    for nombre, aci in [("EJE_KML", 5), ("PC_GISEM", 1), ("PN_CANDIDATO", 4),
                        ("CV_OSM", 30), ("MARCO", 7), ("TEXT", 7),
                        ("POSTES_APROBADOS", 1), ("PAT_TIERRA", 3),
                        ("RETENIDAS_R1", 6), ("EQUIPOS_MT", 2)]:
        doc.layers.new(nombre, dxfattribs={"color": aci})
    define_blocks(doc)
    x0, y0, x1, y1 = img_bbox
    ancho_m, alto_m = x1 - x0, y1 - y0
    image_def = doc.add_image_def(nombre_png, (int(img_px[0]), int(img_px[1])))
    msp = doc.modelspace()
    msp.add_image(image_def, (x0, y0), (ancho_m, alto_m))
    for linea in lineas:
        msp.add_lwpolyline(linea, dxfattribs={"layer": "EJE_KML"})
    for row in pc:
        msp.add_blockref("POSTE_CAC_PLANTA", (float(row["este_m"]), float(row["norte_m"])),
                         dxfattribs={"layer": "PC_GISEM"})
    for row in pn:
        msp.add_circle((float(row["este_utm19s_m"]), float(row["norte_utm19s_m"])), 2.8,
                       dxfattribs={"layer": "PN_CANDIDATO"})
    for row in cv:
        ex, ny = float(row["este_utm19s_m"]), float(row["norte_utm19s_m"])
        msp.add_line((ex - 2.0, ny), (ex + 2.0, ny), dxfattribs={"layer": "CV_OSM"})
        msp.add_line((ex, ny - 2.0), (ex, ny + 2.0), dxfattribs={"layer": "CV_OSM"})
    puntos = puntos_con_imagen(lineas, pc, pn, cv, img_bbox)
    transform, escala, limites = mapa_transform(puntos, MAP_X, MAP_Y, MAP_W, MAP_H)
    layout = doc.layouts.new("CL-01_PLANTA_A3")
    layout.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
    _papel_malla(layout, transform, limites, escala, lineas, pc, pn, cv)
    doc.saveas(salida_dxf)
    return {"inserts_pc": len(pc), "imagenes": 1}


def _texto_papel(layout, x, y, valor, alto=2.0, capa="TEXT"):
    layout.add_text(str(valor), dxfattribs={"height": alto, "layer": capa}).set_placement((x, y))


def _papel_malla(layout, transform, limites, escala, lineas, pc, pn, cv,
                 etiqueta_codigo="CL-01 | Plano de planta del corredor Capachica-Llachon"):
    layout.add_lwpolyline([(8, 8), (412, 8), (412, 289), (8, 289), (8, 8)],
                          dxfattribs={"layer": "MARCO"})
    _texto_papel(layout, 14, 281, etiqueta_codigo, 4.0)
    _texto_papel(layout, 14, 271,
                 "Eje KML manual; PC: referencias GIS pendientes de campo; "
                 "PN: sitios de gabinete; CV: cruces OSM", 2.0)
    _texto_papel(layout, 14, 28, "ANTEPROYECTO ACADEMICO - NO APTO PARA CONSTRUCCION", 2.4)
    layout.add_lwpolyline([(MAP_X, MAP_Y), (MAP_X + MAP_W, MAP_Y),
                           (MAP_X + MAP_W, MAP_Y + MAP_H), (MAP_X, MAP_Y + MAP_H),
                           (MAP_X, MAP_Y)], dxfattribs={"layer": "MARCO"})
    for linea in lineas:
        layout.add_lwpolyline([transform(p) for p in linea], dxfattribs={"layer": "EJE_KML"})
    colocados = []
    for row in pc:
        px, py = transform((float(row["este_m"]), float(row["norte_m"])))
        layout.add_blockref("POSTE_CAC_PLANTA", (px, py), dxfattribs={
            "layer": "PC_GISEM", "xscale": PAPER_SYMBOL_SCALE["POSTE_CAC_PLANTA"],
            "yscale": PAPER_SYMBOL_SCALE["POSTE_CAC_PLANTA"]})
        if all(math.dist((px, py), q) > 13.0 for q in colocados):
            _texto_papel(layout, px + 1.4, py + 1.0, row["id"], 1.5)
            colocados.append((px, py))
    for row in pn:
        px, py = transform((float(row["este_utm19s_m"]), float(row["norte_utm19s_m"])))
        layout.add_circle((px, py), 1.8, dxfattribs={"layer": "PN_CANDIDATO"})
        if all(math.dist((px, py), q) > 13.0 for q in colocados):
            _texto_papel(layout, px + 1.6, py + 1.0, row["id"], 1.4)
            colocados.append((px, py))
    for row in cv:
        px, py = transform((float(row["este_utm19s_m"]), float(row["norte_utm19s_m"])))
        layout.add_line((px - 1.0, py), (px + 1.0, py), dxfattribs={"layer": "CV_OSM"})
        layout.add_line((px, py - 1.0), (px, py + 1.0), dxfattribs={"layer": "CV_OSM"})
    _texto_papel(layout, MAP_X + MAP_W - 13, MAP_Y + MAP_H - 10, "N", 3.0)
    layout.add_line((MAP_X + MAP_W - 10, MAP_Y + MAP_H - 13),
                    (MAP_X + MAP_W - 10, MAP_Y + MAP_H - 22), dxfattribs={"layer": "MARCO"})
    layout.add_line((MAP_X + MAP_W - 10, MAP_Y + MAP_H - 13),
                    (MAP_X + MAP_W - 12, MAP_Y + MAP_H - 17), dxfattribs={"layer": "MARCO"})
    layout.add_line((MAP_X + MAP_W - 10, MAP_Y + MAP_H - 13),
                    (MAP_X + MAP_W - 8, MAP_Y + MAP_H - 17), dxfattribs={"layer": "MARCO"})
    longitud, barra = _escala_barra(transform, escala, limites, MAP_W)
    bx, by = MAP_X + 8.0, MAP_Y + 8.0
    layout.add_line((bx, by), (bx + barra, by), dxfattribs={"layer": "MARCO"})
    _texto_papel(layout, bx, by + 2.0, f"{longitud:g} m", 1.6)
    _texto_papel(layout, MAP_X + 3, MAP_Y + 2.0,
                 f"E {limites[0]:.0f}-{limites[1]:.0f} m | N {limites[2]:.0f}-{limites[3]:.0f} m", 1.5)
    leyenda = [(f"PC {len(pc)}", "PC_GISEM"), (f"PN {len(pn)}", "PN_CANDIDATO"),
               (f"CV {len(cv)}", "CV_OSM")]
    for j, (etiqueta, capa) in enumerate(leyenda):
        lx, ly = MAP_X + 6.0 + j * 44.0, MAP_Y + MAP_H - 7.0
        _texto_papel(layout, lx, ly, etiqueta, 1.6)
        if capa == "CV_OSM":
            layout.add_line((lx + 14, ly + 0.7), (lx + 16, ly + 0.7), dxfattribs={"layer": capa})
        else:
            layout.add_circle((lx + 15, ly + 0.7), 1.4, dxfattribs={"layer": capa})
    _texto_papel(layout, TABLE_X, TABLE_Y, "CUADRO PC - REFERENCIAS GIS (PENDIENTES)", 2.2)
    yy = TABLE_Y - 5.0
    for etiqueta, dx in (("ID / GISEM", 0), ("PK m", 40), ("E", 62), ("N", 88)):
        _texto_papel(layout, TABLE_X + dx, yy, etiqueta, 1.5)
    yy -= 4.0
    for row in pc[:38]:
        _texto_papel(layout, TABLE_X, yy, f"{row['id']} {row['codigo_gisem']}", 1.5)
        _texto_papel(layout, TABLE_X + 40, yy, f"{float(row['estacion_m']):.0f}", 1.5)
        _texto_papel(layout, TABLE_X + 62, yy, f"{float(row['este_m']):.0f}", 1.5)
        _texto_papel(layout, TABLE_X + 88, yy, f"{float(row['norte_m']):.0f}", 1.5)
        yy -= 4.6
    if len(pc) > 38:
        _texto_papel(layout, TABLE_X, yy, f"+{len(pc) - 38} registros en el CSV fuente", 1.4)
    _texto_papel(layout, TABLE_X, 55.0, "UTM EPSG:32719; PK estacion GIS acumulada.", 1.4)
    _texto_papel(layout, TABLE_X, 49.0, "PC no es poste aprobado; verificar en campo.", 1.4)


def _marco_pdf(c, codigo, titulo, subtitulo):
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.rect(8 * MM, 8 * MM, 404 * MM, 281 * MM, stroke=1, fill=0)
    c.line(8 * MM, 39 * MM, 412 * MM, 39 * MM)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(14 * MM, 281 * MM, f"{codigo} | {titulo}")
    c.setFont("Helvetica", 7.5)
    c.drawString(14 * MM, 270 * MM, subtitulo)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(14 * MM, 28 * MM, "ANTEPROYECTO ACADEMICO - NO APTO PARA CONSTRUCCION")
    c.setFillColor(INK)
    c.setFont("Helvetica", 6.5)
    c.drawString(14 * MM, 16 * MM,
                 "WGS84 / UTM 19S EPSG:32719 | Modelo DXF en metros | Presentacion A3 en milimetros")


def _texto_pdf(c, x, y, valor, color=INK, fuente="Helvetica", tam=6.0):
    c.setFillColor(color)
    c.setFont(fuente, tam)
    c.drawString(x * MM, y * MM, str(valor))


def plancha_pdf(destino: Path, con_satelite: Path | None, codigo: str, titulo: str,
                subtitulo: str, transform, escala, limites, lineas, pc, pn, cv) -> None:
    c = canvas.Canvas(str(destino), pagesize=(420 * MM, 297 * MM), invariant=1)
    _marco_pdf(c, codigo, titulo, subtitulo)
    c.setStrokeColor(INK)
    c.setLineWidth(0.35)
    c.rect(MAP_X * MM, MAP_Y * MM, MAP_W * MM, MAP_H * MM, stroke=1, fill=0)
    if con_satelite is not None:
        ix0, iy0 = transform((limites[0], limites[2]))
        ix1, iy1 = transform((limites[1], limites[3]))
        c.drawImage(ImageReader(str(con_satelite)), ix0 * MM, iy0 * MM,
                    (ix1 - ix0) * MM, (iy1 - iy0) * MM, preserveAspectRatio=False, mask=None)
        c.setStrokeColor(INK)
        c.setLineWidth(0.35)
        c.rect(MAP_X * MM, MAP_Y * MM, MAP_W * MM, MAP_H * MM, stroke=1, fill=0)
    for linea in lineas:
        path = c.beginPath()
        p0 = transform(linea[0])
        path.moveTo(p0[0] * MM, p0[1] * MM)
        for xy in linea[1:]:
            px, py = transform(xy)
            path.lineTo(px * MM, py * MM)
        c.setStrokeColor(BLUE)
        c.setLineWidth(0.9)
        c.drawPath(path)
    colocados = []
    for row in pc:
        px, py = transform((float(row["este_m"]), float(row["norte_m"])))
        c.setStrokeColor(RED)
        c.setLineWidth(0.65)
        c.circle(px * MM, py * MM, 1.35 * MM, stroke=1, fill=0)
        if all(math.dist((px, py), q) > 13.0 for q in colocados):
            _texto_pdf(c, px + 1.6, py + 1.0, row["id"], RED, "Helvetica", 5.6)
            colocados.append((px, py))
    for row in pn:
        px, py = transform((float(row["este_utm19s_m"]), float(row["norte_utm19s_m"])))
        c.setStrokeColor(CYAN)
        c.setLineWidth(0.8)
        c.circle(px * MM, py * MM, 1.8 * MM, stroke=1, fill=0)
        if all(math.dist((px, py), q) > 13.0 for q in colocados):
            _texto_pdf(c, px + 2.0, py + 1.0, row["id"], CYAN, "Helvetica", 5.4)
            colocados.append((px, py))
    for row in cv:
        px, py = transform((float(row["este_utm19s_m"]), float(row["norte_utm19s_m"])))
        c.setStrokeColor(AMBER)
        c.setLineWidth(0.55)
        c.line((px - 1.0) * MM, py * MM, (px + 1.0) * MM, py * MM)
        c.line(px * MM, (py - 1.0) * MM, px * MM, (py + 1.0) * MM)
    _texto_pdf(c, MAP_X + MAP_W - 13, MAP_Y + MAP_H - 10, "N", INK, "Helvetica-Bold", 8)
    c.setStrokeColor(INK)
    c.setLineWidth(0.9)
    c.line((MAP_X + MAP_W - 10) * MM, (MAP_Y + MAP_H - 13) * MM,
           (MAP_X + MAP_W - 10) * MM, (MAP_Y + MAP_H - 22) * MM)
    c.line((MAP_X + MAP_W - 10) * MM, (MAP_Y + MAP_H - 13) * MM,
           (MAP_X + MAP_W - 12) * MM, (MAP_Y + MAP_H - 17) * MM)
    c.line((MAP_X + MAP_W - 10) * MM, (MAP_Y + MAP_H - 13) * MM,
           (MAP_X + MAP_W - 8) * MM, (MAP_Y + MAP_H - 17) * MM)
    longitud, barra = _escala_barra(transform, escala, limites, MAP_W)
    bx, by = MAP_X + 8.0, MAP_Y + 8.0
    c.setStrokeColor(INK)
    c.setLineWidth(1.2)
    c.line(bx * MM, by * MM, (bx + barra) * MM, by * MM)
    _texto_pdf(c, bx, by + 2.0, f"{longitud:g} m", INK, "Helvetica", 5.8)
    _texto_pdf(c, MAP_X + 3, MAP_Y + 2.0,
               f"E {limites[0]:.0f}-{limites[1]:.0f} m | N {limites[2]:.0f}-{limites[3]:.0f} m",
               INK, "Helvetica", 5.3)
    leyenda = [(f"PC {len(pc)}", RED), (f"PN {len(pn)}", CYAN), (f"CV {len(cv)}", AMBER)]
    for j, (etiqueta, color) in enumerate(leyenda):
        lx, ly = MAP_X + 6.0 + j * 44.0, MAP_Y + MAP_H - 7.0
        c.setFillColor(color)
        c.setFont("Helvetica", 5.7)
        c.drawString(lx * MM, ly * MM, etiqueta)
        c.setStrokeColor(color)
        c.circle((lx + 15) * MM, (ly + 0.7) * MM, 1.4 * MM, stroke=1, fill=0)
    if con_satelite is not None:
        _texto_pdf(c, MAP_X + 3, MAP_Y + MAP_H - 7.0,
                   "Imagen: ESRI World Imagery (contexto, no topografia)", INK,
                   "Helvetica", 5.5)
    _texto_pdf(c, TABLE_X, TABLE_Y, "CUADRO PC - REFERENCIAS GIS (PENDIENTES)",
               INK, "Helvetica-Bold", 6.5)
    yy = TABLE_Y - 5.0
    for etiqueta, dx in (("ID / GISEM", 0), ("PK m", 40), ("E", 62), ("N", 88)):
        _texto_pdf(c, TABLE_X + dx, yy, etiqueta, INK, "Helvetica", 4.9)
    yy -= 4.6
    for row in pc[:38]:
        _texto_pdf(c, TABLE_X, yy, f"{row['id']} {row['codigo_gisem']}", RED, "Helvetica", 4.6)
        _texto_pdf(c, TABLE_X + 40, yy, f"{float(row['estacion_m']):.0f}", INK, "Helvetica", 4.6)
        _texto_pdf(c, TABLE_X + 62, yy, f"{float(row['este_m']):.0f}", INK, "Helvetica", 4.6)
        _texto_pdf(c, TABLE_X + 88, yy, f"{float(row['norte_m']):.0f}", INK, "Helvetica", 4.6)
        yy -= ROW_STEP
    if len(pc) > 38:
        _texto_pdf(c, TABLE_X, yy, f"+{len(pc) - 38} registros en CSV fuente", INK, "Helvetica", 4.7)
        yy -= ROW_STEP
    _texto_pdf(c, TABLE_X, yy - 4, "UTM EPSG:32719; PK estacion GIS acumulada.",
               INK, "Helvetica", 5.0)
    _texto_pdf(c, TABLE_X, yy - 10, "PC no es poste aprobado; verificar en campo.",
               RED, "Helvetica", 5.0)
    _texto_pdf(c, MAP_X + 3, MAP_Y - 7.0,
               "Marcas PC/PN/CV son cartograficas de gabinete; ninguna es estructura aprobada.",
               RED, "Helvetica", 6.0)
    c.showPage()
    c.save()


def _a4_texto_pagina(c, num_pag, total_pag, titulo, lineas_inicio: float) -> float:
    c.setPageSize(A4)
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.rect(12 * MM, 12 * MM, 186 * MM, 273 * MM, stroke=1, fill=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(18 * MM, 276 * MM,
                 "EXPEDIENTE TECNICO CON IMAGEN SATELITAL - CORREDOR CAPACHICA-LLACHON")
    c.setFont("Helvetica", 6.8)
    c.drawString(18 * MM, 270 * MM, "Anteproyecto cartografico de red MT | Borrador academico")
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(18 * MM, 16 * MM, "NO APTO PARA CONSTRUCCION")
    c.setFillColor(INK)
    c.setFont("Helvetica", 6.5)
    c.drawRightString(192 * MM, 16 * MM, f"Pagina {num_pag} de {total_pag}")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(18 * MM, 260 * MM, titulo)
    c.setFont("Helvetica", 8.2)
    return lineas_inicio * MM


def _a4_parrafo(c, y_mm: float, texto: str, tam=8.2, ancho_chars=98, interlineado=4.4,
                color=INK, fuente="Helvetica") -> float:
    for linea in textwrap.wrap(texto, ancho_chars):
        c.setFillColor(color)
        c.setFont(fuente, tam)
        c.drawString(18 * MM, y_mm * MM, linea)
        y_mm -= interlineado
    return y_mm


def expediente_a4(destino: Path, jpg_plancha: Path, meta: dict, lineas, pc, pn, cv,
                  reporte: dict) -> None:
    total_pag = 8
    c = canvas.Canvas(str(destino), pagesize=A4, invariant=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(18 * MM, 245 * MM, "EXPEDIENTE TECNICO CON")
    c.drawString(18 * MM, 235 * MM, "IMAGEN SATELITAL")
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(BLUE)
    c.drawString(18 * MM, 220 * MM, "Corredor de media tension Capachica - Llachon")
    c.setFillColor(INK)
    c.setFont("Helvetica", 9.5)
    lineas_portada = [
        "Proyecto: Anteproyecto cartografico de red MT Capachica-Llachon (27 tramos GIS)",
        "Autor: Br. Renzo Gabriel Mamani Galindo (Cod. 228447)",
        "Curso: MEC330 - Instalaciones Electricas II | Semestre 2026-II",
        "Institucion: Universidad Nacional del Altiplano - FIME - Puno",
        "Docentes: Ing. Leonidas Vilca Callata / Ing. Marcos Jose Villanueva Cornejo",
        f"Fecha de generacion: {reporte['generado_utc']} UTC",
    ]
    y = 208.0
    for texto in lineas_portada:
        c.drawString(18 * MM, y * MM, texto)
        y -= 6.0
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(18 * MM, (y - 2) * MM, "BORRADOR ACADEMICO - NO APTO PARA CONSTRUCCION")
    y -= 14.0
    c.drawImage(ImageReader(str(jpg_plancha)), 18 * MM, (y - 78) * MM,
                174 * MM, 78 * MM, preserveAspectRatio=True, anchor="c")
    _texto_pdf(c, 18, y - 84, "Imagen satelital de contexto (ESRI World Imagery); el eje azul "
               "es el KML manual de cuatro segmentos.", INK, "Helvetica", 7)
    c.showPage()

    c.setPageSize(A4)
    y = _a4_texto_pagina(c, 2, total_pag, "Indice y resumen ejecutivo", 250)
    indice = [
        "1. Portada y control de generacion",
        "2. Indice y resumen ejecutivo",
        "3. Memoria descriptiva del corredor",
        "4. Imagen satelital: procedencia, metodo y limites",
        "5. Cuadro de estructuras PC (referencias GIS, 40 registros)",
        "6. Cuadro de sitios PN (27) y cruces CV (44)",
        "7. Fuentes, limites de interpretacion y pendientes criticos",
        "8. Control de calidad y trazabilidad",
        "Plancha A3 satelital CL-01-SAT | Plano de planta con imagen satelital",
        "Plancha A3 simbolica CL-01 | Plano de planta simbolico del corredor",
    ]
    for item in indice:
        y = _a4_parrafo(c, y, item, tam=8.6, interlineado=4.8)
    y -= 4.0
    y = _a4_parrafo(c, y, "Resumen ejecutivo", tam=10, fuente="Helvetica-Bold", interlineado=5.4)
    resumen = (
        f"Corredor de {meta['longitud_kml_m']:.1f} m medido sobre el KML manual "
        f"(cuatro segmentos con brechas de {meta['brechas_m']}) y {meta['longitud_gis_m']:.2f} m "
        f"sobre la ruta GIS alternativa de 27 tramos entre las estructuras GISEM "
        f"{meta['origen']} y {meta['final']}. Se colocan automaticamente "
        f"{len(pc)} referencias PC como bloques en el plano de planta; "
        f"{len(pn)} sitios PN se dibujan como circulos y {len(cv)} cruces CV como alertas OSM. "
        "Ninguna de esas marcas es una estructura aprobada. La imagen satelital "
        "es de contexto (resolucion aproximada a la indicada en la pagina 4) y no "
        "sustituye levantamiento topografico. El expediente no contiene calculos "
        "electricos ni mecanicos ni presupuesto: siguen pendientes los datos criticos "
        "enumerados en la pagina 7."
    )
    y = _a4_parrafo(c, y, resumen, tam=8.2)
    c.showPage()

    c.setPageSize(A4)
    y = _a4_texto_pagina(c, 3, total_pag, "Memoria descriptiva del corredor", 250)
    memoria = [
        "Objeto: evaluar la red de media tension publicada entre el entorno de Capachica y "
        "el de Llachon, y definir la informacion necesaria para decidir si corresponde "
        "reforzarla, ampliarla o mantenerla.",
        f"Puntos de referencia: inicio GISEM {meta['origen']} (entorno de Capachica) y final "
        f"GISEM {meta['final']} (entorno de Llachon); la continuidad calculada es una "
        "inferencia GIS, no una verificacion en terreno.",
        "Traza: KML manual de cuatro segmentos trazado sobre imagen satelital, sin uniones "
        "inventadas entre brechas; la ruta GIS alternativa se conserva como eje de comparacion.",
        "Estructuras: 40 referencias PC GISEM a 25 m o menos del KML (pendientes de campo), "
        "27 sitios PN para replanteo (geometria de gabinete) y 44 alertas CV de cruces OSM "
        "(indicios cartograficos). Los intervalos entre PN no son vanos.",
        "Imagen satelital: mosaico ESRI World Imagery reproyectado a UTM 19S y georreferenciado "
        "con archivo de mundo PGW y PRJ; sirve como base de ubicacion de la planta.",
        "Estado: borrador cartografico para revision. No es expediente de construccion ni "
        "acredita una linea nueva. La ingenieria electrica y mecanica esta pendiente de "
        "datos del operador, topografia de precision y aprobacion de conexion.",
    ]
    for parrafo in memoria:
        y = _a4_parrafo(c, y, parrafo, tam=8.2, interlineado=4.3)
        y -= 3.0
    c.showPage()

    c.setPageSize(A4)
    y = _a4_texto_pagina(c, 4, total_pag, "Imagen satelital: procedencia, metodo y limites", 250)
    procedencia = [
        f"Fuente raster: ESRI World Imagery, servicio ArcGIS REST publico "
        f"(MapServer de teselas), patrón {ESRI_TILE_URL.format(z='<z>', y='<y>', x='<x>')}.",
        f"Consulta: {reporte['generado_utc']} UTC. Zoom {reporte['zoom']}; "
        f"{reporte['teselas_descargadas']} teselas JPEG de 256 px descargadas y conservadas "
        f"en {TILES_DIR}/ con manifiesto SHA-256 individual.",
        f"Resolucion aproximada en el paralelo central del corredor: "
        f"{reporte['resolucion_m_px']:.2f} m/px. Mosaico reproyectado de EPSG:3857 a "
        f"EPSG:32719 con transformacion pyproj y remuestreo bilineal; tamano de rejilla "
        f"{reporte['rejilla_px'][0]} x {reporte['rejilla_px'][1]} px.",
        f"Georreferencia: {PNG_NAME} mas archivo de mundo {PGW_NAME} (convencion de centro "
        f"de pixel) y {PRJ_NAME} con WKT EPSG:32719. La imagen se inserta en el DXF como "
        f"entidad IMAGE en metros UTM y en las planchas A3 como raster.",
        "Limites: es imagenes de contexto de proveedor comercial; no tiene certificado de "
        "ortorrectificacion, precision planimetrica documentada ni fecha de captura "
        "verificada. No sirve para medir distancias de seguridad, cotas, gálibos, "
        "servidumbres ni replanteo. Toda distancia de obra debe salir del levantamiento "
        "topografico y del plano ejecutivo firmado.",
    ]
    for parrafo in procedencia:
        y = _a4_parrafo(c, y, parrafo, tam=8.2, interlineado=4.3)
        y -= 3.0
    y = _a4_parrafo(c, y, "Coordenadas UTM del recorte generado:", tam=8.6,
                    fuente="Helvetica-Bold", interlineado=4.6)
    bbox = reporte["bbox_utm_m"]
    y = _a4_parrafo(c, y, f"Este {bbox[0]:.1f} a {bbox[2]:.1f} m | "
                          f"Norte {bbox[1]:.1f} a {bbox[3]:.1f} m (EPSG:32719)",
                    tam=8.2, interlineado=4.3)
    c.showPage()

    c.setPageSize(A4)
    y = _a4_texto_pagina(c, 5, total_pag, "Cuadro de estructuras PC - referencias GIS", 250)
    y = _a4_parrafo(c, y,
                    "40 registros: estructuras GISEM situadas a 25 m o menos del KML manual. "
                    "Pendientes de verificacion de existencia, codigo y estado en campo; "
                    "no son postes nuevos aprobados.", tam=7.8, interlineado=4.2)
    y -= 3.0
    columnas = [(0, "ID / GISEM"), (42, "SEG"), (52, "PK m"), (74, "E"), (108, "N"),
                (142, "Dist. eje m")]
    for dx, etiqueta in columnas:
        _texto_pdf(c, 18 + dx, y, etiqueta, INK, "Helvetica-Bold", 6.8)
    y -= 5.0
    c.setStrokeColor(INK)
    c.setLineWidth(0.3)
    c.line(18 * MM, (y + 1.6) * MM, 192 * MM, (y + 1.6) * MM)
    for row in pc:
        valores = [(0, row["id"] + " " + row["codigo_gisem"]),
                   (42, row["segmento"]), (52, f"{float(row['estacion_m']):.0f}"),
                   (74, f"{float(row['este_m']):.1f}"),
                   (108, f"{float(row['norte_m']):.1f}"),
                   (142, f"{float(row['distancia_eje_m']):.1f}")]
        for dx, valor in valores:
            _texto_pdf(c, 18 + dx, y, valor, RED if dx == 0 else INK, "Helvetica", 6.4)
        y -= 4.3
    y -= 3.0
    _texto_pdf(c, 18, y, "UTM EPSG:32719; PK = estacion acumulada de la capa GIS.",
               INK, "Helvetica", 6.6)
    c.showPage()

    c.setPageSize(A4)
    y = _a4_texto_pagina(c, 6, total_pag, "Cuadro PN (27) y cruces CV (44)", 250)
    y = _a4_parrafo(c, y,
                    "PN: sitios geometricos derivados del KML con filtro de gabinete "
                    "(turno >= 20 grados o extremos). Para inspeccion y evaluacion de apoyo; "
                    "no son postes aprobados ni se deben instalar sin diseno.",
                    tam=7.8, interlineado=4.2)
    y -= 3.0
    for dx, etiqueta in [(0, "ID"), (22, "SEG"), (32, "PK KML m"), (56, "E"), (90, "N"),
                         (124, "Funcion preliminar")]:
        _texto_pdf(c, 18 + dx, y, etiqueta, INK, "Helvetica-Bold", 6.8)
    y -= 5.0
    c.line(18 * MM, (y + 1.6) * MM, 192 * MM, (y + 1.6) * MM)
    for row in pn:
        funcion = row["funcion_preliminar"][:36]
        valores = [(0, row["id"]), (22, row["segmento"]),
                   (32, f"{float(row['progresiva_kml_m']):.0f}"),
                   (56, f"{float(row['este_utm19s_m']):.1f}"),
                   (90, f"{float(row['norte_utm19s_m']):.1f}"), (124, funcion)]
        for dx, valor in valores:
            _texto_pdf(c, 18 + dx, y, valor, CYAN if dx == 0 else INK, "Helvetica", 6.2)
        y -= 4.3
    y -= 4.0
    y = _a4_parrafo(c, y, f"Cruces CV: {len(cv)} alertas de interseccion con cartografia OSM "
                          "(indicios geometricos). Clases registradas:",
                    tam=7.8, interlineado=4.2, fuente="Helvetica-Bold")
    clases: dict[str, int] = {}
    for row in cv:
        clave = (row.get("highway_osm") or "sin clase").strip()
        clases[clave] = clases.get(clave, 0) + 1
    for clave in sorted(clases):
        y = _a4_parrafo(c, y, f"- {clave}: {clases[clave]} cruces", tam=7.6, interlineado=4.1)
    y = _a4_parrafo(c, y, "Cada CV requiere medicion en campo de tipo, ancho, cota, glibo, "
                          "servidumbre y permiso antes de diseñar el cruce.",
                    tam=7.6, interlineado=4.1)
    c.showPage()

    c.setPageSize(A4)
    y = _a4_texto_pagina(c, 7, total_pag, "Fuentes, limites y pendientes criticos", 250)
    fuentes = [
        "KML manual (sources/ruta topografica capachica llachon.kml): cuatro segmentos, "
        f"{meta['longitud_kml_m']:.3f} m UTM, SHA-256 registrado en sources/manifest.json. "
        "Geometria no validada en campo.",
        "GISEM Osinergmin (servicio Redes Media Tension, consultado 14-10-2026 UTC): "
        "27 tramos y estructuras de inventario; origen NMT000367723 y final NMT000027963. "
        "La ubicacion GIS no confirma estado, titularidad ni capacidad.",
        "OpenStreetMap (ODbL): caminos como contexto y cruces CV. La cartografia vial no "
        "define el trazo electrico.",
        "SRTM30m (Open Topo Data): 57 muestras de contexto sobre la ruta GIS. Resolucion "
        "insuficiente para glibos, vanos o implantacion.",
        f"ESRI World Imagery: imagen satelital de contexto consultada {reporte['generado_utc']} UTC.",
    ]
    for item in fuentes:
        y = _a4_parrafo(c, y, item, tam=7.8, interlineado=4.2)
        y -= 2.0
    y -= 3.0
    y = _a4_parrafo(c, y, "Pendientes criticos (de proyecto.yaml):", tam=9,
                    fuente="Helvetica-Bold", interlineado=5.0)
    pendientes = [
        "comprobacion de red y extremos en campo; topografia apta para diseno",
        "tension y capacidad confirmadas por el operador; punto de conexion aprobado",
        "demanda actual y proyectada; inventario de equipos y estructuras",
        "servidumbres y cruces verificados",
    ]
    for item in pendientes:
        y = _a4_parrafo(c, y, "- " + item, tam=7.8, interlineado=4.2)
    y = _a4_parrafo(c, y, "Mientras esos datos no existan, cualquier cifra de postes, vanos, "
                          "flechas, despejes o presupuesto seria inventada y queda fuera de "
                          "este documento.", tam=7.8, interlineado=4.2, color=RED)
    c.showPage()

    c.setPageSize(A4)
    y = _a4_texto_pagina(c, 8, total_pag, "Control de calidad y trazabilidad", 250)
    y = _a4_parrafo(c, y, "Integridad SHA-256 de las salidas de esta generacion:",
                    tam=8.6, fuente="Helvetica-Bold", interlineado=4.8)
    for nombre, digest in reporte["sha256"].items():
        y = _a4_parrafo(c, y, f"{nombre}: {digest}", tam=6.6, ancho_chars=130,
                        interlineado=3.8, fuente="Courier")
    y -= 4.0
    y = _a4_parrafo(c, y, "Conteos verificados frente a las fuentes:", tam=8.6,
                    fuente="Helvetica-Bold", interlineado=4.8)
    conteos = reporte["conteos"]
    for clave, valor in conteos.items():
        y = _a4_parrafo(c, y, f"- {clave}: {valor}", tam=7.8, interlineado=4.2)
    y -= 4.0
    y = _a4_parrafo(c, y, "Verificacion automatizada (verify): reapertura del DXF con auditoria "
                          "ezdxf, unidades metros, 1 entidad IMAGE en modelo y 1 en la lamina "
                          "A3, 4 polilineas de eje, inserciones de bloque PC, PGW/PRJ del "
                          "mosaico y tamanos A4/A3 de los PDF.", tam=7.8, interlineado=4.2)
    y = _a4_parrafo(c, y, "Las pruebas del repositorio validan software y trazabilidad, "
                          "no la ingenieria de construccion. Este documento no sustituye la "
                          "revision y firma de un profesional responsable.",
                    tam=7.8, interlineado=4.2, color=RED)
    c.showPage()
    c.save()


def _unir_pdf(destino: Path, partes: list[Path]) -> None:
    writer = PdfWriter()
    for parte in partes:
        with parte.open("rb") as stream:
            reader = PdfReader(stream)
            for pagina in reader.pages:
                writer.add_page(pagina)
    with destino.open("wb") as stream:
        writer.write(stream)


def verificar(salida: Path, lineas, pc, pn, cv) -> dict:
    errores = []
    doc = ezdxf.readfile(salida / DXF_NAME)
    if doc.audit().has_errors:
        errores.append("DXF con errores de auditoria")
    if doc.header["$INSUNITS"] != 6:
        errores.append("DXF sin unidades metros")
    modelo = doc.modelspace()
    imagenes = [e for e in modelo if e.dxftype() == "IMAGE"]
    if len(imagenes) != 1:
        errores.append(f"Se esperaba 1 IMAGE en modelo, hay {len(imagenes)}")
    eje = [e for e in modelo if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "EJE_KML"]
    if len(eje) != 4:
        errores.append(f"Eje KML incompleto: {len(eje)} segmentos")
    inserts = [e for e in modelo if e.dxftype() == "INSERT" and e.dxf.name == "POSTE_CAC_PLANTA"]
    if len(inserts) != len(pc):
        errores.append(f"INSERTS PC {len(inserts)} != {len(pc)}")
    ubicaciones = {(round(e.dxf.insert.x, 3), round(e.dxf.insert.y, 3)) for e in inserts}
    esperadas = {(round(float(r["este_m"]), 3), round(float(r["norte_m"]), 3)) for r in pc}
    if ubicaciones != esperadas:
        errores.append("Coordenadas INSERTS PC distintas del CSV")
    circulos_pn = [e for e in modelo if e.dxftype() == "CIRCLE" and e.dxf.layer == "PN_CANDIDATO"]
    if len(circulos_pn) != len(pn):
        errores.append(f"Registros PN {len(circulos_pn)} != {len(pn)}")
    cruces = [e for e in modelo if e.dxftype() == "LINE" and e.dxf.layer == "CV_OSM"]
    if len(cruces) != 2 * len(cv):
        errores.append(f"Registros CV {len(cruces) // 2} != {len(cv)}")
    if "CL-01_PLANTA_A3" not in doc.layouts:
        errores.append("Falta la lamina A3 CL-01_PLANTA_A3")
    else:
        paper = doc.layouts.get("CL-01_PLANTA_A3")
        if sum(e.dxftype() == "IMAGE" for e in paper) != 1:
            errores.append("La lamina A3 no contiene la imagen satelital")
    for nombre_archivo in (PNG_NAME, PGW_NAME, PRJ_NAME, JPEG_NAME,
                           PLANCHA_SAT_PDF, PLANCHA_PLANTA_PDF, EXPEDIENTE_PDF):
        if not (salida / nombre_archivo).is_file():
            errores.append(f"Falta {nombre_archivo}")
    reporte = {}
    if (salida / REPORT_NAME).is_file():
        reporte = json.loads((salida / REPORT_NAME).read_text(encoding="utf-8"))
    else:
        errores.append(f"Falta {REPORT_NAME}")
    for nombre_archivo in (PNG_NAME, DXF_NAME, PLANCHA_SAT_PDF, EXPEDIENTE_PDF):
        if reporte and reporte.get("sha256", {}).get(nombre_archivo) != sha(salida / nombre_archivo):
            errores.append(f"SHA-256 no coincide: {nombre_archivo}")
    pgw = (salida / PGW_NAME).read_text(encoding="utf-8").split()
    if reporte and len(pgw) == 6:
        if abs(float(pgw[0]) - reporte["resolucion_m_px"]) > 1e-6:
            errores.append("PGW no coincide con la resolucion del reporte")
        if abs(float(pgw[4]) - (reporte["bbox_utm_m"][0] + float(pgw[0]) / 2.0)) > 1e-3:
            errores.append("PGW no coincide con el bbox del reporte")
    else:
        errores.append("PGW invalido")
    with Image.open(salida / PNG_NAME) as im:
        if reporte and list(im.size) != list(reporte["rejilla_px"]):
            errores.append("Tamano PNG distinto al reporte")
    for pdf, ancho_mm, alto_mm, etiqueta in (
            (PLANCHA_SAT_PDF, 420, 297, "plancha satelital"),
            (PLANCHA_PLANTA_PDF, 420, 297, "plancha planta"),
            (EXPEDIENTE_PDF, None, None, "expediente")):
        with (salida / pdf).open("rb") as stream:
            lector = PdfReader(stream)
            if etiqueta.startswith("plancha"):
                if len(lector.pages) != 1:
                    errores.append(f"{etiqueta}: {len(lector.pages)} paginas")
                pagina = lector.pages[0]
                if (abs(pagina.mediabox.width - ancho_mm * MM) > 1.0
                        or abs(pagina.mediabox.height - alto_mm * MM) > 1.0):
                    errores.append(f"{etiqueta}: no es A3 horizontal")
            else:
                if len(lector.pages) != 10:
                    errores.append(f"expediente: {len(lector.pages)} paginas (esperadas 10)")
                if "NO APTO PARA CONSTRUCCION" not in (lector.pages[0].extract_text() or ""):
                    errores.append("expediente: falta aviso en portada")
    tiles_manifesto = {}
    dir_tiles = salida / TILES_DIR
    if dir_tiles.is_dir():
        tiles_manifesto = json.loads((dir_tiles / "manifiesto.json").read_text(encoding="utf-8"))
    if reporte and tiles_manifesto != reporte.get("tiles_sha256"):
        errores.append("Manifiesto de teselas no coincide con el reporte")
    if errores:
        raise ValueError("Verificacion fallida: " + "; ".join(errores))
    return {"errores": 0, "inserts_pc": len(inserts), "tiles": len(tiles_manifesto)}


def generate(salida: Path = OUT_DIR, zoom: int = ZOOM) -> dict:
    claves = [DXF_NAME, PNG_NAME, PLANCHA_SAT_PDF, PLANCHA_PLANTA_PDF, EXPEDIENTE_PDF, REPORT_NAME]
    existentes = [n for n in claves if (salida / n).exists()]
    if existentes:
        raise FileExistsError(f"Ya existen salidas en {salida}: {', '.join(existentes)}; "
                              "archive antes de regenerar")
    lineas, _ruta, pc, pn, cv, _gaps, reconciliacion = read_inputs()[:7]
    if not (len(lineas) == 4 and len(pc) == 40 and len(pn) == 27 and len(cv) == 44):
        raise ValueError(f"Conteos fuente cambiaron: lineas={len(lineas)} pc={len(pc)} "
                         f"pn={len(pn)} cv={len(cv)}")
    bbox = calcular_bbox(lineas, pc, pn, cv, MARGIN_M)
    rango = cobertura_tiles(bbox, zoom)
    dir_tiles = salida / TILES_DIR
    mosaico, wm, manifiesto = descargar_mosaico(dir_tiles, zoom, rango)
    rgb, xmin, ymax, res = reproyectar_utm(mosaico, wm, bbox, zoom)
    png_path = salida / PNG_NAME
    salida.mkdir(parents=True, exist_ok=True)
    guardar_georeferenciado(png_path, rgb, xmin, ymax, res)
    jpg_plancha = crear_jpeg_plancha(png_path, salida / JPEG_NAME)
    img_bbox = (xmin, ymax - rgb.shape[0] * res, xmin + rgb.shape[1] * res, ymax)
    puntos = puntos_con_imagen(lineas, pc, pn, cv, img_bbox)
    transform, escala, limites = mapa_transform(puntos, MAP_X, MAP_Y, MAP_W, MAP_H)
    construir_dxf(salida / DXF_NAME, PNG_NAME, img_bbox, (rgb.shape[1], rgb.shape[0]),
                  lineas, pc, pn, cv)
    plancha_pdf(salida / PLANCHA_SAT_PDF, jpg_plancha, "CL-01-SAT",
                "Plano de planta con imagen satelital georreferenciada",
                "Eje KML manual; PC: referencias GIS pendientes; PN: sitios de gabinete; "
                "CV: cruces OSM | ESRI World Imagery (contexto)",
                transform, escala, limites, lineas, pc, pn, cv)
    plancha_pdf(salida / PLANCHA_PLANTA_PDF, None, "CL-01",
                "Plano de planta simbolico del corredor",
                "Eje KML manual; simbologia de gabinete PC/PN/CV sin imagen satelital",
                transform, escala, limites, lineas, pc, pn, cv)
    reporte = _construir_reporte(salida, zoom, res, bbox, rgb, pc, pn, cv, manifiesto,
                                 lineas, reconciliacion)
    temp_a4 = salida / "_expediente_a4.pdf"
    expediente_a4(temp_a4, jpg_plancha, reporte["meta"], lineas, pc, pn, cv, reporte)
    _unir_pdf(salida / EXPEDIENTE_PDF,
              [temp_a4, salida / PLANCHA_SAT_PDF, salida / PLANCHA_PLANTA_PDF])
    temp_a4.unlink()
    reporte["sha256"][EXPEDIENTE_PDF] = sha(salida / EXPEDIENTE_PDF)
    (dir_tiles / "manifiesto.json").write_text(
        json.dumps(manifiesto, indent=1, sort_keys=True), encoding="utf-8")
    (salida / REPORT_NAME).write_text(json.dumps(reporte, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    verificacion = verificar(salida, lineas, pc, pn, cv)
    reporte["verificacion"] = verificacion
    (salida / REPORT_NAME).write_text(json.dumps(reporte, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    return reporte


def _formato_brechas(reconciliacion: dict) -> str:
    lista = reconciliacion.get("brechas", [])
    if isinstance(lista, list) and lista and isinstance(lista[0], dict):
        detalle = ", ".join(f"{b.get('id', 'GAP')} {float(b['distancia_recta_m']):.2f} m"
                            for b in lista)
    else:
        detalle = "ver conciliacion"
    total = reconciliacion.get("suma_brechas_rectas_m")
    if isinstance(total, (int, float)):
        return f"{detalle} (suma {float(total):.2f} m)"
    return detalle


def _construir_reporte(salida: Path, zoom: int, res: float, bbox, rgb, pc, pn, cv,
                       manifiesto, lineas, reconciliacion: dict) -> dict:
    kml_m = sum(math.dist(linea[i], linea[i + 1]) for linea in lineas
                for i in range(len(linea) - 1))
    brechas = _formato_brechas(reconciliacion)
    generado = datetime.now(timezone.utc).isoformat(timespec="seconds")
    nombres_archivos = [PNG_NAME, DXF_NAME, PLANCHA_SAT_PDF, PLANCHA_PLANTA_PDF,
                        EXPEDIENTE_PDF, JPEG_NAME]
    return {
        "generado_utc": generado,
        "zoom": zoom,
        "teselas_descargadas": len(manifiesto),
        "resolucion_m_px": round(res, 6),
        "rejilla_px": [int(rgb.shape[1]), int(rgb.shape[0])],
        "bbox_utm_m": [round(v, 3) for v in bbox],
        "tiles_sha256": manifiesto,
        "sha256": {n: sha(salida / n) for n in nombres_archivos if (salida / n).is_file()},
        "conteos": {"segmentos_kml": len(lineas), "pc": len(pc), "pn": len(pn), "cv": len(cv)},
        "meta": {
            "longitud_kml_m": round(kml_m, 3),
            "longitud_gis_m": round(float(reconciliacion.get("longitud_gis_m", 13834.03)), 3),
            "brechas_m": brechas,
            "origen": "NMT000367723",
            "final": "NMT000027963",
        },
        "fuentes": {
            "imagen": "ESRI World Imagery ArcGIS REST MapServer tile",
            "url_patron": ESRI_TILE_URL,
            "kml": "sources/ruta topografica capachica llachon.kml",
            "pc": "datos/ubicaciones_postes_preliminares.csv",
            "pn": "datos/candidatos_nuevos_replanteo_rev3.csv",
            "cv": "datos/cruces_viales_rev3.csv",
        },
        "advertencia": ("Imagen satelital de contexto; PC/PN/CV no son estructuras aprobadas; "
                        "borrador academico no apto para construccion"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera plano de planta DXF con imagen satelital y expediente A4+A3")
    parser.add_argument("--salida", type=Path, default=OUT_DIR,
                        help="Carpeta de salida (no debe tener salidas previas)")
    parser.add_argument("--zoom", type=int, default=ZOOM,
                        help=f"Zoom de teselas satelitales (default {ZOOM}, rango 10-18)")
    args = parser.parse_args()
    if not 10 <= args.zoom <= 18:
        parser.exit(2, "Error: --zoom debe estar entre 10 y 18\n")
    try:
        reporte = generate(args.salida, args.zoom)
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"DXF: {args.salida / DXF_NAME}")
    print(f"Expediente: {args.salida / EXPEDIENTE_PDF}")
    print(f"Teselas: {reporte['teselas_descargadas']} | rejilla: "
          f"{reporte['rejilla_px']} px | {reporte['resolucion_m_px']:.2f} m/px")
    print(f"Verificacion: {reporte['verificacion']}")


if __name__ == "__main__":
    main()
