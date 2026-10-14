"""Plantilla y validación de levantamientos lineales para QGIS/QField."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely.geometry import LineString


ROUTE_COLUMNS = {
    "id_proyecto": "str", "id_eje": "str", "estado": "str",
    "fuente": "str", "metodo": "str", "fecha_registro": "str",
    "responsable": "str", "precision_h_m": "float64",
    "precision_v_m": "float64", "datum_vertical": "str",
    "documento_ref": "str", "observacion": "str",
}
OBS_COLUMNS = {
    "id_proyecto": "str", "id_observacion": "str", "categoria": "str",
    "fuente": "str", "fecha_registro": "str", "responsable": "str",
    "precision_h_m": "float64", "precision_v_m": "float64",
    "cota_m": "float64", "datum_vertical": "str",
    "foto_ref": "str", "observacion": "str",
}
LAYERS = {"eje": (ROUTE_COLUMNS, "LineString"),
          "observaciones": (OBS_COLUMNS, "Point")}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_template(path: Path) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for layer, (columns, geometry_type) in LAYERS.items():
        frame = gpd.GeoDataFrame(
            {name: pd.Series(dtype=dtype) for name, dtype in columns.items()},
            geometry=gpd.GeoSeries([], dtype="geometry", crs="EPSG:4326"),
        )
        pyogrio.write_dataframe(frame, path, layer=layer, driver="GPKG",
                                geometry_type=geometry_type)


def _filled(value) -> bool:
    return value is not None and not pd.isna(value) and bool(str(value).strip())


def _positive(value) -> bool:
    try:
        return math.isfinite(float(value)) and float(value) > 0
    except (TypeError, ValueError):
        return False


def _date(value) -> bool:
    if not _filled(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.tzinfo is not None
    except ValueError:
        return False


def validate(path: Path, project_id: str) -> tuple[dict, list[tuple[float, float]] | None]:
    """Comprueba evidencia declarada; no certifica la exactitud del levantamiento."""
    if not path.is_file():
        raise FileNotFoundError(path)
    layers = {name for name, _ in pyogrio.list_layers(path)}
    errors, warnings = [], []
    for layer in LAYERS:
        if layer not in layers:
            errors.append(f"Falta capa '{layer}'")
    report = {"id_proyecto": project_id, "archivo": str(path.resolve()),
              "sha256": sha256(path), "estado": "invalido",
              "errores": errors, "advertencias": warnings,
              "eje": None, "observaciones": 0,
              "apto_para_diseno": False}
    if errors:
        return report, None

    frames = {}
    for layer, (columns, geometry_type) in LAYERS.items():
        frame = pyogrio.read_dataframe(path, layer=layer)
        missing = set(columns) - set(frame.columns)
        if missing:
            errors.append(f"Capa '{layer}': faltan campos {', '.join(sorted(missing))}")
            continue
        if frame.crs is None:
            errors.append(f"Capa '{layer}': CRS ausente")
            continue
        frames[layer] = frame[frame["id_proyecto"] == project_id].to_crs("EPSG:4326")
    if errors:
        return report, None

    routes = frames["eje"]
    observations = frames["observaciones"]
    report["observaciones"] = len(observations)
    if observations.empty:
        warnings.append("Sin observaciones de campo; revisar cruces, obstáculos y accesos")
    if len(routes) != 1:
        errors.append(f"Se requiere exactamente un eje para '{project_id}'; encontrados {len(routes)}")
        return report, None
    row = routes.iloc[0]
    geometry = row.geometry
    if not isinstance(geometry, LineString) or geometry.is_empty or len(geometry.coords) < 2:
        errors.append("El eje debe ser una LineString no vacía con al menos dos vértices")
        return report, None
    points = [(float(coord[0]), float(coord[1])) for coord in geometry.coords]
    if geometry.has_z:
        warnings.append("Eje 3D: Z no usada como cota; revisar datum y precisión vertical")
    if any(not (math.isfinite(x) and math.isfinite(y) and -180 <= x <= 180 and -90 <= y <= 90)
           for x, y in points):
        errors.append("Coordenadas del eje fuera de rango EPSG:4326")
    if any(a == b for a, b in zip(points, points[1:])) or geometry.length == 0:
        errors.append("El eje contiene vértices consecutivos iguales o longitud nula")
    if not geometry.is_simple:
        warnings.append("El eje se cruza a sí mismo; revisar trazado")
    for key in ("id_eje", "estado", "fuente", "metodo", "responsable"):
        if not _filled(row[key]):
            errors.append(f"Eje: falta {key}")
    if _filled(row["estado"]) and row["estado"] not in ("propuesto", "levantado"):
        errors.append("Eje: estado debe ser 'propuesto' o 'levantado'")
    if not _date(row["fecha_registro"]):
        errors.append("Eje: fecha_registro debe incluir fecha, hora y zona horaria ISO 8601")
    if not _positive(row["precision_h_m"]):
        errors.append("Eje: precision_h_m debe ser positiva y finita")
    if not _filled(row["documento_ref"]):
        if _filled(row["estado"]) and row["estado"] == "levantado":
            errors.append("Eje levantado: falta referencia a libreta, acta o archivo de campo")
        else:
            warnings.append("Eje: falta referencia a libreta, acta o archivo de levantamiento")
    if not _positive(row["precision_v_m"]) or not _filled(row["datum_vertical"]):
        warnings.append("Eje: precisión vertical o datum ausente; no usar cotas para gálibos")

    identifiers = set()
    for index, obs in observations.iterrows():
        prefix = f"Observación {index}"
        for key in ("id_observacion", "categoria", "fuente", "responsable"):
            if not _filled(obs[key]):
                errors.append(f"{prefix}: falta {key}")
        if _filled(obs["id_observacion"]):
            if obs["id_observacion"] in identifiers:
                errors.append(f"{prefix}: id_observacion duplicado")
            identifiers.add(obs["id_observacion"])
        if obs.geometry is None or obs.geometry.is_empty or obs.geometry.geom_type != "Point":
            errors.append(f"{prefix}: geometría de punto inválida")
        elif not (-180 <= obs.geometry.x <= 180 and -90 <= obs.geometry.y <= 90):
            errors.append(f"{prefix}: coordenadas fuera de rango EPSG:4326")
        if not _date(obs["fecha_registro"]):
            errors.append(f"{prefix}: fecha_registro inválida")
        if not _positive(obs["precision_h_m"]):
            errors.append(f"{prefix}: precision_h_m inválida")
        if pd.notna(obs["cota_m"]) and (not _positive(obs["precision_v_m"])
                                       or not _filled(obs["datum_vertical"])):
            errors.append(f"{prefix}: cota sin precisión vertical o datum")

    report["eje"] = {"id_eje": str(row["id_eje"]) if _filled(row["id_eje"]) else None,
                     "estado_declarado": str(row["estado"]) if _filled(row["estado"]) else None,
                     "fuente": str(row["fuente"]) if _filled(row["fuente"]) else None,
                     "metodo": str(row["metodo"]) if _filled(row["metodo"]) else None,
                     "fecha_registro": str(row["fecha_registro"])
                     if _filled(row["fecha_registro"]) else None,
                     "responsable": str(row["responsable"]) if _filled(row["responsable"]) else None,
                     "precision_h_m": float(row["precision_h_m"])
                     if _positive(row["precision_h_m"]) else None,
                     "vertices": len(points),
                     "documento_ref": str(row["documento_ref"])
                     if _filled(row["documento_ref"]) else None}
    report["estado"] = "invalido" if errors else "datos_de_campo_validos_formalmente"
    if not errors:
        warnings.append("Validación formal: pendiente comprobar precisión, terreno y aprobación humana")
    return report, None if errors else points


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="comando", required=True)
    create = commands.add_parser("crear-plantilla")
    create.add_argument("archivo", type=Path)
    check = commands.add_parser("validar")
    check.add_argument("archivo", type=Path)
    check.add_argument("--id-proyecto", required=True)
    check.add_argument("--informe", type=Path)
    args = parser.parse_args()
    if args.comando == "crear-plantilla":
        create_template(args.archivo)
        print(args.archivo.resolve())
        return
    report, _ = validate(args.archivo, args.id_proyecto)
    if args.informe:
        if args.informe.resolve() == args.archivo.resolve():
            raise ValueError("El informe no puede sobrescribir el levantamiento original")
        if args.informe.exists():
            raise FileExistsError(args.informe)
        args.informe.parent.mkdir(parents=True, exist_ok=True)
        args.informe.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["errores"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
