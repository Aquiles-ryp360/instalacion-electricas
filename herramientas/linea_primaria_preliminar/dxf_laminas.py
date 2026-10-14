"""Láminas A3 editables de planta y perfil para exploración cartográfica."""

from __future__ import annotations

import math
from pathlib import Path

import ezdxf


SCALES = (100, 200, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000)


def _scale(span_m: float, space_mm: float) -> int:
    return next((s for s in SCALES if span_m * 1000 / s <= space_mm),
                math.ceil(span_m * 1000 / space_mm / 10000) * 10000)


def _text(layout, value: str, x: float, y: float, height: float = 2.5,
          layer: str = "ROTULO") -> None:
    layout.add_text(value, dxfattribs={"layer": layer, "height": height}).set_placement((x, y))


def _rect(layout, x: float, y: float, w: float, h: float, layer: str = "MARCO") -> None:
    layout.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
                          dxfattribs={"layer": layer})


def _sheet(doc, code: str, title: str, project: str, crs: str):
    for name, color in (("MARCO", 7), ("ROTULO", 7), ("AVISO", 1),
                        ("PERFIL_DEM", 30), ("SITIOS_PERFIL", 1)):
        if name not in doc.layers:
            doc.layers.new(name, dxfattribs={"color": color})
    layout = doc.layouts.new(f"{code}_A3")
    if "Layout1" in doc.layouts:
        doc.layouts.delete("Layout1")
    layout.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
    _rect(layout, 8, 8, 404, 281)
    layout.add_line((8, 43), (412, 43), dxfattribs={"layer": "MARCO"})
    _text(layout, f"{code} | {title}", 15, 277, 4)
    _text(layout, f"PROYECTO: {project[:75]}", 15, 269)
    _text(layout, "ANTEPROYECTO CARTOGRAFICO - NO APTO PARA CONSTRUCCION",
          15, 31, 3, "AVISO")
    _text(layout, f"WGS84 / {crs} | MODELO EN METROS | LAMINA A3 EN MILIMETROS", 15, 21, 2.3)
    _text(layout, "SITIOS Y COTAS DEM REFERENCIALES; VER MANIFIESTO Y CSV", 15, 14, 2.3)
    return layout


def add_plant_sheet(doc, points: list[tuple[float, float]], posts: list[dict],
                    project: str, crs: str) -> None:
    """Añade una presentación A3; el modelo UTM existente permanece intacto."""
    layout = _sheet(doc, "LP-P01", "PLANTA DEL EJE Y SITIOS CANDIDATOS", project, crs)
    x0, y0, w, h = 15.0, 57.0, 390.0, 200.0
    _rect(layout, x0, y0, w, h)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    span_x, span_y = max(xmax - xmin, 1), max(ymax - ymin, 1)
    scale = _scale(max(span_x / (w - 25), span_y / (h - 28)) * (w - 25), w - 25)
    # La segunda condición garantiza el ajuste vertical en el área útil.
    while span_y * 1000 / scale > h - 28:
        scale = _scale(span_y, h - 28)
    factor = 1000 / scale
    left = x0 + (w - span_x * factor) / 2
    bottom = y0 + (h - span_y * factor) / 2

    def on_paper(east: float, north: float) -> tuple[float, float]:
        return left + (east - xmin) * factor, bottom + (north - ymin) * factor

    layout.add_lwpolyline([on_paper(*p) for p in points],
                          dxfattribs={"layer": "EJE_CANDIDATO"})
    last_label = -1000.0
    for post in posts:
        x, y = on_paper(post["este_m"], post["norte_m"])
        layout.add_circle((x, y), 1.5, dxfattribs={"layer": "SITIOS_CANDIDATOS"})
        if math.dist((x, y), (last_label, y)) >= 14:
            _text(layout, post["id"], x + 2, y + 2, 1.9)
            last_label = x
    _text(layout, f"ESCALA PLANTA 1:{scale}", 18, 48, 2.6)
    _text(layout, f"UTM E {xmin:.0f}-{xmax:.0f} m  N {ymin:.0f}-{ymax:.0f} m", 155, 48, 2.2)
    layout.add_line((394, 264), (394, 280), dxfattribs={"layer": "MARCO"})
    layout.add_solid([(391, 275), (397, 275), (394, 282)], dxfattribs={"layer": "MARCO"})
    _text(layout, "N", 392, 284, 2.5)


def make_profile_dxf(path: Path, profile: list[dict], posts: list[dict],
                     project: str, crs: str) -> None:
    """Crea un DXF de perfil DEM con modelo en progresiva/cota y lámina A3."""
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    layout = _sheet(doc, "LP-P02", "PERFIL DEM REFERENCIAL", project, crs)
    model = doc.modelspace()
    coordinates = [(p["progresiva_m"], p["cota_dem_m"]) for p in profile]
    model.add_lwpolyline(coordinates, dxfattribs={"layer": "PERFIL_DEM"})
    for post in posts:
        model.add_circle((post["progresiva_m"], post["cota_dem_m"]), 1.0,
                         dxfattribs={"layer": "SITIOS_PERFIL"})
    x0, y0, w, h = 24.0, 65.0, 365.0, 180.0
    _rect(layout, x0, y0, w, h)
    length = max(float(profile[-1]["progresiva_m"]), 1)
    low = min(p["cota_dem_m"] for p in profile)
    high = max(p["cota_dem_m"] for p in profile)
    datum = math.floor(low / 5) * 5 - 5
    rise = max(high - datum, 5)
    hscale = _scale(length, w - 15)
    vscale = _scale(rise, h - 22)
    fx, fy = 1000 / hscale, 1000 / vscale
    base_x, base_y = x0 + 8, y0 + 10

    def on_paper(station: float, cota: float) -> tuple[float, float]:
        return base_x + station * fx, base_y + (cota - datum) * fy

    layout.add_line((base_x, base_y), (base_x + length * fx, base_y),
                    dxfattribs={"layer": "MARCO"})
    layout.add_lwpolyline([on_paper(*p) for p in coordinates],
                          dxfattribs={"layer": "PERFIL_DEM"})
    last_label = -1000.0
    for post in posts:
        x, y = on_paper(post["progresiva_m"], post["cota_dem_m"])
        layout.add_circle((x, y), 1.5, dxfattribs={"layer": "SITIOS_PERFIL"})
        layout.add_line((x, base_y), (x, base_y - 3), dxfattribs={"layer": "MARCO"})
        if x - last_label >= 16:
            _text(layout, post["id"], x + 1, base_y - 8, 1.8)
            last_label = x
    _text(layout, f"H 1:{hscale}  V 1:{vscale}", 24, 50, 2.6)
    _text(layout, f"DATUM {datum:.0f} m  |  COTA DSM EGM2008", 155, 50, 2.3)
    _text(layout, "NO REPRESENTA CONDUCTORES, FLECHAS NI GALIBOS", 25, 253, 2.4, "AVISO")
    doc.saveas(path)
    if ezdxf.readfile(path).audit().has_errors:
        raise RuntimeError("Auditoría DXF de perfil fallida")
