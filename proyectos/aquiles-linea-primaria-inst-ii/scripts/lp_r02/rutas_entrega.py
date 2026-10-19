"""Equivalencia entre la entrega base y las ocho carpetas de M01."""
from pathlib import Path
import shutil

P=Path(__file__).resolve().parents[2]
CARPETAS={'01_Calculos':'02_Calculos','02_Metrados':'03_Metrados',
          '03_Planos':'04_Planos','04_Cartografia':'05_Cartografia','05_Presupuesto':'06_Presupuesto'}


def ruta_activa(relativo):
    rel=Path(relativo);raiz=P/'entregables/proyecto-final'
    if (raiz/'00_Expediente/Expediente.pdf').is_file():
        if str(rel)=='Expediente.pdf':return raiz/'00_Expediente'/rel
        if rel.parts[0] in CARPETAS:return raiz/CARPETAS[rel.parts[0]]/Path(*rel.parts[1:])
    return raiz/rel


def copiar_base(destino):
    destino.mkdir(parents=True)
    for antigua in CARPETAS:
        shutil.copytree(ruta_activa(antigua),destino/antigua)
    shutil.copy2(ruta_activa('Expediente.pdf'),destino/'Expediente.pdf')
    shutil.copy2(ruta_activa('LEEME.txt'),destino/'LEEME.txt')
    # Los dos archivos UB-01 se regeneran; no forman parte de las 19 láminas base.
    for f in (destino/'03_Planos').glob('Plano_Ubicacion.*'):f.unlink()
