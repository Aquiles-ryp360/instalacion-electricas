from pathlib import Path
import json,shutil,sys
source=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Uso: python -X utf8 restaurar.py CARPETA_NUEVA')
target=Path(sys.argv[1]).resolve()
if target.exists() and any(target.iterdir()):raise SystemExit('Elegir una carpeta nueva vacía')
shutil.copytree(source/'proyecto',target/'proyectos/aquiles-linea-primaria-inst-ii',dirs_exist_ok=True)
shutil.copytree(source/'herramientas',target/'herramientas',dirs_exist_ok=True)
resources=source.parent
for row in json.loads((resources/'fuentes.json').read_text(encoding='utf-8')):
 dest=target/row['archivo'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(resources/'pdf'/Path(row['archivo']).name,dest)
for name in ['rd024-2003-EM.pdf','rd023-2003-EM-DGE.pdf']:
 dest=target/'referencias/normativa/pdf'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(resources/'pdf'/name,dest)
print('Motor LP-R02 restaurado en',target)
