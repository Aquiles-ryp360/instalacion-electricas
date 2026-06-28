#!/usr/bin/env python3
"""Wrapper compatible del scraper de PeruCompras v1."""

from __future__ import annotations

import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from v1.homologacion.perucompras import main


if __name__ == "__main__":
    sys.exit(main())
