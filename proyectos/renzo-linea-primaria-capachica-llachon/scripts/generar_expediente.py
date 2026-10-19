"""Expediente completo en un solo comando: motor LP 22,9 kV + planos EPIME Rev. 8 + ZIP.

    python scripts/generar_expediente.py --motor C:\\Users\\renzo\\EXP_LP\\motor

1. Aplica al motor los parches de datos/motor_lp229/*.patch (si faltan) y lo ejecuta
   con datos/motor_lp229/entrada/proyecto.yaml.
2. Copia sus resultados a datos/motor_lp229/resultados/ y las láminas de armados a plans/armados_lp229/.
3. Genera plans/LP_REV8.dxf/.pdf/.dwg y los DWG de los armados (AutoCAD u ODA File Converter).
4. Arma el paquete en ~/EXP_LP/b/: Vol. VII con los planos EPIME como principales,
   los del motor como complementarios y un DWG junto a cada DXF. Lo comprime en expediente/.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import planos_formato_epime as pe
import planos_motor_epime as pm

ROOT = Path(__file__).resolve().parents[1]
MOTOR_DATOS = ROOT / "datos" / "motor_lp229"
RAIZ = "EXPEDIENTE_LP_22_9_KV_CAPACHICA_LLACHON"
VOL7 = Path("Expediente Tecnico") / "VOL. VII PLANOS Y LAMINAS DE DETALLE"
EPIME = "PLANOS PRINCIPALES - FORMATO EPIME (REV. 8)"
COMPLEMENTARIOS = "PLANOS COMPLEMENTARIOS (MOTOR)"
ZIP = ROOT / "expediente" / "EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip"
PDF_UNICO = ROOT / "expediente" / "EXPEDIENTE_LP229_CAPACHICA_LLACHON_COMPLETO.pdf"
# ponytail: Word, ODA y rmtree fallan con rutas de más de 259 caracteres; la salida del motor y el
# armado del paquete van a rutas cortas fijas fuera del repositorio (regenerables, como build/).
SALIDA = Path.home() / "EXP_LP" / "s"
BUILD = Path.home() / "EXP_LP" / "b"


def parchear(motor: Path) -> None:
    for patch in sorted(MOTOR_DATOS.glob("*.patch")):
        ya = subprocess.run(["git", "apply", "--reverse", "--check", str(patch)], cwd=motor, capture_output=True)
        if ya.returncode:
            subprocess.run(["git", "apply", str(patch)], cwd=motor, check=True)


def correr_motor(motor: Path, salida: Path) -> None:
    parchear(motor)
    proy = motor / "proyectos" / "capachica-llachon"
    shutil.rmtree(proy, ignore_errors=True)
    shutil.copytree(MOTOR_DATOS / "entrada", proy)
    shutil.rmtree(salida, ignore_errors=True)
    subprocess.run([sys.executable, "generar.py", str(proy / "proyecto.yaml"), "--salida", str(salida)],
                   cwd=motor, check=True, env={**os.environ, "PYTHONUTF8": "1"})


def oda_carpeta(src: Path, dst: Path) -> None:
    """Todos los DXF de src -> DWG 2018 en dst (ODA, con AUDIT). Convierte en carpetas temporales
    porque ODA no abre rutas de más de 260 caracteres."""
    dst.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        for dxf in src.glob("*.dxf"):
            shutil.copy(dxf, a)
        subprocess.run([str(pe.ODA), a, b, "ACAD2018", "DWG", "0", "1", "*.DXF"], check=True, timeout=1800)
        for dwg in Path(b).glob("*.dwg"):
            shutil.copy(dwg, dst)
    faltan = {f.stem for f in src.glob("*.dxf")} - {f.stem for f in dst.glob("*.dwg")}
    if faltan:
        raise RuntimeError(f"ODA no convirtió: {sorted(faltan)}")


def copiar_resultados(salida: Path) -> None:
    for f in (MOTOR_DATOS / "resultados").iterdir():
        shutil.copy(salida / "trabajo" / f.name, f)
    lam = salida / RAIZ / VOL7 / "LAMINAS DE DETALLE"
    for dxf in (ROOT / "plans" / "armados_lp229").glob("*.dxf"):
        shutil.copy(lam / "DXF (AutoCAD)" / dxf.name, dxf)
        shutil.copy(lam / "PDF" / dxf.with_suffix(".pdf").name, dxf.with_suffix(".pdf"))


def planos() -> None:
    pm.generar()
    pe.dxf_a_dwg(pm.OUT_DXF)
    for dxf in sorted((ROOT / "plans" / "armados_lp229").glob("*.dxf")):
        pe.dxf_a_dwg(dxf)


def empaquetar(salida: Path) -> Path:
    build = BUILD
    shutil.rmtree(build, ignore_errors=True)
    shutil.copytree(salida / RAIZ, build / RAIZ)
    v7 = build / RAIZ / VOL7
    (v7 / "PLANOS").rename(v7 / COMPLEMENTARIOS)
    for sub in (COMPLEMENTARIOS, "LAMINAS DE DETALLE"):
        oda_carpeta(v7 / sub / "DXF (AutoCAD)", v7 / sub / "DWG (AutoCAD)")
    geo = v7 / "COORDENADAS Y PLANO GEORREFERENCIADO"
    oda_carpeta(geo, geo)
    ep = v7 / EPIME
    ep.mkdir()
    for ext in ("dwg", "dxf", "pdf"):
        shutil.copy(pm.OUT_DXF.with_suffix(f".{ext}"), ep)
    shutil.copy(ROOT / "documentacion" / "GUIA_AUTOCAD_EDITABLES.md", ep)
    ZIP.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted((build / RAIZ).rglob("*")):
            z.write(f, f.relative_to(build).as_posix())
    return build / RAIZ


VOLS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]


def _xlsx_a_pdf(xlsx: list[Path], dst: Path) -> dict[Path, Path]:
    """Excel sin PDF en el paquete -> PDF con Microsoft Excel (como el parche del motor)."""
    import win32com.client
    out = {}
    x = win32com.client.DispatchEx("Excel.Application"); x.Visible = False; x.DisplayAlerts = False
    try:
        for f in xlsx:
            out[f] = dst / f"{len(out):02d}.pdf"
            wb = x.Workbooks.Open(str(f), ReadOnly=True); wb.ExportAsFixedFormat(0, str(out[f])); wb.Close(False)
    finally:
        x.Quit()
    return out


def _dxf_a_pdf_a3(dxf: Path, dst: Path) -> Path:
    """Plano en coordenadas UTM sin PDF -> una hoja A3 ajustada (S/E)."""
    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
    from ezdxf.addons.drawing.config import BackgroundPolicy, Configuration
    doc = ezdxf.readfile(dxf)
    be = pymupdf.PyMuPdfBackend()
    Frontend(RenderContext(doc), be, config=Configuration(background_policy=BackgroundPolicy.WHITE)).draw_layout(doc.modelspace())
    dst.write_bytes(be.get_pdf_bytes(layout.Page(420, 297, layout.Units.mm, margins=layout.Margins.all(10))))
    return dst


def pdf_unico(raiz: Path, out: Path) -> int:
    """Todo el expediente en un PDF con marcadores: carátula, separador + documentos de cada volumen,
    planos (EPIME primero) e informe de verificación al final. Devuelve el número de páginas."""
    import fitz
    et = raiz / "Expediente Tecnico"
    dirs = {v: next(d for d in et.iterdir() if d.name.startswith(f"VOL. {v} ")) for v in VOLS}
    v7 = dirs["VII"]
    tmp = Path(tempfile.mkdtemp())
    sin_pdf = [f for f in et.rglob("*.xlsx") if not any(p.stem == f.stem for p in et.rglob("*.pdf"))]
    extra = _xlsx_a_pdf(sin_pdf, tmp)
    geo = next((v7 / "COORDENADAS Y PLANO GEORREFERENCIADO").glob("*.dxf"))
    extra[geo] = _dxf_a_pdf_a3(geo, tmp / "geo.pdf")

    def docs(v):
        d = dirs[v]
        if v == "VI":
            return [next(d.glob("*.pdf"))] + sorted((d / "ANEXOS" / "PDF").glob("*.pdf"))
        if v == "VII":
            return ([next((v7 / EPIME).glob("*.pdf"))] + sorted((v7 / "LAMINAS DE DETALLE" / "PDF").glob("*.pdf"))
                    + sorted((v7 / COMPLEMENTARIOS / "PDF").glob("*.pdf")) + [geo]
                    + [f for f in sin_pdf if f.parent.name.startswith("COORDENADAS")])
        if v == "IV":   # suministro antes que montaje, como en el índice
            return sorted(d.glob("*.pdf"), key=lambda p: "MONTAJE" in p.name)
        return sorted(d.glob("*.pdf")) + [f for f in sin_pdf if f.parent == d]

    car = fitz.open(next((raiz / "CARATULA Y SEPARADORES").glob("*.pdf")))
    sep = {}
    for i, p in enumerate(car):
        m = re.search(r"VOLUMEN (\w+)\s", p.get_text())
        if i > 2 and m and m.group(1) in VOLS:
            sep[m.group(1)] = i
    pdf, toc = fitz.open(), []
    pdf.insert_pdf(car, from_page=0, to_page=2)
    toc.append([1, "Carátula y contenido", 1])
    for v in VOLS:
        toc.append([1, dirs[v].name, len(pdf) + 1])
        if v in sep:
            pdf.insert_pdf(car, from_page=sep[v], to_page=sep[v])
        for f in docs(v):
            toc.append([2, f.stem, len(pdf) + 1])
            pdf.insert_pdf(fitz.open(extra.get(f, f)))
    toc.append([1, "Informe de generación y verificación", len(pdf) + 1])
    pdf.insert_pdf(fitz.open(next(raiz.glob("00 INFORME*.pdf"))))
    pdf.set_toc(toc)
    pdf.set_metadata({"title": "Expediente técnico LP 22,9 kV Capachica–Llachón (Rev. 8)",
                      "author": "Renzo Gabriel Mamani Galindo", "subject": "Revisor: Leonidas Vilca Callata"})
    pdf.save(out, garbage=4, deflate=True)
    return len(pdf)


def verificar(raiz: Path) -> list[str]:
    """Rutas del paquete que aún dicen «Por designar» (Word, Excel, DXF)."""
    pat = re.compile(rb"(?i)por designar")
    malos = []
    for f in raiz.rglob("*"):
        if f.suffix in (".docx", ".xlsx"):
            z = zipfile.ZipFile(f)
            if any(pat.search(z.read(n)) for n in z.namelist() if n.endswith(".xml")):
                malos.append(str(f))
        elif f.suffix == ".dxf" and pat.search(f.read_bytes()):
            malos.append(str(f))
    return malos


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--motor", type=Path, required=True, help="clon de github.com/dilmar231gabriel-ops/expediente-lp-22.9kv")
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--sin-motor", action="store_true", help="reusar la salida del motor que ya está en --salida")
    a = ap.parse_args()
    if not a.sin_motor:
        correr_motor(a.motor.resolve(), a.salida)
    copiar_resultados(a.salida)
    planos()
    raiz = empaquetar(a.salida)
    malos = verificar(raiz)
    print(f"{ZIP} ({ZIP.stat().st_size // 1024} KB)")
    print(f"{PDF_UNICO} ({pdf_unico(raiz, PDF_UNICO)} páginas, {PDF_UNICO.stat().st_size // 1024} KB)")
    if malos:
        sys.exit("Con «Por designar»: " + ", ".join(malos))


if __name__ == "__main__":
    main()
