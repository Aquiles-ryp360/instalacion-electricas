#!/usr/bin/env python3
"""Prepara el escudo UNAP vectorial usado por el expediente.

La fuente es el SVG publicado por una facultad en el dominio oficial UNAP. Se
verifica su huella antes de convertirlo a PDF para evitar depender del PNG de
113 x 124 px heredado del expediente de la primera unidad.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path


URL = "https://derecho.unap.edu.pe/storage/2019/05/unap_logo.svg"
EXPECTED_SHA256 = "9f15da7b391761fe2fc9eb64ff0f4039e2d96e95b360056b8cb7b1675152bebe"
EXPECTED_PDF_SHA256 = "23078802af82a33d9f578ccf24ac5cade9ec0582ae3433e9a9a68cd0779ae5f9"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> int:
    root = repository_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "build/unidad-2-industrial/expediente/assets")
    parser.add_argument(
        "--actualizar-desde-web",
        action="store_true",
        help="comprueba el SVG oficial en linea; la compilacion normal es reproducible y no usa red",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    bundled = root / "proyectos/unidad-2-industrial/fuentes/versionadas/identidad"
    bundled_svg = bundled / "unap_logo.svg"
    bundled_pdf = bundled / "unap_logo.pdf"
    if not bundled_svg.is_file() or not bundled_pdf.is_file():
        raise SystemExit(f"Faltan recursos UNAP versionados en {bundled}")

    bundled_svg_payload = bundled_svg.read_bytes()
    actual = hashlib.sha256(bundled_svg_payload).hexdigest()
    actual_pdf = hashlib.sha256(bundled_pdf.read_bytes()).hexdigest()
    if actual != EXPECTED_SHA256 or actual_pdf != EXPECTED_PDF_SHA256:
        raise SystemExit("Los recursos UNAP versionados no coinciden con sus huellas registradas")
    if args.actualizar_desde_web:
        remote_payload = urllib.request.urlopen(URL, timeout=30).read()
        remote_hash = hashlib.sha256(remote_payload).hexdigest()
        if remote_hash != EXPECTED_SHA256:
            raise SystemExit(f"Huella inesperada del SVG UNAP remoto: {remote_hash}")

    svg_path = output / "unap_logo.svg"
    pdf_path = output / "unap_logo.pdf"
    shutil.copy2(bundled_svg, svg_path)
    shutil.copy2(bundled_pdf, pdf_path)
    manifest = {
        "source_url": URL,
        "source_sha256": actual,
        "source_pdf_sha256": actual_pdf,
        "source_domain": "derecho.unap.edu.pe",
        "source_mode": "recurso_versionado_verificado",
        "purpose": "escudo vectorial para portada y encabezados; conserva el formato Aquiles sin desenfoque",
        "outputs": {"svg": display_path(svg_path, root), "pdf": display_path(pdf_path, root)},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
