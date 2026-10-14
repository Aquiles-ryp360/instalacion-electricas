"""Prepara una carpeta académica georreferenciada sin aprobar el diseño de obra."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import ezdxf
import fitz
import requests
from PIL import Image, ImageDraw, ImageFont
from pyproj import CRS, Transformer
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "build" / ROOT.name / "presentacion_auditada_rev3"
URL = "https://gisem.osinergmin.gob.pe/serverosih/rest/services/OGC/PeruOsinergmin019RedesMediaTension/MapServer/22/query"
CODES = ("TMT000012389", "TMT001847370")
TO_UTM = Transformer.from_crs(4326, 32719, always_xy=True)
PLAN_NAMES = (
    "LP-01_PLANTA_LINEA_PRIMARIA_A3_AUTOCAD.dxf",
    "PL-01_PERFIL_LONGITUDINAL_A3_AUTOCAD.dxf",
    "U-01_DIAGRAMA_UNIFILAR_MT_A3_AUTOCAD.dxf",
    "D-01_ARMADOS_PS1_PA1_A3_AUTOCAD.dxf",
    "D-02_ARMADOS_PR1_SAB1_A3_AUTOCAD.dxf",
    "D-03_CIMENTACION_RETENIDA_PAT3_A3_AUTOCAD.dxf",
)
PLAN_PDFS = (
    "plano_LP01_planta_linea_primaria.pdf", "plano_PL01_perfil_longitudinal.pdf",
    "plano_U01_diagrama_unifilar_detalles.pdf", "plano_D01_armados_dge_ps1_pa1.pdf",
    "plano_D02_armados_dge_pr1_sab1.pdf", "plano_D03_detalles_cimentacion_retenida_pat.pdf",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distance_point_segment(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    u = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - u * dx, p[1] - a[1] - u * dy)


def get_source():
    params = {
        "where": "CODTRAMOMT IN ('TMT000012389','TMT001847370')",
        "outFields": "*", "returnGeometry": "true", "outSR": "4326", "f": "json",
    }
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    found = {feature["attributes"]["CODTRAMOMT"] for feature in data.get("features", [])}
    if found != set(CODES):
        raise ValueError(f"Tramos oficiales incompletos: {found}")
    return response.url, data


def route_points():
    path = ROOT / "datos/topografia/planilla_vertices_lp.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 13:
        raise ValueError("Planilla local de vertices incompleta")
    return [(float(row["este_m"]), float(row["norte_m"])) for row in rows], rows


def font(size, bold=False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size)


def draw_map(official, proposal, rows, gap):
    all_points = [p for line in official for p in line] + proposal
    xmin = min(p[0] for p in all_points) - 130
    xmax = max(p[0] for p in all_points) + 130
    ymin = min(p[1] for p in all_points) - 130
    ymax = max(p[1] for p in all_points) + 130
    width, height = 3200, 2200
    # Relación de aspecto cartográfica 1:1, sin deformación de distancia.
    span = max(xmax - xmin, (ymax - ymin) * width / height)
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    xmin, xmax = cx - span / 2, cx + span / 2
    dy = span * height / width
    ymin, ymax = cy - dy / 2, cy + dy / 2

    def pix(point):
        return (round((point[0] - xmin) * width / span),
                round((ymax - point[1]) * height / dy))

    im = Image.new("RGB", (width, height), "#f8fbfc")
    draw = ImageDraw.Draw(im)
    step = 100
    for x in range(math.ceil(xmin / step) * step, math.floor(xmax / step) * step + 1, step):
        px = pix((x, ymin))[0]
        draw.line((px, 0, px, height), fill="#d8e3e8", width=2)
        draw.text((px + 7, 12), f"{x} E", font=font(23), fill="#426070")
    for y in range(math.ceil(ymin / step) * step, math.floor(ymax / step) * step + 1, step):
        py = pix((xmin, y))[1]
        draw.line((0, py, width, py), fill="#d8e3e8", width=2)
        draw.text((12, py + 5), f"{y} N", font=font(23), fill="#426070")
    for line in official:
        draw.line([pix(p) for p in line], fill="#145783", width=15, joint="curve")
    draw.line([pix(p) for p in proposal], fill="#db7032", width=11, joint="curve")
    for label, point in (("E-01", proposal[0]), ("E-04", proposal[1]), ("E-09", proposal[-1])):
        x, y = pix(point)
        draw.ellipse((x-15, y-15, x+15, y+15), fill="#a62036", outline="white", width=4)
        draw.text((x+21, y-18), label, font=font(31, True), fill="#75182c",
                  stroke_width=4, stroke_fill="white")
    draw.rectangle((35, height-285, 1570, height-25), fill="#ffffff", outline="#809bac", width=3)
    draw.line((70, height-237, 210, height-237), fill="#145783", width=15)
    draw.text((235, height-257), "Tramos GISEM consultados: geometria oficial", font=font(30), fill="#19394d")
    draw.line((70, height-174, 210, height-174), fill="#db7032", width=11)
    draw.text((235, height-194), "Eje local propuesto: requiere replanteo", font=font(30), fill="#19394d")
    draw.text((70, height-115), f"Separacion E-01 a red GISEM: {gap:.1f} m", font=font(32, True), fill="#a62036")
    draw.text((70, height-65), "EPSG:32719 / WGS84 UTM 19S | SIN BASE SATELITAL", font=font(24), fill="#426070")
    draw.text((width-155, 95), "N", font=font(48, True), fill="#19394d")
    draw.line((width-125, 145, width-125, 245), fill="#19394d", width=8)
    draw.polygon(((width-125, 130), (width-145, 170), (width-105, 170)), fill="#19394d")
    image_path = OUT / "LP-00_MAPA_GEOREFERENCIADO_GISEM.png"
    im.save(image_path, dpi=(250, 250))
    cell = span / width
    (OUT / "LP-00_MAPA_GEOREFERENCIADO_GISEM.pgw").write_text(
        f"{cell:.12f}\n0\n0\n{-cell:.12f}\n{xmin + cell/2:.8f}\n{ymax - cell/2:.8f}\n", encoding="ascii")
    (OUT / "LP-00_MAPA_GEOREFERENCIADO_GISEM.prj").write_text(
        CRS.from_epsg(32719).to_wkt(), encoding="utf-8")
    return image_path, (xmin, ymin, xmax, ymax)


def make_dxf(official, proposal, bbox, gap):
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6  # metros en espacio modelo
    for name, color in (("RED_MT_GISEM", 5), ("EJE_LOCAL_PROPUESTO", 30),
                        ("EXTREMOS_POR_VALIDAR", 1), ("ROTULO", 7), ("AVISO", 1)):
        doc.layers.add(name, color=color)
    model = doc.modelspace()
    for line in official:
        model.add_lwpolyline(line, dxfattribs={"layer": "RED_MT_GISEM"})
    model.add_lwpolyline(proposal, dxfattribs={"layer": "EJE_LOCAL_PROPUESTO"})
    for point in (proposal[0], proposal[1], proposal[-1]):
        model.add_circle(point, radius=6, dxfattribs={"layer": "EXTREMOS_POR_VALIDAR"})
    sheet = doc.layouts.new("LP-00_A3")
    sheet.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
    sheet.add_lwpolyline([(8, 8), (412, 8), (412, 289), (8, 289), (8, 8)],
                         dxfattribs={"layer": "ROTULO"})
    sheet.add_viewport(center=(160, 160), size=(296, 240),
                       view_center_point=((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2),
                       view_height=(bbox[3]-bbox[1])*1.08)
    for msg, x, y, h, layer in (
        ("LP-00  UBICACION Y CONTRASTE GISEM", 12, 278, 6, "ROTULO"),
        ("WGS84 / UTM 19S - EPSG:32719", 12, 18, 3, "ROTULO"),
        ("CAPACHICA - CHIFRON | ESTUDIO ACADEMICO", 12, 12, 3, "ROTULO"),
        (f"E-01 a red citada: {gap:.1f} m", 308, 260, 3, "AVISO"),
        ("CONEXION NO VERIFICADA", 308, 251, 3, "AVISO"),
        ("Azul: GISEM oficial", 308, 231, 3, "ROTULO"),
        ("Naranja: eje local", 308, 222, 3, "ROTULO"),
        ("NO APTO PARA OBRA", 308, 203, 3.5, "AVISO"),
    ):
        sheet.add_text(msg, dxfattribs={"height": h, "layer": layer}).set_placement((x, y))
    path = OUT / "LP-00_UBICACION_GISEM_A3.dxf"
    doc.saveas(path)
    check = ezdxf.readfile(path)
    if check.audit().has_errors or check.header["$INSUNITS"] != 6:
        raise ValueError("DXF georreferenciado inválido")
    return path


def make_map_pdf(image, gap):
    path = OUT / "LP-00_UBICACION_GISEM_A3.pdf"
    c = canvas.Canvas(str(path), pagesize=landscape(A3))
    w, h = landscape(A3)
    c.setFillColorRGB(.07, .22, .34)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, h-32, "LP-00 | UBICACION Y CONTRASTE DE RED MT")
    c.setFont("Helvetica", 9)
    c.drawString(30, h-49, "Capachica - Chifron | WGS84 / UTM 19S | EPSG:32719 | revision academica")
    c.drawImage(ImageReader(str(image)), 30, 78, width=w-60, height=h-145, preserveAspectRatio=False)
    c.setFillColorRGB(.62, .10, .15)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, 58, f"E-01 se ubica a {gap:.1f} m del tramo GISEM citado. Punto de conexion por confirmar con Electro Puno.")
    c.setFillColorRGB(.17, .27, .32)
    c.setFont("Helvetica", 8)
    c.drawString(30, 42, "Fuente: consulta directa capa 22 GISEM/Osinergmin; eje naranja: planilla local. No es replanteo topografico.")
    c.drawString(30, 29, "Imagen con archivo de georreferencia PGW y proyeccion PRJ. Plano preliminar, no apto para construccion.")
    c.showPage(); c.save()
    return path


def make_cover(gap, length, source_url, date):
    path = OUT / "PORTADA_Y_DICTAMEN.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    c.setFillColorRGB(.08,.26,.40); c.rect(0,h-125,w,125,fill=1,stroke=0)
    c.setFillColorRGB(1,1,1); c.setFont("Helvetica-Bold",20)
    c.drawString(43,h-62,"CAPACHICA - CHIFRON")
    c.setFont("Helvetica",12);c.drawString(43,h-85,"Linea primaria MT | Carpeta academica para revision")
    c.setFillColorRGB(.12,.22,.30);c.setFont("Helvetica-Bold",13)
    c.drawString(43,h-165,"Dictamen de ubicacion")
    paragraphs = [
        f"El eje local de la planilla mide {length:.2f} m (EPSG:32719). Sus puntos son una propuesta documental, no un levantamiento validado.",
        f"La consulta directa a GISEM del {date} devuelve los tramos {', '.join(CODES)}. La distancia minima del E-01 local al tramo citado es {gap:.1f} m.",
        "Por esa separacion, la afirmacion anterior de que E-01 es una derivacion existente confirmada NO queda sustentada. Electro Puno debe confirmar el punto y la factibilidad.",
        "Los seis planos existentes se incluyen como antecedentes tecnicos para exposicion y llevan aviso de revision. Sus cotas, protecciones, servidumbre, costos y cumplimiento requieren validacion independiente.",
    ]
    y=h-195
    for paragraph in paragraphs:
        for line in __import__('textwrap').wrap(paragraph, 89):
            c.setFont("Helvetica",10);c.drawString(43,y,line);y-=15
        y-=13
    c.setFont("Helvetica-Bold",11);c.setFillColorRGB(.62,.10,.15)
    c.drawString(43,y-8,"ESTADO: PRESENTABLE PARA REVISION ACADEMICA")
    c.drawString(43,y-27,"NO APTO PARA CONSTRUCCION NI CONEXION")
    c.setFillColorRGB(.12,.22,.30);c.setFont("Helvetica",8)
    c.drawString(43,80,"Referencia: servicio GISEM/Osinergmin, capa Tramos de Media Tension (22).")
    c.drawString(43,66,"URL y JSON de respuesta incluidos en el paquete de revision.")
    c.drawString(43,52,"CNE Suministro 2011: referencia normativa; cumplimiento no verificado en esta carpeta.")
    c.showPage();c.save()
    return path


def dossier(cover, map_pdf):
    writer = PdfWriter()
    writer.append(str(cover));writer.append(str(map_pdf))
    for name in PLAN_PDFS:
        original = ROOT / "entregables/planos" / name
        with fitz.open(original) as src:
            if len(src) != 1:
                raise ValueError(f"Plano PDF con paginas inesperadas: {original}")
        reader = PdfReader(str(original))
        page = reader.pages[0]
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        overlay = io.BytesIO()
        c = canvas.Canvas(overlay, pagesize=(w,h))
        c.setFillColorRGB(.68,.12,.15);c.setFont("Helvetica-Bold",9)
        c.drawString(33,h-29,"REFERENCIAL - NO APTO PARA OBRA")
        c.showPage();c.save();overlay.seek(0)
        page.merge_page(PdfReader(overlay).pages[0])
        writer.add_page(page)
    path = OUT / "DOSSIER_PRESENTACION_ACADEMICA_REV3.pdf"
    with path.open("xb") as stream:
        writer.write(stream)
    with fitz.open(path) as pdf:
        if len(pdf) != 8:
            raise ValueError("Dossier incompleto")
        pdf[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT / "VISTA_PORTADA.png")
        pdf[1].get_pixmap(matrix=fitz.Matrix(1.0,1.0)).save(OUT / "VISTA_LP00.png")
    return path


def main():
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError("La carpeta Rev. 1 ya existe; no se sobrescribe")
    OUT.mkdir(parents=True, exist_ok=True)
    source_url, data = get_source()
    source_path = OUT / "GISEM_TRAMOS_22_RESPUESTA.json"
    source_path.write_text(json.dumps({"retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                                       "url": source_url, "response": data}, ensure_ascii=False, indent=2), encoding="utf-8")
    official = [[TO_UTM.transform(*point) for point in path]
                for feature in data["features"] for path in feature["geometry"]["paths"]]
    proposal, rows = route_points()
    gap = min(distance_point_segment(proposal[0], a, b)
              for line in official for a,b in zip(line,line[1:]))
    length = sum(math.dist(a,b) for a,b in zip(proposal,proposal[1:]))
    if gap < 50 or not 815 < length < 818:
        raise ValueError("Geometria de auditoria fuera del rango esperado; revisar entrada")
    image, bbox = draw_map(official, proposal, rows, gap)
    dxf = make_dxf(official, proposal, bbox, gap)
    map_pdf = make_map_pdf(image, gap)
    cover = make_cover(gap, length, source_url, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    pdf = dossier(cover, map_pdf)
    report = {
        "status":"ACADEMIC_REVIEW_ONLY_NOT_FOR_CONSTRUCTION",
        "crs":"EPSG:32719", "local_route_length_m":round(length,2),
        "gisem_gap_e01_m":round(gap,2), "gisem_codes":list(CODES),
        "source_url":source_url, "source_response_sha256":sha(source_path),
        "warning":"Punto de conexion, tension, capacidad, censo, equipos, topografia y servidumbre requieren confirmacion independiente.",
        "files_sha256":{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},
    }
    report_path=OUT/"MANIFIESTO_PRESENTACION_REV3.json"
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    archive=OUT/"PAQUETE_PRESENTACION_ACADEMICA_REV3.zip"
    with ZipFile(archive,"x",compression=ZIP_DEFLATED) as bundle:
        for path in OUT.iterdir():
            if path.is_file() and path != archive:
                bundle.write(path,arcname=path.name)
        for name in PLAN_NAMES:
            bundle.write(ROOT/"entregables/planos/autocad_lp"/name,
                         arcname="CAD_REFERENCIAL_NO_VERIFICADO/"+name)
    with ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("Paquete ZIP dañado")
    print(json.dumps({"output":str(OUT),"gap_e01_m":round(gap,2),"route_m":round(length,2),
                      "dossier_pages":8,"zip":str(archive)},ensure_ascii=False))


if __name__ == "__main__":
    main()
