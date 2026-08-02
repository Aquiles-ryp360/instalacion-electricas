#!/usr/bin/env python3
"""Compila el expediente y la guia sin crear rutas build anidadas."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run(command: list[str], *, cwd: Path) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    root = repository_root()
    project = root / "proyectos/unidad-2-industrial"
    source = project / "expediente"
    output = root / "build/unidad-2-industrial/expediente"
    python = root / ".venv/bin/python"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regenerar-planos",
        action="store_true",
        help="regenera las seis laminas DXF/PDF antes de compilar (proceso lento)",
    )
    parser.add_argument(
        "--regenerar-base-cad",
        action="store_true",
        help="reextrae A-01 y su PDF vectorial desde el DXF local verificado",
    )
    args = parser.parse_args()

    if not python.is_file():
        python = Path(sys.executable)

    scripts = [
        "calcular_proyecto.py",
        "calcular_alumbrado.py",
        "calcular_metrados_presupuesto.py",
        "preparar_recursos_ubicacion.py",
        "preparar_recursos_expediente.py",
        "generar_fragmentos_expediente.py",
    ]
    if args.regenerar_planos:
        scripts.insert(3, "generar_planos_grifo.py")
    if args.regenerar_base_cad or args.regenerar_planos:
        run(
            [str(python), str(project / "scripts/preparar_base_cad.py"), "--sheet", "A-01"],
            cwd=root,
        )
    for script in scripts:
        run([str(python), str(project / "scripts" / script)], cwd=root)

    quote = root / "build/unidad-2-industrial/cotizaciones/promelsa.json"
    if quote.is_file():
        run([str(python), str(project / "scripts/revalidar_cotizacion_automatica.py")], cwd=root)
        run([str(python), str(project / "scripts/resumir_cotizacion_automatica.py")], cwd=root)
    else:
        raise SystemExit(
            "Falta build/unidad-2-industrial/cotizaciones/promelsa.json. "
            "Ejecute primero el flujo documentado en presupuesto/README.md."
        )

    plans = root / "build/unidad-2-industrial/cad/planos/planos-electricos-grifo-unap-aquiles.pdf"
    if not plans.is_file():
        raise SystemExit("Falta el PDF conjunto de planos; use --regenerar-planos.")

    output.mkdir(parents=True, exist_ok=True)
    latex_base = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", f"-outdir={output}"]
    run([*latex_base, "main.tex"], cwd=source)
    run([*latex_base, "-jobname=guia-sustentacion", "guia-sustentacion.tex"], cwd=source)
    print(f"Expediente: {output / 'main.pdf'}")
    print(f"Guia: {output / 'guia-sustentacion.pdf'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
