"""Pipeline Rev. 2 desde cualquier directorio; archiva salidas solo por opción expresa."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUTPUTS = [ROOT / d / name for d, name in [
    ("datos", "vertices_corredor_manual.csv"), ("datos", "estaciones_corredor.csv"),
    ("datos", "ubicaciones_postes_preliminares.csv"), ("datos", "cruces_y_puntos_criticos.csv"),
    ("derived", "auditoria_corredor_manual.json"), (".", "inventario_archivos.csv"),
    (".", "manifest.json")]] + [ROOT/"plans"/f"CL-{n:02d}_REV2_MANUAL.{ext}"
                 for n in range(1,6) for ext in ("dxf","pdf","png")]


def call(*args):
    subprocess.run([sys.executable,*args], cwd=REPO, check=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive-existing",action="store_true",help="respalda las salidas Rev. 2 y regenera")
    options=parser.parse_args()
    missing=[str(p) for p in (ROOT/"sources/ruta topografica capachica llachon.kml",
                              ROOT/"sources/gisem_mt_estructuras.geojson",
                              ROOT/"sources/osm_roads.json") if not p.is_file()]
    if missing:raise FileNotFoundError("Faltan fuentes obligatorias: "+", ".join(missing))
    existing=[p for p in OUTPUTS if p.exists()]
    if existing and not options.archive_existing:
        raise FileExistsError("Hay salidas Rev. 2. Use --archive-existing para respaldar y regenerar")
    if existing:
        archive=REPO/"build"/ROOT.name/"archive_rev2"/datetime.now().strftime("%Y%m%d_%H%M%S")
        for path in existing:
            rel=path.resolve().relative_to(ROOT.resolve())
            dest=archive/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(path),str(dest))
        print(f"Respaldadas {len(existing)} salidas en {archive}")
    call(str(ROOT/"scripts/auditar_corredor_manual.py"))
    call(str(ROOT/"scripts/generar_revision_manual.py"))
    call("-m","pytest",str(ROOT/"tests"),"-q")
    call(str(ROOT/"scripts/verificar_revision_manual.py"))
    print("Pipeline Rev. 2 completo; expediente editable en expediente/07_revision_corredor_manual.md")

if __name__=="__main__":main()
