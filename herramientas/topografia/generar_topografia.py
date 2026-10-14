"""Genera topografía preliminar de gabinete a partir de un nombre de lugar."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import textwrap
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import contourpy
import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import requests
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT

REPO = Path(__file__).resolve().parents[2]
USER_AGENT = "instalacion-electricas-topografia/1.0 (https://github.com/gaelrenzo/instalacion-electricas)"
GEOCODER = "https://nominatim.openstreetmap.org/search"
DEM_BASE = "https://copernicus-dem-{resolution}m.s3.amazonaws.com"
NODATA = -9999.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slug(value: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", value.lower()).encode("ascii", "ignore").decode()
    name = re.sub(r"[^a-z0-9]+", "-", ascii_name)
    return name.strip("-")[:50] or "lugar"


def geocode(lugar: str) -> dict:
    response = requests.get(
        GEOCODER,
        params={"q": lugar, "format": "jsonv2", "limit": 3, "addressdetails": 1},
        headers={"User-Agent": USER_AGENT, "Accept-Language": "es"},
        timeout=30,
    )
    response.raise_for_status()
    candidates = response.json()
    if not candidates:
        raise ValueError(f"No se encontró el lugar: {lugar}")
    selected = candidates[0]
    return {
        "consulta": lugar,
        "seleccion": {
            "nombre": selected["display_name"],
            "lat": float(selected["lat"]),
            "lon": float(selected["lon"]),
            "osm_id": selected.get("osm_id"),
            "tipo": selected.get("type"),
        },
        "alternativas": [item["display_name"] for item in candidates[1:]],
        "proveedor": "OpenStreetMap Nominatim",
        "url": GEOCODER,
    }


def utm_crs(lat: float, lon: float) -> str:
    if not -80 <= lat <= 84:
        raise ValueError("El lugar está fuera de las zonas UTM admitidas")
    zone = min(60, max(1, math.floor((lon + 180) / 6) + 1))
    return f"EPSG:{32600 + zone if lat >= 0 else 32700 + zone}"


def tile_names(bounds: tuple[float, float, float, float], crs: str) -> list[str]:
    xmin, ymin, xmax, ymax = bounds
    to_geo = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    corners = [to_geo.transform(x, y) for x in (xmin, xmax) for y in (ymin, ymax)]
    west, east = min(p[0] for p in corners), max(p[0] for p in corners)
    south, north = min(p[1] for p in corners), max(p[1] for p in corners)
    names = []
    for latitude in range(math.floor(south), math.floor(north) + 1):
        for longitude in range(math.floor(west), math.floor(east) + 1):
            ns = f"N{latitude:02d}" if latitude >= 0 else f"S{abs(latitude):02d}"
            ew = f"E{longitude:03d}" if longitude >= 0 else f"W{abs(longitude):03d}"
            names.append(f"{ns}_00_{ew}_00")
    if len(names) > 9:
        raise ValueError("El área cruza demasiadas teselas; reduzca --radio-km")
    return names


def tile_url(name: str, resolution: int) -> str:
    arcsec = 10 if resolution == 30 else 30
    stem = f"Copernicus_DSM_COG_{arcsec}_{name}_DEM"
    return f"{DEM_BASE.format(resolution=resolution)}/{stem}/{stem}.tif"


def read_dem(lat: float, lon: float, radius_km: float) -> tuple[np.ndarray, dict, list[dict]]:
    if not 0.25 <= radius_km <= 5:
        raise ValueError("--radio-km debe estar entre 0.25 y 5")
    crs = utm_crs(lat, lon)
    east, north = Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform(lon, lat)
    radius = radius_km * 1000
    values, meta, sources = read_dem_bounds(
        (east - radius, north - radius, east + radius, north + radius), crs
    )
    meta["centro_utm_m"] = [east, north]
    return values, meta, sources


def read_dem_bounds(bounds: tuple[float, float, float, float], crs: str
                    ) -> tuple[np.ndarray, dict, list[dict]]:
    """Recorta DEM para un corredor UTM; la fuente sigue siendo un DSM preliminar."""
    xmin, ymin, xmax, ymax = bounds
    if xmin >= xmax or ymin >= ymax or max(xmax - xmin, ymax - ymin) > 30000:
        raise ValueError("El área DEM debe ser válida y tener hasta 30 km por lado")
    width = math.ceil((xmax - xmin) / 30)
    height = math.ceil((ymax - ymin) / 30)
    transform = from_origin(xmin, ymax, 30, 30)
    bounds = (transform.c, transform.f - height * 30,
              transform.c + width * 30, transform.f)
    result = np.full((height, width), NODATA, dtype="float32")
    sources = []
    for name in tile_names(bounds, crs):
        for resolution in (30, 90):
            url = tile_url(name, resolution)
            try:
                with rasterio.open(url) as src:
                    with WarpedVRT(
                        src, crs=crs, transform=transform, width=width, height=height,
                        resampling=Resampling.bilinear, nodata=NODATA,
                    ) as vrt:
                        values = vrt.read(1, masked=True)
                        valid = ~np.ma.getmaskarray(values) & np.isfinite(values.data)
                        fill = valid & (result == NODATA)
                        result[fill] = values.data[fill]
                if valid.any():
                    try:
                        head = requests.head(url, timeout=20)
                        head.raise_for_status()
                        etag = head.headers.get("ETag")
                        last_modified = head.headers.get("Last-Modified")
                    except requests.RequestException:
                        etag = last_modified = None
                    sources.append({
                        "url": url, "resolucion_nominal_m": resolution, "tesela": name,
                        "etag": etag, "ultima_modificacion": last_modified,
                    })
                    break
            except rasterio.errors.RasterioIOError:
                continue
    if np.all(result == NODATA):
        raise RuntimeError("No se obtuvo elevación; revise lugar o conexión de red")
    if np.any(result == NODATA):
        raise RuntimeError("El DEM no cubre toda el área; reduzca el radio o revise las teselas")
    meta = {"crs": crs, "transform": transform, "bounds": bounds,
            "resolucion_salida_m": 30}
    return result, meta, sources


def write_products(output: Path, values: np.ndarray, meta: dict, interval: float,
                   location: dict, sources: list[dict]) -> dict:
    if not 1 <= interval <= 100:
        raise ValueError("--equidistancia-m debe estar entre 1 y 100")
    if output.exists():
        raise FileExistsError(f"La carpeta ya existe: {output}")
    transform = meta["transform"]
    crs = meta["crs"]
    height, width = values.shape
    vmin, vmax = float(values.min()), float(values.max())
    levels = np.arange(math.ceil(vmin / interval) * interval, vmax, interval)
    if len(levels) > 150:
        raise ValueError("Demasiadas curvas: aumente --equidistancia-m")
    output.mkdir(parents=True)
    tif = output / "modelo_elevacion_preliminar.tif"
    with rasterio.open(
        tif, "w", driver="GTiff", height=height, width=width, count=1,
        dtype="float32", crs=crs, transform=transform, nodata=NODATA,
        compress="deflate",
    ) as dst:
        dst.write(values, 1)
    xs = transform.c + (np.arange(width) + 0.5) * transform.a
    ys = transform.f + (np.arange(height) + 0.5) * transform.e
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    doc.layers.new("CURVAS_DEM_PRELIMINAR", dxfattribs={"color": 8})
    doc.layers.new("CENTRO_LUGAR", dxfattribs={"color": 1})
    model = doc.modelspace()
    generator = contourpy.contour_generator(x=xs, y=ys, z=values)
    contour_count = 0
    for level in levels:
        for line in generator.lines(float(level)):
            if len(line) >= 2:
                model.add_lwpolyline(line, dxfattribs={
                    "layer": "CURVAS_DEM_PRELIMINAR", "elevation": float(level),
                })
                contour_count += 1
    center = meta["centro_utm_m"]
    model.add_circle(center, radius=20, dxfattribs={"layer": "CENTRO_LUGAR"})
    dxf = output / "curvas_nivel_preliminares.dxf"
    doc.saveas(dxf)
    if ezdxf.readfile(dxf).audit().has_errors:
        raise RuntimeError("El DXF generado no pasó la auditoría")
    xmin, ymin, xmax, ymax = meta["bounds"]
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    fig.subplots_adjust(left=0.10, right=0.88, bottom=0.13, top=0.90)
    image = ax.imshow(values, extent=(xmin, xmax, ymin, ymax), origin="upper", cmap="terrain")
    if len(levels):
        ax.contour(xs, ys, values, levels=levels, colors="#252525", linewidths=0.45)
    ax.plot(center[0], center[1], "ro", markersize=5)
    ax.set_title("TOPOGRAFÍA PRELIMINAR DE GABINETE — NO ES LEVANTAMIENTO DE CAMPO")
    ax.set_xlabel(f"Este (m) · {crs}")
    ax.set_ylabel(f"Norte (m) · {crs}")
    ax.set_aspect("equal")
    ax.ticklabel_format(style="plain", useOffset=False, axis="both")
    fig.colorbar(image, ax=ax, label="Elevación del modelo digital (m)")
    caption = (f"Lugar: {location['seleccion']['nombre']} | Relieve: Copernicus DEM "
               f"| Ubicación: © OpenStreetMap | Equidistancia: {interval:g} m")
    fig.text(0.10, 0.035, textwrap.fill(caption, width=105), fontsize=9)
    fig.savefig(output / "mapa_topografico_preliminar.pdf", dpi=160)
    fig.savefig(output / "mapa_topografico_preliminar.png", dpi=160)
    plt.close(fig)
    report = {
        "estado": "topografia_preliminar_dem_no_apta_para_diseno_de_obra",
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "lugar": location,
        "dem": {
            "producto": "Copernicus DEM DSM GLO-30 Public; GLO-90 si falta tesela",
            "fuentes": sources, "crs_horizontal": crs, "datum_vertical": "EGM2008",
            "resolucion_salida_m": meta["resolucion_salida_m"],
            "resolucion_fuente_m": sorted({item["resolucion_nominal_m"] for item in sources}),
            "bbox_utm_m": list(meta["bounds"]), "elevacion_min_m": vmin,
            "elevacion_max_m": vmax, "equidistancia_curvas_m": interval,
            "curvas_dxf": contour_count,
        },
        "limitaciones": [
            "DSM incluye vegetacion y construcciones; no equivale a cotas de terreno levantadas en campo.",
            "El nombre del lugar no define eje de linea, apoyos, cruces ni punto de conexion.",
            "No utilizar para aprobar postes, flechas, galibos, cimentaciones o servidumbres.",
        ],
        "archivos_sha256": {p.name: sha256(p) for p in output.iterdir() if p.is_file()},
    }
    (output / "manifiesto.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lugar", help="Nombre del lugar, por ejemplo: Capachica, Puno, Perú")
    parser.add_argument("--radio-km", type=float, default=2.0, help="Radio del área (0.25–5 km)")
    parser.add_argument("--equidistancia-m", type=float, default=10.0, help="Curvas cada N metros")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva de salida")
    args = parser.parse_args()
    location = geocode(args.lugar)
    point = location["seleccion"]
    values, meta, sources = read_dem(point["lat"], point["lon"], args.radio_km)
    output = args.salida or REPO / "build" / "topografia" / (
        slug(args.lugar) + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    report = write_products(output, values, meta, args.equidistancia_m, location, sources)
    print(json.dumps({"salida": str(output), "estado": report["estado"],
                      "lugar": point["nombre"], "curvas": report["dem"]["curvas_dxf"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
