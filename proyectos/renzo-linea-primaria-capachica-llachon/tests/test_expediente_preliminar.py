"""Control del expediente Rev. 1 sin presentar información ausente como diseñada."""

import csv
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import fitz
import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT.parents[1] / "build" / ROOT.name


def test_editable_chapters_and_empty_construction_quantities():
    chapters = sorted((ROOT / "expediente").glob("0[0-6]_*.md"))
    assert len(chapters) == 7
    assert chapters[0].name.startswith("00_") and chapters[-1].name.startswith("06_")
    for chapter in chapters:
        assert len(chapter.read_text(encoding="utf-8")) > 900

    with (ROOT / "datos/matriz_metrados_pendientes.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) >= 8
    assert all(row["cantidad"] == "" and row["precio_unitario_pen"] == "" for row in rows)
    assert all(row["estado"] == "PENDIENTE" for row in rows)


def test_local_compiled_review_package_when_available():
    pdf = BUILD / "EXPEDIENTE_PRELIMINAR_CAPACHICA_LLACHON_REV1.pdf"
    archive = BUILD / "PAQUETE_REVISION_CAPACHICA_LLACHON_REV1.zip"
    report = BUILD / "MANIFIESTO_PAQUETE_REV1.json"
    if not pdf.exists():
        pytest.skip("PDF local de build no presente en este clon")
    if not archive.exists():
        pytest.skip("Paquete Rev. 1 local aún no generado")
    assert archive.exists() and report.exists()
    manifest = json.loads(report.read_text(encoding="utf-8"))
    assert manifest["status"] == "DRAFT_FOR_REVIEW_NOT_FOR_CONSTRUCTION"
    assert manifest["revision"] == "1"
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == manifest["pdf_sha256"]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["zip_sha256"]
    with fitz.open(pdf) as document:
        assert len(document) == 12
        assert "NO APTO PARA CONSTRUCCIÓN" in document[0].get_text()
        assert all(page.rect.width > page.rect.height for page in document[-2:])
    with ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        names = set(bundle.namelist())
        assert pdf.name in names
        assert "plans/CL-01_A3_AUTOCAD_PRELIMINAR.dxf" in names
        assert "plans/CL-02_A3_AUTOCAD_PRELIMINAR.dxf" in names
        assert "datos/matriz_metrados_pendientes.csv" in names
        assert all(f"expediente/{chapter.name}" in names for chapter in
                   (ROOT / "expediente").glob("0[0-6]_*.md"))
        assert names == {pdf.name, *manifest["included_files_sha256"]}
        historical = {
            "README.md": ROOT / "documentacion/respaldo_rev1/README_original.md",
            "proyecto.yaml": ROOT / "documentacion/respaldo_rev1/proyecto_original.yaml",
            "requirements.txt": ROOT / "documentacion/respaldo_rev1/requirements_original.txt",
            "tests/test_expediente_preliminar.py": ROOT / "documentacion/respaldo_rev1/test_expediente_preliminar_original.py",
        }
        for name, expected_sha in manifest["included_files_sha256"].items():
            assert hashlib.sha256(bundle.read(name)).hexdigest() == expected_sha
            # El paquete Rev. 1 conserva las fuentes de esa revisión; las activas ya son Rev. 2.
            assert hashlib.sha256(historical.get(name, ROOT / name).read_bytes()).hexdigest() == expected_sha
