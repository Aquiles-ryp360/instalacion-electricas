# -*- coding: utf-8 -*-
"""
Compila un expediente tecnico exclusivo para la Linea Primaria 22.9 kV.

Genera un PDF A4 con portada, memoria resumida, especificaciones, APU y
cronograma, y anexa las laminas A3 de linea primaria preservando su tamano.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
EXPEDIENTE_DIR = ROOT / "expediente"
PLANOS_DIR = ROOT / "entregables" / "planos"
TMP_DIR = ROOT / "tmp" / "pdfs"
TMP_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_TEXT = TMP_DIR / "expediente_linea_primaria_texto.pdf"
OUTPUT_FINAL = EXPEDIENTE_DIR / "expediente_linea_primaria_22_9kv_compilado.pdf"

PLANOS_LP = [
    ("LP-01", "Planta de linea primaria 22.9 kV", PLANOS_DIR / "plano_LP01_planta_linea_primaria.pdf"),
    ("PL-01", "Perfil longitudinal topografico y catenaria", PLANOS_DIR / "plano_PL01_perfil_longitudinal.pdf"),
    ("U-01", "Diagrama unifilar MT y limite de alcance", PLANOS_DIR / "plano_U01_diagrama_unifilar_detalles.pdf"),
    ("D-01", "Armados DGE PS-1 y PA-1", PLANOS_DIR / "plano_D01_armados_dge_ps1_pa1.pdf"),
    ("D-02", "Armados DGE PR-1 y SAB-1", PLANOS_DIR / "plano_D02_armados_dge_pr1_sab1.pdf"),
    ("D-03", "Cimentacion, retenida R-1 y puesta a tierra PAT-3", PLANOS_DIR / "plano_D03_detalles_cimentacion_retenida_pat.pdf"),
]


def register_fonts() -> tuple[str, str, str]:
    candidates = [
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/consola.ttf")),
        (Path("C:/Windows/Fonts/calibri.ttf"), Path("C:/Windows/Fonts/calibrib.ttf"), Path("C:/Windows/Fonts/consola.ttf")),
    ]
    for regular, bold, mono in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("DocRegular", str(regular)))
            pdfmetrics.registerFont(TTFont("DocBold", str(bold)))
            if mono.exists():
                pdfmetrics.registerFont(TTFont("DocMono", str(mono)))
                return "DocRegular", "DocBold", "DocMono"
            return "DocRegular", "DocBold", "Courier"
    return "Helvetica", "Helvetica-Bold", "Courier"


FONT, FONT_BOLD, FONT_MONO = register_fonts()


def clean_inline(text: str) -> str:
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("≤", "&le;").replace("≥", "&ge;")
    text = text.replace("Ø", "&Oslash;").replace("φ", "phi")
    text = text.replace("μ", "u").replace("Ω", "ohm")
    text = text.replace("°", "&deg;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    text = text.replace("$", "")
    return text


def strip_markdown_noise(line: str) -> str:
    line = line.strip()
    line = line.replace("`", "")
    line = line.replace("[!NOTE]", "NOTA")
    return line


def make_styles():
    base = getSampleStyleSheet()
    navy = colors.HexColor("#1F3A5F")
    teal = colors.HexColor("#0F766E")
    dark = colors.HexColor("#111827")
    muted = colors.HexColor("#475569")

    styles = {
        "cover_univ": ParagraphStyle(
            "cover_univ", parent=base["Normal"], fontName=FONT_BOLD, fontSize=12, leading=15,
            alignment=TA_CENTER, textColor=navy, spaceAfter=8
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Normal"], fontName=FONT_BOLD, fontSize=16, leading=21,
            alignment=TA_CENTER, textColor=navy, spaceBefore=10, spaceAfter=12
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", parent=base["Normal"], fontName=FONT_BOLD, fontSize=11, leading=16,
            alignment=TA_CENTER, textColor=dark, spaceAfter=10
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName=FONT_BOLD, fontSize=14, leading=18,
            textColor=navy, spaceBefore=14, spaceAfter=7
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName=FONT_BOLD, fontSize=11.5, leading=15,
            textColor=teal, spaceBefore=10, spaceAfter=5
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName=FONT_BOLD, fontSize=10, leading=13,
            textColor=navy, spaceBefore=7, spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontName=FONT, fontSize=9.2, leading=12.6,
            alignment=TA_JUSTIFY, textColor=dark, spaceAfter=4
        ),
        "small": ParagraphStyle(
            "small", parent=base["BodyText"], fontName=FONT, fontSize=8, leading=10,
            textColor=muted, spaceAfter=3
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["BodyText"], fontName=FONT, fontSize=8.8, leading=12,
            leftIndent=14, firstLineIndent=-8, textColor=dark, spaceAfter=2
        ),
        "pre": ParagraphStyle(
            "pre", parent=base["Code"], fontName=FONT_MONO, fontSize=6.5, leading=8,
            textColor=dark, backColor=colors.HexColor("#F8FAFC"), borderColor=colors.HexColor("#CBD5E1"),
            borderWidth=0.4, borderPadding=4, spaceBefore=3, spaceAfter=5
        ),
    }
    return styles


STYLES = make_styles()


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont(FONT, 7.5)
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.drawString(2.0 * cm, 28.4 * cm, "EXPEDIENTE TECNICO - LINEA PRIMARIA 22.9 kV - CHIFRON, CAPACHICA")
        canvas.drawRightString(A4[0] - 2.0 * cm, 28.4 * cm, "UNA PUNO - FIME")
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.line(2.0 * cm, 28.2 * cm, A4[0] - 2.0 * cm, 28.2 * cm)
        canvas.line(2.0 * cm, 1.7 * cm, A4[0] - 2.0 * cm, 1.7 * cm)
        canvas.drawString(2.0 * cm, 1.3 * cm, "Alcance: linea primaria MT, SED SAB-1, protecciones, retenidas y PAT-3")
        canvas.drawRightString(A4[0] - 2.0 * cm, 1.3 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def paragraph(text: str, style: str = "body") -> Paragraph:
    return Paragraph(clean_inline(text), STYLES[style])


def cover_story() -> list:
    story = [Spacer(1, 1.2 * cm)]
    story.append(paragraph("UNIVERSIDAD NACIONAL DEL ALTIPLANO - PUNO", "cover_univ"))
    story.append(paragraph("FACULTAD DE INGENIERIA MECANICA ELECTRICA, ELECTRONICA Y SISTEMAS", "cover_univ"))
    story.append(paragraph("ESCUELA PROFESIONAL DE INGENIERIA MECANICA ELECTRICA", "cover_univ"))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="88%", thickness=1.2, color=colors.HexColor("#1F3A5F")))
    story.append(paragraph("EXPEDIENTE TECNICO COMPILADO", "cover_title"))
    story.append(paragraph("LINEA PRIMARIA EN MEDIA TENSION 22.9 kV Y SUBESTACION BIPOSTE SAB-1 100 kVA", "cover_subtitle"))
    story.append(paragraph("SECTOR CHIFRON - DISTRITO DE CAPACHICA - PUNO", "cover_subtitle"))
    story.append(HRFlowable(width="88%", thickness=1.2, color=colors.HexColor("#1F3A5F")))
    story.append(Spacer(1, 0.7 * cm))

    data = [
        ["Proyectista", "Br. Renzo Gabriel Mamani Galindo"],
        ["Codigo universitario", "228447"],
        ["Curso", "MEC330 - Instalaciones Electricas II"],
        ["Docentes", "Ing. Leonidas Vilca Callata / Ing. Marcos Jose Villanueva Cornejo"],
        ["Alcance", "Linea primaria 22.9 kV, SED SAB-1, protecciones MT, retenidas, cimentaciones y PAT-3"],
        ["Exclusion expresa", "No desarrolla redes secundarias, acometidas domiciliarias ni alumbrado publico"],
        ["Fecha", "Octubre 2026"],
    ]
    table = Table(data, colWidths=[4.4 * cm, 10.6 * cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 8.8),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF6FF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    story.append(PageBreak())
    return story


def memoria_lp_story() -> list:
    items = [
        paragraph("CAPITULO I: MEMORIA DESCRIPTIVA DE LINEA PRIMARIA", "h1"),
        paragraph(
            "El presente expediente tecnico compila exclusivamente el alcance de linea primaria en media tension "
            "22.9 kV para el sector Chifron, distrito de Capachica, Puno. El sistema comprende la derivacion MT, "
            "nueve estructuras proyectadas E-01 a E-09, conductor AAAC 35 mm2, la subestacion biposte SAB-1 de "
            "100 kVA como punto de llegada y los elementos de proteccion, maniobra, retenida, cimentacion y puesta "
            "a tierra requeridos para su ejecucion.",
            "body",
        ),
        paragraph("1.1 Datos generales", "h2"),
    ]
    data = [
        ["Nivel de tension", "22.9 kV, trifasico, 3 hilos, 60 Hz"],
        ["Longitud de eje", "0.8166 km"],
        ["Estructuras MT", "9 unidades: E-01 a E-09"],
        ["Conductor", "AAAC 35 mm2, 7 hilos, diametro exterior 7.50 mm"],
        ["Vano critico", "E-05 a E-06, longitud 115.59 m"],
        ["Punto de derivacion", "E-01, cerro Chifron, cota 3924.17 msnm"],
        ["Punto de llegada", "E-04, SED SAB-1 100 kVA, cota 3839.56 msnm"],
        ["Estructura terminal", "E-09, progresiva 0+816.60 m"],
    ]
    table = Table(data, colWidths=[4.0 * cm, 11.0 * cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 8.4),
        ("LEADING", (0, 0), (-1, -1), 10.5),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    items.append(table)
    items.extend([
        paragraph("1.2 Criterios de diseno", "h2"),
        paragraph("Tension nominal 22.9 kV; aislamiento y proteccion corregidos por altitud de diseno mayor a 3800 msnm.", "bullet"),
        paragraph("Verificacion mecanica bajo hipotesis CNE de viento, hielo, temperatura minima, temperatura maxima y EDS.", "bullet"),
        paragraph("Uso de armados normalizados DGE PR-1, PS-1, PA-1 y SAB-1.", "bullet"),
        paragraph("Puestas a tierra PAT-3 con resistencia objetivo R <= 10 ohm en la subestacion y equipos MT.", "bullet"),
        paragraph("El expediente excluye expresamente el diseno de redes secundarias, acometidas domiciliarias y alumbrado publico.", "bullet"),
        paragraph("1.3 Planos compilados", "h2"),
    ])
    plan_data = [["Codigo", "Contenido", "Anexo"]]
    for code, title, path in PLANOS_LP:
        plan_data.append([code, title, f"Plano {code}"])
    plan_table = Table(plan_data, colWidths=[2.1 * cm, 8.8 * cm, 4.1 * cm])
    plan_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("LEADING", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    items.append(plan_table)
    items.append(PageBreak())
    return items


def markdown_to_story(path: Path, title: str) -> list:
    story = [paragraph(title, "h1")]
    lines = path.read_text(encoding="utf-8").splitlines()
    table_lines: list[str] = []
    code_lines: list[str] = []
    in_code = False

    def flush_table():
        nonlocal table_lines
        if table_lines:
            wrapped = []
            for row in table_lines:
                wrapped.extend(textwrap.wrap(row, width=118, subsequent_indent="  ") or [""])
            story.append(Preformatted("\n".join(wrapped), STYLES["pre"]))
            table_lines = []

    def flush_code():
        nonlocal code_lines
        if code_lines:
            story.append(Preformatted("\n".join(code_lines), STYLES["pre"]))
            code_lines = []

    for raw in lines:
        line = strip_markdown_noise(raw)
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_table()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line:
            flush_table()
            story.append(Spacer(1, 3))
            continue
        if line.startswith("|"):
            table_lines.append(line)
            continue
        flush_table()
        if line in {"---", "***"}:
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1")))
        elif line.startswith("### "):
            story.append(paragraph(line[4:], "h3"))
        elif line.startswith("## "):
            story.append(paragraph(line[3:], "h2"))
        elif line.startswith("# "):
            story.append(paragraph(line[2:], "h2"))
        elif line.startswith(("* ", "- ")):
            story.append(paragraph(line[2:], "bullet"))
        elif re.match(r"^\d+\.\s+", line):
            story.append(paragraph(line, "bullet"))
        elif line.startswith(">"):
            story.append(paragraph(line.lstrip("> ").strip(), "small"))
        else:
            story.append(paragraph(line, "body"))
    flush_table()
    flush_code()
    story.append(PageBreak())
    return story


def cronograma_lp_story() -> list:
    rows = [
        ["Fase", "Actividad exclusiva LP", "Duracion", "Periodo"],
        ["F-01", "Movilizacion y replanteo topografico de E-01 a E-09", "10 dias", "Dias 1-10"],
        ["F-02", "Excavacion de hoyos, zanjas de retenida y preparacion de PAT-3", "15 dias", "Dias 8-22"],
        ["F-03", "Izaje y cimentacion de postes CAC 12 m y 13 m", "18 dias", "Dias 18-35"],
        ["F-04", "Montaje de armados DGE PR-1, PS-1, PA-1 y SAB-1", "14 dias", "Dias 32-45"],
        ["F-05", "Instalacion de transformador, cut-outs, pararrayos y puesta a tierra", "12 dias", "Dias 42-53"],
        ["F-06", "Tendido, flechado y engrapado de conductor AAAC 35 mm2", "14 dias", "Dias 50-63"],
        ["F-07", "Pruebas de aislamiento, continuidad, puesta a tierra y energizacion", "7 dias", "Dias 64-70"],
    ]
    story = [paragraph("CAPITULO IV: CRONOGRAMA DE EJECUCION - LINEA PRIMARIA", "h1")]
    story.append(paragraph("Plazo referencial de ejecucion para el alcance de linea primaria: 70 dias calendario.", "body"))
    table = Table(rows, colWidths=[1.5 * cm, 8.0 * cm, 2.5 * cm, 3.0 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("LEADING", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    story.append(PageBreak())
    return story


def build_text_pdf() -> None:
    doc = SimpleDocTemplate(
        str(OUTPUT_TEXT),
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.1 * cm,
        bottomMargin=2.1 * cm,
        title="Expediente Tecnico Linea Primaria 22.9 kV Chifron Capachica",
        author="Br. Renzo Gabriel Mamani Galindo",
    )
    story: list = []
    story.extend(cover_story())
    story.extend(memoria_lp_story())
    story.extend(markdown_to_story(
        EXPEDIENTE_DIR / "02_tdr_especificaciones_tecnicas_linea_primaria_seace.md",
        "CAPITULO II: TERMINOS DE REFERENCIA Y ESPECIFICACIONES TECNICAS LP",
    ))
    story.extend(markdown_to_story(
        EXPEDIENTE_DIR / "03_analisis_precios_unitarios_linea_primaria_seace.md",
        "CAPITULO III: ANALISIS DE PRECIOS UNITARIOS Y PRESUPUESTO LP",
    ))
    story.extend(cronograma_lp_story())
    story.append(paragraph("CAPITULO V: ANEXO DE PLANOS DE LINEA PRIMARIA", "h1"))
    story.append(paragraph(
        "A continuacion se anexan las laminas oficiales del paquete de linea primaria. "
        "Las paginas anexas conservan su formato A3 horizontal original.",
        "body",
    ))
    story.append(PageBreak())
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def merge_with_plans() -> None:
    missing = [str(path) for _, _, path in PLANOS_LP if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan planos requeridos:\n" + "\n".join(missing))

    writer = PdfWriter()
    for page in PdfReader(str(OUTPUT_TEXT)).pages:
        writer.add_page(page)
    for _, _, plan_path in PLANOS_LP:
        reader = PdfReader(str(plan_path))
        for page in reader.pages:
            writer.add_page(page)
    with OUTPUT_FINAL.open("wb") as f:
        writer.write(f)


def main() -> None:
    build_text_pdf()
    merge_with_plans()
    reader = PdfReader(str(OUTPUT_FINAL))
    print(f"OK: {OUTPUT_FINAL}")
    print(f"Paginas: {len(reader.pages)}")


if __name__ == "__main__":
    main()
