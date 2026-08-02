"""Pruebas sin red del selector automatico conservador de Promelsa."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tiendas" / "promelsa.py"


def load_module():
    spec = importlib.util.spec_from_file_location("promelsa_v1", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_heuristic_selects_only_traceable_exact_candidate():
    module = load_module()
    candidates = [{
        "opcion": 1,
        "nombre": "Cable electrico LSZH 2.5 mm2",
        "familia_candidato": "cable",
        "especificaciones_coincidentes": ["2.5mm2"],
        "coincidencia_score": 5.25,
        "precio_soles": 4.90,
        "disponible": True,
    }]

    result = module.decidir_heuristico_seguro("Conductor Cu LSZH 2.5 mm2", candidates)

    assert result["opcion"] == 1
    assert result["decision"] == "coincidencia_heuristica_trazable"
    assert result["requiere_revision"] is True


def test_heuristic_rejects_candidate_without_matching_nominal_spec():
    module = load_module()
    candidates = [{
        "opcion": 1,
        "nombre": "Cable electrico LSZH 4 mm2",
        "familia_candidato": "cable",
        "especificaciones_coincidentes": [],
        "coincidencia_score": 5.00,
        "precio_soles": 7.20,
        "disponible": True,
    }]

    result = module.decidir_heuristico_seguro("Conductor Cu LSZH 2.5 mm2", candidates)

    assert result["opcion"] is None
    assert result["decision"] == "sin_opcion_segura"
    assert result["requiere_revision"] is True


def test_heuristic_rejects_accessory_that_only_mentions_target_family():
    module = load_module()
    candidate = {
        "opcion": 1,
        "nombre": "Luminaria LED para tablero 9 W",
        "texto_visible": "Accesorio de iluminacion para tablero",
        "familia_candidato": module.detect_family("Luminaria LED para tablero 9 W"),
        "especificaciones_coincidentes": [],
        "coincidencia_score": 5.0,
        "precio_soles": 290.49,
        "disponible": True,
    }

    result = module.decidir_heuristico_seguro("Tablero electrico administrativo", [candidate])

    assert result["opcion"] is None


def test_heuristic_rejects_cable_stripping_tool_as_control_cable():
    module = load_module()
    candidate = {
        "opcion": 1,
        "nombre": "Cuchillo pela cable aislado 1000V L=165mm",
        "texto_visible": "Herramienta aislada para pelar cable",
        "familia_candidato": "cable",
        "especificaciones_coincidentes": [],
        "coincidencia_score": 4.35,
        "precio_soles": 28.64,
        "disponible": True,
    }

    result = module.decidir_heuristico_seguro(
        "Cableado de control e interbloqueo del paro de emergencia",
        [candidate],
    )

    assert result["opcion"] is None
    assert "herramienta_o_accesorio_no_es_cable" in result["criterios"][-1]


def test_heuristic_rejects_non_autonomous_luminaire_for_emergency():
    module = load_module()
    candidate = {
        "opcion": 1,
        "nombre": "Luminaria hermetica LED 40 W",
        "texto_visible": "Luminaria hermetica de uso general",
        "familia_candidato": "luminaria",
        "especificaciones_coincidentes": [],
        "coincidencia_score": 5.0,
        "precio_soles": 117.17,
        "disponible": True,
    }

    result = module.decidir_heuristico_seguro("Luminaria autonoma de emergencia", [candidate])

    assert result["opcion"] is None


def test_heuristic_rejects_low_power_bulb_advertised_as_60w_equivalent_panel():
    module = load_module()
    candidate = {
        "opcion": 1,
        "nombre": "Lampara LED Bulb A60 9-60W E27",
        "texto_visible": "Bombilla LED 9-60W de uso interior",
        "familia_candidato": "luminaria",
        "especificaciones_coincidentes": ["60w"],
        "coincidencia_score": 5.25,
        "precio_soles": 2.11,
        "disponible": True,
    }

    result = module.decidir_heuristico_seguro("Panel luminaria LED interior 60 W", [candidate])

    assert result["opcion"] is None
