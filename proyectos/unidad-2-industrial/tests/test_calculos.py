"""Pruebas de coherencia del modelo electrico y de sus fuentes canonicas."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import yaml


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
CALCULATION_SCRIPT = PROJECT / "scripts" / "calcular_proyecto.py"
BUDGET_SCRIPT = PROJECT / "scripts" / "calcular_metrados_presupuesto.py"


def load_calculation_module():
    spec = importlib.util.spec_from_file_location("calcular_proyecto", CALCULATION_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_electrical_calculation_passes_design_guards():
    module = load_calculation_module()
    data = load_yaml(PROJECT / "diseno-electrico" / "datos" / "cargas.yaml")
    result = module.calculate(data)

    assert result["status"] == "PASS", result["failures"]
    assert not result["failures"]
    assert result["summary"]["phase_unbalance_percent"] <= 10.0
    assert result["summary"]["service_design_kva_with_reserve"] <= 50.0
    assert result["generator"]["pass"] is True

    for circuit in result["circuits"]:
        assert circuit["branch_voltage_drop_percent"] <= 2.5
        assert circuit["total_voltage_drop_percent"] <= 4.0
        assert circuit["design_current_a"] <= circuit["corrected_ampacity_a"]
        assert 0 < circuit["rcd_ma"] <= 30


def test_title_block_matches_confirmed_scope():
    title_block = load_yaml(PROJECT / "datos" / "rotulo-planos.yaml")

    assert title_block["institucion"]["universidad"] == "UNIVERSIDAD NACIONAL DEL ALTIPLANO"
    assert title_block["academico"]["curso"] == "INSTALACIONES ELECTRICAS I"
    assert title_block["academico"]["estudiante"] == "AQUILES TAYLOR RAMOS YAPO"
    assert title_block["academico"]["docente"] == "MG. GREGORIO MEZA MAROCHO"
    assert title_block["proyecto"]["propietario"] == "MIGUEL MAMANI CHUQUICALLATA"
    assert "GLP" in title_block["proyecto"]["exclusiones"]
    assert "GNV" in title_block["proyecto"]["exclusiones"]
    assert title_block["responsabilidades"]["cip"] is None


def test_local_cad_copy_matches_recorded_immutable_hash_when_present():
    architecture = __import__("json").loads(
        (PROJECT / "arquitectura" / "datos" / "grifo.json").read_text(encoding="utf-8")
    )
    relative = Path(architecture["source"]["local_path"])
    source = REPO / relative
    if not source.exists():
        return
    assert file_sha256(source) == architecture["source"]["sha256"]


def test_generated_title_block_contains_unap_identity_without_fake_cip():
    generator_path = PROJECT / "scripts" / "generar_planos_grifo.py"
    spec = importlib.util.spec_from_file_location("generar_planos_grifo", generator_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    title_data = load_yaml(PROJECT / "datos" / "rotulo-planos.yaml")
    sheet = title_data["laminas_previstas"][0]
    doc = module.new_document()
    module.add_title_block(doc.modelspace(), title_data, sheet, 1, 6, "1:100")
    texts = [entity.dxf.text for entity in doc.modelspace().query("TEXT")]

    assert any("UNIVERSIDAD NACIONAL DEL ALTIPLANO" in value for value in texts)
    assert any("AQUILES TAYLOR RAMOS YAPO" in value for value in texts)
    assert any("GREGORIO MEZA MAROCHO" in value for value in texts)
    assert any("MIGUEL MAMANI CHUQUICALLATA" in value for value in texts)
    assert any("PUNO" in value for value in texts)
    assert not any("CIP:" in value for value in texts)
    assert len(doc.modelspace().query("WIPEOUT")) == 1


def test_lighting_zones_meet_declared_targets():
    script = PROJECT / "scripts" / "calcular_alumbrado.py"
    spec = importlib.util.spec_from_file_location("calcular_alumbrado", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = load_yaml(PROJECT / "diseno-electrico" / "datos" / "alumbrado.yaml")
    result = module.calculate(data)

    assert result["status"] == "PASS", result["failures"]
    assert all(zone["average_lux"] >= zone["target_lux"] for zone in result["zones"])


def test_budget_is_reproducible_and_labeled_referential():
    spec = importlib.util.spec_from_file_location("calcular_metrados_presupuesto", BUDGET_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    loads = load_yaml(PROJECT / "diseno-electrico" / "datos" / "cargas.yaml")
    budget = load_yaml(PROJECT / "presupuesto" / "datos" / "partidas.yaml")
    result = module.calculate(loads, budget)

    assert result["status"] == "PASS"
    assert result["assumptions"]["circuits_count"] == 35
    assert len(result["items"]) >= 45
    assert all(row["cantidad"] > 0 and row["precio_unitario"] > 0 for row in result["items"])
    assert result["totals"]["total"] > result["totals"]["direct_cost"] > 0
    assert "referencial" in result["estado"]
    assert any(row["tipo_precio"] == "estimado_anteproyecto" for row in result["items"])


def test_defense_guide_uses_current_key_values():
    guide = (PROJECT / "documentacion" / "guia-sustentacion.md").read_text(encoding="utf-8")
    assert "35 circuitos" in guide
    assert "39.97 kVA" in guide
    assert "4x35 mm2 + PE 16 mm2" in guide
    assert "GLP y GNV" in guide
    assert "no una cotizacion" in guide.lower()
