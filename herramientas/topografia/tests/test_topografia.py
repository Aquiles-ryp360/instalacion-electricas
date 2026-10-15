"""Prueba sin red del CAD, el raster y la trazabilidad de topografía preliminar."""

import importlib.util
import json
from pathlib import Path

import ezdxf
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

SCRIPT = Path(__file__).resolve().parents[1] / "generar_topografia.py"
SPEC = importlib.util.spec_from_file_location("generar_topografia", SCRIPT)
topografia = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(topografia)


def test_productos_coherentes_y_sin_sobrescritura(tmp_path):
    rows, cols = np.indices((30, 30))
    values = (3800 + rows * 1.5 + cols * 0.5).astype("float32")
    transform = from_origin(410000, 8271000, 30, 30)
    meta = {
        "crs": "EPSG:32719", "transform": transform,
        "bounds": (410000, 8270100, 410900, 8271000),
        "centro_utm_m": [410450, 8270550], "resolucion_salida_m": 30,
    }
    location = {"seleccion": {"nombre": "Lugar de prueba"}, "alternativas": []}
    output = tmp_path / "salida"
    report = topografia.write_products(
        output, values, meta, 10, location, [{"url": "fuente.tif", "resolucion_nominal_m": 30}],
    )
    assert report["estado"] == "topografia_preliminar_dem_no_apta_para_diseno_de_obra"
    with rasterio.open(output / "modelo_elevacion_preliminar.tif") as raster:
        assert raster.crs.to_string() == "EPSG:32719"
        np.testing.assert_allclose(raster.read(1), values)
    dxf = ezdxf.readfile(output / "curvas_nivel_preliminares.dxf")
    assert not dxf.audit().has_errors
    curves = list(dxf.modelspace().query("LWPOLYLINE[layer=='CURVAS_DEM_PRELIMINAR']"))
    assert curves and all(curve.dxf.elevation % 10 == 0 for curve in curves)
    manifest = json.loads((output / "manifiesto.json").read_text(encoding="utf-8"))
    for filename, digest in manifest["archivos_sha256"].items():
        assert topografia.sha256(output / filename) == digest
    with pytest.raises(FileExistsError):
        topografia.write_products(output, values, meta, 10, location, [])


def test_tesela_y_crs_para_puno():
    assert topografia.utm_crs(-15.6, -69.8) == "EPSG:32719"
    assert topografia.tile_names((400000, 8270000, 401000, 8271000), "EPSG:32719") == [
        "S16_00_W070_00"
    ]
    assert "Copernicus_DSM_COG_10_S16_00_W070_00_DEM" in topografia.tile_url(
        "S16_00_W070_00", 30
    )
