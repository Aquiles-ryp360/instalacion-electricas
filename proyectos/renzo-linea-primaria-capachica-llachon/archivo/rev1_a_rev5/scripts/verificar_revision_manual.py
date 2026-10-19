"""Verifica entregables Rev. 2 y escribe inventario/manifiesto sin sobrescribir."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import ezdxf
import fitz

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {"__pycache__", ".pytest_cache", "respaldo_generacion_inicial_20261014",
           "mapa enegetico minero .png"}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    required = [ROOT/"derived/auditoria_corredor_manual.json",
                ROOT/"datos/estaciones_corredor.csv", ROOT/"datos/vertices_corredor_manual.csv",
                ROOT/"datos/ubicaciones_postes_preliminares.csv", ROOT/"datos/cruces_y_puntos_criticos.csv"]
    for n in (1,2,3,4,5):
        for ext in ("dxf", "pdf", "png"):
            required.append(ROOT/"plans"/f"CL-{n:02d}_REV2_MANUAL.{ext}")
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Entregable obligatorio ausente o vacío: {path}")
    for n in (1,2,3,4,5):
        base=ROOT/"plans"/f"CL-{n:02d}_REV2_MANUAL"
        doc=ezdxf.readfile(base.with_suffix(".dxf"))
        if doc.audit().has_errors or doc.header["$INSUNITS"] != 6:
            raise ValueError(f"DXF inválido: {base}")
        pdf=fitz.open(base.with_suffix(".pdf"))
        if len(pdf)!=1 or not (1180 < pdf[0].rect.width < 1200 and 830 < pdf[0].rect.height < 850):
            raise ValueError(f"PDF no es A3 horizontal: {base}")
    report=json.loads(required[0].read_text(encoding="utf-8"))
    if report["segmentos"] != 4 or report["vertices"] != 187:
        raise ValueError("Cambió el KML; revise resultados antes de publicar")
    inventory=ROOT/"inventario_archivos.csv";manifest=ROOT/"manifest.json"
    if inventory.exists() or manifest.exists():
        raise FileExistsError("Inventario o manifest existente: archive antes de regenerar")
    paths=sorted(p for p in ROOT.rglob("*") if p.is_file() and
                 not any(x in EXCLUDE for x in p.parts) and p not in (inventory,manifest))
    with inventory.open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f);writer.writerow(["ruta","bytes","sha256"])
        for path in paths:writer.writerow([path.relative_to(ROOT).as_posix(),path.stat().st_size,sha(path)])
    payload={"revision":2,"status":"PRELIMINARY_NOT_FOR_CONSTRUCTION",
             "kml_sha256":report["kml_sha256"],"outputs":{p.relative_to(ROOT).as_posix():
             {"bytes":p.stat().st_size,"sha256":sha(p)} for p in required}}
    manifest.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Verificados {len(required)} entregables; inventariados {len(paths)} archivos")

if __name__ == "__main__":main()
