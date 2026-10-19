"""Planta satelital: cobertura de teselas, reproyección, georreferenciado y bloqueos.

Las pruebas usan datos sintéticos en tmp_path (mosaicos JPEG 256×256, coordenadas
UTM reales del corredor); no descargan red ni certifican ingeniería.
"""
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generar_planta_satelital import (  # noqa: E402
    MAX_TILES, WM_R,
    calcular_bbox, cobertura_tiles, construir_dxf,
    guardar_georeferenciado, reproyectar_utm,
)

# Bbox real del corredor (margen 150 m), UTM 19S
BBOX = (408741.273, 8261241.633, 416167.768, 8270624.215)


def test_cobertura_tiles_limites_zoom():
    with pytest.raises(ValueError, match="Zoom fuera de rango"):
        cobertura_tiles(BBOX, -1)
    with pytest.raises(ValueError, match="Zoom fuera de rango"):
        cobertura_tiles(BBOX, 20)


def test_cobertura_tiles_zoom10_es_pequeno():
    tx0, tx1, ty0, ty1 = cobertura_tiles(BBOX, 10)
    total = (tx1 - tx0 + 1) * (ty1 - ty0 + 1)
    assert 1 <= total <= MAX_TILES
    assert tx0 <= tx1 and ty0 <= ty1


def test_cobertura_tiles_zoom18_excede_max():
    with pytest.raises(ValueError, match="demasiado grande"):
        cobertura_tiles(BBOX, 18)


def test_cobertura_tiles_punto_unico_da_una_tesela():
    tx0, tx1, ty0, ty1 = cobertura_tiles((408741.273, 8270474.0, 408741.273, 8270474.0), 10)
    assert tx0 == tx1 and ty0 == ty1


def test_reproyectar_utm_sintetica():
    # 2×2 teselas de 4×4 px (suficiente para bilineal)
    mosaico = np.zeros((8, 8, 3), dtype=np.uint8)
    mosaico[:, :, 0] = 128  # rojo medio
    zoom = 10
    # Web-Mercator del bbox a este zoom
    import math
    from pyproj import Transformer
    t = Transformer.from_crs(32719, 3857, always_xy=True)
    wm = [t.transform(x, y) for x, y in
          [(BBOX[0], BBOX[1]), (BBOX[0], BBOX[3]), (BBOX[2], BBOX[1]), (BBOX[2], BBOX[3])]]
    wx = [p[0] for p in wm]
    wy = [p[1] for p in wm]
    n = 2 ** zoom
    paso = 2 * math.pi * WM_R / n
    tx0 = math.floor((min(wx) + math.pi * WM_R) / paso)
    ty0 = math.floor((math.pi * WM_R - max(wy)) / paso)
    wm_res = paso / 256.0
    wm_meta = {"wm_x0": -math.pi * WM_R + tx0 * wm_res * 256.0,
               "wm_y0": math.pi * WM_R - ty0 * wm_res * 256.0,
               "wm_res": wm_res}
    rgb, xmin, ymax, res = reproyectar_utm(mosaico, wm_meta, BBOX, zoom)
    assert rgb.ndim == 3 and rgb.shape[2] == 3
    assert res > 0
    assert rgb.shape[0] > 10 and rgb.shape[1] > 10


def test_reproyectar_utm_bbox_vacio():
    mosaico = np.zeros((4, 4, 3), dtype=np.uint8)
    wm = {"wm_x0": 0.0, "wm_y0": 0.0, "wm_res": 1.0}
    # Bbox minúsculo que produce rejilla < 2 puntos
    with pytest.raises(ValueError, match="vacia"):
        reproyectar_utm(mosaico, wm, (0.0, 0.0, 0.1, 0.1), 19)


def test_guardar_georeferenciado_pgw_prj(tmp_path):
    rgb = np.zeros((10, 12, 3), dtype=np.uint8)
    rgb[:, :, 1] = 200
    png = tmp_path / "test.png"
    xmin, ymax, res = 408000.0, 8271000.0, 2.5
    guardar_georeferenciado(png, rgb, xmin, ymax, res)
    assert png.is_file()
    pgw = png.with_suffix(".pgw").read_text(encoding="utf-8").split()
    assert len(pgw) == 6
    assert abs(float(pgw[0]) - res) < 1e-9
    assert abs(float(pgw[3]) + res) < 1e-9  # norte negativo
    assert abs(float(pgw[4]) - (xmin + res / 2.0)) < 1e-6
    assert abs(float(pgw[5]) - (ymax - res / 2.0)) < 1e-6
    prj = png.with_suffix(".prj").read_text(encoding="utf-8")
    assert "UTM" in prj or "Transverse_Mercator" in prj


