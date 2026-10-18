"""Construcción portableLP-R02; rechaza sobrescritura y conserva fuentes originales."""
from pathlib import Path
import sys,argparse,json,hashlib,zipfile,subprocess
P=Path(__file__).resolve().parents[2];ROOT=P.parents[1]
from analizar import calcular
from documentar import documentar
from planos import planos
from complementos import completar,guardar_codigo
from verificar import verificar
CARPETAS=['01-expediente','02-metrados','03-calculos','04-planos','05-especificaciones','06-presupuesto-y-cronograma','07-evaluacion-y-pendientes','08-recursos']

def empaquetar(O):
    manifest=dict(revision='LP-R02',estado='REVISION ACADEMICA CON DATOS REQUERIDOS',aprobacion_ingenieria=False,
                  entradas=[dict(ruta=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in [P/'datos/lp-r02/parametros.json',P/'datos/lp-r02/geometria-base.json',P/'datos/lp-r01/casas-originales.geojson',P/'datos/lp-r01/referencias-osm.geojson',P/'datos/lp-r01/curvas-dem.geojson']],archivos=[])
    for f in sorted(O.rglob('*')):
        if f.is_file() and f.name!='manifest.json':manifest['archivos'].append(dict(ruta=str(f.relative_to(O)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    (O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    dest=O.with_name(O.name+'.zip')
    if dest.exists():raise FileExistsError('Paquete yaexiste: '+str(dest))
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(O.rglob('*')):
            if f.is_file():z.write(f,Path(O.name)/f.relative_to(O))
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise ValueError('ZIPcorrupto')
    return dest

def main():
    a=argparse.ArgumentParser();a.add_argument('--salida',type=Path,default=ROOT/'build'/P.name/'lp-r02');args=a.parse_args();O=args.salida.resolve()
    if O.exists():raise FileExistsError('La salida existe; crear unanueva revisión: '+str(O))
    for name in CARPETAS:(O/name).mkdir(parents=True,exist_ok=True)
    r,met,civil=calcular(P,O);completar(P,O,r);documentar(P,O,r,met,civil);print('Memorias yXLSXgenerados',flush=True)
    planos(P,O,r);print('CAD yPDFdelmismomodelo generados',flush=True)
    guardar_codigo(P,O);res=verificar(O);dest=empaquetar(O);print(json.dumps(dict(salida=str(O),zip=str(dest),controles=res['controles_aprobados'],ingenieria_aprobada=False),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
