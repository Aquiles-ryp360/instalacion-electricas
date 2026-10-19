"""Compila capítulos verificados y dos planos A3 en un PDF/ZIP de revisión.

No convierte este borrador en expediente aprobado. No sobrescribe salidas.
"""

from __future__ import annotations

import csv
import hashlib
import html as html_lib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import fitz
from bs4 import BeautifulSoup, NavigableString, Tag
from pypdf import PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, KeepTogether, LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, TableStyle


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BUILD = REPO / "build" / ROOT.name
PDF = BUILD / "EXPEDIENTE_PRELIMINAR_CAPACHICA_LLACHON_REV1.pdf"
ZIP = BUILD / "PAQUETE_REVISION_CAPACHICA_LLACHON_REV1.zip"
MANIFEST = BUILD / "MANIFIESTO_PAQUETE_REV1.json"
CHAPTERS = sorted((ROOT / "expediente").glob("0[0-6]_*.md"))
PLAN_PDFS = [
    ROOT / "plans/CL-01_ubicacion_corredor.pdf",
    ROOT / "plans/CL-02_perfil_referencial.pdf",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_inputs():
    if len(CHAPTERS) != 7:
        raise ValueError("Se esperaban los siete capítulos 00 a 06")
    with (ROOT / "datos/cuadro_tramos_gisem.csv").open(encoding="utf-8-sig", newline="") as stream:
        if len(list(csv.DictReader(stream))) != 27:
            raise ValueError("Cuadro GIS incompleto")
    project = json.loads((ROOT / "datos/parametros_diseno_pendientes.json").read_text(encoding="utf-8"))
    if project["status"] != "PRELIMINARY" or not all(
        value is None for value in project["derived_design_results"].values()
    ):
        raise ValueError("El expediente contiene resultados de diseño sin validación")
    for path in PLAN_PDFS:
        with fitz.open(path) as doc:
            if len(doc) != 1:
                raise ValueError(f"Plano anexo inesperado: {path}")


def html_from_chapters() -> str:
    markdown = "\n\n".join(path.read_text(encoding="utf-8") for path in CHAPTERS)
    result = subprocess.run(
        ["pandoc", "--from=markdown+pipe_tables", "--to=html5", "--standalone"],
        input=markdown, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return result.stdout


def inline_markup(node) -> str:
    if isinstance(node, NavigableString):
        return html_lib.escape(str(node))
    if not isinstance(node, Tag):
        return ""
    contents = "".join(inline_markup(child) for child in node.children)
    if node.name in ("strong", "b"):
        return f"<b>{contents}</b>"
    if node.name in ("em", "i"):
        return f"<i>{contents}</i>"
    if node.name == "code":
        return f'<font color="#164f79">{contents}</font>'
    if node.name == "a":
        href = node.get("href", "")
        if href.startswith(("https://", "http://")):
            return f'<link href="{html_lib.escape(href, quote=True)}" color="#145e98">{contents}</link>'
    if node.name == "br":
        return "<br/>"
    return contents


def render_core_pdf(markup: str, output: Path):
    pdfmetrics.registerFont(TTFont("ArialLocal", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("ArialLocal-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
    pdfmetrics.registerFontFamily("ArialLocal", normal="ArialLocal", bold="ArialLocal-Bold")
    base = dict(fontName="ArialLocal", textColor=colors.HexColor("#19344A"),
                leading=13.2, spaceAfter=5, allowWidows=0, allowOrphans=0)
    styles = {
        "body": ParagraphStyle("Body", fontSize=9.2, **base),
        "h1": ParagraphStyle("Heading1", fontName="ArialLocal-Bold", fontSize=17,
                             leading=21, textColor=colors.HexColor("#0E538B"),
                             spaceBefore=6, spaceAfter=13, keepWithNext=True),
        "cover": ParagraphStyle("Cover", fontName="ArialLocal-Bold", fontSize=23,
                                leading=29, textColor=colors.HexColor("#0E538B"),
                                spaceBefore=62, spaceAfter=25, keepWithNext=True),
        "h2": ParagraphStyle("Heading2", fontName="ArialLocal-Bold", fontSize=11.6,
                             leading=15, textColor=colors.HexColor("#155D93"),
                             spaceBefore=12, spaceAfter=6, keepWithNext=True),
        "h3": ParagraphStyle("Heading3", fontName="ArialLocal-Bold", fontSize=10,
                             leading=13, textColor=colors.HexColor("#256789"),
                             spaceBefore=8, spaceAfter=4, keepWithNext=True),
        "table": ParagraphStyle("Table", fontName="ArialLocal", fontSize=7.1,
                                leading=9.2, textColor=colors.HexColor("#17354B"),
                                splitLongWords=True),
        "table_header": ParagraphStyle("TableHeader", fontName="ArialLocal-Bold", fontSize=7.1,
                                       leading=9.2, textColor=colors.white,
                                       splitLongWords=True),
        "list": ParagraphStyle("List", fontName="ArialLocal", fontSize=9,
                               leading=12.5, textColor=colors.HexColor("#19344A"),
                               leftIndent=13, firstLineIndent=-9, spaceAfter=4),
    }
    soup = BeautifulSoup(markup, "html.parser")
    body = soup.body or soup
    story = []
    heading_count = 0

    def process(node):
        nonlocal heading_count
        if not isinstance(node, Tag):
            return
        if node.name == "h1":
            if heading_count:
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(node), styles["cover" if heading_count == 0 else "h1"]))
            heading_count += 1
        elif node.name in ("h2", "h3"):
            story.append(Paragraph(inline_markup(node), styles[node.name]))
        elif node.name == "p":
            story.append(Paragraph(inline_markup(node), styles["body"]))
        elif node.name in ("ul", "ol"):
            for index, item in enumerate(node.find_all("li", recursive=False), start=1):
                prefix = f"{index}. " if node.name == "ol" else "• "
                story.append(Paragraph(prefix + inline_markup(item), styles["list"]))
            story.append(Spacer(1, 2 * mm))
        elif node.name == "table":
            rows = node.find_all("tr")
            if not rows:
                return
            matrix = []
            columns = max(len(row.find_all(["th", "td"], recursive=False)) for row in rows)
            for row_index, row in enumerate(rows):
                cells = row.find_all(["th", "td"], recursive=False)
                matrix.append([
                    Paragraph(inline_markup(cells[col]),
                              styles["table_header" if row_index == 0 else "table"])
                    if col < len(cells) else "" for col in range(columns)
                ])
            widths = [(174 * mm) / columns] * columns
            table = LongTable(matrix, colWidths=widths, repeatRows=1, hAlign="LEFT",
                              splitByRow=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D5D96")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C9D7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.extend([Spacer(1, 2 * mm), table, Spacer(1, 3 * mm)])
        elif node.name == "hr":
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#AFC3D2")))
        else:
            for child in node.children:
                process(child)

    for child in body.children:
        process(child)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("ArialLocal", 7)
        canvas.setFillColor(colors.HexColor("#688096"))
        canvas.drawString(18 * mm, 12 * mm, "CAPACHICA - LLACHON | REV. 1 | BORRADOR")
        canvas.drawRightString(192 * mm, 12 * mm, f"Pagina {doc.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=18 * mm,
                                 rightMargin=18 * mm, topMargin=18 * mm,
                                 bottomMargin=20 * mm, title="Expediente preliminar Capachica-Llachon")
    document.build(story, onFirstPage=footer, onLaterPages=footer)


def package_files():
    wanted = [ROOT / "README.md", ROOT / "proyecto.yaml", ROOT / "requirements.txt",
              ROOT / "PLANTEAMIENTO_CAPACHICA_LLACHON.md"]
    for directory in ("expediente", "documentacion", "datos", "derived", "plans", "sources", "scripts", "tests"):
        wanted.extend(path for path in (ROOT / directory).rglob("*") if path.is_file()
                      and "__pycache__" not in path.parts and path.suffix not in (".pyc", ".bak"))
    return sorted(set(wanted), key=lambda path: str(path))


def main():
    validate_inputs()
    if any(path.exists() for path in (PDF, ZIP, MANIFEST)):
        raise FileExistsError("El paquete Rev. 1 ya existe; no se sobrescribe")
    BUILD.mkdir(parents=True, exist_ok=True)
    html = html_from_chapters()
    with tempfile.TemporaryDirectory() as temp_dir:
        core = Path(temp_dir) / "memoria_a4.pdf"
        render_core_pdf(html, core)
        writer = PdfWriter()
        writer.append(str(core))
        for plan in PLAN_PDFS:
            writer.append(str(plan))
        with PDF.open("xb") as output:
            writer.write(output)

    with fitz.open(PDF) as document:
        if len(document) < 9:
            raise ValueError("Faltan capítulos o láminas en el PDF")
        total_pages = len(document)
        sizes = [tuple(round(value, 2) for value in (page.rect.width, page.rect.height))
                 for page in document]
        for index, label in ((0, "portada"), (total_pages - 2, "plano_01"),
                             (total_pages - 1, "plano_02")):
            pix = document[index].get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False)
            pix.save(BUILD / f"REV1_QA_{label}.png")

    files = package_files()
    with ZipFile(ZIP, "x", compression=ZIP_DEFLATED) as bundle:
        bundle.write(PDF, arcname=PDF.name)
        for path in files:
            bundle.write(path, arcname=str(path.relative_to(ROOT)).replace("\\", "/"))
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DRAFT_FOR_REVIEW_NOT_FOR_CONSTRUCTION",
        "revision": "1",
        "chapter_count": len(CHAPTERS),
        "pdf_page_count": total_pages,
        "pdf_page_sizes_pt": sizes,
        "appended_plan_count": len(PLAN_PDFS),
        "pdf_sha256": digest(PDF),
        "zip_sha256": digest(ZIP),
        "source_chapters": {path.name: digest(path) for path in CHAPTERS},
        "included_files": [str(path.relative_to(ROOT)).replace("\\", "/") for path in files],
        "included_files_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path)
                                  for path in files},
        "warnings": [
            "Tensión, demanda, topografía, punto de conexión y alcance de obra pendientes.",
            "Los planos A3 son cartográficos y no aptos para construcción.",
            "AutoCAD no se ejecutó; los DXF fueron validados con ezdxf.",
        ],
    }
    with MANIFEST.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(f"PDF {total_pages} páginas: {PDF}")
    print(f"ZIP {len(files)+1} archivos: {ZIP}")


if __name__ == "__main__":
    main()
