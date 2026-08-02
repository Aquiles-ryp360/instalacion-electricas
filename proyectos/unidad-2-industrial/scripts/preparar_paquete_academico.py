#!/usr/bin/env python3
"""Reune en build el paquete academico de revision sin publicar entregables."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    root = repository_root()
    project = root / "proyectos/unidad-2-industrial"
    build = root / "build/unidad-2-industrial"
    package = build / "paquete-academico-revision"
    plans_out = package / "planos-editables-y-pdf"
    if package.exists():
        shutil.rmtree(package)
    package.mkdir(parents=True, exist_ok=True)
    plans_out.mkdir(parents=True, exist_ok=True)

    files = [
        (build / "expediente/main.pdf", package / "01-expediente-grifo-aquiles.pdf"),
        (build / "expediente/guia-sustentacion.pdf", package / "02-guia-sustentacion-aquiles.pdf"),
        (build / "cad/planos/planos-electricos-grifo-unap-aquiles.pdf", package / "03-planos-electricos-A1-vectoriales.pdf"),
        (build / "presupuesto/metrados-presupuesto.csv", package / "04-metrados-presupuesto.csv"),
        (build / "cotizaciones/cotizacion-automatica-resumen.md", package / "04a-cotizacion-automatica-resumen.md"),
        (build / "cotizaciones/cotizacion-automatica-resumen.csv", package / "04b-cotizacion-automatica-resumen.csv"),
        (build / "cotizaciones/promelsa.json", package / "04c-evidencia-cotizacion-promelsa.json"),
        (build / "cotizaciones/bom-cotizable.json", package / "04d-bom-cotizable.json"),
        (build / "calculos/cuadro-cargas.csv", package / "05-cuadro-cargas.csv"),
        (project / "documentacion/dudas-pendientes.md", package / "06-dudas-pendientes.md"),
        (project / "documentacion/guia-sustentacion.md", package / "07-guia-sustentacion-editable.md"),
        (project / "datos/ubicacion.yaml", package / "08-ubicacion-y-trazabilidad.yaml"),
        (project / "fuentes/inventario-ubicacion.md", package / "09-inventario-ubicacion.md"),
        (project / "documentacion/prompt-codex-windows-mejora-cad.md", package / "10-prompt-codex-windows-mejora-cad.md"),
    ]
    plan_dir = build / "cad/planos"
    for code in ("IE-01", "IE-02", "IE-03", "IE-04", "IE-05", "IE-06"):
        for suffix in (".pdf", ".dxf"):
            matches = sorted(plan_dir.glob(f"{code.lower()}*{suffix}"))
            if len(matches) != 1:
                raise SystemExit(f"Se esperaba un archivo {code}*{suffix}; encontrados: {len(matches)}")
            files.append((matches[0], plans_out / matches[0].name))

    copied: list[dict[str, object]] = []
    for source, destination in files:
        if not source.exists() or source.stat().st_size == 0:
            raise SystemExit(f"Falta resultado requerido: {source}")
        shutil.copy2(source, destination)
        copied.append({
            "archivo": str(destination.relative_to(package)),
            "bytes": destination.stat().st_size,
            "sha256": sha256(destination),
        })

    readme = package / "LEEME-ANTES-DE-IMPRIMIR.txt"
    readme.write_text(
        "PAQUETE ACADEMICO DE REVISION - GRIFO DE COMBUSTIBLES LIQUIDOS\n\n"
        "Autor: Aquiles Taylor Ramos Yapo\n"
        "Docente: Mg. Gregorio Meza Marocho\n\n"
        "Imprimir el expediente en tamaño carta y las seis laminas IE-01 a IE-06 en A1. "
        "Los PDF de planos son vectoriales; los PNG del build son solo vistas previas.\n\n"
        "La cotizacion automatica adjunta conserva candidatos, precios visibles, URL, fecha y estados. "
        "No reemplaza el presupuesto instalado ni autoriza una compra.\n\n"
        "Este paquete esta completo para revision y sustentacion academica, pero NO AUTORIZA CONSTRUCCION. "
        "Antes de obra se requieren factibilidad e Icc de Electro Puno, placas definitivas, verificacion de campo, "
        "fotometria, medicion de PAT, coordinacion de protecciones y revision/firma profesional de areas clasificadas.\n",
        encoding="utf-8",
    )
    copied.append({"archivo": readme.name, "bytes": readme.stat().st_size, "sha256": sha256(readme)})
    manifest = package / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1, "estado": "revision_academica", "archivos": copied}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    zip_path = build / "paquete-academico-grifo-aquiles-revision.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(package.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(package))
    print(f"Paquete: {package}")
    print(f"ZIP: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
