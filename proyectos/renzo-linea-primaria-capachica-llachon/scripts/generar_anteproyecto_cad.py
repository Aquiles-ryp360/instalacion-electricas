"""Genera láminas A3 CAD y cuadro GIS; solo anteproyecto Capachica-Llachón.

Entradas: instantáneas GISEM, ruta inferida y cotas SRTM conservadas en el proyecto.
No dimensiona conductor, estructuras ni protecciones y nunca sobrescribe salidas.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import ezdxf
from pyproj import Transformer


ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "plans"
DATA = ROOT / "datos"
TO_UTM = Transformer.from_crs(4326, 32719, always_xy=True)
DXF_MAP = PLANS / "CL-01_A3_AUTOCAD_PRELIMINAR.dxf"
DXF_PROFILE = PLANS / "CL-02_A3_AUTOCAD_PRELIMINAR.dxf"
CSV_SCHEDULE = DATA / "cuadro_tramos_gisem.csv"
REPORT = DATA / "reporte_generacion_cad.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(space, message, x, y, height=3.0, layer="ROTULO"):
    return space.add_text(message, dxfattribs={"height": height, "layer": layer}).set_placement((x, y))


def frame(layout, number: str, title: str):
    layout.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
    layout.add_lwpolyline([(8, 8), (412, 8), (412, 289), (8, 289), (8, 8)],
                          dxfattribs={"layer": "MARCO"})
    layout.add_line((8, 47), (412, 47), dxfattribs={"layer": "MARCO"})
    layout.add_line((310, 8), (310, 47), dxfattribs={"layer": "MARCO"})
    text(layout, "CAPACHICA - LLACHON | ESTUDIO DE RED MT PUBLICADA", 13, 35, 5)
    text(layout, title, 13, 26, 4)
    text(layout, "WGS84 / UTM 19S | DATOS GIS Y SRTM REFERENCIALES", 13, 17, 2.7)
    text(layout, "BORRADOR - NO APTO PARA CONSTRUCCION", 13, 11, 2.7, "AVISOS")
    text(layout, number, 316, 34, 6)
    text(layout, "A3 HORIZONTAL | mm en papel", 316, 24, 2.7)
    text(layout, "14 OCT 2026 | REV 0", 316, 17, 2.7)


def new_doc():
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6  # metros en modelo; layout A3 en milímetros.
    for name, color in (("RED_MT_GISEM", 8), ("CORREDOR_GISEM", 5),
                        ("EXTREMOS_GIS", 1), ("TERRENO_SRTM", 3),
                        ("MARCO", 7), ("ROTULO", 7), ("AVISOS", 1),
                        ("CUADRICULA", 8), ("VIEWPORTS", 7)):
        doc.layers.add(name, color=color)
    return doc


def map_sheet(route: dict, features: list[dict]):
    doc = new_doc()
    model = doc.modelspace()
    for feature in features:
        xy = [TO_UTM.transform(*pair) for pair in feature["geometry"]["coordinates"]]
        model.add_lwpolyline(xy, dxfattribs={"layer": "RED_MT_GISEM"})
    xy = route["route_utm_xy"]
    model.add_lwpolyline(xy, dxfattribs={"layer": "CORREDOR_GISEM"})
    for end in (route["start"], route["end"]):
        model.add_circle(TO_UTM.transform(*end["structure_lonlat"]), 65,
                         dxfattribs={"layer": "EXTREMOS_GIS"})

    sheet = doc.layouts.new("CL-01_A3")
    frame(sheet, "CL-01", "PLANTA DE UBICACION Y CORREDOR GIS")
    xlo, xhi = min(p[0] for p in xy), max(p[0] for p in xy)
    ylo, yhi = min(p[1] for p in xy), max(p[1] for p in xy)
    view_width_mm, view_height_mm = 285, 203
    view_height_m = max((yhi - ylo) * 1.15, (xhi - xlo) * view_height_mm / view_width_mm * 1.15)
    sheet.add_viewport(center=(154, 163), size=(view_width_mm, view_height_mm),
                       view_center_point=((xlo + xhi) / 2, (ylo + yhi) / 2),
                       view_height=view_height_m, dxfattribs={"layer": "VIEWPORTS"})
    sheet.add_lwpolyline([(11, 60), (297, 60), (297, 267), (11, 267), (11, 60)],
                         dxfattribs={"layer": "MARCO"})
    text(sheet, "N", 275, 271, 4)
    sheet.add_line((278, 270), (278, 280), dxfattribs={"layer": "ROTULO"})
    sheet.add_line((278, 280), (275, 275), dxfattribs={"layer": "ROTULO"})
    sheet.add_line((278, 280), (281, 275), dxfattribs={"layer": "ROTULO"})
    bar_mm = 2000 * view_height_mm / view_height_m
    sheet.add_line((18, 67), (18 + bar_mm, 67), dxfattribs={"layer": "ROTULO"})
    text(sheet, "2 km", 18 + bar_mm / 2 - 5, 70, 2.8)
    denominator = round(view_height_m * 1000 / view_height_mm)
    info = [
        "REFERENCIAS GIS", f"Inicio: {route['start']['structure_code']}", "Capachica",
        f"Fin: {route['end']['structure_code']}", "Llachon",
        f"Longitud geom.: {route['route_length_m']/1000:.3f} km",
        f"Tramos GISEM: {len(route['segment_codes'])}",
        "Azul: ruta sobre red MT", "Gris: otros tramos MT",
        "Sin nuevos apoyos definidos", "Tension: por confirmar",
        "Conexion: por confirmar", "Capacidad: por confirmar",
        "No mide servidumbre", "ni verifica continuidad.",
        f"Escala A3 ~1:{denominator:,}".replace(",", " "),
    ]
    for index, line in enumerate(info):
        text(sheet, line, 306, 273 - index * 13.3, 2.8 if index else 3.5)
    return doc, denominator


def profile_sheet(route: dict, samples: list[dict]):
    doc = new_doc()
    model = doc.modelspace()
    model.add_lwpolyline([(p["chainage_m"], p["elevation_m"]) for p in samples],
                         dxfattribs={"layer": "TERRENO_SRTM"})
    sheet = doc.layouts.new("CL-02_A3")
    frame(sheet, "CL-02", "PERFIL DE TERRENO SRTM30m - REFERENCIAL")
    left, right, low, high = 35, 400, 81, 249
    zmin, zmax = 3810, 3900
    chainage_max = route["route_length_m"]

    def plot(point):
        return (left + point["chainage_m"] / chainage_max * (right - left),
                low + (point["elevation_m"] - zmin) / (zmax - zmin) * (high - low))

    for elevation in range(zmin, zmax + 1, 20):
        y = low + (elevation - zmin) / (zmax - zmin) * (high - low)
        sheet.add_line((left, y), (right, y), dxfattribs={"layer": "CUADRICULA"})
        text(sheet, str(elevation), 13, y - 1, 2.6)
    for km in range(0, 15, 2):
        x = left + km * 1000 / chainage_max * (right - left)
        sheet.add_line((x, low), (x, high), dxfattribs={"layer": "CUADRICULA"})
        text(sheet, str(km), x - 2, low - 7, 2.7)
    sheet.add_lwpolyline([plot(p) for p in samples], dxfattribs={"layer": "TERRENO_SRTM"})
    sheet.add_circle(plot(samples[0]), 2, dxfattribs={"layer": "EXTREMOS_GIS"})
    sheet.add_circle(plot(samples[-1]), 2, dxfattribs={"layer": "EXTREMOS_GIS"})
    text(sheet, "PROGRESIVA (km) SOBRE RUTA GIS", 165, 64, 3)
    text(sheet, "COTA SRTM (m)", 13, 256, 3)
    text(sheet, "SOLO TERRENO - SIN CONDUCTOR, POSTES NI GALIBOS", 60, 270, 4, "AVISOS")
    text(sheet, "Escala vertical exagerada; no usar para calculo mecanico.", 35, 55, 2.8, "AVISOS")
    return doc


def segment_rows(route: dict, features: list[dict]):
    by_code = {f["properties"]["CODTRAMOMT"]: f for f in features}
    position = 0.0
    rows = []
    for index, code in enumerate(route["segment_codes"], start=1):
        feature = by_code[code]
        xy = [TO_UTM.transform(*pair) for pair in feature["geometry"]["coordinates"]]
        length = math.fsum(math.dist(a, b) for a, b in zip(xy, xy[1:]))
        properties = feature["properties"]
        rows.append({
            "orden": index, "codigo_gisem": code,
            "progresiva_inicio_gis_m": round(position, 2),
            "progresiva_fin_gis_m": round(position + length, 2),
            "longitud_geometria_utm_m": round(length, 2),
            "longitud_atributo_gisem_sin_unidad_confirmada": properties["LONGITUD"],
            "codigo_empresa": properties["CODEMP"],
            "codigo_tipo_red": properties["CODTIPORED"],
            "codigo_propiedad": properties["PROPIEDAD"],
        })
        position += length
    if not math.isclose(position, route["route_length_m"], abs_tol=0.05):
        raise ValueError("La suma geométrica de los tramos no coincide con la ruta")
    return rows


def main():
    for path in (DXF_MAP, DXF_PROFILE, CSV_SCHEDULE, REPORT):
        if path.exists():
            raise FileExistsError(f"Salida existente; no se sobrescribe: {path}")
    route = load("derived/route.json")
    features = load("sources/gisem_mt_tramos.geojson")["features"]
    elevation = load("sources/srtm30m_route_samples.json")
    if elevation["route_sha256"] != sha256(ROOT / "derived/route.json"):
        raise ValueError("Las cotas SRTM no corresponden a esta versión de la ruta")
    if route["crs"]["metric"] != "EPSG:32719" or len(elevation["samples"]) != 57:
        raise ValueError("CRS o muestreo inesperado")

    rows = segment_rows(route, features)
    DATA.mkdir(exist_ok=True)
    with CSV_SCHEDULE.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    map_doc, denominator = map_sheet(route, features)
    map_doc.saveas(DXF_MAP)
    profile_sheet(route, elevation["samples"]).saveas(DXF_PROFILE)

    for path in (DXF_MAP, DXF_PROFILE):
        doc = ezdxf.readfile(path)
        audit = doc.audit()
        if doc.header["$INSUNITS"] != 6 or audit.has_errors:
            raise ValueError(f"DXF inválido: {path}")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PRELIMINARY_NOT_FOR_CONSTRUCTION",
        "inputs": {p: sha256(ROOT / p) for p in (
            "derived/route.json", "sources/gisem_mt_tramos.geojson",
            "sources/srtm30m_route_samples.json")},
        "outputs": {p.relative_to(ROOT).as_posix(): sha256(p) for p in
                    (CSV_SCHEDULE, DXF_MAP, DXF_PROFILE)},
        "map_paper_layout": "CL-01_A3",
        "profile_paper_layout": "CL-02_A3",
        "paper_size_mm": [420, 297],
        "model_units": "metres",
        "map_approximate_scale_at_A3": f"1:{denominator}",
        "segment_count": len(rows),
        "geometry_length_m": rows[-1]["progresiva_fin_gis_m"],
        "gis_attribute_length_sum_unverified_units": round(sum(float(row["longitud_atributo_gisem_sin_unidad_confirmada"]) for row in rows), 2),
        "warnings": [
            "La red es GIS y no acredita continuidad física ni estado operativo.",
            "La unidad del atributo LONGITUD no figura en el esquema consultado.",
            "El perfil SRTM no permite diseñar vanos ni verificar gálibos.",
            "Tensión, cargas, equipos y conexión pendientes de confirmar con operador y campo.",
        ],
    }
    with REPORT.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(f"Generados {DXF_MAP.name}, {DXF_PROFILE.name}, {CSV_SCHEDULE.name}")


if __name__ == "__main__":
    main()
