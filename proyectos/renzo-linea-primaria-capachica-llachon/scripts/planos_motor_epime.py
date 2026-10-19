"""Planos Rev. 8: ingeniería del motor «expediente-lp-22.9kv» + formato EPIME.

El motor de D. H. Ccora (github.com/dilmar231gabriel-ops/expediente-lp-22.9kv)
calcula sobre el DEM Copernicus el plantillado, los armados, los postes, las
retenidas y la PAT. Sus resultados se copian en datos/motor_lp229/resultados/.
Este script los dibuja con el formato de lámina EPIME de la Rev. 6 y agrega:

  PP  perfil y planimetría A3, H 1:5000 y V automática (1:500 a 1:2500), con
      conductor a flecha máxima, distancia de seguridad, tabla de estructuras
      bajo cada poste y franja de planimetría con vías y agua de OSM

Rev. 8: conductor AAAC 35 mm² (óptimo económico), revisor en el cajetín.
Salidas: plans/LP_REV8.dxf (modelo UTM 19S + presentaciones A3), .dwg y .pdf.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from ezdxf.enums import TextEntityAlignment as TA
from shapely.geometry import LineString, Point, shape

import planos_formato_epime as pe

ROOT = Path(__file__).resolve().parents[1]
MOTOR = ROOT / "datos" / "motor_lp229"
OUT_DXF = ROOT / "plans" / "LP_REV8.dxf"
OUT_PDF = ROOT / "plans" / "LP_REV8.pdf"

ESC_H = 5000                     # perfil: escala horizontal
XL, XR = 45.0, 400.0             # zona de dibujo del perfil (mm)
PERFIL_Y = (175.0, 282.0)        # banda del perfil
PLANI_Y, PLANI_MEDIA = 79.0, 14.0   # eje y semiancho (mm) de la planimetría
D_INF, DIST_GENERAL, DIST_CRUCE = 1.10, 6.0, 7.0   # m (proyecto.yaml del motor)
FILAS_TABLA = [   # (título, altura mm, rotado)
    ("ESTRUCTURA", 9, True), ("ARMADO", 9, True), ("POSTE", 8, True), ("RETENIDA", 8, True),
    ("PAT", 8, True), ("PROGRESIVA (m)", 9, True), ("COTA TERRENO (m)", 8, True),
    ("VANO (m)", 8, True), ("FLECHA H6 (m)", 8, True),
]
DESCRIPCION_MOTOR = {
    "PS1-3": "Suspension 0-5, aislador pin",
    "PA1-3": "Angulo 5-30, suspension",
    "PA2-3": "Angulo 30-60, suspension",
    "TS-3": "Retencion-suspension",
    "PR3-3": "Retencion o anclaje",
    "PSER-3": "Arranque con reconectador",
    "PTH-3": "Terminal horizontal",
    "DT-3": "Derivacion con seccionamiento",
}


# ---------------------------------------------------------------- datos del motor
def _lado(a, b, c) -> int:
    cz = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
    return 1 if cz > 0 else -1


def cargar_motor(d: Path = MOTOR) -> dict:
    res = d / "resultados"
    with (res / "planilla_estructuras.csv").open(encoding="utf-8") as f:
        E = list(csv.DictReader(f))
    meta = json.loads((res / "trazado_meta.json").read_text(encoding="utf-8"))
    with (res / "perfil_troncal.csv").open(encoding="utf-8") as f:
        prof = [(float(r["progresiva_m"]), float(r["cota_m"])) for r in csv.DictReader(f)]
    with (res / "parametros_vano.csv").open(encoding="utf-8") as f:
        par = [(float(r["vano_m"]), float(r["p_H6_m"])) for r in csv.DictReader(f)]
    with (res / "cruces.csv").open(encoding="utf-8") as f:
        cruces = [r for r in csv.DictReader(f) if r["tramo"] == "TRONCAL"]
    pts = [(float(r["este"]), float(r["norte"])) for r in E]
    filas = []
    for i, r in enumerate(E):
        arm = r["armado"]
        ang = float(r["angulo_deg"] or 0)
        if 0 < i < len(E) - 1 and ang:
            ang *= _lado(pts[i - 1], pts[i], pts[i + 1])
        if i in (0, len(E) - 1):
            motivo = "terminal"
        elif arm in ("PR3-3", "TS-3"):
            motivo = "anclaje"
        elif arm.startswith("PA"):
            motivo = "angulo"
        elif arm in ("PSER-3", "DT-3"):
            motivo = "equipo"
        else:
            motivo = "alineamiento"
        n_ret = int(float(r["n_retenidas"] or 0))
        pat = r["puesta_tierra"].strip()
        filas.append({
            "id": r["estructura"], "codigo_gisem": "", "segmento": "1",
            "progresiva_m": f"{float(r['progresiva_m']):.2f}", "este_m": f"{pts[i][0]:.2f}",
            "norte_m": f"{pts[i][1]:.2f}", "utm": "EPSG:32719", "tipo_poste": f"CAC {r['poste']}",
            "armado": arm, "angulo_deflexion_grados": f"{ang:.2f}",
            "retenida": f"{n_ret}xRI" if n_ret else "NINGUNA",
            "pat": pat if pat and pat != "-" else "NINGUNO",
            "observaciones": f"{motivo}; motor LP 22,9 kV" + (f"; {r['equipamiento']}" if r["equipamiento"] not in ("", "-") else ""),
            "vano_anterior_m": f"{float(r['vano_atras_m'] or 0):.1f}",
            "cota_m": float(r["cota_m"]), "poste": r["poste"],
        })
    seccion = json.loads((res / "resultados.json").read_text(encoding="utf-8"))["electrico"]["seccion"]
    return {"filas": filas, "troncal": LineString(meta["vertices"]), "perfil": np.array(prof), "seccion": seccion,
            "par": np.array(par), "cruces": cruces, "osm": d / "entrada" / "datos" / "osm_corredor.geojson"}


def cortes_por_longitud(prog: list[float], largo: float) -> list[tuple[int, int]]:
    out, i = [], 0
    while i < len(prog) - 1:
        j = i + 1
        while j + 1 < len(prog) and prog[j + 1] - prog[i] <= largo:
            j += 1
        out.append((i, j))
        i = j
    return out


def _alturas(poste: str) -> tuple[float, float]:
    L = float(poste.split("/")[0])
    top = L - (L / 10 + 0.6)
    return top, top - D_INF


def flecha(par: np.ndarray, vano: float) -> float:
    p = float(np.interp(vano, par[:, 0], par[:, 1]))
    return vano * vano / (8 * p)


def _proyectar(troncal: LineString, coords, s0, s1, media_m):
    """Polilínea UTM -> tramos (progresiva, desplazamiento) dentro de la franja."""
    tramos, actual = [], []
    for x, y in coords:
        s = troncal.project(Point(x, y))
        p = troncal.interpolate(s)
        q = troncal.interpolate(min(s + 1, troncal.length))
        tx, ty = q.x - p.x, q.y - p.y
        n = math.hypot(tx, ty) or 1
        d = ((x - p.x) * (-ty) + (y - p.y) * tx) / n
        if s0 <= s <= s1 and abs(d) <= media_m:
            actual.append((s, d))
        elif actual:
            tramos.append(actual)
            actual = []
    if actual:
        tramos.append(actual)
    return [t for t in tramos if len(t) > 1]


def leer_osm(path: Path, troncal: LineString):
    if not path.is_file():
        return []
    out = []
    for f in json.loads(path.read_text(encoding="utf-8")).get("features", []):
        g = shape(f["geometry"])
        if g.geom_type == "Polygon":
            g = g.exterior
        if g.geom_type not in ("LineString", "LinearRing"):
            continue
        utm = LineString([pe.TO_UTM.transform(x, y) for x, y in g.coords])
        if utm.distance(troncal) > 150:
            continue
        dens = [utm.interpolate(t).coords[0] for t in np.arange(0, utm.length, 8.0)] + [utm.coords[-1]]
        out.append(("VIAS" if f["properties"].get("highway") else "AGUA", dens))
    return out


# ---------------------------------------------------------------- lámina PP
def dibujar_pp(lay, mot, i0, i1, osm):
    filas, prof, par = mot["filas"], mot["perfil"], mot["par"]
    sub = filas[i0:i1 + 1]
    s0, s1 = float(sub[0]["progresiva_m"]), float(sub[-1]["progresiva_m"])
    eh = 1000.0 / ESC_H
    X = lambda s: XL + (s - s0) * eh
    zt = lambda s: float(np.interp(s, prof[:, 0], prof[:, 1]))
    m = (prof[:, 0] >= s0 - 1) & (prof[:, 0] <= s1 + 1)
    zmin = math.floor((prof[m, 1].min() - 2) / 5) * 5
    zmax = max(prof[m, 1].max() + _alturas(f["poste"])[0] for f in sub) + 3
    alto = PERFIL_Y[1] - PERFIL_Y[0] - 6
    esc_v = next(e for e in (200, 250, 500, 1000, 2000, 2500, 5000) if (zmax - zmin) * 1000 / e <= alto)
    ev = 1000.0 / esc_v
    paso = {200: 2, 250: 2, 500: 5, 1000: 10, 2000: 20, 2500: 25, 5000: 50}[esc_v]
    zmin -= math.floor((alto / ev - (zmax - zmin)) / 2 / paso) * paso   # centra el perfil en su franja
    Y = lambda z: PERFIL_Y[0] + (z - zmin) * ev
    # rejilla y cotas
    for z in range(int(zmin), int(zmax) + paso, paso):
        if Y(z) > PERFIL_Y[1]:
            break
        lay.add_line((XL, Y(z)), (X(s1), Y(z)), dxfattribs={"layer": "PP_GRILLA"})
        pe._t(lay, XL - 2, Y(z), f"{z:.0f}", 1.6, "PP_GRILLA", TA.MIDDLE_RIGHT)
    lay.add_line((XL, PERFIL_Y[0]), (XL, PERFIL_Y[1]), dxfattribs={"layer": "PP_GRILLA"})
    pe._t(lay, 12, PERFIL_Y[1] - 4, f"PERFIL LONGITUDINAL  H 1:{ESC_H}  V 1:{esc_v}", 2.2, "PP_TEXTO")
    pe._t(lay, 12, PERFIL_Y[1] - 8, "COTA (m s.n.m.)", 1.6, "PP_TEXTO")
    # terreno y distancia de seguridad
    lay.add_lwpolyline([(X(s), Y(z)) for s, z in prof[m]], dxfattribs={"layer": "PP_TERRENO"})
    cr = np.array([float(c["progresiva_m"]) for c in mot["cruces"]]) if mot["cruces"] else np.array([])
    ss = np.arange(s0, s1 + 0.1, 5.0)
    req = [DIST_CRUCE if len(cr) and np.min(np.abs(cr - s)) <= 20 else DIST_GENERAL for s in ss]
    lay.add_lwpolyline([(X(s), Y(zt(s) + q)) for s, q in zip(ss, req)], dxfattribs={"layer": "PP_DIST_SEGURIDAD"})
    # postes, conductor y flechas
    for k, f in enumerate(sub):
        s, zg = float(f["progresiva_m"]), zt(float(f["progresiva_m"]))
        top, low = _alturas(f["poste"])
        lay.add_line((X(s), Y(zg)), (X(s), Y(zg + top)), dxfattribs={"layer": "PP_POSTE"})
        lay.add_line((X(s) - 1.0, Y(zg + low)), (X(s) + 1.0, Y(zg + low)), dxfattribs={"layer": "PP_POSTE"})
        if k < len(sub) - 1:
            g = sub[k + 1]
            s2 = float(g["progresiva_m"])
            d = s2 - s
            p = float(np.interp(d, par[:, 0], par[:, 1]))
            ya, yb = zg + low, zt(s2) + _alturas(g["poste"])[1]
            xs = np.linspace(0, d, 24)
            zz = ya + (yb - ya) * xs / d - xs * (d - xs) / (2 * p)
            lay.add_lwpolyline([(X(s + a), Y(b)) for a, b in zip(xs, zz)], dxfattribs={"layer": "PP_CONDUCTOR"})
    # tabla bajo el perfil
    y = PERFIL_Y[0] - 3
    filas_y = []
    for titulo, h, _ in FILAS_TABLA:
        filas_y.append((y - h, y))
        pe._rect(lay, 12, y - h, XR + 5, y, "PP_TABLA")
        pe._t(lay, 13, y - h / 2, titulo, 1.5, "PP_TEXTO", TA.MIDDLE_LEFT)
        y -= h
    for k, f in enumerate(sub):
        s = float(f["progresiva_m"])
        vals = [f["id"], f["armado"], f["poste"], f["retenida"].replace("NINGUNA", "-"),
                f["pat"].replace("NINGUNO", "-"), f"{s:,.1f}", f"{zt(s):.1f}"]
        for (ya, yb), v in zip(filas_y, vals):
            pe._t(lay, X(s) + 0.6, (ya + yb) / 2, v, 1.3, "PP_TEXTO", TA.MIDDLE_CENTER, 90)
        if k < len(sub) - 1:
            d = float(sub[k + 1]["progresiva_m"]) - s
            for (ya, yb), v in zip(filas_y[7:], (f"{d:.1f}", f"{flecha(par, d):.2f}")):
                pe._t(lay, X(s + d / 2) + 0.6, (ya + yb) / 2, v, 1.3, "PP_TEXTO", TA.MIDDLE_CENTER, 90)
    # planimetría
    pe._t(lay, 13, PLANI_Y + PLANI_MEDIA - 2, "PLANIMETRIA", 1.8, "PP_TEXTO")
    pe._t(lay, 13, PLANI_Y - PLANI_MEDIA + 2, f"franja +/-{PLANI_MEDIA * ESC_H / 1000:.0f} m", 1.4, "PP_TEXTO")
    pe._rect(lay, XL, PLANI_Y - PLANI_MEDIA, X(s1), PLANI_Y + PLANI_MEDIA, "PP_TABLA")
    media_m = PLANI_MEDIA * ESC_H / 1000
    for capa, coords in osm:
        for tramo in _proyectar(mot["troncal"], coords, s0, s1, media_m):
            lay.add_lwpolyline([(X(s), PLANI_Y + d * eh) for s, d in tramo], dxfattribs={"layer": capa})
    lay.add_line((X(s0), PLANI_Y), (X(s1), PLANI_Y), dxfattribs={"layer": "RP_CONDUCTOR", "lineweight": 35})
    for f in sub:
        s = float(f["progresiva_m"])
        lay.add_circle((X(s), PLANI_Y), 0.7, dxfattribs={"layer": "RP_POSTE"})
        ang = float(f["angulo_deflexion_grados"])
        if abs(ang) >= 1:
            pe._t(lay, X(s) + 0.5, PLANI_Y + 1.5, f"{'Izq' if ang > 0 else 'Der'}. {abs(ang):.1f}", 1.3, "PP_TEXTO", rot=60)
    for c in mot["cruces"]:
        s = float(c["progresiva_m"])
        if s0 <= s <= s1:
            lay.add_line((X(s) - 0.9, PLANI_Y - 0.9), (X(s) + 0.9, PLANI_Y + 0.9), dxfattribs={"layer": "CRUCES"})
            lay.add_line((X(s) - 0.9, PLANI_Y + 0.9), (X(s) + 0.9, PLANI_Y - 0.9), dxfattribs={"layer": "CRUCES"})
            pe._t(lay, X(s), PLANI_Y - 3.0, c["cruce_id"], 1.2, "CRUCES", TA.TOP_CENTER, 90)
    for km in range(math.ceil(s0 / 1000), int(s1 / 1000) + 1):
        lay.add_line((X(km * 1000), PLANI_Y - 2.5), (X(km * 1000), PLANI_Y + 2.5), dxfattribs={"layer": "PP_TEXTO"})
        pe._t(lay, X(km * 1000) + 0.8, PLANI_Y - PLANI_MEDIA + 1.5, f"Km {km}", 1.8, "PP_TEXTO")
    return esc_v


def notas_pp(lay, seccion):
    lineas = [
        "NOTAS",
        "1. Terreno: DEM Copernicus GLO-30 (30 m), no apto para replanteo; verificar con topografia.",
        f"2. Conductor AAAC {seccion} mm2 a flecha maxima (H6: 40 C + 10 C creep) segun calculo mecanico del motor.",
        f"3. Linea discontinua: distancia minima al terreno {DIST_GENERAL:.1f} m ({DIST_CRUCE:.1f} m en cruces de via), CNE-S 2011.",
        "4. Estructuras por plantillado automatico (motor expediente-lp-22.9kv, D. H. Ccora).",
        "5. Planimetria: eje rectificado desarrollado; vias y agua de OpenStreetMap.",
    ]
    for n, s in enumerate(lineas):
        pe._t(lay, 14, 56 - 5 * n, s, 2.0 if n == 0 else 1.55, "PP_TEXTO")


# ---------------------------------------------------------------- armado
def generar(out_dxf: Path = OUT_DXF, out_pdf: Path | None = OUT_PDF, motor: Path = MOTOR) -> dict:
    mot = cargar_motor(motor)
    filas = mot["filas"]
    pe.CAJETIN["revision"] = "REV. 8"
    pe.CONDUCTOR = f"AAAC 3x{mot['seccion']} mm2"
    pe.TENSION = "22.9 kV(*)"
    pe.DESCRIPCION.update(DESCRIPCION_MOTOR)
    pe.LEYENDA.update({"retenida": "RETENIDA INCLINADA RI", "pat": "PUESTA A TIERRA PAT-1 / PAT-2",
                       "empalmes": 0, "cruces": len(mot["cruces"])})
    pe.UNIFILAR.update({"seccionamiento": "RECONECTADOR + CUT-OUT 38 kV", "pararrayos": "PARARRAYOS 24 kV"})
    cortes = cortes_por_longitud([float(f["progresiva_m"]) for f in filas], (XR - XL) * ESC_H / 1000)
    osm = leer_osm(mot["osm"], mot["troncal"])
    escalas = []

    def extra(doc, nueva, primero, n_total):
        for name, color, lt in [("PP_TERRENO", 34, "CONTINUOUS"), ("PP_CONDUCTOR", 5, "CONTINUOUS"),
                                ("PP_POSTE", 1, "CONTINUOUS"), ("PP_DIST_SEGURIDAD", 6, "DASHED"),
                                ("PP_GRILLA", 8, "CONTINUOUS"), ("PP_TABLA", 8, "CONTINUOUS"),
                                ("PP_TEXTO", 7, "CONTINUOUS"), ("AGUA", 5, "CONTINUOUS")]:
            doc.layers.add(name, color=color, linetype=lt)
        for k, (i0, i1) in enumerate(cortes):
            nombre = f"LP-{primero + k:02d}"
            lay = nueva(nombre)
            esc_v = dibujar_pp(lay, mot, i0, i1, osm)
            escalas.append(esc_v)
            notas_pp(lay, mot["seccion"])
            s0, s1 = float(filas[i0]["progresiva_m"]), float(filas[i1]["progresiva_m"])
            pe.cajetin(lay, f"PERFIL Y PLANIMETRIA  KM {s0 / 1000:.3f} - {s1 / 1000:.3f}", nombre,
                       f"{primero + k:02d}/{n_total:02d}", f"H1:{ESC_H} V1:{esc_v}")

    segs = {1: list(mot["troncal"].coords)}
    cruces = [(c["cruce_id"], float(c["este"]), float(c["norte"])) for c in mot["cruces"]]
    info = pe.armar_doc(filas, segs, out_dxf, out_pdf, cruces=cruces, extra=extra, n_extra=len(cortes))
    info.update({"hojas_perfil": len(cortes), "escalas_v": sorted(set(escalas))})
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--autocad", action="store_true", help="DWG + PDF con accoreconsole (si AutoCAD está instalado)")
    ap.add_argument("--dwg", action="store_true", help="DWG con AutoCAD o, si no está, con ODA File Converter")
    a = ap.parse_args()
    print(json.dumps(generar(out_pdf=None if a.autocad else OUT_PDF), ensure_ascii=False))
    if a.autocad:
        pe.exportar_autocad(OUT_DXF)
    elif a.dwg:
        pe.dxf_a_dwg(OUT_DXF)
    if a.autocad or a.dwg:
        for dxf in sorted((OUT_DXF.parent / "armados_lp229").glob("*.dxf")):
            pe.dxf_a_dwg(dxf)


if __name__ == "__main__":
    main()
