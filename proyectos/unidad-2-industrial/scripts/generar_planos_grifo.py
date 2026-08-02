#!/usr/bin/env python3
"""Genera las seis laminas electricas A1 del anteproyecto del grifo.

La arquitectura procede de una copia derivada e inmutable del DXF recibido.
Las superposiciones electricas son una propuesta academica y todos los rotulos
se componen desde ``datos/rotulo-planos.yaml``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Callable

import ezdxf
import yaml
from ezdxf import bbox
from ezdxf.addons import Importer
from ezdxf.addons.drawing import matplotlib as ezdxf_matplotlib
from ezdxf.enums import TextEntityAlignment


PAGE_W = 84.1
PAGE_H = 59.4
FRAME = (0.5, 0.5, 83.6, 58.9)
ARCH_SCALE = 0.5
TITLE = (54.2, 0.8, 83.6, 14.0)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def add_layer(doc: ezdxf.document.Drawing, name: str, color: int, lineweight: int = 18, linetype: str = "CONTINUOUS") -> None:
    if name not in doc.layers:
        doc.layers.add(name=name, color=color, lineweight=lineweight, linetype=linetype)


def new_document() -> ezdxf.document.Drawing:
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 6  # metros
    doc.header["$LUNITS"] = 2
    doc.header["$LUPREC"] = 3
    layers = (
        ("MARCO", 7, 35, "CONTINUOUS"),
        ("ROTULO", 5, 25, "CONTINUOUS"),
        ("ROTULO_TEXTO", 7, 18, "CONTINUOUS"),
        ("ADVERTENCIA", 1, 25, "CONTINUOUS"),
        ("IE_ALUMBRADO", 2, 25, "CONTINUOUS"),
        ("IE_FUERZA", 1, 30, "CONTINUOUS"),
        ("IE_EMERGENCIA", 6, 30, "CONTINUOUS"),
        ("IE_CANALIZACION", 4, 18, "DASHED"),
        ("IE_TIERRA", 3, 35, "CONTINUOUS"),
        ("IE_RAYO", 30, 30, "CONTINUOUS"),
        ("IE_ZONA_1", 1, 35, "DASHED"),
        ("IE_ZONA_2", 30, 25, "DASHED"),
        ("IE_TABLA", 7, 13, "CONTINUOUS"),
        ("IE_TEXTO", 7, 18, "CONTINUOUS"),
        ("ARQ_REFERENCIA", 8, 9, "CONTINUOUS"),
    )
    for layer in layers:
        add_layer(doc, *layer)
    return doc


def rect(msp: ezdxf.layouts.BaseLayout, x0: float, y0: float, x1: float, y1: float, layer: str, color: int | None = None) -> None:
    attribs: dict[str, Any] = {"layer": layer}
    if color is not None:
        attribs["color"] = color
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], dxfattribs=attribs, close=True)


def text_left(msp: ezdxf.layouts.BaseLayout, value: str, x: float, y: float, height: float = 0.28, layer: str = "IE_TEXTO", color: int | None = None) -> None:
    attribs: dict[str, Any] = {"layer": layer, "height": height}
    if color is not None:
        attribs["color"] = color
    msp.add_text(str(value), dxfattribs=attribs).set_placement((x, y), align=TextEntityAlignment.LEFT)


def text_center(msp: ezdxf.layouts.BaseLayout, value: str, x: float, y: float, height: float = 0.28, layer: str = "IE_TEXTO", color: int | None = None) -> None:
    attribs: dict[str, Any] = {"layer": layer, "height": height}
    if color is not None:
        attribs["color"] = color
    msp.add_text(str(value), dxfattribs=attribs).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)


def add_frame(msp: ezdxf.layouts.BaseLayout) -> None:
    rect(msp, *FRAME, layer="MARCO")
    text_left(msp, "PROYECTO ACADEMICO - ANTEPROYECTO ELECTRICO", 0.9, 58.05, 0.28, "ADVERTENCIA")
    text_left(msp, "NO CONSTRUIR SIN FACTIBILIDAD, VERIFICACION DE CAMPO Y REVISION PROFESIONAL", 32.0, 58.05, 0.25, "ADVERTENCIA")


def entity_center(entity: ezdxf.entities.DXFGraphic, cache: bbox.Cache) -> tuple[float, float] | None:
    try:
        ext = bbox.extents([entity], cache=cache)
    except Exception:
        return None
    if not ext.has_data:
        return None
    center = ext.center
    return float(center.x), float(center.y)


def add_architecture(doc: ezdxf.document.Drawing, source_path: Path) -> int:
    """Importa la base A-01 a media escala y omite su cajetin empresarial."""
    source = ezdxf.readfile(source_path)
    cache = bbox.Cache()
    entities: list[ezdxf.entities.DXFGraphic] = []
    for entity in source.modelspace():
        # Las DIMENSION de la copia derivada perdieron sus bloques graficos al
        # separarse de la lamina fuente; se omiten para evitar entidades rotas.
        if entity.dxftype() in {"HATCH", "SOLID", "TRACE", "WIPEOUT", "IMAGE", "DIMENSION"}:
            continue
        center = entity_center(entity, cache)
        # El cajetin original ocupa la banda inferior derecha. Se conserva la
        # arquitectura, pero no se reproduce la autoria empresarial de la fuente.
        if center is not None and center[0] > 108.0 and center[1] < 28.0:
            continue
        entities.append(entity)

    block = doc.blocks.new(name="ARQUITECTURA_A01_REFERENCIA")
    importer = Importer(source, doc)
    importer.import_entities(entities, block)
    importer.finalize()
    doc.modelspace().add_blockref(
        "ARQUITECTURA_A01_REFERENCIA",
        (0.0, 0.0),
        dxfattribs={"xscale": ARCH_SCALE, "yscale": ARCH_SCALE, "zscale": ARCH_SCALE, "layer": "ARQ_REFERENCIA"},
    )
    return len(entities)


def add_title_block(msp: ezdxf.layouts.BaseLayout, title_data: dict[str, Any], sheet: dict[str, str], number: int, total: int, scale: str) -> None:
    x0, y0, x1, y1 = TITLE
    # El WIPEOUT cubre la grilla UTM y cualquier elemento de la referencia que
    # cruce el cajetin. El rotulo se dibuja despues para conservar su lectura.
    msp.add_wipeout([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], dxfattribs={"layer": "ROTULO"})
    rect(msp, x0, y0, x1, y1, "ROTULO", 5)
    for y in (12.85, 11.65, 9.95, 8.55, 6.95, 5.35, 3.75, 2.15):
        msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "ROTULO"})
    for x in (61.7, 69.5, 75.0, 79.2):
        msp.add_line((x, y0), (x, 3.75), dxfattribs={"layer": "ROTULO"})
    msp.add_line((68.4, 3.75), (68.4, 6.95), dxfattribs={"layer": "ROTULO"})

    inst = title_data["institucion"]
    acad = title_data["academico"]
    project = title_data["proyecto"]
    resp = title_data["responsabilidades"]
    text_center(msp, inst["universidad"], (x0 + x1) / 2, 13.55, 0.50, "ROTULO_TEXTO")
    text_center(msp, inst["facultad"], (x0 + x1) / 2, 13.15, 0.24, "ROTULO_TEXTO")
    text_center(msp, inst["escuela"], (x0 + x1) / 2, 12.55, 0.28, "ROTULO_TEXTO")
    text_center(msp, "PROYECTO: INSTALACIONES ELECTRICAS EN BAJA TENSION", (x0 + x1) / 2, 12.20, 0.25, "ROTULO_TEXTO")
    text_center(msp, "GRIFO DE COMBUSTIBLES LIQUIDOS - PROYECTO ACADEMICO NUEVO", (x0 + x1) / 2, 11.25, 0.33, "ROTULO_TEXTO")
    text_center(msp, "DIESEL B5 S-50 / GASOHOL REGULAR / GASOHOL PREMIUM - SIN GLP NI GNV", (x0 + x1) / 2, 10.72, 0.24, "ROTULO_TEXTO")
    text_center(msp, sheet["titulo"], (x0 + x1) / 2, 9.28, 0.40, "ROTULO_TEXTO")

    text_left(msp, f"PROPIETARIO: {project['propietario']}", x0 + 0.25, 8.08, 0.28, "ROTULO_TEXTO")
    text_left(msp, "Dato consignado en documentacion tecnica de referencia facilitada por la DREM", x0 + 0.25, 7.63, 0.20, "ROTULO_TEXTO")
    text_left(msp, "UBICACION: PREDIO REUMITA B-8/B-9, C.C. SAN FRANCISCO DE BUENAVISTA", x0 + 0.25, 7.19, 0.22, "ROTULO_TEXTO")
    text_left(msp, "CARRETERA JULIACA-PUNO, CARACOTO, SAN ROMAN, PUNO", x0 + 0.25, 6.62, 0.25, "ROTULO_TEXTO")

    text_left(msp, f"CURSO: {acad['curso']}", x0 + 0.25, 6.05, 0.28, "ROTULO_TEXTO")
    text_left(msp, f"DOCENTE: {acad['docente']}", x0 + 0.25, 5.58, 0.28, "ROTULO_TEXTO")
    text_left(msp, f"DISENADO Y DIBUJADO: {resp['disenado_por']}", 68.7, 6.05, 0.25, "ROTULO_TEXTO")
    text_left(msp, "REVISION DOCENTE: CAMPO ACADEMICO - SIN FIRMA NI APROBACION AFIRMADA", 68.7, 5.58, 0.19, "ROTULO_TEXTO")

    text_left(msp, "MODALIDAD: INDIVIDUAL", x0 + 0.25, 4.78, 0.25, "ROTULO_TEXTO")
    text_left(msp, "CODIGO EST.: __________", x0 + 0.25, 4.30, 0.24, "ROTULO_TEXTO")
    text_left(msp, "SEMESTRE: __________", 68.7, 4.78, 0.24, "ROTULO_TEXTO")
    text_left(msp, "SEDE: PUNO - PERU", 68.7, 4.30, 0.24, "ROTULO_TEXTO")

    labels = (
        (x0 + 0.25, "LAMINA", sheet["codigo"]),
        (61.95, "ESCALA", scale),
        (69.75, "FECHA", title_data["presentacion"]["fecha_base"]),
        (75.25, "REV.", "R00"),
        (79.45, "HOJA", f"{number:02d}/{total:02d}"),
    )
    for x, label, value in labels:
        text_left(msp, label, x, 3.28, 0.19, "ROTULO_TEXTO")
        text_left(msp, value, x, 2.63, 0.42 if label == "LAMINA" else 0.29, "ROTULO_TEXTO")

    text_center(msp, "UNAP - PUNO | ANTEPROYECTO SUJETO A VERIFICACION DE CAMPO, FACTIBILIDAD Y REVISION PROFESIONAL", (x0 + x1) / 2, 1.62, 0.20, "ADVERTENCIA")
    text_center(msp, "NO SE CONSIGNA CIP, SELLO NI FIRMA POR NO EXISTIR ESOS DATOS EN LAS FUENTES", (x0 + x1) / 2, 1.12, 0.19, "ADVERTENCIA")


def add_luminaire(msp: ezdxf.layouts.BaseLayout, point: tuple[float, float], label: str = "", emergency: bool = False) -> None:
    x, y = point
    layer = "IE_EMERGENCIA" if emergency else "IE_ALUMBRADO"
    msp.add_circle((x, y), 0.22, dxfattribs={"layer": layer})
    msp.add_line((x - 0.15, y - 0.15), (x + 0.15, y + 0.15), dxfattribs={"layer": layer})
    msp.add_line((x - 0.15, y + 0.15), (x + 0.15, y - 0.15), dxfattribs={"layer": layer})
    if label:
        text_left(msp, label, x + 0.28, y + 0.15, 0.18, layer)


def add_outlet(msp: ezdxf.layouts.BaseLayout, point: tuple[float, float], label: str = "TC") -> None:
    x, y = point
    msp.add_circle((x, y), 0.20, dxfattribs={"layer": "IE_FUERZA"})
    msp.add_line((x - 0.13, y), (x + 0.13, y), dxfattribs={"layer": "IE_FUERZA"})
    msp.add_line((x, y), (x, y + 0.13), dxfattribs={"layer": "IE_FUERZA"})
    text_left(msp, label, x + 0.25, y + 0.10, 0.17, "IE_FUERZA")


def add_panel(msp: ezdxf.layouts.BaseLayout, point: tuple[float, float], label: str, layer: str = "IE_FUERZA") -> None:
    x, y = point
    rect(msp, x - 0.32, y - 0.25, x + 0.32, y + 0.25, layer)
    text_center(msp, label, x, y, 0.18, layer)


def add_route(msp: ezdxf.layouts.BaseLayout, points: list[tuple[float, float]], layer: str = "IE_CANALIZACION") -> None:
    msp.add_lwpolyline(points, dxfattribs={"layer": layer, "linetype": "DASHED"})


def add_legend(msp: ezdxf.layouts.BaseLayout, title: str, rows: list[tuple[str, str]], x: float = 55.0, y: float = 55.8, width: float = 28.0) -> None:
    row_h = 0.72
    height = 1.05 + row_h * len(rows)
    rect(msp, x, y - height, x + width, y, "IE_TABLA")
    text_center(msp, title, x + width / 2, y - 0.48, 0.32, "IE_TEXTO")
    msp.add_line((x, y - 0.90), (x + width, y - 0.90), dxfattribs={"layer": "IE_TABLA"})
    for index, (code, description) in enumerate(rows):
        yy = y - 1.30 - index * row_h
        text_left(msp, code, x + 0.25, yy, 0.23, "IE_TEXTO")
        text_left(msp, description, x + 4.0, yy, 0.22, "IE_TEXTO")


def sheet_ie01(doc: ezdxf.document.Drawing, _: dict[str, Any], __: dict[str, Any]) -> None:
    msp = doc.modelspace()
    # Marquesina: 18 luminarias en tres circuitos alternados.
    index = 0
    for y in (18.0, 20.5, 23.0, 25.5, 28.0, 30.5):
        for x in (36.0, 38.4, 40.8):
            index += 1
            add_luminaire(msp, (x, y), f"L{index:02d}", emergency=index <= 6)
    exterior = ((26.0, 12.8), (31.0, 13.0), (43.0, 13.0), (49.0, 14.5), (26.0, 36.5), (32.0, 38.5), (43.0, 38.5), (50.0, 36.0))
    for index, point in enumerate(exterior, 1):
        add_luminaire(msp, point, f"PE{index}", emergency=index <= 4)

    tge = (31.58, 37.15)
    add_panel(msp, tge, "TGE")
    add_panel(msp, (32.5, 36.6), "ATS", "IE_EMERGENCIA")
    add_panel(msp, (33.5, 36.6), "TDE", "IE_EMERGENCIA")
    for point in ((36.0, 18.0), (38.4, 23.0), (40.8, 28.0), (26.0, 12.8), (50.0, 36.0)):
        add_route(msp, [tge, (34.0, tge[1]), (34.0, point[1]), point])
    add_legend(msp, "IE-01 | LEYENDA Y CRITERIOS", [
        ("X", "Luminaria LED; verde = circuito normal, magenta = critico"),
        ("TGE", "Tablero general 380/220 V, 80 A, 4P"),
        ("TDE", "Tablero de emergencia mediante ATS 4P, 63 A"),
        ("---", "Canalizacion enterrada/techo segun tramo; verificar recorrido"),
        ("NOTA", "18 x 100 W marquesina y 8 x 120 W exterior como criterio"),
        ("CNE", "dV ramal <= 2.5 % y total <= 4 %; PE en todo circuito"),
    ])


def sheet_ie02(doc: ezdxf.document.Drawing, _: dict[str, Any], __: dict[str, Any]) -> None:
    msp = doc.modelspace()
    # Los tres planos administrativos aparecen apilados en la lamina A-01.
    levels = (
        ("N1", (30.0, 33.8), "TD-A1", ((28.5, 33.5), (30.2, 33.5), (31.8, 33.5), (29.2, 31.8), (31.0, 31.8))),
        ("N2", (30.0, 43.0), "TD-A2", ((28.5, 43.0), (30.2, 43.0), (31.8, 43.0), (29.2, 41.4), (31.0, 41.4))),
        ("N3", (30.0, 52.2), "TD-A3", ((28.5, 52.2), (30.2, 52.2), (31.8, 52.2), (29.2, 50.6), (31.0, 50.6))),
    )
    for level, panel_point, panel_name, lights in levels:
        add_panel(msp, (panel_point[0] - 2.2, panel_point[1] + 1.2), panel_name)
        for index, point in enumerate(lights, 1):
            add_luminaire(msp, point, f"{level}-L{index}")
        for index, point in enumerate(((lights[0][0] - 0.7, lights[0][1] - 0.7), (lights[2][0] + 0.7, lights[2][1] - 0.7), (lights[4][0] + 0.7, lights[4][1] - 0.7)), 1):
            add_outlet(msp, point, f"{level}-TC{index}")
        add_route(msp, [(panel_point[0] - 2.2, panel_point[1] + 1.2), (panel_point[0], panel_point[1] + 1.2), lights[0], lights[1], lights[2]])
    add_legend(msp, "IE-02 | EDIFICIO ADMINISTRATIVO", [
        ("N1", "120.35 m2: minimarket, administracion, atencion y servicios"),
        ("N2", "160.20 m2: oficinas 1 a 3 y SS.HH."),
        ("N3", "160.20 m2: oficinas 4 a 6 y SS.HH."),
        ("TC", "Tomacorriente doble 220 V, 2P+T; RCBO 30 mA"),
        ("L", "Punto de alumbrado LED; conductor minimo 2.5 mm2 Cu"),
        ("NOTA", "Posiciones sujetas a replanteo con arquitectura acotada"),
    ])


def sheet_ie03(doc: ezdxf.document.Drawing, architecture: dict[str, Any], __: dict[str, Any]) -> None:
    msp = doc.modelspace()
    tdf = (31.58, 37.15)
    add_panel(msp, tdf, "TDF")
    for index, dispenser in enumerate(architecture["dispensing"]["dispensers_local_A01"], 1):
        point = tuple(value * ARCH_SCALE for value in dispenser["point"])
        add_panel(msp, point, f"SD{index}", "IE_FUERZA")
        add_route(msp, [tdf, (34.0, tdf[1]), (34.0, point[1]), point], "IE_FUERZA")
    for index, tank in enumerate(architecture["fuel_storage"]["tanks"], 1):
        point = tuple(value * ARCH_SCALE for value in tank["local_A01_center"])
        msp.add_circle(point, 0.25, dxfattribs={"layer": "IE_FUERZA"})
        text_left(msp, f"STP-{index} 1.5 hp", point[0] + 0.32, point[1], 0.19, "IE_FUERZA")
        add_route(msp, [tdf, (34.8, tdf[1]), (34.8, point[1]), point], "IE_FUERZA")
    for index, point in enumerate(((27.0, 15.7), (46.0, 34.8)), 1):
        msp.add_circle(point, 0.32, dxfattribs={"layer": "IE_EMERGENCIA"})
        text_center(msp, "PE", point[0], point[1], 0.20, "IE_EMERGENCIA")
        text_left(msp, f"PARO-{index}", point[0] + 0.38, point[1], 0.20, "IE_EMERGENCIA")
    add_legend(msp, "IE-03 | FUERZA Y CONTROL DE COMBUSTIBLE", [
        ("STP", "4 bombas sumergibles 1.5 hp; arranque secuencial"),
        ("SD", "6 cabezales de surtidor 220 V, 103 VA de referencia"),
        ("PE", "Paro de emergencia remoto; corta bombas y surtidores"),
        ("UPS", "UPS-FUEL 3 kVA senoidal para cabezales/control/ATG"),
        ("CNE", "Equipos y sellos certificados para la zona donde se instalen"),
        ("NOTA", "Rutas y placas definitivas requieren coordinacion del proveedor"),
    ])


def earth_symbol(msp: ezdxf.layouts.BaseLayout, point: tuple[float, float], label: str) -> None:
    x, y = point
    msp.add_line((x, y + 0.45), (x, y), dxfattribs={"layer": "IE_TIERRA"})
    for width, yy in ((0.45, 0.0), (0.30, -0.15), (0.15, -0.30)):
        msp.add_line((x - width, y + yy), (x + width, y + yy), dxfattribs={"layer": "IE_TIERRA"})
    text_left(msp, label, x + 0.55, y - 0.12, 0.18, "IE_TIERRA")


def sheet_ie04(doc: ezdxf.document.Drawing, architecture: dict[str, Any], __: dict[str, Any]) -> None:
    msp = doc.modelspace()
    ring = [(24.7, 10.3), (51.7, 10.3), (51.7, 38.3), (25.8, 38.3), (24.7, 10.3)]
    msp.add_lwpolyline(ring, dxfattribs={"layer": "IE_TIERRA", "closed": True})
    rods = ((25.0, 11.0), (38.0, 10.6), (51.2, 11.0), (51.2, 24.0), (51.2, 37.7), (39.0, 38.0), (27.0, 38.0), (25.0, 24.0))
    for index, point in enumerate(rods, 1):
        earth_symbol(msp, point, f"PT-{index}")
    for dispenser in architecture["dispensing"]["dispensers_local_A01"]:
        point = tuple(value * ARCH_SCALE for value in dispenser["point"])
        add_route(msp, [point, (point[0], 32.5), (25.8, 32.5)], "IE_TIERRA")
    for tank in architecture["fuel_storage"]["tanks"]:
        point = tuple(value * ARCH_SCALE for value in tank["local_A01_center"])
        add_route(msp, [point, (43.2, point[1]), (43.2, 38.3)], "IE_TIERRA")
    # Captadores convencionales y anillo de marquesina.
    lps = [(35.0, 16.5), (41.8, 16.5), (41.8, 32.5), (35.0, 32.5), (35.0, 16.5)]
    msp.add_lwpolyline(lps, dxfattribs={"layer": "IE_RAYO", "closed": True})
    for point in lps[:-1]:
        msp.add_circle(point, 0.23, dxfattribs={"layer": "IE_RAYO"})
        text_left(msp, "CAP", point[0] + 0.28, point[1], 0.16, "IE_RAYO")
    add_legend(msp, "IE-04 | TIERRA, EQUIPOTENCIALIDAD Y RAYO", [
        ("ANILLO", "Cu desnudo 35 mm2 como criterio; verificar por calculo y corrosion"),
        ("PT-1..8", "Electrodos distribuidos; cantidad final depende de resistividad"),
        ("R <= 25", "Limite CNE-U 060-712; objetivo de diseno <= 10 ohm"),
        ("BOND", "Unir tanques, tuberias, surtidores, marquesina y masas"),
        ("LPS", "Sistema convencional coordinado; evaluar riesgo IEC 62305"),
        ("SPD", "SPD Tipo 1+2 en TGE y Tipo 2 en tableros sensibles"),
    ])


def breaker_symbol(msp: ezdxf.layouts.BaseLayout, point: tuple[float, float], label: str) -> None:
    x, y = point
    msp.add_line((x, y + 0.4), (x, y + 0.12), dxfattribs={"layer": "IE_FUERZA"})
    msp.add_line((x - 0.18, y - 0.10), (x + 0.18, y + 0.12), dxfattribs={"layer": "IE_FUERZA"})
    msp.add_line((x, y - 0.10), (x, y - 0.40), dxfattribs={"layer": "IE_FUERZA"})
    text_left(msp, label, x + 0.30, y, 0.20, "IE_TEXTO")


def add_unifilar(msp: ezdxf.layouts.BaseLayout) -> None:
    y = 52.5
    nodes = ((4.0, "RED\n380/220V"), (12.0, "MEDIDOR"), (20.0, "ITM\n80A 4P"), (29.0, "TGE"), (39.0, "ATS\n63A 4P"), (48.0, "TDE"))
    for index, (x, label) in enumerate(nodes):
        rect(msp, x - 1.25, y - 1.0, x + 1.25, y + 1.0, "IE_FUERZA")
        for offset, line in enumerate(label.split("\n")):
            text_center(msp, line, x, y + 0.25 - offset * 0.48, 0.26, "IE_TEXTO")
        if index:
            msp.add_line((nodes[index - 1][0] + 1.25, y), (x - 1.25, y), dxfattribs={"layer": "IE_FUERZA"})
    rect(msp, 37.75, 47.0, 40.25, 49.0, "IE_EMERGENCIA")
    text_center(msp, "GE 37.5 kVA", 39.0, 48.0, 0.25, "IE_EMERGENCIA")
    msp.add_line((39.0, 49.0), (39.0, 51.5), dxfattribs={"layer": "IE_EMERGENCIA"})
    branches = ((29.0, "TDF 40A"), (25.0, "TD-A1 25A"), (21.0, "TD-A2 20A"), (17.0, "TD-A3 20A"))
    for x, label in branches:
        msp.add_line((29.0, 51.5), (x, 46.0), dxfattribs={"layer": "IE_FUERZA"})
        rect(msp, x - 1.3, 44.8, x + 1.3, 46.0, "IE_FUERZA")
        text_center(msp, label, x, 45.4, 0.22, "IE_TEXTO")
    for index, label in enumerate(("UPS-FUEL 3kVA", "UPS-IT 2kVA", "CARGAS CRITICAS")):
        x = 51.0 + index * 7.0
        msp.add_line((48.0, 51.5), (x, 46.0), dxfattribs={"layer": "IE_EMERGENCIA"})
        rect(msp, x - 1.7, 44.8, x + 1.7, 46.0, "IE_EMERGENCIA")
        text_center(msp, label, x, 45.4, 0.21, "IE_TEXTO")
    text_left(msp, "ALIMENTADOR PRINCIPAL: Cu 4x35 mm2 + PE 16 mm2 | ITM 80 A 4P | Icu >= 25 kA (VALIDAR Icc)", 2.0, 56.2, 0.30, "IE_TEXTO")


def add_load_table(msp: ezdxf.layouts.BaseLayout, calculations: dict[str, Any]) -> None:
    x0, x1 = 1.2, 53.2
    y_top = 42.0
    row_h = 0.70
    widths = (4.1, 19.8, 5.0, 4.0, 4.4, 4.2, 5.0, 5.5)
    headers = ("ID", "DESCRIPCION", "TABLERO", "FASE", "kVA MD", "ITM A", "Cu/PE", "dV %")
    xs = [x0]
    for width in widths:
        xs.append(xs[-1] + width)
    rows = calculations["circuits"]
    y_bottom = y_top - row_h * (len(rows) + 1)
    rect(msp, x0, y_bottom, x1, y_top, "IE_TABLA")
    for x in xs[1:-1]:
        msp.add_line((x, y_bottom), (x, y_top), dxfattribs={"layer": "IE_TABLA"})
    for index in range(1, len(rows) + 1):
        yy = y_top - row_h * index
        msp.add_line((x0, yy), (x1, yy), dxfattribs={"layer": "IE_TABLA"})
    for index, header in enumerate(headers):
        text_center(msp, header, (xs[index] + xs[index + 1]) / 2, y_top - row_h / 2, 0.20, "IE_TEXTO")
    for row_index, circuit in enumerate(rows, 1):
        values = (
            circuit["id"],
            circuit["description"][:38],
            circuit["panel"],
            circuit["phase"],
            f"{circuit['demand_kva']:.2f}",
            f"{float(circuit['breaker_a']):.0f}",
            f"{float(circuit['conductor_mm2']):g}/{float(circuit['pe_mm2']):g}",
            f"{circuit['total_voltage_drop_percent']:.2f}",
        )
        yy = y_top - row_h * row_index - row_h / 2
        for col, value in enumerate(values):
            height = 0.15 if col == 1 else 0.18
            text_center(msp, str(value), (xs[col] + xs[col + 1]) / 2, yy, height, "IE_TEXTO")
    text_left(msp, "CUADRO DE CARGAS - TODOS LOS CIRCUITOS CON RCBO <= 30 mA", x0, y_top + 0.45, 0.30, "IE_TEXTO")


def sheet_ie05(doc: ezdxf.document.Drawing, _: dict[str, Any], calculations: dict[str, Any]) -> None:
    msp = doc.modelspace()
    add_unifilar(msp)
    add_load_table(msp, calculations)
    summary = calculations["summary"]
    generator = calculations["generator"]
    x0, y0, x1, y1 = 55.0, 15.0, 83.0, 42.0
    rect(msp, x0, y0, x1, y1, "IE_TABLA")
    text_center(msp, "RESUMEN DE DIMENSIONAMIENTO", (x0 + x1) / 2, 41.2, 0.34, "IE_TEXTO")
    lines = (
        f"Potencia instalada: {summary['installed_kw']:.2f} kW / {summary['installed_kva']:.2f} kVA",
        f"Maxima demanda: {summary['maximum_demand_kw']:.2f} kW / {summary['maximum_demand_kva']:.2f} kVA",
        f"Demanda + 20 % reserva: {summary['service_design_kva_with_reserve']:.2f} kVA",
        "Suministro propuesto: 50 kVA, 380/220 V, 3F+N+PE",
        f"Corriente maxima de fase: {summary['maximum_phase_current_with_reserve_a']:.2f} A",
        f"Desbalance de fases: {summary['phase_unbalance_percent']:.2f} %",
        "Principal: ITM 80 A, 4P, Icu >= 25 kA (por validar)",
        "Alimentador: Cu 4x35 mm2 + PE 16 mm2",
        f"GE: {generator['selected_nameplate_kva']:.1f} kVA standby; factor altitud {generator['altitude_factor']:.4f}",
        f"GE disponible en sitio: {generator['available_standby_kva_at_site']:.2f} kVA",
        f"Arranque con margen: {generator['starting_with_margin_kva']:.2f} kVA - CUMPLE",
        "Caida: ramal <= 2.5 % y total <= 4 % (CNE-U 050-102)",
        "Selectividad, Icc y placas: PENDIENTES DE FACTIBILIDAD/CAMPO",
        "N y PE separados; ATS 4 polos con neutro conmutado",
        "Todas las cifras son de anteproyecto academico reproducible.",
    )
    for index, line in enumerate(lines):
        text_left(msp, line, x0 + 0.5, 39.9 - index * 1.48, 0.25, "IE_TEXTO")


def zone_circle(msp: ezdxf.layouts.BaseLayout, point: tuple[float, float], radius: float, label: str, layer: str) -> None:
    msp.add_circle(point, radius, dxfattribs={"layer": layer})
    text_left(msp, label, point[0] + radius * 0.72, point[1] + radius * 0.72, 0.18, layer)


def sheet_ie06(doc: ezdxf.document.Drawing, architecture: dict[str, Any], __: dict[str, Any]) -> None:
    msp = doc.modelspace()
    for dispenser in architecture["dispensing"]["dispensers_local_A01"]:
        point = tuple(value * ARCH_SCALE for value in dispenser["point"])
        zone_circle(msp, point, 3.0, "Z2 r=6m (CNE)", "IE_ZONA_2")
    for fill in architecture["fuel_storage"]["fill_points_local_A01"]:
        point = tuple(value * ARCH_SCALE for value in fill["point"])
        zone_circle(msp, point, 1.5, "Z1/Z2 llenado", "IE_ZONA_1")
    for vent in architecture["fuel_storage"]["vent_points_local_A01"]:
        point = tuple(value * ARCH_SCALE for value in vent["point"])
        zone_circle(msp, point, 0.45, "Z1", "IE_ZONA_1")
        zone_circle(msp, point, 0.75, "Z2", "IE_ZONA_2")
    add_legend(msp, "IE-06 | AREAS PELIGROSAS - PROPUESTA ACADEMICA", [
        ("ZONA 0", "Interior de tanques y tuberias con vapor inflamable"),
        ("ZONA 1", "Envolventes de llenado/venteo segun CNE-U 120"),
        ("ZONA 2", "Alrededor de surtidores: radio horizontal 6 m"),
        ("EQUIPO", "Seleccion Ex y temperatura compatibles con combustible"),
        ("SELLO", "Sellos y canalizaciones conforme a limite de zona"),
        ("ALERTA", "Validar alturas, ventilacion y geometria con especialista"),
        ("DS 054", "Las divisiones sectoriales se contrastan; no se igualan 1:1"),
    ])
    # Detalle esquematico para que la altura no quede implicita solo en planta.
    x0, y0 = 55.0, 32.0
    rect(msp, x0, y0, 82.8, 44.5, "IE_TABLA")
    text_center(msp, "DETALLE ESQUEMATICO DE VENTEO Y LLENADO", 68.9, 43.9, 0.30, "IE_TEXTO")
    msp.add_line((x0 + 1.0, 34.0), (82.0, 34.0), dxfattribs={"layer": "IE_TABLA"})
    msp.add_line((61.0, 34.0), (61.0, 41.5), dxfattribs={"layer": "IE_FUERZA"})
    zone_circle(msp, (61.0, 41.5), 0.9, "Venteo: Z1 0.9m; Z2 hasta 1.5m", "IE_ZONA_1")
    rect(msp, 70.0, 33.4, 76.0, 35.8, "IE_FUERZA")
    zone_circle(msp, (73.0, 35.8), 1.5, "Llenado: verificar envolvente vertical", "IE_ZONA_2")
    text_left(msp, "DIMENSIONES DE PLANTA ESCALADAS DESDE CNE-U 120; ELEVACIONES REQUIEREN CAMPO", 56.0, 32.7, 0.20, "ADVERTENCIA")


SHEET_BUILDERS: dict[str, Callable[[ezdxf.document.Drawing, dict[str, Any], dict[str, Any]], None]] = {
    "IE-01": sheet_ie01,
    "IE-02": sheet_ie02,
    "IE-03": sheet_ie03,
    "IE-04": sheet_ie04,
    "IE-05": sheet_ie05,
    "IE-06": sheet_ie06,
}


def sheet_stem(sheet: dict[str, str]) -> str:
    return f"{sheet['codigo'].lower()}-{sheet['titulo'].lower().replace(' ', '-').replace(',', '').replace('/', '-')[:48]}"


def render(doc: ezdxf.document.Drawing, png_path: Path, pdf_path: Path) -> None:
    def render_filter(entity: ezdxf.entities.DXFGraphic) -> bool:
        return entity.dxftype() not in {"HATCH", "SOLID", "TRACE", "IMAGE"}

    ezdxf_matplotlib.qsave(
        doc.modelspace(),
        png_path,
        bg="#FFFFFF",
        fg="#111111",
        dpi=220,
        size_inches=(16.54, 11.69),
        filter_func=render_filter,
    )
    # PDF vectorial A1 horizontal. No convertir desde PNG: esa ruta rasteriza
    # textos y lineas y se vuelve borrosa al ampliar o imprimir.
    ezdxf_matplotlib.qsave(
        doc.modelspace(),
        pdf_path,
        bg="#FFFFFF",
        fg="#111111",
        size_inches=(33.11, 23.39),
        filter_func=render_filter,
    )


def main() -> int:
    root = repository_root()
    project = root / "proyectos/unidad-2-industrial"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--architecture-base", type=Path, default=root / "build/unidad-2-industrial/cad/base/a_01_referencia_local.dxf")
    parser.add_argument("--output", type=Path, default=root / "build/unidad-2-industrial/cad/planos")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--sheet", action="append", choices=tuple(SHEET_BUILDERS), help="regenera solo una lamina; puede repetirse")
    args = parser.parse_args()

    title_data = load_yaml(project / "datos/rotulo-planos.yaml")
    architecture = load_json(project / "arquitectura/datos/grifo.json")
    calculations = load_json(root / "build/unidad-2-industrial/calculos/resumen-calculos.json")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not args.architecture_base.is_file():
        raise SystemExit(f"No existe la base arquitectonica derivada: {args.architecture_base}")
    if calculations["status"] != "PASS":
        raise SystemExit("El calculo electrico no esta en estado PASS")

    manifest_path = output / "manifest.json"
    previous_manifest = load_json(manifest_path) if manifest_path.is_file() else None
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "generated_on": date.today().isoformat(),
        "title_block_source": "proyectos/unidad-2-industrial/datos/rotulo-planos.yaml",
        "architecture_source": str(args.architecture_base.resolve()),
        "architecture_source_sha256": sha256(args.architecture_base.resolve()),
        "calculation_source_sha256": calculations["source_sha256"],
        "sheets": [],
    }
    all_sheets = title_data["laminas_previstas"]
    sheets = [sheet for sheet in all_sheets if not args.sheet or sheet["codigo"] in args.sheet]
    architecture_count: int | None = None
    for sheet in sheets:
        number = next(index for index, item in enumerate(all_sheets, 1) if item["codigo"] == sheet["codigo"])
        code = sheet["codigo"]
        print(f"Generando {code}: {sheet['titulo']}", flush=True)
        doc = new_document()
        msp = doc.modelspace()
        add_frame(msp)
        if code != "IE-05":
            architecture_count = add_architecture(doc, args.architecture_base.resolve())
        SHEET_BUILDERS[code](doc, architecture, calculations)
        scale = "1:100 / IND." if code != "IE-05" else "S/E"
        add_title_block(msp, title_data, sheet, number, len(all_sheets), scale)
        stem = sheet_stem(sheet)
        dxf_path = output / f"{stem}.dxf"
        png_path = output / f"{stem}.png"
        pdf_path = output / f"{stem}.pdf"
        doc.saveas(dxf_path)
        if not args.skip_render:
            render(doc, png_path, pdf_path)
        manifest["sheets"].append({
            "code": code,
            "title": sheet["titulo"],
            "dxf": str(dxf_path.relative_to(root)),
            "png": None if args.skip_render else str(png_path.relative_to(root)),
            "pdf": None if args.skip_render else str(pdf_path.relative_to(root)),
            "entity_count": len(msp),
            "title_block": {
                "university": title_data["institucion"]["universidad"],
                "student": title_data["academico"]["estudiante"],
                "teacher": title_data["academico"]["docente"],
                "owner": title_data["proyecto"]["propietario"],
                "site": "CARACOTO, SAN ROMAN, PUNO",
            },
        })
    if not args.skip_render:
        all_pdf_paths = [output / f"{sheet_stem(sheet)}.pdf" for sheet in all_sheets]
        missing = [path.name for path in all_pdf_paths if not path.is_file()]
        if missing:
            raise SystemExit(f"Faltan PDF vectoriales para componer el juego: {', '.join(missing)}")
        combined = output / "planos-electricos-grifo-unap-aquiles.pdf"
        temporary = output / ".planos-electricos-grifo-unap-aquiles.tmp.pdf"
        if temporary.exists():
            temporary.unlink()
        subprocess.run(["pdfunite", *(str(path) for path in all_pdf_paths), str(temporary)], check=True)
        temporary.replace(combined)
        manifest["combined_pdf"] = str(combined.relative_to(root))
        manifest["pdf_quality"] = "vectorial_directo_A1; PNG_solo_vista_previa_220_dpi"
    if args.sheet and previous_manifest:
        records = {record["code"]: record for record in previous_manifest.get("sheets", [])}
        records.update({record["code"]: record for record in manifest["sheets"]})
        manifest["sheets"] = [records[sheet["codigo"]] for sheet in all_sheets if sheet["codigo"] in records]
    manifest["architecture_entities_imported_per_sheet"] = (
        architecture_count
        if architecture_count is not None
        else (previous_manifest or {}).get("architecture_entities_imported_per_sheet")
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "sheets": len(sheets), "output": str(output)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
