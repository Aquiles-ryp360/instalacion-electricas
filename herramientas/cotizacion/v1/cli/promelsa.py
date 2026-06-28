#!/usr/bin/env python3
"""CLI para cotizar materiales en Promelsa."""

from __future__ import annotations

import sys
from pathlib import Path


COTIZACION_DIR = Path(__file__).resolve().parents[2]
if str(COTIZACION_DIR) not in sys.path:
    sys.path.insert(0, str(COTIZACION_DIR))

from v1.tiendas.promelsa import main


if __name__ == "__main__":
    raise SystemExit(main())
