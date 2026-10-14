"""Controles de la carpeta georreferenciada usada para revisión académica."""

import json
from pathlib import Path
from zipfile import ZipFile

import ezdxf
import fitz
import pytest


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "build" / ROOT.name / "presentacion_auditada_rev3"


def test_local_presentation_when_available():
    report_path = OUT / "MANIFIESTO_PRESENTACION_REV3.json"
    if not report_path.exists():
        pytest.skip("Carpeta local de presentación todavía no generada")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "ACADEMIC_REVIEW_ONLY_NOT_FOR_CONSTRUCTION"
    assert report["crs"] == "EPSG:32719"
    assert report["local_route_length_m"] == 816.6
    assert 130 < report["gisem_gap_e01_m"] < 134
    source = json.loads((OUT / "GISEM_TRAMOS_22_RESPUESTA.json").read_text(encoding="utf-8"))
    assert {f["attributes"]["CODTRAMOMT"] for f in source["response"]["features"]} == set(report["gisem_codes"])

    doc = ezdxf.readfile(OUT / "LP-00_UBICACION_GISEM_A3.dxf")
    assert doc.header["$INSUNITS"] == 6
    assert len(doc.audit().errors) == 0
    assert "LP-00_A3" in doc.layouts
    assert len(doc.modelspace().query('LWPOLYLINE[layer=="RED_MT_GISEM"]')) == 2
    assert len(doc.modelspace().query('LWPOLYLINE[layer=="EJE_LOCAL_PROPUESTO"]')) == 1

    worldfile = [float(value) for value in (OUT / "LP-00_MAPA_GEOREFERENCIADO_GISEM.pgw").read_text().split()]
    assert len(worldfile) == 6 and worldfile[0] > 0 and worldfile[3] < 0
    assert "32719" in (OUT / "LP-00_MAPA_GEOREFERENCIADO_GISEM.prj").read_text()

    with fitz.open(OUT / "DOSSIER_PRESENTACION_ACADEMICA_REV3.pdf") as pdf:
        assert len(pdf) == 8
        assert "131.8 m" in pdf[0].get_text()
        assert all("REFERENCIAL" in pdf[i].get_text() for i in range(2, 8))
    with ZipFile(OUT / "PAQUETE_PRESENTACION_ACADEMICA_REV3.zip") as bundle:
        assert bundle.testzip() is None
        assert len([name for name in bundle.namelist() if name.startswith("CAD_REFERENCIAL_NO_VERIFICADO/")]) == 6
