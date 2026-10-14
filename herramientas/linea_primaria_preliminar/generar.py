"""Genera un anteproyecto cartográfico reutilizable de línea primaria."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer

from herramientas.topografia.generar_topografia import (
    geocode, read_dem, read_dem_bounds, sha256, slug, utm_crs, write_products,
)
from herramientas.linea_primaria_preliminar.dxf_laminas import add_plant_sheet, make_profile_dxf

REPO = Path(__file__).resolve().parents[2]
PENDIENTES = [
    "punto de conexión y condiciones de la concesionaria",
    "eje, cruces, servidumbres y accesos verificados",
    "topografía y estructuras existentes levantadas en campo",
    "demanda, tensión, conductor y cálculos eléctricos",
    "clima, flechas, esfuerzos, despejes, suelo, cimentaciones y PAT",
]


def read_project(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    for key in ("id", "lugar"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"Falta {key} en el proyecto")
    if "ruta" in data and ("origen" in data or "destino" in data):
        raise ValueError("Use una ruta o dos extremos, no ambos")
    if ("origen" in data) != ("destino" in data):
        raise ValueError("Se requieren origen y destino juntos")
    if any(k in data for k in ("ruta", "origen")):
        spacing = data.get("separacion_exploratoria_m")
        if not isinstance(spacing, (int, float)) or not math.isfinite(spacing) or not 20 <= spacing <= 500:
            raise ValueError("separacion_exploratoria_m debe ser 20 a 500 m")
    return data


def route_from_file(path: Path) -> list[tuple[float, float]]:
    if path.suffix.lower() in (".json", ".geojson"):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if data["type"] == "FeatureCollection":
            features = [feature["geometry"] for feature in data["features"]]
            if len(features) != 1:
                raise ValueError("Se requiere una sola línea continua en GeoJSON")
            geometry = features[0]
        elif data["type"] == "Feature":
            geometry = data["geometry"]
        else:
            geometry = data
        if geometry["type"] != "LineString":
            raise ValueError("La ruta debe ser un LineString EPSG:4326")
        coords = geometry["coordinates"]
    elif path.suffix.lower() == ".kml":
        root = ET.parse(path).getroot()
        nodes = root.findall(".//{http://www.opengis.net/kml/2.2}LineString/"
                             "{http://www.opengis.net/kml/2.2}coordinates")
        if len(nodes) != 1:
            raise ValueError("Se requiere una sola línea continua en KML")
        coords = [[float(v) for v in item.split(",")[:2]] for item in nodes[0].text.split()]
    else:
        raise ValueError("La ruta debe ser GeoJSON o KML")
    if len(coords) < 2:
        raise ValueError("La ruta debe tener al menos dos puntos")
    points = [(float(p[0]), float(p[1])) for p in coords]
    if any(not (math.isfinite(x) and math.isfinite(y) and -180 <= x <= 180 and -90 <= y <= 90)
           for x, y in points):
        raise ValueError("Coordenadas de ruta fuera de rango lon/lat")
    return points


def endpoint(value: dict) -> tuple[float, float, dict]:
    if "lugar" in value:
        result = geocode(value["lugar"])
        point = result["seleccion"]
        return point["lon"], point["lat"], result
    if "lon" not in value or "lat" not in value:
        raise ValueError("Cada extremo requiere lugar o coordenadas lon/lat")
    lon, lat = float(value["lon"]), float(value["lat"])
    if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
        raise ValueError("Coordenadas de extremo fuera de rango")
    return lon, lat, {"coordenadas_informadas": [lon, lat]}


def route_for_project(data: dict, base: Path) -> tuple[list[tuple[float, float]] | None, dict]:
    if "ruta" in data:
        path = (base / data["ruta"]).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return route_from_file(path), {"modo": "ruta_informada", "archivo": str(path),
                                       "sha256": sha256(path)}
    if "origen" in data:
        a_lon, a_lat, a_source = endpoint(data["origen"])
        if "lugar" in data["origen"]:
            time.sleep(1.1)  # Nominatim público: máximo una consulta por segundo.
        b_lon, b_lat, b_source = endpoint(data["destino"])
        return [(a_lon, a_lat), (b_lon, b_lat)], {
            "modo": "recta_exploratoria_entre_extremos",
            "origen": a_source, "destino": b_source,
            "advertencia": "La recta no considera cruces, predios, obstáculos ni factibilidad.",
        }
    return None, {"modo": "sin_eje", "dato_requerido": "ruta o extremos"}


def stations(points: list[tuple[float, float]], step: float) -> tuple[list[tuple[float, float, float]], float]:
    distances = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(distances)
    if total <= 0 or any(distance == 0 for distance in distances):
        raise ValueError("El eje contiene un tramo nulo")
    count = max(1, math.ceil(total / step))
    cumulative = np.r_[0, np.cumsum(distances)]
    result = []
    for station in np.linspace(0, total, count + 1):
        index = min(len(distances) - 1, int(np.searchsorted(cumulative, station, side="right") - 1))
        fraction = min(1, (station - cumulative[index]) / distances[index])
        a, b = points[index], points[index + 1]
        result.append((float(station), a[0] + fraction * (b[0] - a[0]),
                       a[1] + fraction * (b[1] - a[1])))
    return result, total


def elevation(values: np.ndarray, transform, east: float, north: float) -> float:
    col, row = (~transform) @ (east, north)
    if not (0 <= row < values.shape[0] and 0 <= col < values.shape[1]):
        raise ValueError("Punto fuera del DEM recortado")
    row = min(max(row - 0.5, 0), values.shape[0] - 1)
    col = min(max(col - 0.5, 0), values.shape[1] - 1)
    r0, c0 = int(row), int(col)
    r1, c1 = min(r0 + 1, values.shape[0] - 1), min(c0 + 1, values.shape[1] - 1)
    dr, dc = row - r0, col - c0
    return float((1 - dr) * ((1 - dc) * values[r0, c0] + dc * values[r0, c1]) +
                 dr * ((1 - dc) * values[r1, c0] + dc * values[r1, c1]))


def table(path: Path, headings: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headings)
        writer.writeheader()
        writer.writerows(rows)


def draw_plans(output: Path, points: list[tuple[float, float]], posts: list[dict],
               profile: list[dict], values: np.ndarray, meta: dict, title: str) -> None:
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    for name, color in (("EJE_CANDIDATO", 5), ("SITIOS_CANDIDATOS", 1), ("TEXTOS", 7)):
        doc.layers.new(name, dxfattribs={"color": color})
    model = doc.modelspace()
    model.add_lwpolyline(points, dxfattribs={"layer": "EJE_CANDIDATO"})
    for post in posts:
        xy = (post["este_m"], post["norte_m"])
        model.add_circle(xy, 5, dxfattribs={"layer": "SITIOS_CANDIDATOS"})
        model.add_text(post["id"], dxfattribs={"layer": "TEXTOS", "height": 3}
                       ).set_placement((xy[0] + 7, xy[1] + 7))
    add_plant_sheet(doc, points, posts, title, meta["crs"])
    dxf = output / "planta_sitios_candidatos.dxf"
    doc.saveas(dxf)
    if ezdxf.readfile(dxf).audit().has_errors:
        raise RuntimeError("Auditoría DXF fallida")
    make_profile_dxf(output / "perfil_dem_preliminar.dxf", profile, posts,
                     title, meta["crs"])
    xmin, ymin, xmax, ymax = meta["bounds"]
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    fig.subplots_adjust(left=.10, right=.87, bottom=.14, top=.88)
    image = ax.imshow(values, extent=(xmin, xmax, ymin, ymax), origin="upper", cmap="terrain")
    ax.plot([p[0] for p in points], [p[1] for p in points], color="navy", lw=2)
    ax.scatter([p["este_m"] for p in posts], [p["norte_m"] for p in posts],
               color="red", s=14, zorder=3)
    ax.set_title(f"{title} | PLANTA PRELIMINAR")
    ax.set_xlabel(f"Este (m) · {meta['crs']}")
    ax.set_ylabel(f"Norte (m) · {meta['crs']}")
    ax.ticklabel_format(style="plain", useOffset=False, axis="both")
    ax.set_aspect("equal")
    fig.colorbar(image, ax=ax, label="Cota DSM (m, EGM2008)")
    fig.text(.10, .05, "SITIOS GEOMÉTRICOS CANDIDATOS · NO APTOS PARA CONSTRUCCIÓN "
                      "| Copernicus DEM / OpenStreetMap", fontsize=9)
    fig.savefig(output / "planta_preliminar.pdf")
    fig.savefig(output / "planta_preliminar.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    fig.subplots_adjust(left=.09, right=.95, bottom=.15, top=.88)
    ax.plot([p["progresiva_m"] for p in profile], [p["cota_dem_m"] for p in profile],
            color="saddlebrown", label="Superficie DEM")
    ax.scatter([p["progresiva_m"] for p in posts], [p["cota_dem_m"] for p in posts],
               color="red", s=18, label="Sitio candidato")
    ax.set_title(f"{title} | PERFIL REFERENCIAL")
    ax.set_xlabel("Progresiva del eje candidato (m)")
    ax.set_ylabel("Cota DSM EGM2008 (m)")
    ax.grid(alpha=.3)
    ax.legend()
    fig.text(.09, .05, "El perfil DEM no sirve para verificar flechas, gálibos ni alturas de postes.",
             fontsize=9)
    fig.savefig(output / "perfil_preliminar.pdf")
    fig.savefig(output / "perfil_preliminar.png", dpi=150)
    plt.close(fig)


def generate(project_path: Path, output: Path) -> dict:
    data = read_project(project_path)
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    geocoded = geocode(data["lugar"])
    point = geocoded["seleccion"]
    if "origen" in data and any("lugar" in data[key] for key in ("origen", "destino")):
        time.sleep(1.1)  # Entre consultas al servicio público de Nominatim.
    route_geo, route_source = route_for_project(data, project_path.parent)
    if route_geo:
        route_lon = sum(lon for lon, _ in route_geo) / len(route_geo)
        route_lat = sum(lat for _, lat in route_geo) / len(route_geo)
        crs = utm_crs(route_lat, route_lon)
        to_utm = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        points = [to_utm.transform(lon, lat) for lon, lat in route_geo]
        margin = 300
        bounds = (min(p[0] for p in points) - margin, min(p[1] for p in points) - margin,
                  max(p[0] for p in points) + margin, max(p[1] for p in points) + margin)
        values, meta, sources = read_dem_bounds(bounds, crs)
        meta["centro_utm_m"] = to_utm.transform(route_lon, route_lat)
    else:
        values, meta, sources = read_dem(point["lat"], point["lon"], data.get("radio_km", 2))
    write_products(output / "topografia", values, meta, 10, geocoded, sources)
    report = {
        "id": data["id"], "estado": "anteproyecto_cartografico",
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": sha256(project_path), "lugar": geocoded,
        "eje": route_source, "pendientes": list(PENDIENTES),
    }
    if route_geo:
        support_step = float(data["separacion_exploratoria_m"])
        supports, length = stations(points, support_step)
        profile_points, _ = stations(points, 30)
        profile_points = sorted({station: (station, east, north)
                                 for station, east, north in profile_points + supports}.values())
        post_rows = []
        for i, (chainage, east, north) in enumerate(supports, 1):
            post_rows.append({
                "id": f"SC-{i:03d}", "progresiva_m": round(chainage, 2),
                "este_m": round(east, 3), "norte_m": round(north, 3),
                "cota_dem_m": round(elevation(values, meta["transform"], east, north), 2),
                "funcion": "extremo" if i in (1, len(supports)) else "intermedio",
                "estado": "candidato_geometrico", "tipo_poste": "dato requerido",
                "armado": "dato requerido",
            })
        profile_rows = [{
            "progresiva_m": round(chainage, 2), "este_m": round(east, 3),
            "norte_m": round(north, 3),
            "cota_dem_m": round(elevation(values, meta["transform"], east, north), 2),
        } for chainage, east, north in profile_points]
        table(output / "sitios_candidatos.csv", list(post_rows[0]), post_rows)
        table(output / "perfil_dem.csv", list(profile_rows[0]), profile_rows)
        draw_plans(output, points, post_rows, profile_rows, values, meta, data["id"])
        report["eje"].update({
            "longitud_utm_m": round(length, 2), "crs": meta["crs"],
            "separacion_exploratoria_solicitada_m": support_step,
            "sitios_candidatos": len(post_rows),
            "separacion_resultante_m": round(length / (len(post_rows) - 1), 2),
        })
    else:
        report["pendientes"].insert(0, "dato requerido: eje o extremos para proponer sitios")
    report["archivos_sha256"] = {
        p.relative_to(output).as_posix(): sha256(p)
        for p in output.rglob("*") if p.is_file()
    }
    (output / "manifiesto.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proyecto", type=Path, help="JSON de un anteproyecto o carpeta con archivos JSON")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva para un proyecto, o carpeta base para varios")
    args = parser.parse_args()
    source = args.proyecto.resolve()
    projects = sorted(source.glob("*.json")) if source.is_dir() else [source]
    if not projects:
        parser.error("La carpeta no contiene proyectos JSON")
    failed = []
    for project in projects:
        try:
            data = read_project(project)
            name = slug(data["id"]) + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            output = (args.salida or REPO / "build" / "linea_primaria_preliminar") / name \
                if source.is_dir() else (args.salida or REPO / "build" / "linea_primaria_preliminar" / name)
            report = generate(project, output)
            print(json.dumps({"proyecto": str(project), "salida": str(output),
                              "estado": report["estado"], "eje": report["eje"]}, ensure_ascii=False))
        except Exception as exc:
            if not source.is_dir():
                raise
            failed.append(str(project))
            print(json.dumps({"proyecto": str(project), "error": str(exc)}, ensure_ascii=False))
    if failed:
        raise SystemExit(f"Fallaron {len(failed)} de {len(projects)} proyectos")


if __name__ == "__main__":
    main()
