"""Expediente completo en un solo comando: motor LP 22,9 kV + planos EPIME Rev. 8 + ZIP.

    python scripts/generar_expediente.py --motor C:\\Users\\renzo\\EXP_LP\\motor

1. Aplica al motor los parches de datos/motor_lp229/*.patch (si faltan) y lo ejecuta
   con datos/motor_lp229/entrada/proyecto.yaml.
2. Copia sus resultados a datos/motor_lp229/resultados/ y las láminas de armados a plans/armados_lp229/.
3. Genera plans/LP_REV8.dxf/.pdf/.dwg y los DWG de los armados (AutoCAD u ODA File Converter).
4. Arma el paquete en ~/EXP_LP/b/: Vol. VII con los planos EPIME como principales,
   los del motor como complementarios y un DWG junto a cada DXF. Lo comprime en expediente/.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import planos_formato_epime as pe
import planos_motor_epime as pm

ROOT = Path(__file__).resolve().parents[1]
MOTOR_DATOS = ROOT / "datos" / "motor_lp229"
RAIZ = "EXPEDIENTE_LP_22_9_KV_CAPACHICA_LLACHON"
VOL7 = Path("Expediente Tecnico") / "VOL. VII PLANOS Y LAMINAS DE DETALLE"
EPIME = "PLANOS PRINCIPALES - FORMATO EPIME (REV. 8)"
COMPLEMENTARIOS = "PLANOS COMPLEMENTARIOS (MOTOR)"
ZIP = ROOT / "expediente" / "EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip"
# ponytail: Word, ODA y rmtree fallan con rutas de más de 259 caracteres; la salida del motor y el
# armado del paquete van a rutas cortas fijas fuera del repositorio (regenerables, como build/).
SALIDA = Path.home() / "EXP_LP" / "s"
BUILD = Path.home() / "EXP_LP" / "b"


def parchear(motor: Path) -> None:
    for patch in sorted(MOTOR_DATOS.glob("*.patch")):
        ya = subprocess.run(["git", "apply", "--reverse", "--check", str(patch)], cwd=motor, capture_output=True)
        if ya.returncode:
            subprocess.run(["git", "apply", str(patch)], cwd=motor, check=True)


def correr_motor(motor: Path, salida: Path) -> None:
    parchear(motor)
    proy = motor / "proyectos" / "capachica-llachon"
    shutil.rmtree(proy, ignore_errors=True)
    shutil.copytree(MOTOR_DATOS / "entrada", proy)
    shutil.rmtree(salida, ignore_errors=True)
    subprocess.run([sys.executable, "generar.py", str(proy / "proyecto.yaml"), "--salida", str(salida)],
                   cwd=motor, check=True, env={**os.environ, "PYTHONUTF8": "1"})


def oda_carpeta(src: Path, dst: Path) -> None:
    """Todos los DXF de src -> DWG 2018 en dst (ODA, con AUDIT). Convierte en carpetas temporales
    porque ODA no abre rutas de más de 260 caracteres."""
    dst.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        for dxf in src.glob("*.dxf"):
            shutil.copy(dxf, a)
        subprocess.run([str(pe.ODA), a, b, "ACAD2018", "DWG", "0", "1", "*.DXF"], check=True, timeout=1800)
        for dwg in Path(b).glob("*.dwg"):
            shutil.copy(dwg, dst)
    faltan = {f.stem for f in src.glob("*.dxf")} - {f.stem for f in dst.glob("*.dwg")}
    if faltan:
        raise RuntimeError(f"ODA no convirtió: {sorted(faltan)}")


def copiar_resultados(salida: Path) -> None:
    for f in (MOTOR_DATOS / "resultados").iterdir():
        shutil.copy(salida / "trabajo" / f.name, f)
    lam = salida / RAIZ / VOL7 / "LAMINAS DE DETALLE"
    for dxf in (ROOT / "plans" / "armados_lp229").glob("*.dxf"):
        shutil.copy(lam / "DXF (AutoCAD)" / dxf.name, dxf)
        shutil.copy(lam / "PDF" / dxf.with_suffix(".pdf").name, dxf.with_suffix(".pdf"))


def planos() -> None:
    pm.generar()
    pe.dxf_a_dwg(pm.OUT_DXF)
    for dxf in sorted((ROOT / "plans" / "armados_lp229").glob("*.dxf")):
        pe.dxf_a_dwg(dxf)


def empaquetar(salida: Path) -> Path:
    build = BUILD
    shutil.rmtree(build, ignore_errors=True)
    shutil.copytree(salida / RAIZ, build / RAIZ)
    v7 = build / RAIZ / VOL7
    (v7 / "PLANOS").rename(v7 / COMPLEMENTARIOS)
    for sub in (COMPLEMENTARIOS, "LAMINAS DE DETALLE"):
        oda_carpeta(v7 / sub / "DXF (AutoCAD)", v7 / sub / "DWG (AutoCAD)")
    geo = v7 / "COORDENADAS Y PLANO GEORREFERENCIADO"
    oda_carpeta(geo, geo)
    ep = v7 / EPIME
    ep.mkdir()
    for ext in ("dwg", "dxf", "pdf"):
        shutil.copy(pm.OUT_DXF.with_suffix(f".{ext}"), ep)
    shutil.copy(ROOT / "documentacion" / "GUIA_AUTOCAD_EDITABLES.md", ep)
    ZIP.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted((build / RAIZ).rglob("*")):
            z.write(f, f.relative_to(build).as_posix())
    return build / RAIZ


def verificar(raiz: Path) -> list[str]:
    """Rutas del paquete que aún dicen «Por designar» (Word, Excel, DXF)."""
    pat = re.compile(rb"(?i)por designar")
    malos = []
    for f in raiz.rglob("*"):
        if f.suffix in (".docx", ".xlsx"):
            z = zipfile.ZipFile(f)
            if any(pat.search(z.read(n)) for n in z.namelist() if n.endswith(".xml")):
                malos.append(str(f))
        elif f.suffix == ".dxf" and pat.search(f.read_bytes()):
            malos.append(str(f))
    return malos


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--motor", type=Path, required=True, help="clon de github.com/dilmar231gabriel-ops/expediente-lp-22.9kv")
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--sin-motor", action="store_true", help="reusar la salida del motor que ya está en --salida")
    a = ap.parse_args()
    if not a.sin_motor:
        correr_motor(a.motor.resolve(), a.salida)
    copiar_resultados(a.salida)
    planos()
    raiz = empaquetar(a.salida)
    malos = verificar(raiz)
    print(f"{ZIP} ({ZIP.stat().st_size // 1024} KB)")
    if malos:
        sys.exit("Con «Por designar»: " + ", ".join(malos))


if __name__ == "__main__":
    main()
