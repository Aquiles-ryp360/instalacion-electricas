"""Planos Rev. 6 con el formato de lámina EPIME (referencia: LP Conima–Tilali).

Toma el eje KML manual (datos/vertices_corredor_manual.csv), propone una
distribución ACADÉMICA de estructuras y dibuja:

  LP-01        ubicación, clave de láminas, diagrama unifilar y datos técnicos
  LP-02..n-1   planta 1:5000 con postes numerados, cuadro por poste, vanos,
               retenidas, PAT, vías OSM, leyenda con cantidades y cajetín
  LP-n         cuadro de estructuras con coordenadas UTM y resumen por tipo

Salidas: datos/estructuras_propuesta_academica_rev6.csv, plans/LP_REV6.dxf
(modelo en metros UTM 19S + presentaciones A3) y plans/LP_REV6.pdf.

La distribución de postes es una hipótesis de gabinete (vano máximo, ángulos
del KML). No reemplaza la lista aprobada que exige colocar_postes_automatico.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment
from pyproj import Transformer
from shapely.geometry import LineString, Point

ROOT = Path(__file__).resolve().parents[1]
VERTICES = ROOT / "datos" / "vertices_corredor_manual.csv"
ROADS = ROOT / "sources" / "osm_roads.json"
CRUCES = ROOT / "datos" / "cruces_viales_rev3.csv"
OUT_CSV = ROOT / "datos" / "estructuras_propuesta_academica_rev6.csv"
OUT_DXF = ROOT / "plans" / "LP_REV6.dxf"
OUT_PDF = ROOT / "plans" / "LP_REV6.pdf"

# Datos del cajetín: editar aquí.
CAJETIN = {
    "escuela": "ESCUELA PROFESIONAL DE INGENIERIA MECANICA ELECTRICA - EPIME",
    "universidad": "UNIVERSIDAD NACIONAL DEL ALTIPLANO - PUNO",
    "proyecto": "LINEA PRIMARIA 22.9 kV(*) CAPACHICA - LLACHON",
    "ubicacion": "DIST. CAPACHICA - PROV. PUNO - REG. PUNO",
    "autor": "POR DESIGNAR",
    "revisado": "",
    "fecha": "18/10/2026",
    "revision": "REV. 6",
}
# Hipótesis académicas (marcadas con (*) en planos).
TENSION = "22.9 kV(*)"
CONDUCTOR = "AAAC 3x35 mm2(*)"
VANO_MAX = 100.0          # m, vano máximo de gabinete
ANCLAJE_CADA = 1000.0     # m, retención de paso
PAT_CADA = 4              # PAT-3 cada n postes de alineamiento
SIMPLIFICAR = 6.0         # m, tolerancia para vértices de diseño
SEPARACION_MIN = 30.0     # m, vértices más cercanos se fusionan
ESCALA_PLANTA = 5000

POSTE = {"PS-1": "CAC 12/300", "PA-1": "CAC 12/400", "PR-1": "CAC 12/500"}
DESCRIPCION = {
    "PS-1": "Alineamiento 0-5, aislador pin",
    "PA-1": "Angulo 5-30, cadena suspension",
    "PR-1": "Retencion, doble cadena anclaje",
}
TO_UTM = Transformer.from_crs(4326, 32719, always_xy=True)

A3 = (420.0, 297.0)
VP = (15.0, 62.0, 405.0, 279.0)   # zona de dibujo de planta (mm papel)


# ---------------------------------------------------------------- geometría
def leer_segmentos(path: Path = VERTICES) -> dict[int, list[tuple[float, float]]]:
    segs: dict[int, list[tuple[float, float]]] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            segs.setdefault(int(r["segmento"]), []).append((float(r["este_m"]), float(r["norte_m"])))
    return dict(sorted(segs.items()))


def deflexion(a, b, c) -> float:
    """Ángulo de desvío en b (grados, + izquierda)."""
    h1 = math.atan2(b[1] - a[1], b[0] - a[0])
    h2 = math.atan2(c[1] - b[1], c[0] - b[0])
    return math.degrees((h2 - h1 + math.pi) % (2 * math.pi) - math.pi)


def vertices_diseno(eje: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = list(LineString(eje).simplify(SIMPLIFICAR).coords)
    # ponytail: fusiona el tramo más corto en su punto medio (O(n²), basta para ~60 vértices);
    # así una curva dibujada con puntos cada 20 m conserva su forma y longitud.
    while len(pts) > 2:
        i = min(range(len(pts) - 1), key=lambda k: math.dist(pts[k], pts[k + 1]))
        if math.dist(pts[i], pts[i + 1]) >= SEPARACION_MIN:
            break
        if i == 0:
            del pts[1]
        elif i + 1 == len(pts) - 1:
            del pts[i]
        else:
            pts[i:i + 2] = [((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)]
    return pts


def proponer_estructuras(segs: dict[int, list[tuple[float, float]]]) -> list[dict]:
    eje = [p for s in segs.values() for p in s]   # los empalmes quedan como recta entre extremos
    v = vertices_diseno(eje)
    puntos: list[tuple[float, float]] = [v[0]]
    for a, b in zip(v, v[1:]):
        n = max(1, math.ceil(math.dist(a, b) / VANO_MAX))
        puntos += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    seg_lines = {k: LineString(s) for k, s in segs.items()}
    filas, desde_anclaje, n_ps, prog = [], 0.0, 0, 0.0
    for i, p in enumerate(puntos):
        ang = 0.0 if i in (0, len(puntos) - 1) else deflexion(puntos[i - 1], p, puntos[i + 1])
        vano_ant = math.dist(puntos[i - 1], p) if i else 0.0
        desde_anclaje += vano_ant
        prog += vano_ant
        if i in (0, len(puntos) - 1):
            armado, ret, motivo = "PR-1", "1xR-1", "terminal"
        elif abs(ang) > 30:
            armado, ret, motivo = "PR-1", "2xR-1", "angulo"
        elif desde_anclaje >= ANCLAJE_CADA:   # también sobre un PA-1: el anclaje no se posterga
            armado, ret, motivo = "PR-1", "2xR-1", "anclaje de paso"
        elif abs(ang) > 5:
            armado, ret, motivo = "PA-1", "1xR-1", "angulo"
        else:
            armado, ret, motivo = "PS-1", "", "alineamiento"
        if armado == "PR-1":
            desde_anclaje = 0.0
        if armado == "PS-1":
            n_ps += 1
        pat = "PAT-3" if armado != "PS-1" or n_ps % PAT_CADA == 0 else ""
        seg = min(seg_lines, key=lambda k: seg_lines[k].distance(Point(p)))
        filas.append({
            "id": f"E-{i + 1:03d}", "codigo_gisem": "", "segmento": str(seg),
            "progresiva_m": f"{prog:.2f}", "este_m": f"{p[0]:.2f}",
            "norte_m": f"{p[1]:.2f}", "utm": "EPSG:32719", "tipo_poste": POSTE[armado],
            "armado": armado, "angulo_deflexion_grados": f"{ang:.2f}",
            "retenida": ret or "NINGUNA", "pat": pat or "NINGUNO",
            "observaciones": f"{motivo}; propuesta academica de gabinete, por replantear",
            "vano_anterior_m": f"{vano_ant:.1f}",
        })
    return filas


# ---------------------------------------------------------------- dibujo
def _layers(doc):
    for name, color, lt in [
        ("RP_CONDUCTOR", 5, "CONTINUOUS"), ("RP_EMPALME", 1, "DASHED"), ("RP_POSTE", 1, "CONTINUOUS"),
        ("RP_RETENIDA", 1, "CONTINUOUS"), ("RP_PTIERRA", 2, "CONTINUOUS"), ("RP_CUADROPOSTE", 5, "CONTINUOUS"),
        ("RP_TEXT", 130, "CONTINUOUS"), ("RP_VANO", 4, "CONTINUOUS"), ("VIAS", 8, "CONTINUOUS"),
        ("CRUCES", 30, "CONTINUOUS"), ("CLAVE_LAMINAS", 6, "CONTINUOUS"), ("ROTULO", 7, "CONTINUOUS"),
        ("RP_LEYENDA", 7, "CONTINUOUS"), ("NM", 5, "CONTINUOUS"), ("MARCO", 7, "CONTINUOUS"),
        ("UNIFILAR", 7, "CONTINUOUS"), ("REDCAD_VIEWPORTS", 8, "CONTINUOUS"),
    ]:
        if name not in doc.layers:
            doc.layers.add(name, color=color, linetype=lt)
    doc.layers.get("REDCAD_VIEWPORTS").dxf.plot = 0


def _blocks(doc):
    """Bloques en mm de papel; se insertan con escala = m de modelo por mm."""
    b = doc.blocks.new("POSTE_LP")
    b.add_circle((0, 0), 0.9, dxfattribs={"layer": "0"})
    b = doc.blocks.new("RETENIDA")
    b.add_line((0, 0), (4.5, 0), dxfattribs={"layer": "0"})
    b.add_arc((5.3, 0), 0.8, 90, 270, dxfattribs={"layer": "0"})
    b = doc.blocks.new("PAT")
    b.add_line((0, 0), (0, -1.0), dxfattribs={"layer": "0"})
    for y, w in ((-1.0, 1.0), (-1.4, 0.65), (-1.8, 0.3)):
        b.add_line((-w, y), (w, y), dxfattribs={"layer": "0"})
    b = doc.blocks.new("CUADRO_POSTE")
    w, h = 13.0, 7.5
    b.add_lwpolyline([(0, 0), (w, 0), (w, h), (0, h)], close=True, dxfattribs={"layer": "0"})
    b.add_line((0, h * 2 / 3), (w, h * 2 / 3), dxfattribs={"layer": "0"})
    b.add_line((0, h / 3), (w, h / 3), dxfattribs={"layer": "0"})
    for tag, y in (("NUMERO", h * 5 / 6), ("ARMADO", h / 2), ("PAT", h / 6)):
        b.add_attdef(tag, (w / 2, y), dxfattribs={"height": 1.5, "layer": "0", "style": "ROMANS"}
                     ).set_placement((w / 2, y), align=TextEntityAlignment.MIDDLE_CENTER)
    b = doc.blocks.new("NM")
    b.add_lwpolyline([(0, 0), (-2.2, -6), (0, -4.5), (2.2, -6)], close=True, dxfattribs={"layer": "0"})
    b.add_hatch(color=5).paths.add_polyline_path([(0, 0), (0, -4.5), (-2.2, -6)], is_closed=True)
    b.add_circle((0, -9), 1.6, dxfattribs={"layer": "0"})
    b.add_line((-3.5, -9), (3.5, -9), dxfattribs={"layer": "0"})
    b.add_line((0, -4.5), (0, -14), dxfattribs={"layer": "0"})
    b.add_text("N.M.", dxfattribs={"height": 3, "layer": "0", "style": "ROMANS"}).set_placement(
        (0, 2.5), align=TextEntityAlignment.BOTTOM_CENTER)


def _t(lay, x, y, s, h=2.0, layer="ROTULO", align=TextEntityAlignment.LEFT, rot=0.0):
    lay.add_text(str(s), dxfattribs={"height": h, "layer": layer, "style": "ROMANS", "rotation": rot}
                 ).set_placement((x, y), align=align)


def _rect(lay, x0, y0, x1, y1, layer="ROTULO"):
    lay.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})


def leer_cruces_rev3() -> list[tuple[str, float, float]]:
    if not CRUCES.is_file():
        return []
    with CRUCES.open(encoding="utf-8-sig", newline="") as f:
        return [(r["id"], float(r["este_utm19s_m"]), float(r["norte_utm19s_m"])) for r in csv.DictReader(f)]


def dibujar_modelo(msp, filas, segs, cruces=None):
    k = ESCALA_PLANTA / 1000.0   # m de modelo por mm de papel
    for s in segs.values():
        msp.add_lwpolyline(s, dxfattribs={"layer": "RP_CONDUCTOR", "const_width": 0.25 * k})
    lst = list(segs.values())
    for a, b in zip(lst, lst[1:]):
        msp.add_line(a[-1], b[0], dxfattribs={"layer": "RP_EMPALME"})
    pts = [(float(f["este_m"]), float(f["norte_m"])) for f in filas]
    for i, (f, p) in enumerate(zip(filas, pts)):
        msp.add_blockref("POSTE_LP", p, dxfattribs={"layer": "RP_POSTE", "xscale": k, "yscale": k})
        prev, nxt = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        rumbo = math.degrees(math.atan2(nxt[1] - prev[1], nxt[0] - prev[0]))
        normal = rumbo + 90
        if f["retenida"] != "NINGUNA":
            if f["observaciones"].startswith("terminal"):
                dirs = [math.degrees(math.atan2(p[1] - (nxt if i == 0 else prev)[1],
                                                p[0] - (nxt if i == 0 else prev)[0]))]
            elif f["observaciones"].startswith("anclaje"):
                dirs = [rumbo, rumbo + 180]
            else:   # ángulo: hacia el exterior de la curva
                ang = float(f["angulo_deflexion_grados"])
                out = rumbo - 90 if ang > 0 else rumbo + 90
                dirs = [out] if f["retenida"].startswith("1") else [out - 25, out + 25]
            for d in dirs:
                msp.add_blockref("RETENIDA", p, dxfattribs={"layer": "RP_RETENIDA", "xscale": k, "yscale": k, "rotation": d})
        if f["pat"] != "NINGUNO":
            msp.add_blockref("PAT", (p[0] + 1.6 * k, p[1] - 1.0 * k), dxfattribs={"layer": "RP_PTIERRA", "xscale": k, "yscale": k})
        lado = 1 if i % 2 == 0 else -1
        off = 11.0 * k
        c = (p[0] + lado * off * math.cos(math.radians(normal)), p[1] + lado * off * math.sin(math.radians(normal)))
        msp.add_line(p, c, dxfattribs={"layer": "RP_CUADROPOSTE"})
        ref = msp.add_blockref("CUADRO_POSTE", (c[0] - 6.5 * k, c[1] - 3.75 * k),
                               dxfattribs={"layer": "RP_CUADROPOSTE", "xscale": k, "yscale": k})
        ref.add_auto_attribs({"NUMERO": f"{i + 1:03d}", "ARMADO": f["armado"],
                              "PAT": f["pat"] if f["pat"] != "NINGUNO" else "--"})
        for a in ref.attribs:
            a.dxf.height = 1.5 * k
        if i:
            m = ((p[0] + prev[0]) / 2, (p[1] + prev[1]) / 2)
            r = math.degrees(math.atan2(p[1] - prev[1], p[0] - prev[0]))
            r = r + 180 if 90 < r <= 270 or -270 <= r < -90 else r
            _t(msp, m[0], m[1] + 0.6 * k, f"{float(f['vano_anterior_m']):.0f} m", 1.3 * k, "RP_VANO",
               TextEntityAlignment.BOTTOM_CENTER, r)
    # vías OSM y cruces
    if ROADS.is_file():
        data = json.loads(ROADS.read_text(encoding="utf-8"))
        for w in data.get("elements", []):
            g = w.get("geometry") or []
            if len(g) > 1:
                msp.add_lwpolyline([TO_UTM.transform(q["lon"], q["lat"]) for q in g], dxfattribs={"layer": "VIAS"})
    for ident, x, y in leer_cruces_rev3() if cruces is None else cruces:
        msp.add_circle((x, y), 1.8 * k, dxfattribs={"layer": "CRUCES"})
        _t(msp, x + 2.2 * k, y - 3.2 * k, ident, 1.2 * k, "CRUCES")


def ventanas(pts, ancho_m, alto_m):
    """Corta el recorrido en ventanas N-arriba que caben en el viewport."""
    out, i = [], 0
    while i < len(pts) - 1:
        j = i + 1
        while j + 1 < len(pts):
            xs, ys = [p[0] for p in pts[i:j + 2]], [p[1] for p in pts[i:j + 2]]
            if max(xs) - min(xs) > ancho_m * 0.86 or max(ys) - min(ys) > alto_m * 0.80:
                break
            j += 1
        xs, ys = [p[0] for p in pts[i:j + 1]], [p[1] for p in pts[i:j + 1]]
        out.append((i, j, ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)))
        i = j
    return out


def cajetin(lay, tema, plano, hoja, escala):
    W, H = A3
    _rect(lay, 5, 5, W - 5, H - 5, "MARCO")
    _rect(lay, 10, 10, W - 10, H - 10, "MARCO")
    x0, y0, x1 = W - 10 - 235, 10, W - 10
    rows = [y0, y0 + 11, y0 + 22, y0 + 33, y0 + 44, y0 + 52]
    _rect(lay, x0, y0, x1, rows[-1])
    for y in rows[1:-1]:
        lay.add_line((x0, y), (x1 - 35, y), dxfattribs={"layer": "ROTULO"})
    lay.add_line((x1 - 35, y0), (x1 - 35, rows[4]), dxfattribs={"layer": "ROTULO"})
    lay.add_line((x0, rows[4]), (x1, rows[4]), dxfattribs={"layer": "ROTULO"})
    lay.add_line((x0 + 55, y0), (x0 + 55, rows[3]), dxfattribs={"layer": "ROTULO"})
    lay.add_line((x0 + 27, rows[2]), (x0 + 27, rows[3]), dxfattribs={"layer": "ROTULO"})
    _t(lay, x0 + 3, rows[4] + 2.2, CAJETIN["escuela"], 2.6)
    _t(lay, x1 - 3, rows[4] + 2.2, CAJETIN["universidad"], 1.8, align=TextEntityAlignment.RIGHT)
    _t(lay, x0 + 3, rows[3] + 3.5, "PROYECTO:", 2.2)
    _t(lay, x0 + 26, rows[3] + 3.5, CAJETIN["proyecto"], 3.0)
    _t(lay, x0 + 3, rows[2] + 6.5, "ESCALA", 1.8)
    _t(lay, x0 + 30, rows[2] + 6.5, "FECHA", 1.8)
    _t(lay, x0 + 3, rows[2] + 2, escala, 2.6 if len(escala) <= 8 else 1.6)
    _t(lay, x0 + 30, rows[2] + 2, CAJETIN["fecha"], 2.4)
    _t(lay, x0 + 58, rows[2] + 3.5, "TEMA:", 2.0)
    _t(lay, x0 + 72, rows[2] + 3.5, tema, 2.6)
    _t(lay, x0 + 3, rows[1] + 6.5, "UBICACION:", 1.8)
    _t(lay, x0 + 3, rows[1] + 2, CAJETIN["revision"], 2.2)
    _t(lay, x0 + 58, rows[1] + 3.5, CAJETIN["ubicacion"], 2.4)
    _t(lay, x0 + 3, y0 + 7, "REVISADO:", 1.8)
    _t(lay, x0 + 3, y0 + 2.5, CAJETIN["revisado"] or "_" * 24, 1.8)
    _t(lay, x0 + 58, y0 + 3.5, "AUTOR:", 2.0)
    _t(lay, x0 + 74, y0 + 3.5, CAJETIN["autor"], 2.6)
    _t(lay, x1 - 33, rows[3] + 6, "PLANO N", 1.8)
    _t(lay, x1 - 17.5, rows[2] + 3, plano, 5.0, align=TextEntityAlignment.MIDDLE_CENTER)
    _t(lay, x1 - 17.5, y0 + 6, hoja, 2.6, align=TextEntityAlignment.MIDDLE_CENTER)


LEYENDA = {"retenida": "RETENIDA SIMPLE R-1", "pat": "PUESTA A TIERRA PAT-3", "empalmes": 3, "cruces": 44}


def leyenda(lay, filas, x, y):
    n_ret = sum(int(f["retenida"][0]) for f in filas if f["retenida"] != "NINGUNA")
    L = sum(float(f["vano_anterior_m"]) for f in filas)
    items = [
        ("POSTE_LP", len(filas), "POSTE DE C.A.C. " + "/".join(sorted({f["tipo_poste"].split()[-1].split("/")[0] for f in filas})) + " m (PROYECTADO)"),
        ("RETENIDA", n_ret, LEYENDA["retenida"]),
        ("PAT", sum(1 for f in filas if f["pat"] != "NINGUNO"), LEYENDA["pat"]),
        ("LINEA", f"{L:,.0f} m", f"CONDUCTOR {CONDUCTOR} - {TENSION}"),
        ("EMPALME", LEYENDA["empalmes"], "EMPALME ENTRE TRAMOS KML (POR LEVANTAR)"),
        ("CRUCE", LEYENDA["cruces"], "CRUCE VIAL OSM (VERIFICAR EN CAMPO)"),
    ]
    items = [it for it in items if it[1] != 0]
    _t(lay, x, y + 4, "LEYENDA", 2.4, "RP_LEYENDA")
    for n, (sym, q, txt) in enumerate(items):
        yy = y - n * 6
        if sym in ("POSTE_LP", "RETENIDA", "PAT"):
            lay.add_blockref(sym, (x + 4, yy), dxfattribs={"layer": {"POSTE_LP": "RP_POSTE", "RETENIDA": "RP_RETENIDA", "PAT": "RP_PTIERRA"}[sym], "xscale": 1.3, "yscale": 1.3})
        elif sym == "LINEA":
            lay.add_line((x, yy), (x + 9, yy), dxfattribs={"layer": "RP_CONDUCTOR", "lineweight": 50})
        elif sym == "EMPALME":
            lay.add_line((x, yy), (x + 9, yy), dxfattribs={"layer": "RP_EMPALME"})
        else:
            lay.add_circle((x + 4, yy), 1.2, dxfattribs={"layer": "CRUCES"})
        _t(lay, x + 14, yy - 0.8, q, 1.8, "RP_LEYENDA")
        _t(lay, x + 30, yy - 0.8, txt, 1.8, "RP_LEYENDA")


def cuadro_tipos(lay, filas, x, y):
    cols = [("TIPO", 0), ("ARMADO", 32), ("POSTE", 50), ("RETENIDA", 72), ("PAT", 90), ("CANT.", 104), ("DESCRIPCION", 116)]
    _t(lay, x, y + 4, "CUADRO DE ESTRUCTURAS", 2.4, "RP_LEYENDA")
    for c, dx in cols:
        _t(lay, x + dx, y, c, 1.7, "RP_LEYENDA")
    grupos = {}
    for f in filas:
        key = (f["observaciones"].split(";")[0], f["armado"], f["retenida"], f["pat"])
        grupos[key] = grupos.get(key, 0) + 1
    for n, ((motivo, arm, ret, pat), q) in enumerate(sorted(grupos.items(), key=lambda kv: (kv[0][1], kv[0][0]))):
        yy = y - 4.2 * (n + 1)
        for v, dx in ((motivo.capitalize(), 0), (arm, 32), (next(f["tipo_poste"] for f in filas if f["armado"] == arm).replace("CAC ", ""), 50),
                      (ret.replace("NINGUNA", "-"), 72), (pat.replace("NINGUNO", "-"), 90), (q, 104),
                      (DESCRIPCION.get(arm, ""), 116)):
            _t(lay, x + dx, yy, v, 1.5, "RP_LEYENDA")
    _t(lay, x + 80, y - 4.2 * (len(grupos) + 1), f"TOTAL DE POSTES      {len(filas)}", 1.8, "RP_LEYENDA")


def generar(out_dxf: Path = OUT_DXF, out_csv: Path = OUT_CSV, out_pdf: Path | None = OUT_PDF) -> dict:
    segs = leer_segmentos()
    filas = proponer_estructuras(segs)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    return armar_doc(filas, segs, out_dxf, out_pdf)


def armar_doc(filas, segs, out_dxf, out_pdf, cruces=None, extra=None, n_extra=0) -> dict:
    """Modelo UTM + LP-01 ubicación, plantas, [láminas extra], cuadro final.

    extra(doc, nueva, primer_numero, n_total) agrega n_extra presentaciones tras las plantas."""
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 6
    doc.styles.add("ROMANS", font="romans.shx") if "ROMANS" not in doc.styles else None
    _layers(doc)
    _blocks(doc)
    msp = doc.modelspace()
    dibujar_modelo(msp, filas, segs, cruces)

    pts = [(float(f["este_m"]), float(f["norte_m"])) for f in filas]
    vw, vh = VP[2] - VP[0], VP[3] - VP[1]
    k = ESCALA_PLANTA / 1000.0
    vents = ventanas(pts, vw * k, vh * k)
    n_total = len(vents) + 2 + n_extra
    def nueva(nombre):
        lay = doc.layouts.new(nombre)
        if "Layout1" in doc.layouts:
            doc.layouts.delete("Layout1")
        lay.page_setup(size=A3, margins=(0, 0, 0, 0), units="mm")
        return lay

    # LP-01 ubicación + unifilar
    lay = nueva("LP-01")
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    bw, bh, cy = 245.0, 215.0, 72.0 + 215.0 / 2
    esc = next(e for e in (10000, 15000, 20000, 25000, 30000, 40000, 50000, 60000, 75000, 100000)
               if (max(xs) - min(xs)) * 1.15 <= bw * e / 1000 and (max(ys) - min(ys)) * 1.15 <= bh * e / 1000)
    vp = lay.add_viewport(center=(15 + bw / 2, cy), size=(bw, bh),
                          view_center_point=((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2), view_height=bh * esc / 1000)
    vp.dxf.layer = "REDCAD_VIEWPORTS"
    vp.frozen_layer_names = ["RP_CUADROPOSTE", "RP_VANO", "RP_PTIERRA", "RP_RETENIDA", "CRUCES"]
    mc = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)
    papel = lambda x, y: (15 + bw / 2 + (x - mc[0]) * 1000 / esc, cy + (y - mc[1]) * 1000 / esc)
    for n, (i, j, c) in enumerate(vents):   # clave de láminas en papel, no en el modelo
        x0, y0 = papel(c[0] - vw * k / 2, c[1] - vh * k / 2)
        x1, y1 = papel(c[0] + vw * k / 2, c[1] + vh * k / 2)
        _rect(lay, x0, y0, x1, y1, "CLAVE_LAMINAS")
        _t(lay, x1 + 1, (y0 + y1) / 2, f"LP-{n + 2:02d}", 2.0, "CLAVE_LAMINAS")
    _t(lay, 268, 278, "PLANO DE UBICACION Y CLAVE DE LAMINAS", 3.0)
    lay.add_blockref("NM", (250, 262), dxfattribs={"layer": "NM"})
    unifilar(lay, 268, 230, filas)
    datos_tecnicos(lay, 268, 150, filas)
    cajetin(lay, "UBICACION Y DIAGRAMA UNIFILAR", "LP-01", f"01/{n_total:02d}", f"1:{esc}")
    _t(lay, 15, 66, "(*) Tension, conductor y distribucion de postes: hipotesis academica; confirmar con Electro Puno y topografia.", 1.8)

    # planta
    for n, (i, j, c) in enumerate(vents):
        nombre = f"LP-{n + 2:02d}"
        lay = nueva(nombre)
        vp = lay.add_viewport(center=((VP[0] + VP[2]) / 2, (VP[1] + VP[3]) / 2), size=(vw, vh),
                              view_center_point=c, view_height=vh * k)
        vp.dxf.layer = "REDCAD_VIEWPORTS"
        _rect(lay, VP[0], VP[1], VP[2], VP[3], "MARCO")
        lay.add_blockref("NM", (VP[2] - 12, VP[3] - 12), dxfattribs={"layer": "NM"})
        _t(lay, VP[0] + 1, VP[3] + 2.5, f"PLANTA - ESTRUCTURAS E-{i + 1:03d} A E-{j + 1:03d}   |   PROG. {float(filas[i]['progresiva_m']):,.0f} - {float(filas[j]['progresiva_m']):,.0f} m", 2.4)
        if n:
            _t(lay, VP[0] + 3, VP[1] + 3, f"VIENE DE LP-{n + 1:02d}", 2.0)
        if n < len(vents) - 1:
            _t(lay, VP[2] - 3, VP[1] + 3, f"CONTINUA EN LP-{n + 3:02d}", 2.0, align=TextEntityAlignment.RIGHT)
        escala_grafica(lay, VP[2] - 112, VP[1] + 12, ESCALA_PLANTA)
        leyenda(lay, filas, 15, 52)
        cajetin(lay, "RED DE LINEA PRIMARIA - PLANTA", nombre, f"{n + 2:02d}/{n_total:02d}", f"1:{ESCALA_PLANTA}")

    if extra:
        extra(doc, nueva, len(vents) + 2, n_total)

    # cuadro de estructuras
    nombre = f"LP-{n_total:02d}"
    lay = nueva(nombre)
    cuadro_coordenadas(lay, filas)
    cuadro_tipos(lay, filas, 15, 52)
    cajetin(lay, "CUADRO DE ESTRUCTURAS Y COORDENADAS", nombre, f"{n_total:02d}/{n_total:02d}", "S/E")

    for n, lay in enumerate(l for l in doc.layouts if l.name != "Model"):
        lay.dxf_layout.dxf.taborder = n + 1   # AutoCAD omite láminas con taborder repetido
    doc.saveas(out_dxf)
    if out_pdf:
        exportar_pdf(doc, out_pdf)
    return {"estructuras": len(filas), "laminas": n_total, "escala_ubicacion": esc,
            "longitud_m": round(sum(float(f["vano_anterior_m"]) for f in filas), 1)}


def escala_grafica(lay, x, y, escala):
    paso = 100.0 * 1000 / escala   # mm por 100 m
    for n in range(5):
        _rect(lay, x + n * paso, y, x + (n + 1) * paso, y + 1.5, "ROTULO")
        if n % 2 == 0:
            lay.add_hatch(color=7).paths.add_polyline_path(
                [(x + n * paso, y), (x + (n + 1) * paso, y), (x + (n + 1) * paso, y + 1.5), (x + n * paso, y + 1.5)], is_closed=True)
        _t(lay, x + n * paso, y + 2.5, f"{n * 100}", 1.5, align=TextEntityAlignment.BOTTOM_CENTER)
    _t(lay, x + 5 * paso, y + 2.5, "500 m", 1.5, align=TextEntityAlignment.BOTTOM_CENTER)
    _t(lay, x, y - 3.5, f"ESCALA GRAFICA 1:{escala}", 1.6)


UNIFILAR = {"seccionamiento": "SECC. CUT-OUT 27 kV", "pararrayos": "PARARRAYOS 21 kV"}


def unifilar(lay, x, y, filas):
    L = sum(float(f["vano_anterior_m"]) for f in filas)
    _t(lay, x, y + 32, "DIAGRAMA UNIFILAR", 3.0, "UNIFILAR")
    lay.add_line((x, y - 12), (x, y + 12), dxfattribs={"layer": "UNIFILAR", "lineweight": 70})
    _t(lay, x - 2, y + 15, "RED MT EXISTENTE", 1.7, "UNIFILAR")
    _t(lay, x - 2, y + 18, "ELECTRO PUNO (NMT000367723)", 1.7, "UNIFILAR")
    lay.add_line((x, y), (x + 14, y), dxfattribs={"layer": "UNIFILAR"})
    # seccionador fusible tipo expulsión (cut-out)
    lay.add_line((x + 14, y), (x + 22, y + 4), dxfattribs={"layer": "UNIFILAR"})
    _rect(lay, x + 16, y + 0.5, x + 20, y + 2.5, "UNIFILAR")
    _t(lay, x + 12, y - 5, UNIFILAR["seccionamiento"], 1.5, "UNIFILAR")
    lay.add_line((x + 22, y), (x + 30, y), dxfattribs={"layer": "UNIFILAR"})
    # pararrayos
    lay.add_line((x + 26, y), (x + 26, y - 6), dxfattribs={"layer": "UNIFILAR"})
    _rect(lay, x + 24.8, y - 10, x + 27.2, y - 6, "UNIFILAR")
    lay.add_blockref("PAT", (x + 26, y - 10), dxfattribs={"layer": "RP_PTIERRA"})
    _t(lay, x + 22, y - 17, UNIFILAR["pararrayos"], 1.5, "UNIFILAR")
    lay.add_line((x + 30, y), (x + 120, y), dxfattribs={"layer": "RP_CONDUCTOR", "lineweight": 50})
    for xx in (x + 55, x + 57, x + 59):
        lay.add_line((xx - 1, y - 1.5), (xx + 1, y + 1.5), dxfattribs={"layer": "UNIFILAR"})
    _t(lay, x + 45, y + 3, f"L.P. 3o {TENSION}", 1.8, "UNIFILAR")
    _t(lay, x + 45, y - 4, f"{CONDUCTOR}  L = {L / 1000:.2f} km", 1.8, "UNIFILAR")
    lay.add_line((x + 120, y - 8), (x + 120, y + 8), dxfattribs={"layer": "UNIFILAR", "lineweight": 70})
    _t(lay, x + 104, y + 11, "LLACHON", 1.8, "UNIFILAR")
    _t(lay, x + 100, y - 13, "CARGA: POR DEFINIR", 1.6, "UNIFILAR")


def datos_tecnicos(lay, x, y, filas):
    L = sum(float(f["vano_anterior_m"]) for f in filas)
    vanos = [float(f["vano_anterior_m"]) for f in filas[1:]]
    lineas = [
        "CARACTERISTICAS TECNICAS",
        f"Tension nominal: {TENSION}   Sistema: trifasico 3 hilos",
        f"Conductor: {CONDUCTOR}",
        "Postes C.A.C.: " + ", ".join(sorted({f["tipo_poste"].replace("CAC ", "") for f in filas})),
        "Aislamiento: polimerico (pin y suspension)",
        f"Longitud total: {L:,.0f} m   Estructuras: {len(filas)}",
        f"Vano max/prom: {max(vanos):.0f} / {sum(vanos) / len(vanos):.0f} m",
        "Normas: CNE Suministro 2011, RD 018-2003-EM/DGE",
        "Coordenadas: UTM WGS84 zona 19S (EPSG:32719)",
    ]
    _rect(lay, x - 3, y - 4.5 * len(lineas) - 2, x + 135, y + 5, "RP_LEYENDA")
    for n, s in enumerate(lineas):
        _t(lay, x, y - 4.5 * n, s, 2.2 if n == 0 else 1.8, "RP_LEYENDA")


def cuadro_coordenadas(lay, filas):
    cols = [("N", 0), ("ARM.", 9), ("POSTE", 20), ("RET.", 39), ("PAT", 50), ("PROG.", 61), ("VANO", 75), ("ESTE", 86), ("NORTE", 104)]
    ancho, filas_por_bloque, h = 125.0, 58, 3.4
    _t(lay, 15, 280, "CUADRO DE ESTRUCTURAS - COORDENADAS UTM WGS84 19S (PROPUESTA ACADEMICA, POR REPLANTEAR)", 2.6)
    for b in range(math.ceil(len(filas) / filas_por_bloque)):
        x0, y0 = 15 + b * (ancho + 5), 272
        _rect(lay, x0 - 1, y0 - h * (filas_por_bloque + 1) - 1, x0 + ancho, y0 + 3, "RP_LEYENDA")
        for c, dx in cols:
            _t(lay, x0 + dx, y0 - 1, c, 1.6, "RP_LEYENDA")
        for n, f in enumerate(filas[b * filas_por_bloque:(b + 1) * filas_por_bloque]):
            yy = y0 - h * (n + 1) - 1
            for v, dx in ((f["id"][2:], 0), (f["armado"], 9), (f["tipo_poste"].replace("CAC ", ""), 20),
                          (f["retenida"].replace("NINGUNA", "-"), 39), (f["pat"].replace("NINGUNO", "-"), 50),
                          (f"{float(f['progresiva_m']):.0f}", 61), (f["vano_anterior_m"], 75),
                          (f["este_m"], 86), (f["norte_m"], 104)):
                _t(lay, x0 + dx, yy, v, 1.4, "RP_LEYENDA")


def exportar_pdf(doc, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE)
    with PdfPages(path) as pdf:
        for name in doc.layouts.names_in_taborder():
            if name == "Model":
                continue
            fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
            ax = fig.add_axes([0, 0, 1, 1])
            Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.layouts.get(name), finalize=False)
            ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.set_aspect("equal"); ax.axis("off")
            pdf.savefig(fig)
            plt.close(fig)


ACCORE = Path(r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe")


def exportar_autocad(dxf: Path, accore: Path = ACCORE) -> None:
    """DXF -> DWG 2018 y PDF de todas las láminas con AutoCAD (si está instalado)."""
    import subprocess
    import tempfile
    dwg, pdf = dxf.with_suffix(".dwg"), dxf.with_suffix(".pdf")
    for viejo in (dwg, pdf):   # si existen, AutoCAD pregunta si reemplazar y se queda esperando
        viejo.unlink(missing_ok=True)
    scr = Path(tempfile.mkdtemp()) / "exportar.scr"
    scr.write_text(f'FILEDIA 0\n_.SAVEAS 2018 "{dwg}"\n_.LAYOUT _Set LP-01\n'
                   f'_-EXPORT _P _A "{pdf}"\n_.QUIT _Y\n', encoding="ascii")
    subprocess.run([str(accore), "/i", str(dxf), "/s", str(scr)], cwd=scr.parent,
                   capture_output=True, timeout=600, check=False)
    if not dwg.is_file():
        raise RuntimeError("AutoCAD no generó el DWG")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sin-pdf", action="store_true")
    ap.add_argument("--autocad", action="store_true",
                    help="DWG + PDF con accoreconsole (reemplaza el PDF de matplotlib)")
    a = ap.parse_args()
    print(json.dumps(generar(out_pdf=None if a.sin_pdf or a.autocad else OUT_PDF), ensure_ascii=False))
    if a.autocad:
        exportar_autocad(OUT_DXF)


if __name__ == "__main__":
    main()
