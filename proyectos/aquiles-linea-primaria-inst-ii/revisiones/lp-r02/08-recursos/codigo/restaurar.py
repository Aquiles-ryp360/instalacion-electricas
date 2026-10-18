from pathlib import Path
import shutil,json,sys
source=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit("Uso: python3 restaurar.py CARPETA_NUEVA")
target=Path(sys.argv[1]).resolve()
if target.exists() and any(target.iterdir()):raise SystemExit("Elegir una carpeta nueva vacía para no sobrescribir trabajo")
shutil.copytree(source/"fragmento-repositorio",target,dirs_exist_ok=True)
resources=source.parent
for row in json.loads((resources/"fuentes.json").read_text()):
 dest=target/row["archivo"];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(resources/"pdf"/Path(row["archivo"]).name,dest)
for name in ["rd024-2003-EM.pdf","rd023-2003-EM-DGE.pdf"]:
 dest=target/"referencias/normativa/pdf"/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(resources/"pdf"/name,dest)
print("Reconstruir desde",target)
