"""Renderiza layouts A3 DXF con ezdxf como vista de control independiente de AutoCAD."""

from pathlib import Path

import ezdxf
import fitz
from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf


ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "plans"


def render(name: str, layout_name: str):
    source = PLANS / f"{name}.dxf"
    target = PLANS / f"{name}_vista.pdf"
    png = PLANS / f"{name}_vista.png"
    if target.exists() or png.exists():
        raise FileExistsError("Las vistas de control existentes no se sobrescriben")
    doc = ezdxf.readfile(source)
    sheet = doc.layouts.get(layout_name)
    backend = pymupdf.PyMuPdfBackend()
    Frontend(RenderContext(doc), backend).draw_layout(sheet)
    page = layout.Page.from_dxf_layout(sheet)
    target.write_bytes(backend.get_pdf_bytes(page))
    with fitz.open(target) as pdf:
        if len(pdf) != 1:
            raise ValueError("La vista CAD no produjo una página")
        pix = pdf[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        pix.save(png)
    print(source.name, target.name, png.name)


if __name__ == "__main__":
    render("CL-01_A3_AUTOCAD_PRELIMINAR", "CL-01_A3")
    render("CL-02_A3_AUTOCAD_PRELIMINAR", "CL-02_A3")
