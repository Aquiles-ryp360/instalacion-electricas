"""Paquete de revisión íntegro, manifiesto y ZIP sin incluir archivos históricos."""
from pathlib import Path
import shutil,json,hashlib,zipfile,subprocess,sys
P=Path(__file__).resolve().parents[2];R=P.parents[1];O=R/'output/linea-primaria-limbani-huancasayani';T=P/'entregables/linea-primaria-r01'
def main():
    subprocess.run([sys.executable,str(Path(__file__).with_name('verificar.py'))],check=True)
    subprocess.run([sys.executable,str(Path(__file__).with_name('publicar.py'))],check=True)
    for f in [O/'verificacion-final.json',P/'documentacion/PENDIENTES_LP_R01.md',P/'documentacion/RESUMEN_CORRECCIONES_LP_R01.md',P/'README-LINEA-PRIMARIA.md']:
        shutil.copy2(f,T/f.name)
    shutil.copytree(P/'expediente/lp-r01',T/'memoria-editable',dirs_exist_ok=True)
    shutil.copytree(P/'datos/lp-r01',T/'datos',dirs_exist_ok=True)
    (T/'.gitattributes').write_text('** -text\n',encoding='ascii')
    (T/'README-LINEA-PRIMARIA.md').write_text('# Línea primaria Limbani–Huancasayani · LP-R01\n\nEstudiante: Aquiles Taylor Ramos Yapo, 227368. Curso Instalaciones Eléctricas II.\n\n- [Expediente](Linea_Primaria_Limbani_Huancasayani_R01_expediente.pdf), [cálculos](Linea_Primaria_Limbani_Huancasayani_R01_calculos.pdf) y [12 láminas A3](Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf).\n- [DWG nativo](cad/LP_Limbani_Huancasayani_R01.dwg), [DXF](cad/LP_Limbani_Huancasayani_R01.dxf), [QGIS](qgis/LP-Limbani-Huancasayani.qgz).\n- [Resumen](RESUMEN_CORRECCIONES_LP_R01.md), [pendientes](PENDIENTES_LP_R01.md), [fuentes](datos/fuentes.json), [memoria editable](memoria-editable/memoria-completa.md) y [tablas](tablas).\n\nMantener juntas las capas del directorio qgis. El diseño es académico, aislado y con datos de campo pendientes. La planta usa un único eje para la terna; las funciones de los apoyos se indican por rótulos.\n',encoding='utf-8')
    (T/'LEER_PRIMERO.md').write_text('# Entrega académica LP-R01\n\nAbra los tresPDF para expediente, cálculos y planos. El CAD se encuentra en cad(DWG nativo yDXF). ParaQGIS abra qgis/LP-Limbani-Huancasayani.qgz conservando todos los archivos del directorio. El proyecto usa rutas relativas y se verificó conQGIS3.44.15.\n\nLa planta representa un solo eje trifásico,3×AAAC50mm²; los detalles muestran disposición de fases. Coordenadas/topografía/equipos son de estudio y los pendientes se documentan.\n\n© OpenStreetMap contributors, ODbL1.0, https://www.openstreetmap.org/copyright. Catastro aportado conservado; Mapzen Terrain Tiles/datosglobalesUSGS.\n',encoding='utf-8')
    files=sorted(f for f in T.rglob('*') if f.is_file() and f.name!='manifest-entrega.json')
    manifest=dict(revision='LP-R01',estado='Entrega académica revisada, con pendientes de campo',archivos=[dict(ruta=f.relative_to(T).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files])
    (T/'manifest-entrega.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    zipfile_path=P/'entregables/Paquete_LP_Limbani_Huancasayani_R01.zip'
    with zipfile.ZipFile(zipfile_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for f in sorted(T.rglob('*')):
            if f.is_file():archive.write(f,'Linea_Primaria_Limbani_Huancasayani_R01/'+f.relative_to(T).as_posix())
    with zipfile.ZipFile(zipfile_path) as archive:assert archive.testzip() is None
    print('ZIP íntegro',zipfile_path,zipfile_path.stat().st_size,'bytes; archivos',len(manifest['archivos']))
if __name__=='__main__':main()
