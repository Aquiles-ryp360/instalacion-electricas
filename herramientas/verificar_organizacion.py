"""Comprueba navegación y rutas del repositorio sin regenerar diseños ni entregas."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]


def verificar() -> dict:
    errores = []
    catalogo = (ROOT / "proyectos/README.md").read_text(encoding="utf-8")
    proyectos = sorted(p for p in (ROOT / "proyectos").iterdir() if p.is_dir())
    ids = set()
    for proyecto in proyectos:
        ruta = proyecto / "proyecto.yaml"
        if not ruta.is_file():
            errores.append(f"Falta identificación: {ruta.relative_to(ROOT)}")
            continue
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
        identificador = datos.get("id") if isinstance(datos, dict) else None
        if identificador != proyecto.name or identificador in ids:
            errores.append(f"Identificador inválido o duplicado: {proyecto.name}")
        ids.add(identificador)
        if f"]({proyecto.name}/README.md)" not in catalogo:
            errores.append(f"Proyecto sin entrada en el catálogo: {proyecto.name}")

    navegacion = [ROOT / p for p in (
        "README.md", "proyectos/README.md", "docs/README.md",
        "docs/organizacion-repositorio.md", "docs/validacion-organizacion.md", "herramientas/README.md",
        "referencias/README.md", "recursos/README.md",
        "recursos/identidad/README.md", "recursos/ubicacion/limbani/README.md",
    )]
    propios = [ROOT / "proyectos" / p for p in (
        "aquiles-central-michell-banki", "aquiles-linea-primaria-inst-ii",
        "diego-unifamiliar",
    )]
    for proyecto in propios:
        navegacion.extend(p for p in (
            proyecto / "README.md", proyecto / "README-LINEA-PRIMARIA.md",
            proyecto / "expediente/README.md", proyecto / "archivo/README.md",
            proyecto / "archivo/r02/README.md", proyecto / "archivo/red-urbana/README.md",
        ) if p.is_file())
    enlaces = 0
    for documento in navegacion:
        if not documento.is_file():
            errores.append(f"Falta documento de navegación: {documento.relative_to(ROOT)}")
            continue
        texto = re.sub(r"```.*?```", "", documento.read_text(encoding="utf-8"), flags=re.S)
        for destino in re.findall(r"\]\(([^)]+)\)", texto):
            destino = destino.strip().strip("<>")
            url = urlsplit(destino)
            if url.scheme or url.netloc or not url.path:
                continue
            enlaces += 1
            ruta = (documento.parent / unquote(url.path)).resolve()
            if not ruta.is_relative_to(ROOT) or not ruta.exists():
                errores.append(f"Enlace roto: {documento.relative_to(ROOT)} -> {destino}")

    def exigir(base: Path, ruta: str) -> None:
        destino = (base / ruta).resolve()
        if not destino.is_relative_to(ROOT) or not destino.exists():
            errores.append(f"Ruta activa inexistente: {base.relative_to(ROOT)}/{ruta}")

    hidro, linea, diego = propios
    h = yaml.safe_load((hidro / "proyecto.yaml").read_text(encoding="utf-8"))
    for clave, ruta in h["entradas"].items():
        if clave.endswith("_json"):
            exigir(hidro, ruta)
    for ruta in h["entregables"]["para_revision"]:
        exigir(hidro, ruta)
    l = yaml.safe_load((linea / "proyecto.yaml").read_text(encoding="utf-8"))
    for clave in ("fuente_unica", "resultados", "documentos", "google_earth", "biblioteca_normativa", "antecedente_historico"):
        exigir(linea, l[clave])
    exigir(linea, l["paquete_revision"] if "paquete_revision" in l else l["entregables"])
    exigir(linea, l["cad_dxf_activo"] if "cad_dxf_activo" in l else l["cad_dwg_activo"])
    d = yaml.safe_load((diego / "proyecto.yaml").read_text(encoding="utf-8"))
    for ruta in [*d["entradas"].values(), *d["entregables"].values(), d["expediente_editable"]]:
        exigir(diego, ruta)

    programas = 0
    for proyecto in propios:
        for programa in (proyecto / "scripts").rglob("*.py"):
            try:
                ast.parse(programa.read_text(encoding="utf-8-sig"), filename=str(programa))
                programas += 1
            except (SyntaxError, UnicodeError) as exc:
                errores.append(f"Sintaxis: {programa.relative_to(ROOT)}: {exc}")
    resultado = dict(estado="ERROR" if errores else "OK", proyectos=len(proyectos),
                     documentos_navegacion=len(navegacion), enlaces_locales=enlaces,
                     programas_reubicados=programas, errores=errores)
    return resultado


if __name__ == "__main__":
    resultado = verificar()
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    raise SystemExit(bool(resultado["errores"]))