def test_descargar_mosaico_offline_tiles_sinteticas(tmp_path):
    """descargar_mosaico usa tiles pre-sembrados sin tocar la red."""
    from generar_planta_satelital import descargar_mosaico
    zoom = 10
    rango = cobertura_tiles(BBOX, zoom)
    tx0, tx1, ty0, ty1 = rango
    dir_tiles = tmp_path / "tiles"
    dir_tiles.mkdir()
    for x in range(tx0, tx1 + 1):
        for y in range(ty0, ty1 + 1):
            img = Image.new("RGB", (256, 256), (x % 256, y % 256, 64))
            img.save(dir_tiles / f"z{zoom}_{x}_{y}.jpg", "JPEG", quality=85)
    mosaico, meta, manifiesto = descargar_mosaico(dir_tiles, zoom, rango)
    assert mosaico.shape[0] == (ty1 - ty0 + 1) * 256
    assert mosaico.shape[1] == (tx1 - tx0 + 1) * 256
    assert meta["ancho_px"] == mosaico.shape[1]
    assert meta["alto_px"] == mosaico.shape[0]
    assert len(manifiesto) == (tx1 - tx0 + 1) * (ty1 - ty0 + 1)
    assert all(len(h) == 64 for h in manifiesto.values())


def test_construir_dxf_rehusa_sobrescritura(tmp_path):
    salida = tmp_path / "CL-01_TEST.dxf"
    salida.write_bytes(b"placeholder")
    with pytest.raises(FileExistsError, match="archive antes de regenerar"):
        construir_dxf(salida, "test.png", BBOX, (100, 100),
                      [[(408741.0, 8270474.0), (408750.0, 8270480.0)]],
                      [], [], [])


def test_construir_dxf_minimo(tmp_path):
    """Un DXF sintético con 1 línea, 1 PC, 1 PN y 1 CV pasa la auditoría."""
    import ezdxf
    salida = tmp_path / "CL-01_MIN.dxf"
    lineas = [[(408741.0, 8270474.0), (408760.0, 8270490.0)]]
    pc = [{"este_m": "408750.0", "norte_m": "8270480.0", "estacion_m": "0.0",
           "id": "PC-001", "codigo_gisem": "NMT000367723", "segmento": "1",
           "tipo_poste": "CAC 12/400", "armado": "PR-1"}]
    pn = [{"este_utm19s_m": "408755.0", "norte_utm19s_m": "8270485.0", "id": "PN-001"}]
    cv = [{"este_utm19s_m": "408745.0", "norte_utm19s_m": "8270477.0", "id": "CV-001"}]
    reporte = construir_dxf(salida, "test.png", BBOX, (3229, 4080),
                            lineas, pc, pn, cv)
    assert salida.is_file()
    doc = ezdxf.readfile(salida)
    assert doc.header["$INSUNITS"] == 6
    msp = doc.modelspace()
    inserts = [e for e in msp if e.dxftype() == "INSERT" and e.dxf.name == "POSTE_CAC_PLANTA"]
    assert len(inserts) == 1
    assert abs(inserts[0].dxf.insert.x - 408750.0) < 1e-6
    circulos = [e for e in msp if e.dxftype() == "CIRCLE" and e.dxf.layer == "PN_CANDIDATO"]
    assert len(circulos) == 1
    cruces = [e for e in msp if e.dxftype() == "LINE" and e.dxf.layer == "CV_OSM"]
    assert len(cruces) == 2
    assert "CL-01_PLANTA_A3" in doc.layouts
    assert reporte.get("inserts_pc") == 1
    assert reporte.get("imagenes") == 1


def test_calcular_bbox():
    lineas = [[(100.0, 200.0), (300.0, 400.0)]]
    pc = [{"este_m": "150.0", "norte_m": "250.0"}]
    pn = [{"este_utm19s_m": "120.0", "norte_utm19s_m": "220.0"}]
    cv = [{"este_utm19s_m": "280.0", "norte_utm19s_m": "380.0"}]
    x0, y0, x1, y1 = calcular_bbox(lineas, pc, pn, cv, margen=10.0)
    assert x0 == pytest.approx(90.0)
    assert y0 == pytest.approx(190.0)
    assert x1 == pytest.approx(310.0)
    assert y1 == pytest.approx(410.0)
