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
import subprocess
import urllib.request
from pathlib import Path


URL = "https://derecho.unap.edu.pe/storage/2019/05/unap_logo.svg"
EXPECTED_SHA256 = "9f15da7b391761fe2fc9eb64ff0f4039e2d96e95b360056b8cb7b1675152bebe"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> int:
    root = repository_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "build/unidad-2-industrial/expediente/assets")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    svg_path = output / "unap_logo.svg"
    pdf_path = output / "unap_logo.pdf"
    payload = urllib.request.urlopen(URL, timeout=30).read()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != EXPECTED_SHA256:
        raise SystemExit(f"Huella inesperada del SVG UNAP: {actual}")
    svg_path.write_bytes(payload)
    subprocess.run(["rsvg-convert", "--format=pdf", f"--output={pdf_path}", str(svg_path)], check=True)
    manifest = {
        "source_url": URL,
        "source_sha256": actual,
        "source_domain": "derecho.unap.edu.pe",
        "purpose": "escudo vectorial para portada y encabezados; conserva el formato Aquiles sin desenfoque",
        "outputs": {"svg": str(svg_path.relative_to(root)), "pdf": str(pdf_path.relative_to(root))},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
