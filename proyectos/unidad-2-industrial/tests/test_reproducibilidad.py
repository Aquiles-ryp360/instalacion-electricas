"""Pruebas de que un clon nuevo contiene todas las entradas de Unidad 2."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
VERIFIER = PROJECT / "scripts/verificar_preparacion.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verificar_preparacion", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_required_inputs_exist_with_recorded_hashes():
    module = load_verifier()
    for relative, expected in module.REQUIRED_FILES.items():
        path = REPO / relative
        assert path.is_file(), relative
        assert module.sha256(path) == expected["sha256"], relative


def test_unap_assets_prepare_without_network(tmp_path):
    script = PROJECT / "scripts/preparar_recursos_expediente.py"
    subprocess.run(
        [sys.executable, str(script), "--output", str(tmp_path)],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    assert (tmp_path / "unap_logo.svg").is_file()
    assert (tmp_path / "unap_logo.pdf").is_file()
