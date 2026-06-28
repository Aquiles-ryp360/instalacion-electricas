#!/usr/bin/env python3
"""Orquestador inicial del flujo de cotizacion v1.

Por ahora ejecuta la etapa de tienda Promelsa. PeruCompras queda como
homologacion opcional/diagnostica hasta completar su cobertura.
"""

from __future__ import annotations

import sys
from pathlib import Path


COTIZACION_DIR = Path(__file__).resolve().parents[2]
if str(COTIZACION_DIR) not in sys.path:
    sys.path.insert(0, str(COTIZACION_DIR))

from v1.tiendas.promelsa import main as promelsa_main


def main(argv: list[str] | None = None) -> int:
    return promelsa_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
