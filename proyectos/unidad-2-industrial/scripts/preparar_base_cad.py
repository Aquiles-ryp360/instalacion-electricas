#!/usr/bin/env python3
"""Separa y renderiza las laminas del DXF fuente sin modificarlo.

Las salidas son regenerables y pertenecen a ``build/``. La seleccion se hace
por interseccion de la caja grafica de cada entidad con el marco observado de
cada lamina. Cada DXF derivado se traslada a un origen local y declara metros
como unidad; la fuente conserva intacta su configuracion original.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import ezdxf
from ezdxf import bbox, select
from ezdxf.addons import Importer
from ezdxf.addons.drawing import matplotlib as ezdxf_matplotlib


EXPECTED_SHA256 = "7980dda84d5ea40ed85e5458b487edfc219584d8c4b6e62f7fd9442e7443d805"


@dataclass(frozen=True)
class Sheet:
    code: str
    title: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin


SHEETS = (
    Sheet("A-01", "Distribucion y circulacion", 1596.7895, 1521.3837, 1764.9895, 1640.1837),
    Sheet("S-01", "Seguridad y SCI", 1791.8270, 1521.3837, 1960.0270, 1640.1837),
    Sheet("M-01", "Monitoreo", 1982.3884, 1518.1668, 2150.5884, 1636.9668),
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_sheet_entities(
    entities: Iterable[ezdxf.entities.DXFGraphic], sheet: Sheet, cache: bbox.Cache
) -> list[ezdxf.entities.DXFGraphic]:
    window = select.Window((sheet.xmin, sheet.ymin), (sheet.xmax, sheet.ymax))
    return list(select.bbox_overlap(window, entities, cache=cache))


def import_entities(
    source_doc: ezdxf.document.Drawing,
    entities: list[ezdxf.entities.DXFGraphic],
) -> ezdxf.document.Drawing:
    target_doc = ezdxf.new("R2018", setup=True)
    importer = Importer(source_doc, target_doc)
    importer.import_entities(entities, target_doc.modelspace())
    importer.finalize()
    return target_doc


def translate_to_local_origin(
    doc: ezdxf.document.Drawing, sheet: Sheet
) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    dx = -sheet.xmin
    dy = -sheet.ymin
    for entity in doc.modelspace():
        try:
            entity.translate(dx, dy, 0.0)
        except (AttributeError, NotImplementedError, TypeError) as exc:
            warnings.append(
                {
                    "handle": str(entity.dxf.handle),
                    "type": entity.dxftype(),
                    "warning": str(exc),
                }
            )

    doc.header["$INSUNITS"] = 6  # metros en la copia interpretada
    doc.header["$EXTMIN"] = (0.0, 0.0, 0.0)
    doc.header["$EXTMAX"] = (sheet.width, sheet.height, 0.0)
    return warnings


def render_review(doc: ezdxf.document.Drawing, destination: Path) -> None:
    # Los HATCH importados del levantamiento hacen que un render vectorial
    # completo tarde varios minutos y no aportan a la revision geometrica.
    # El DXF derivado conserva esas entidades; solo se omiten en la vista.
    def review_filter(entity: ezdxf.entities.DXFGraphic) -> bool:
        return entity.dxftype() not in {"HATCH", "SOLID", "TRACE"}

    ezdxf_matplotlib.qsave(
        doc.modelspace(),
        destination,
        bg="#FFFFFF",
        fg="#111111",
        dpi=120,
        size_inches=(12.0, 0.0),
        filter_func=review_filter,
    )


def main() -> int:
    root = repository_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=root
        / "proyectos/unidad-2-industrial/fuentes/local/cad"
        / "DISTRIBUCION Y CIRCULACION MIGUEL.dxf",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "build/unidad-2-industrial/cad/base",
    )
    parser.add_argument(
        "--skip-render",
        action="store_true",
        help="genera DXF y manifiesto sin PNG/PDF",
    )
    parser.add_argument(
        "--sheet",
        choices=[sheet.code for sheet in SHEETS],
        help="procesa solo una lamina; sin esta opcion procesa las tres",
    )
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    if not source.is_file():
        print(f"ERROR: no existe la fuente local: {source}", file=sys.stderr)
        return 2

    actual_hash = sha256(source)
    if actual_hash != EXPECTED_SHA256:
        print(
            "ERROR: la huella de la fuente no coincide; no se generaran derivados.\n"
            f"esperada={EXPECTED_SHA256}\nactual={actual_hash}",
            file=sys.stderr,
        )
        return 3

    print(f"Leyendo fuente verificada: {source.name}")
    source_doc = ezdxf.readfile(source)
    source_entities = list(source_doc.modelspace())
    cache = bbox.Cache()
    manifest: dict[str, object] = {
        "schema_version": 1,
        "generated_on": date.today().isoformat(),
        "source": {
            "path": str(source),
            "sha256": actual_hash,
            "size_bytes": source.stat().st_size,
            "dxfversion": source_doc.dxfversion,
            "insunits_original": int(source_doc.header.get("$INSUNITS", 0)),
            "modelspace_entities": len(source_entities),
        },
        "interpretation": {
            "derived_unit": "m",
            "translation": "cada lamina se traslada desde su esquina inferior izquierda al origen 0,0",
            "warning": "la fuente declara milimetros, pero cotas, escala y geometria se interpretan como metros",
        },
        "sheets": [],
    }

    selected_sheets = [sheet for sheet in SHEETS if args.sheet in (None, sheet.code)]
    for sheet in selected_sheets:
        print(f"Seleccionando {sheet.code}...")
        entities = select_sheet_entities(source_entities, sheet, cache)
        if not entities:
            print(f"ERROR: no se encontraron entidades en {sheet.code}", file=sys.stderr)
            return 4

        derived = import_entities(source_doc, entities)
        warnings = translate_to_local_origin(derived, sheet)
        stem = sheet.code.lower().replace("-", "_") + "_referencia_local"
        dxf_path = output / f"{stem}.dxf"
        png_path = output / f"{stem}.png"
        pdf_path = output / f"{stem}.pdf"
        derived.saveas(dxf_path)

        if not args.skip_render:
            print(f"Renderizando vista liviana {sheet.code} a PNG y PDF vectorial...", flush=True)
            render_review(derived, png_path)
            render_review(derived, pdf_path)

        counts = Counter(entity.dxftype() for entity in entities)
        layers = Counter(str(entity.dxf.layer) for entity in entities)
        manifest["sheets"].append(
            {
                "code": sheet.code,
                "title": sheet.title,
                "source_bbox": {
                    "xmin": sheet.xmin,
                    "ymin": sheet.ymin,
                    "xmax": sheet.xmax,
                    "ymax": sheet.ymax,
                },
                "local_bbox": {
                    "xmin": 0.0,
                    "ymin": 0.0,
                    "xmax": sheet.width,
                    "ymax": sheet.height,
                },
                "entity_count": len(entities),
                "entity_types": dict(sorted(counts.items())),
                "layers": dict(sorted(layers.items())),
                "translation_warnings": warnings,
                "outputs": {
                    "dxf": str(dxf_path.relative_to(root)),
                    "png": None if args.skip_render else str(png_path.relative_to(root)),
                    "pdf": None if args.skip_render else str(pdf_path.relative_to(root)),
                },
                "dxf_sha256": sha256(dxf_path),
            }
        )

    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Manifiesto: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
