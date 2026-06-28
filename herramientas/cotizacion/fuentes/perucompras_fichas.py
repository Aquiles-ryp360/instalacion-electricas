#!/usr/bin/env python3
"""Wrapper compatible para PeruCompras v1."""

from __future__ import annotations

import sys
from pathlib import Path


COTIZACION_DIR = Path(__file__).resolve().parents[1]
if str(COTIZACION_DIR) not in sys.path:
    sys.path.insert(0, str(COTIZACION_DIR))

from v1.homologacion.perucompras import main


if __name__ == "__main__":
    raise SystemExit(main())
