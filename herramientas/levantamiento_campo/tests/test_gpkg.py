from pathlib import Path

import geopandas as gpd
import pyogrio
import pytest
from shapely.geometry import LineString, Point

from herramientas.levantamiento_campo.gpkg import create_template, validate
from herramientas.linea_primaria_preliminar.generar import route_for_project


def _route(path: Path, project_id: str = "p-001", document: str | None = "acta-01") -> None:
    frame = gpd.GeoDataFrame([{
        "id_proyecto": project_id, "id_eje": "EJE-01", "estado": "levantado",
        "fuente": "levantamiento GNSS", "metodo": "RTK",
        "fecha_registro": "2026-10-14T12:00:00-05:00", "responsable": "equipo de campo",
        "precision_h_m": 0.03, "precision_v_m": 0.05,
        "datum_vertical": "EGM2008", "documento_ref": document,
    }], geometry=[LineString([(-70.0, -15.0), (-70.01, -15.01)])], crs="EPSG:4326")
    pyogrio.write_dataframe(frame, path, layer="eje", driver="GPKG", append=True)


def test_template_and_formal_route_import(tmp_path):
    path = tmp_path / "campo.gpkg"
    create_template(path)
    assert dict(pyogrio.list_layers(path)) == {"eje": "LineString", "observaciones": "Point"}
    with pytest.raises(FileExistsError):
        create_template(path)
    _route(path)
    report, points = validate(path, "p-001")
    assert report["estado"] == "datos_de_campo_validos_formalmente"
    assert report["apto_para_diseno"] is False
    assert points == [(-70.0, -15.0), (-70.01, -15.01)]
    imported, source = route_for_project({"id": "p-001", "levantamiento_campo": path.name}, tmp_path)
    assert imported == points
    assert source["modo"] == "eje_de_campo_importado"
    assert source["sha256"] == report["sha256"]


def test_rejects_missing_route_for_another_project(tmp_path):
    path = tmp_path / "campo.gpkg"
    create_template(path)
    _route(path)
    report, points = validate(path, "p-002")
    assert points is None
    assert "exactamente un eje" in report["errores"][0]


def test_surveyed_route_needs_document_reference(tmp_path):
    path = tmp_path / "campo.gpkg"
    create_template(path)
    _route(path, document=None)
    report, points = validate(path, "p-001")
    assert points is None
    assert any("falta referencia" in error for error in report["errores"])


def test_rejects_observed_height_without_vertical_metadata(tmp_path):
    path = tmp_path / "campo.gpkg"
    create_template(path)
    _route(path)
    frame = gpd.GeoDataFrame([{
        "id_proyecto": "p-001", "id_observacion": "CR-01", "categoria": "cruce",
        "fuente": "campo", "fecha_registro": "2026-10-14T12:00:00-05:00",
        "responsable": "equipo de campo", "precision_h_m": 0.04,
        "cota_m": 3800.0,
    }], geometry=[Point(-70.005, -15.005)], crs="EPSG:4326")
    pyogrio.write_dataframe(frame, path, layer="observaciones", driver="GPKG", append=True)
    report, points = validate(path, "p-001")
    assert points is None
    assert any("cota sin precisión vertical o datum" in e for e in report["errores"])
