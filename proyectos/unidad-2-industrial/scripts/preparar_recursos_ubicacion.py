#!/usr/bin/env python3
"""Verifica y recorta las capturas de ubicacion sin alterar los originales."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from PIL import Image


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
    data = yaml.safe_load((project / "datos/ubicacion.yaml").read_text(encoding="utf-8"))
    output = root / "build/unidad-2-industrial/expediente/assets/ubicacion"
    output.mkdir(parents=True, exist_ok=True)

    crops = {
        "LOC-CAT-01": (135, 205, 1802, 916),
        "LOC-MAP-01": (500, 90, 1808, 1018),
    }
    destinations = {
        "LOC-CAT-01": "catastro-municipal-caracoto.png",
        "LOC-MAP-01": "mapa-satelital-caracoto.png",
    }
    records: list[dict[str, object]] = []
    for source_data in data["capturas_recibidas"]:
        source = project / source_data["ruta_local"]
        if not source.is_file():
            raise SystemExit(f"Falta captura local requerida: {source}")
        actual_hash = sha256(source)
        if actual_hash != source_data["sha256"]:
            raise SystemExit(f"La captura {source_data['id']} no coincide con su SHA-256 registrado")
        destination = output / destinations[source_data["id"]]
        with Image.open(source) as image:
            cropped = image.convert("RGB").crop(crops[source_data["id"]])
            cropped.save(destination, format="PNG", optimize=True)
        records.append({
            "id": source_data["id"],
            "source": str(source.relative_to(root)),
            "source_sha256": actual_hash,
            "crop_pixels": list(crops[source_data["id"]]),
            "output": str(destination.relative_to(root)),
            "output_sha256": sha256(destination),
        })

    manifest = output / "manifest.json"
    manifest.write_text(
        json.dumps({"schema_version": 1, "records": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Recursos de ubicacion preparados en {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
