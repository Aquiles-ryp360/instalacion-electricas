"""Exporta hojas CAD derivadas de DGE a PDF vectorial, sin rasterizarlas.

La vectorización procede de Potrace, no de redibujo por IA. El PDF conserva
los contornos del DXF y agrega un rótulo de procedencia separado del original.
"""
from pathlib import Path
import hashlib, json, sys

sys.path.insert(0, 'G:/Aquiles/dependencias-linea-primaria')
import ezdxf
import pymupdf
from ezdxf.addons.drawing import Frontend, RenderContext, config, layout
from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend
from ezdxf.math import BoundingBox2d

R = Path(__file__).resolve().parents[2]
LIB = R / 'build/biblioteca-dge/biblioteca'
OUT = R / 'build/biblioteca-dge/pdf-vectorial'
VERSION = 'CAD-vector-A3-1'
MM = 72 / 25.4


def exportar(entry):
    """Devuelve una lámina A3 con dibujo, cotas y tablas como vectores PDF."""
    OUT.mkdir(parents=True, exist_ok=True)
    source = LIB / entry['cad']
    target = OUT / (entry['bloque'] + '.pdf')
    record = target.with_suffix('.json')
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists() and record.exists():
        cached = json.loads(record.read_text(encoding='utf-8'))
        if cached['dxf_sha256'] == sha and cached['version'] == VERSION:
            return target

    doc = ezdxf.readfile(source)
    assert not doc.audit().errors
    assert not list(doc.modelspace().query('IMAGE'))
    backend = PyMuPdfBackend()
    settings = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.COLOR,
        min_lineweight=.01,
    )
    Frontend(RenderContext(doc), backend, config=settings).draw_layout(
        doc.modelspace(), finalize=True)
    width, height = entry['ancho_hoja_mm'], entry['alto_hoja_mm']
    raw = backend.get_pdf_bytes(
        layout.Page(width, height, layout.Units.mm),
        settings=layout.Settings(fit_page=False, scale=1, min_stroke_width=.01),
        render_box=BoundingBox2d([(0, 0), (width, height)]),
    )
    cad_pdf = pymupdf.open(stream=raw, filetype='pdf')
    assert not cad_pdf[0].get_images(full=True)
    final = pymupdf.open()
    paper_width,paper_height=(420,297) if width>height else (297,420)
    page = final.new_page(width=paper_width*MM, height=paper_height*MM)
    navy, teal, pale = (24/255, 54/255, 74/255), (40/255, 125/255, 137/255), (.93, .96, .97)
    page.draw_rect(pymupdf.Rect(12*MM, 12*MM, (paper_width-12)*MM, 35*MM), color=None, fill=pale)
    page.draw_rect(pymupdf.Rect(12*MM, 12*MM, 14*MM, 35*MM), color=None, fill=teal)
    page.insert_text((19*MM, 21*MM), f"DGE | {entry['familia']} | LÁMINA {entry['lamina']}",
                     fontsize=14, fontname='hebo', color=navy)
    page.insert_text((19*MM, 29*MM), 'Armado y componentes | CAD vectorizado de fuente normativa',
                     fontsize=9, fontname='helv', color=navy)
    # La hoja entera se incluye como Form XObject vectorial; no es una imagen.
    page.show_pdf_page(pymupdf.Rect(15*MM, 40*MM, (paper_width-15)*MM, (paper_height-29)*MM), cad_pdf, 0)
    page.draw_line((12*MM, (paper_height-23)*MM), ((paper_width-12)*MM, (paper_height-23)*MM), color=teal, width=.7)
    page.insert_text((15*MM, (paper_height-18)*MM),
        f"RD 024-2003-EM/DGE | Fuente PDF p. {entry['pagina_pdf']} | Rótulo original y tablas preservados",
        fontsize=8, fontname='helv', color=navy)
    page.insert_text((15*MM, (paper_height-12)*MM),
        'Derivado CAD; no archivo emitido por MINEM. Cotas originales prevalecen. Referencia documental.',
        fontsize=8, fontname='helv', color=navy)
    page.insert_text((15*MM, (paper_height-6)*MM),
        'Copia de mayor resolución: Esolutions REDLIN 2025-12. Contraste: PDF oficial MINEM.',
        fontsize=7.5, fontname='helv', color=navy)
    final.set_metadata({'title': f"DGE {entry['familia']} {entry['lamina']} - CAD vectorial",
                        'subject': 'Hoja completa, no detalle paramétrico; adaptación CAC pendiente',
                        'producer': 'ezdxf / PyMuPDF; vectores del DXF derivado de Potrace'})
    final.save(target, garbage=4, deflate=True)
    check = pymupdf.open(target)
    assert len(check) == 1 and not check[0].get_images(full=True)
    paths = len(check[0].get_drawings())
    assert paths > 5
    result = dict(version=VERSION, lamina=entry['lamina'], cad=entry['cad'],
                  dxf_sha256=sha, pdf_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  imagenes_raster=0, elementos_vectoriales=paths, formato='A3 horizontal' if width>height else 'A3 vertical',
                  dibujo_completo_con_rotulo=True)
    record.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('PDF vectorial', entry['lamina'], target.stat().st_size, 'bytes', flush=True)
    return target
