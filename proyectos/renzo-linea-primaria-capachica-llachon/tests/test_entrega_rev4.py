"""Controles de integración de la entrega, distintos de aprobación de ingeniería."""
import csv
import json
import sys
from pathlib import Path

import ezdxf
import fitz
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generar_entrega_rev4 import build, read_inputs, sha, verify  # noqa: E402


@pytest.fixture(scope="module")
def package(tmp_path_factory):
    output = tmp_path_factory.mktemp("entrega_rev4") / "paquete"
    source_sha = sha(ROOT / "sources/ruta topografica capachica llachon.kml")
    build(output)
    assert sha(ROOT / "sources/ruta topografica capachica llachon.kml") == source_sha
    return output


def test_fuentes_y_geometrias_controladas():
    lines, gis, pc, pn, cv, gaps, report, kml, gis_m, _ = read_inputs()
    assert len(lines) == 4 and sum(map(len, lines)) == 187
    assert len(gis) > 2 and (len(pc), len(pn), len(cv), len(gaps)) == (40, 27, 44, 3)
    assert kml == pytest.approx(report["longitud_kml_sin_empalmes_m"], abs=.001)
    assert gis_m == pytest.approx(report["longitud_gis_m"], abs=.001)


def test_paquete_se_reabre_y_conserva_fuentes(package):
    manifest = verify(package)
    assert manifest["file_count"] >= 60
    assert manifest["source_kml_sha256"] == sha(package / "08_DATOS_GIS_Y_CAMPO/KML_ORIGINAL.kml")
    for n in range(1, 6):
        code = f"CL-{n:02d}"
        assert not ezdxf.readfile(package / f"05_PLANOS_EDITABLES/{code}_REV4.dxf").audit().has_errors
        with fitz.open(package / f"04_PLANOS_PDF/{code}_REV4.pdf") as pdf:
            assert len(pdf) == 1


def test_registro_campo_y_presupuesto_sin_datos_inventados(package):
    with (package / "08_DATOS_GIS_Y_CAMPO/REGISTRO_REPLANTEO.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 114  # 40 PC + 27 PN + 44 CV + 3 extremos GAP
    assert all(not row["este_levantado_m"] and not row["fecha_inspeccion"] for row in rows)
    with (package / "06_METRADOS_Y_PRESUPUESTO/PRESUPUESTO_PENDIENTE.csv").open(encoding="utf-8-sig", newline="") as fh:
        budget = list(csv.DictReader(fh))
    assert budget and all(row["cantidad"] == "dato requerido" and row["precio_unitario_pen"] == "dato requerido" for row in budget)
    with (package / "02_MEMORIA_DESCRIPTIVA/PARAMETROS_PENDIENTES.json").open(encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["design_inputs_required"]


def test_manifiesto_detecta_alteracion(package):
    target = package / "01_INDICE_Y_CONTROL/CARATULA.md"
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\nCAMBIO NO REGISTRADO")
        with pytest.raises(ValueError, match="Manifiesto inconsistente"):
            verify(package)
    finally:
        target.write_bytes(original)
