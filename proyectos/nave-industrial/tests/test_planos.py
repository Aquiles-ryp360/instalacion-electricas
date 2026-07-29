import json
import os
import sys

import ezdxf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from generar_planos_industriales import generar_distribucion


def test_distribucion_usa_simbologia_dge(tmp_path):
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "diseno-electrico", "datos", "cargas-industriales.json"
    )
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    out = tmp_path / "distribucion.dxf"
    generar_distribucion(data, str(out))

    msp = ezdxf.readfile(out).modelspace()
    layers = [entity.dxf.layer for entity in msp]
    texts = [entity.dxf.text for entity in msp.query("TEXT")]

    assert "IND_LUM" in layers
    assert layers.count("IND_CARGA") >= len(data["tomacorrientes"])
    assert "SIMBOLOGIA DGE" in texts
