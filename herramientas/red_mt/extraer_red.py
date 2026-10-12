"""Extraccion de topologia de red MT desde fuentes GIS o canonicas."""
import json
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd
import yaml

FORMATOS_GIS = {".gpkg", ".geojson", ".json", ".gml", ".shp", ".kml", ".kmz"}


def extraer_red_gpkg(ruta_archivo):
    """Lee un GeoPackage/GeoJSON/KML/Shapefile y devuelve la red canonica.

    Espera capas con atributos de nodo (id, tipo, cota) y tramo (desde, hasta,
    longitud). Si la capa unica contiene ambos, se infiere por tipo_geometria.
    Retorna dict: {nodos, tramos, cargas, crs, fuente, grafo}.
    """
    ruta = Path(ruta_archivo)
    if ruta.suffix.lower() not in FORMATOS_GIS:
        raise ValueError(f"Formato GIS no soportado: {ruta.suffix}")

    gdf = gpd.read_file(ruta)
    nodos, tramos, cargas = [], [], []
    columnas = {c.lower() for c in gdf.columns}

    if any(k in columnas for k in ("tipo", "tipo_nodo", "clase")):
        col_tipo = next(c for c in gdf.columns if c.lower() in ("tipo", "tipo_nodo", "clase"))
        for _, f in gdf.iterrows():
            nodo = {
                "id": str(f.get("id", f.get("codigo", ""))),
                "tipo": str(f[col_tipo]),
                "x": None,
                "y": None,
                "cota_msnm": float(f["cota_msnm"]) if "cota_msnm" in columnas else None,
            }
            if f.geometry is not None and f.geometry.has_z:
                nodo["x"], nodo["y"], _ = f.geometry.coords[0]
            elif f.geometry is not None:
                nodo["x"], nodo["y"] = f.geometry.coords[0]
            nodos.append(nodo)
    else:
        raise ValueError("La capa GIS no contiene atributo de tipo de nodo (tipo/tipo_nodo/clase)")

    if any(k in columnas for k in ("desde", "nodo_desde")):
        for _, f in gdf.iterrows():
            tramos.append({
                "id": str(f.get("id", f.get("codigo", ""))),
                "desde": str(f.get("desde", f.get("nodo_desde", ""))),
                "hasta": str(f.get("hasta", f.get("nodo_hasta", ""))),
                "longitud_m": float(f["longitud_m"]) if "longitud_m" in columnas else None,
            })

    if any(k in columnas for k in ("kw", "potencia_kw")):
        for _, f in gdf.iterrows():
            if f.get("tipo", "").lower() in ("carga", "abono", "abonado"):
                cargas.append({
                    "nodo": str(f.get("id", "")),
                    "kw": float(f["kw"]) if "kw" in columnas else float(f["potencia_kw"]),
                    "kva": float(f["kva"]) if "kva" in columnas else None,
                })

    grafo = nx.Graph()
    for n in nodos:
        grafo.add_node(n["id"], **n)
    for t in tramos:
        grafo.add_edge(t["desde"], t["hasta"], **t)

    return {"nodos": nodos, "tramos": tramos, "cargas": cargas,
            "crs": str(gdf.crs) if gdf.crs else None,
            "fuente": str(ruta), "grafo": grafo}


def extraer_red_canonical(ruta_matriz_yaml):
    """Construye la red canonica desde la matriz maestra del proyecto
    (estructuras_mt_canonicas con progresivas, cotas y vanos)."""
    ruta = Path(ruta_matriz_yaml)
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))

    estructuras = datos["estructuras_mt_canonicas"]
    nodos, tramos = [], []
    for i, e in enumerate(estructuras):
        nodos.append({
            "id": e["id"],
            "tipo": e.get("tipo", "alineamiento"),
            "x": None,
            "y": None,
            "cota_msnm": float(e["cota_terreno_msnm"]),
            "progresiva_m": float(e["progresiva_m"]),
            "poste": e.get("poste"),
            "armado": e.get("armado_dge"),
            "angulo_deg": float(e.get("angulo_deg", 0.0)),
            "coordenadas": {k: e[k] for k in ("este_m", "norte_m") if k in e},
        })
        if i > 0:
            tramos.append({
                "id": f"T-{estructuras[i-1]['id']}_{e['id']}",
                "desde": estructuras[i - 1]["id"],
                "hasta": e["id"],
                "longitud_m": float(e["vano_anterior_m"]),
            })

    cargas = []
    carga_total = datos.get("cargas_y_demanda_canonicas", {})
    sed = next((n for n in nodos if "SAB" in str(n.get("armado", ""))), None)
    if sed and "totales_sed" in carga_total:
        cargas.append({
            "nodo": sed["id"],
            "kw": float(carga_total["totales_sed"]["potencia_activa_total_kw"]),
            "kva": float(carga_total["totales_sed"]["potencia_aparente_total_kva"]),
        })

    grafo = nx.Graph()
    for n in nodos:
        grafo.add_node(n["id"], **n)
    for t in tramos:
        grafo.add_edge(t["desde"], t["hasta"], **t)

    return {"nodos": nodos, "tramos": tramos, "cargas": cargas,
            "crs": "EPSG:32719 (canonico UTM 19S WGS84)",
            "fuente": str(ruta), "grafo": grafo,
            "metadatos": {"tension_mt_kv": datos["proyecto"]["tension_nominal_mt_kv"]}}
