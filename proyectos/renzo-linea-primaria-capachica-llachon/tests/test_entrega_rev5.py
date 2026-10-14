"""Integración Rev. 5: fuentes, modelos y planos, sin certificar ingeniería."""
import csv
import hashlib
import json
import sys
from pathlib import Path

import ezdxf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generar_entrega_rev5 import REV4, build, verify  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def package(tmp_path_factory):
    before = sha(REV4 / "manifest_entrega.json")
    output = tmp_path_factory.mktemp("rev5") / "delivery"
    build(output)
    assert sha(REV4 / "manifest_entrega.json") == before
    return output


def test_integridad_fuentes_y_formatos(package):
    manifest = verify(package)
    assert manifest["file_count"] >= 40
    assert manifest["rev4_manifest_sha256"] == sha(REV4 / "manifest_entrega.json")
    dxf = ezdxf.readfile(package / "06_PLANOS_EDITABLES/CL-06_REV5.dxf")
    model = dxf.modelspace()
    assert sum(e.dxf.layer == "KML" and e.dxftype() == "LWPOLYLINE" for e in model) == 4
    assert sum(e.dxf.layer == "BRECHA" and e.dxftype() == "LINE" for e in model) == 3


def test_entradas_reales_separadas_de_hipotesis(package):
    with (package / "02_DATOS_Y_CRITERIOS/DATOS_MAESTROS.csv").open(encoding="utf-8-sig", newline="") as fh:
        entries = list(csv.DictReader(fh))
    pending = [r for r in entries if r["estado"] == "pendiente"]
    assert len(pending) == 21
    assert all(r["valor"] == "dato requerido" for r in pending)
    with (package / "03_CALCULO_ELECTRICO/ESCENARIOS_ADIMENSIONALES.csv").open(encoding="utf-8-sig", newline="") as fh:
        scenarios = list(csv.DictReader(fh))
    assert len(scenarios) == 9 and all("hipótesis" in row["clase"] for row in scenarios)
    with (package / "04_CALCULO_MECANICO/SITIOS_PARA_INGRESO_CAMPO.csv").open(encoding="utf-8-sig", newline="") as fh:
        sites = list(csv.DictReader(fh))
    assert len(sites) == 27
    assert all(row["apoyo_aprobado"] == "" and row["despeje_calculado_m"] == "" for row in sites)


def test_prohibicion_sobrescritura(package):
    with pytest.raises(FileExistsError):
        build(package)


def test_manifiesto_detecta_edicion(package):
    path = package / "02_DATOS_Y_CRITERIOS/BRECHAS.csv"
    original = path.read_bytes()
    try:
        path.write_bytes(original + b"inconsistente\n")
        with pytest.raises(ValueError, match="hash/tamaño alterado"):
            verify(package)
    finally:
        path.write_bytes(original)
