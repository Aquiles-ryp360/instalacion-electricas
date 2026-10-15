"""Audita el KML original y propone puntos de inspección, sin dimensionar postes."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import date
from pathlib import Path

from lxml import etree
from pyproj import Geod, Transformer
from shapely.geometry import LineString, Point, shape
from shapely.ops import nearest_points

ROOT = Path(__file__).resolve().parents[1]
KML = ROOT / "sources/ruta topografica capachica llachon.kml"
NS = {"k": "http://www.opengis.net/kml/2.2"}
TO_UTM = Transformer.from_crs(4326, 32719, always_xy=True)
TO_GEO = Transformer.from_crs(32719, 4326, always_xy=True)
GEOD = Geod(ellps="WGS84")
CONNECTION = (-69.8316111, -15.6421333)


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    if path.exists():
        raise FileExistsError(f"Salida existente: {path}; archive la revisión antes de regenerar")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, value: str) -> None:
    if path.exists():
        raise FileExistsError(f"Salida existente: {path}; archive la revisión antes de regenerar")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def read_lines() -> tuple[etree._ElementTree, list[dict]]:
    if not KML.is_file():
        raise FileNotFoundError(f"Entrada obligatoria ausente: {KML}")
    tree = etree.parse(str(KML))
    segments = []
    for placemark in tree.xpath("//k:Placemark", namespaces=NS):
        for coordinates in placemark.xpath(".//k:LineString/k:coordinates", namespaces=NS):
            lonlat = [tuple(float(v) for v in token.split(",")[:2]) for token in coordinates.text.split()]
            if len(lonlat) < 2:
                raise ValueError("Segmento KML con menos de dos vértices")
            if any(not (-180 <= lon <= 180 and -90 <= lat <= 90) for lon, lat in lonlat):
                raise ValueError("Coordenadas KML fuera de rango")
            xy = [TO_UTM.transform(*p) for p in lonlat]
            segments.append({"name": placemark.findtext("{http://www.opengis.net/kml/2.2}name"),
                             "lonlat": lonlat, "xy": xy, "line": LineString(xy)})
    if not segments:
        raise ValueError("El KML no contiene LineString")
    return tree, segments


def load_gis(name: str) -> list[dict]:
    return json.loads((ROOT / "sources" / name).read_text(encoding="utf-8"))["features"]


def angle(a, b, c) -> float:
    u = (b[0]-a[0], b[1]-a[1]); v = (c[0]-b[0], c[1]-b[1])
    if math.hypot(*u) < .01 or math.hypot(*v) < .01:
        return 0.0
    return math.degrees(math.atan2(u[0]*v[1]-u[1]*v[0], u[0]*v[0]+u[1]*v[1]))


def run() -> dict:
    tree, segments = read_lines()
    geod_m = sum(GEOD.line_length(*zip(*s["lonlat"])) for s in segments)
    utm_m = sum(s["line"].length for s in segments)
    gaps = [Point(a["xy"][-1]).distance(Point(b["xy"][0])) for a, b in zip(segments, segments[1:])]
    if any(g > 100 for g in gaps):
        raise ValueError("Discontinuidad KML mayor de 100 m; requiere revisión del orden")
    vertices, stations, posts, critical = [], [], [], []
    cumulative = 0.0
    for si, seg in enumerate(segments, 1):
        local = 0.0
        for vi, (lonlat, xy) in enumerate(zip(seg["lonlat"], seg["xy"]), 1):
            if vi > 1:
                local += Point(seg["xy"][vi-2]).distance(Point(xy))
            deflection = angle(*seg["xy"][vi-2:vi+1]) if 1 < vi < len(seg["xy"]) else 0.0
            vertices.append({"segmento": si, "vertice": vi, "estacion_m": round(cumulative+local, 3),
                             "longitud": lonlat[0], "latitud": lonlat[1], "este_m": round(xy[0], 3),
                             "norte_m": round(xy[1], 3), "deflexion_grados": round(deflection, 2),
                             "origen": "KML manual; geometría no validada en campo"})
        stations.append({"segmento": si, "nombre": seg["name"], "inicio_m": round(cumulative, 3),
                         "fin_m": round(cumulative+local, 3), "longitud_m": round(local, 3),
                         "vertices": len(seg["xy"]), "brecha_siguiente_m": round(gaps[si-1], 3) if si <= len(gaps) else ""})
        cumulative += local
    for i, gap in enumerate(gaps, 1):
        critical.append({"id": f"GAP-{i}", "tipo": "empalme KML no conectado", "segmento": i,
                         "estacion_m": stations[i-1]["fin_m"], "distancia_m": round(gap, 3),
                         "fuente": KML.name, "estado": "inspección requerida"})

    manual_lines = [s["line"] for s in segments]
    gis = json.loads((ROOT / "derived/route.json").read_text(encoding="utf-8"))
    gis_line = LineString(gis["route_utm_xy"])
    # Muestreo espacial: distancia de cada vértice manual a la polilínea GIS, sin alterar el KML.
    offsets = [gis_line.distance(Point(p["xy"][j])) for p in segments for j in range(len(p["xy"]))]
    structures = load_gis("gisem_mt_estructuras.geojson")
    seen_codes = set()
    for feat in structures:
        code = feat["properties"].get("CODESTRUCTURA")
        lon, lat = feat["geometry"]["coordinates"][:2]
        point = Point(TO_UTM.transform(lon, lat))
        nearest = min(enumerate(manual_lines, 1), key=lambda t: t[1].distance(point))
        distance = nearest[1].distance(point)
        if distance > 25 or code in seen_codes:
            continue
        seen_codes.add(code)
        si, line = nearest
        station = stations[si-1]["inicio_m"] + line.project(point)
        posts.append({"codigo_gisem": code, "segmento": si, "estacion_m": round(station, 3),
                      "latitud": lat, "longitud": lon, "este_m": round(point.x, 3),
                      "norte_m": round(point.y, 3), "utm": "EPSG:32719", "distancia_eje_m": round(distance, 3),
                      "tipo_estructura": "pendiente", "angulo_deflexion_grados": "",
                      "distancia_anterior_m": "", "distancia_siguiente_m": "",
                      "motivo": "estructura GIS existente cercana al corredor; verificar en campo",
                      "fuente": "GISEM capa estructuras; KML manual", "confianza": "baja",
                      "validacion": "pendiente", "observaciones_campo": "confirmar existencia, código y estado; no es poste nuevo aprobado"})
    posts.sort(key=lambda p: (p["estacion_m"], p["codigo_gisem"]))
    for i, p in enumerate(posts):
        p["id"] = f"PC-{i+1:03d}"
        if i:
            p["distancia_anterior_m"] = round(p["estacion_m"] - posts[i-1]["estacion_m"], 3)
        if i+1 < len(posts):
            p["distancia_siguiente_m"] = round(posts[i+1]["estacion_m"] - p["estacion_m"], 3)
    # Una deflexión en la polilínea manual es una zona de inspección, no un poste obligado.
    for v in vertices:
        if abs(v["deflexion_grados"]) >= 25:
            critical.append({"id": f"V-{v['segmento']}-{v['vertice']}", "tipo": "cambio de dirección KML",
                             "segmento": v["segmento"], "estacion_m": v["estacion_m"],
                             "distancia_m": "", "fuente": KML.name, "estado": "inspección requerida"})
    road_features = json.loads((ROOT / "sources/osm_roads.json").read_text(encoding="utf-8"))
    # OSM puede ser respuesta Overpass o FeatureCollection.
    if isinstance(road_features, dict) and road_features.get("type") == "FeatureCollection":
        roads = [shape(f["geometry"]) for f in road_features["features"] if f.get("geometry")]
    elif isinstance(road_features, dict) and "elements" in road_features:
        roads = [LineString([(p["lon"], p["lat"]) for p in e["geometry"]])
                 for e in road_features["elements"] if e.get("type") == "way" and len(e.get("geometry", [])) >= 2]
    else:
        roads = []
    road_intersections = 0
    for road in roads:
        if road.geom_type not in ("LineString", "MultiLineString"):
            continue
        from shapely.ops import transform
        road_utm = transform(TO_UTM.transform, road)
        for si, seg in enumerate(segments, 1):
            hit = seg["line"].intersection(road_utm)
            if hit.is_empty:
                continue
            points = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
            for pt in points:
                if pt.geom_type != "Point":
                    continue
                road_intersections += 1
                critical.append({"id": f"OSM-{road_intersections}", "tipo": "intersección geométrica vial OSM",
                                 "segmento": si, "estacion_m": round(stations[si-1]["inicio_m"]+seg["line"].project(pt), 3),
                                 "distancia_m": "", "fuente": "OpenStreetMap snapshot", "estado": "verificar tipo de cruce y despeje"})
    fields = ["id", "codigo_gisem", "segmento", "estacion_m", "latitud", "longitud", "este_m", "norte_m", "utm", "distancia_eje_m", "tipo_estructura", "angulo_deflexion_grados", "distancia_anterior_m", "distancia_siguiente_m", "motivo", "fuente", "confianza", "validacion", "observaciones_campo"]
    write_csv(ROOT/"datos/vertices_corredor_manual.csv", vertices, list(vertices[0]))
    write_csv(ROOT/"datos/estaciones_corredor.csv", stations, list(stations[0]))
    write_csv(ROOT/"datos/ubicaciones_postes_preliminares.csv", posts, fields)
    write_csv(ROOT/"datos/cruces_y_puntos_criticos.csv", critical, list(critical[0]))
    summary = {"fecha": str(date.today()), "kml_sha256": hashlib.sha256(KML.read_bytes()).hexdigest(),
               "segmentos": len(segments), "vertices": len(vertices), "longitud_geodesica_m": round(geod_m, 3),
               "longitud_utm_m": round(utm_m, 3), "brechas_m": [round(g, 3) for g in gaps],
               "longitud_gis_referencia_m": gis["route_length_m"], "diferencia_kml_gis_m": round(utm_m-gis["route_length_m"], 3),
               "desviacion_vertices_mediana_m": round(sorted(offsets)[len(offsets)//2], 3),
               "desviacion_vertices_max_m": round(max(offsets), 3), "candidatos_gis_cercanos": len(posts),
               "cruces_osm_geometricos": road_intersections,
               "distancia_conexion_inicio_m": round(Point(TO_UTM.transform(*CONNECTION)).distance(Point(segments[0]["xy"][0])), 3)}
    write_text(ROOT/"derived/auditoria_corredor_manual.json", json.dumps(summary, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
