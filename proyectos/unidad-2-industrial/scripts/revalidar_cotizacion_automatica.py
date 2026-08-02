#!/usr/bin/env python3
"""Reaplica los filtros locales a una evidencia Promelsa ya descargada."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> int:
    root = repository_root()
    cotizacion_dir = root / "herramientas/cotizacion"
    if str(cotizacion_dir) not in sys.path:
        sys.path.insert(0, str(cotizacion_dir))
    from v1.tiendas.promelsa import decidir_heuristico_seguro

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=root / "build/unidad-2-industrial/cotizaciones/promelsa.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.input
    data = json.loads(args.input.read_text(encoding="utf-8"))
    rejected = 0
    reviewed = 0
    for item in data.get("materiales", []):
        quote = item.get("cotizacion_promelsa") or {}
        if quote.get("estado") != "OK" or not quote.get("candidatos"):
            continue
        reviewed += 1
        decision = decidir_heuristico_seguro(str(item.get("item") or ""), quote["candidatos"])
        if decision.get("opcion") is not None:
            continue
        rejected += 1
        quote["estado"] = "SIN_SELECCION"
        quote["producto_descartado_por_revalidacion"] = quote.pop("producto", None)
        quote["mensaje"] = decision.get("justificacion")
        quote["seleccion"] = {
            "opcion": None,
            "decision": decision.get("decision"),
            "requiere_revision": True,
            "justificacion": decision.get("justificacion"),
            "criterios": decision.get("criterios", []),
        }
        quote["revalidacion"] = {
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "resultado": "candidato_descartado_por_filtros_vigentes",
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(json.dumps({"status": "PASS", "ok_revisados": reviewed, "descartados": rejected}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
