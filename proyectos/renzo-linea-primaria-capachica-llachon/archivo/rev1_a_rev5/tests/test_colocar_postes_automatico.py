"""Colocación automática de postes: software, trazabilidad y bloqueos.

Las pruebas usan datos sintéticos en tmp_path; no certifican ingeniería.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import ezdxf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from colocar_postes_automatico import (  # noqa: E402
    DXF_NAME, REQUIRED_FIELDS, REPORT_NAME,
    generate, read_estructuras, verify,
)

FILAS = [
    {
        "id": "E-001", "codigo_gisem": "NMT000367723", "segmento": "1",
        "progresiva_m": "0.00", "este_m": "410865.19", "norte_m": "8270474.22",
        "utm": "EPSG:32719", "tipo_poste": "CAC 12/400", "armado": "PR-1",
        "angulo_deflexion_grados": "0.00", "retenida": "NINGUNA",
        "pat": "PAT-3", "observaciones": "derivación MT",
    },
    {
        "id": "E-002", "codigo_gisem": "", "segmento": "2",
        "progresiva_m": "0.68", "este_m": "410791.122", "norte_m": "8270307.183",
        "utm": "EPSG:32719", "tipo_poste": "CAC 13/400 BIPOSTE", "armado": "SAB-1",
        "angulo_deflexion_grados": "-35.20", "retenida": "R-1",
        "pat": "NINGUNO", "observaciones": "SED biposte 100 kVA",
    },
    {
        "id": "E-003", "codigo_gisem": "", "segmento": "2",
        "progresiva_m": "45.00", "este_m": "410734.435", "norte_m": "8270237.829",
        "utm": "EPSG:32719", "tipo_poste": "CAC 12/300", "armado": "PS-1",
        "angulo_deflexion_grados": "12.11", "retenida": "NINGUNA",
        "pat": "NINGUNO", "observaciones": "suspensión alineamiento",
    },
]


def escribir_csv(path: Path, filas: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(filas)


@pytest.fixture
def paquete(tmp_path):
    csv_path = tmp_path / "estructuras_aprobadas.csv"
    escribir_csv(csv_path, FILAS)
    salida = tmp_path / "salida"
    reporte = generate(csv_path, salida)
    return csv_path, salida, reporte


def test_bloques_insertados_en_coordenadas(paquete):
    csv_path, salida, _ = paquete
    doc = ezdxf.readfile(salida / DXF_NAME)
    modelo = doc.modelspace()
    inserts = [e for e in modelo if e.dxftype() == "INSERT"]
    por_bloque: dict[str, int] = {}
    for entity in inserts:
        por_bloque[entity.dxf.name] = por_bloque.get(entity.dxf.name, 0) + 1
    assert por_bloque == {
        "POSTE_CAC_PLANTA": 2, "SED_BIPOSTE": 1,
        "PAT3_PLANTA": 1, "RETENIDA_R1": 1,
    }
    ubicaciones = {
        (round(e.dxf.insert.x, 3), round(e.dxf.insert.y, 3))
        for e in inserts if e.dxf.name in ("POSTE_CAC_PLANTA", "SED_BIPOSTE")
    }
    assert (410865.19, 8270474.22) in ubicaciones
    assert (410791.122, 8270307.183) in ubicaciones
    assert (410734.435, 8270237.829) in ubicaciones
    pat = [e for e in inserts if e.dxf.name == "PAT3_PLANTA"][0]
    assert (round(pat.dxf.insert.x, 3), round(pat.dxf.insert.y, 3)) == (
        round(410865.19 + 3.8, 3), round(8270474.22 - 4.2, 3))


def test_verificacion_y_rechazo_sobrescritura(paquete):
    csv_path, salida, reporte = paquete
    assert verify(salida, csv_path)["total_estructuras"] == 3
    assert reporte["csv_sha256"] == hashlib.sha256(csv_path.read_bytes()).hexdigest()
    assert reporte["bloques_usados"]["POSTE_CAC_PLANTA"] == 2
    assert reporte["por_segmento"] == {"1": 1, "2": 2}
    assert reporte["alertas_lejanas_eje"] == []
    with pytest.raises(FileExistsError):
        generate(csv_path, salida)


def test_lamina_a3_y_eje_en_modelo(paquete):
    _, salida, _ = paquete
    doc = ezdxf.readfile(salida / DXF_NAME)
    assert "CL-01_POSTES_A3" in doc.layouts
    modelo = doc.modelspace()
    eje = [e for e in modelo if e.dxftype() == "LWPOLYLINE"
           and e.dxf.layer == "EJE_KML"]
    assert len(eje) == 4


def test_rechaza_coordenadas_fuera_de_rango(tmp_path):
    filas = [dict(FILAS[0])]
    filas[0]["este_m"] = "12345.0"
    escribir_csv(tmp_path / "malo.csv", filas)
    with pytest.raises(ValueError, match="Este fuera de rango"):
        generate(tmp_path / "malo.csv", tmp_path / "salida")


def test_rechaza_columnas_faltantes(tmp_path):
    (tmp_path / "malo.csv").write_text("id,este_m,norte_m\nE-001,1,2\n",
                                       encoding="utf-8-sig")
    with pytest.raises(ValueError, match="faltan columnas"):
        generate(tmp_path / "malo.csv", tmp_path / "salida")


def test_rechaza_csv_ausente(tmp_path):
    with pytest.raises(FileNotFoundError, match="estructuras_aprobadas"):
        generate(tmp_path / "no_existe.csv", tmp_path / "salida")


def test_rechaza_progresivas_desordenadas(tmp_path):
    filas = [dict(FILAS[1]), dict(FILAS[2])]
    filas[0]["progresiva_m"] = "90.0"
    filas[1]["progresiva_m"] = "45.0"
    escribir_csv(tmp_path / "malo.csv", filas)
    with pytest.raises(ValueError, match="no monótonas"):
        generate(tmp_path / "malo.csv", tmp_path / "salida")


def test_plantilla_tiene_solo_encabezados():
    with (ROOT / "datos/estructuras_aprobadas_plantilla.csv").open(
            encoding="utf-8-sig", newline="") as stream:
        filas = list(csv.reader(stream))
    assert filas == [REQUIRED_FIELDS]


def test_lista_aprobada_ausente_es_bloqueo_explicito():
    with pytest.raises(FileNotFoundError):
        read_estructuras(ROOT / "datos/estructuras_aprobadas.csv")


def test_reporte_es_json_valido(paquete):
    _, salida, _ = paquete
    reporte = json.loads((salida / REPORT_NAME).read_text(encoding="utf-8"))
    assert set(reporte) >= {"csv_sha256", "total_estructuras", "bloques_usados",
                            "con_pat", "con_retenida", "advertencia"}
