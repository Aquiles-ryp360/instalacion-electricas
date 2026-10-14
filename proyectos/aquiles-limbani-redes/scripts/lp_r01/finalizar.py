"""Paquete de revisión íntegro, manifiesto y ZIP sin incluir archivos históricos."""
from pathlib import Path
import shutil,json,hashlib,zipfile,subprocess,sys
P=Path(__file__).resolve().parents[2];R=P.parents[1];O=R/'output/linea-primaria-limbani-huancasayani';T=P/'entregables/linea-primaria-r01'
def main():
    subprocess.run([sys.executable,str(Path(__file__).with_name('adjuntar_armados.py'))],check=True)
    subprocess.run([sys.executable,str(Path(__file__).with_name('verificar.py'))],check=True)
    subprocess.run([sys.executable,str(Path(__file__).with_name('publicar.py'))],check=True)
    pagination=json.loads((P/'datos/lp-r01/armados-adjuntos.json').read_text(encoding='utf-8'))
    for f in [O/'verificacion-final.json',P/'documentacion/PENDIENTES_LP_R01.md',P/'documentacion/RESUMEN_CORRECCIONES_LP_R01.md',P/'README-LINEA-PRIMARIA.md']:
        shutil.copy2(f,T/f.name)
    shutil.copytree(P/'expediente/lp-r01',T/'memoria-editable',dirs_exist_ok=True)
    shutil.copytree(P/'datos/lp-r01',T/'datos',dirs_exist_ok=True)
    shutil.copy2(R/'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf',T/'Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf')
    shutil.copytree(O/'google-earth',T/'google-earth',dirs_exist_ok=True)
    (T/'.gitattributes').write_text('** -text\n',encoding='ascii')
    (T/'README-LINEA-PRIMARIA.md').write_text('# Línea primaria Limbani–Huancasayani · LP-R01\n\nEstudiante: Aquiles Taylor Ramos Yapo, 227368. Curso Instalaciones Eléctricas II.\n\n- [Expediente](Linea_Primaria_Limbani_Huancasayani_R01_expediente.pdf), [cálculos](Linea_Primaria_Limbani_Huancasayani_R01_calculos.pdf) y [19 láminas A3](Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf).\n- [DWG nativo](cad/LP_Limbani_Huancasayani_R01_Armados_Perfiles.dwg), [DXF](cad/LP_Limbani_Huancasayani_R01.dxf), [QGIS](qgis/LP-Limbani-Huancasayani.qgz).\n- [Resumen](RESUMEN_CORRECCIONES_LP_R01.md), [pendientes](PENDIENTES_LP_R01.md), [fuentes](datos/fuentes.json), [memoria editable](memoria-editable/memoria-completa.md) y [tablas](tablas).\n\nMantener juntas las capas del directorio qgis. El diseño es académico, aislado y con datos de campo pendientes. La planta usa un único eje para la terna; las funciones de los apoyos se indican por rótulos.\n',encoding='utf-8')
    (T/'LEER_PRIMERO.md').write_text('# Entrega académica LP-R01\n\nAbra los cuatro PDF: expediente integrado, memoria de cálculo, planos A3 y anexo de armados. En cad, el DWG activo es LP_Limbani_Huancasayani_R01_Armados_Perfiles.dwg; también se incluye DXF. Para QGIS abra qgis/LP-Limbani-Huancasayani.qgz conservando todos los archivos del directorio. El proyecto usa rutas relativas y se verificó con QGIS 3.44.15.\n\nPara Google Earth Pro abra google-earth/LP_Limbani_Huancasayani_R01.kmz y consulte la guía incluida. La planta representa un solo eje trifásico, 3 × AAAC 50 mm²; los detalles muestran disposición de fases. Coordenadas/topografía/equipos son de estudio y los pendientes se documentan.\n\n© OpenStreetMap contributors, ODbL 1.0, https://www.openstreetmap.org/copyright. Catastro aportado conservado; Mapzen Terrain Tiles/datos globales USGS.\n',encoding='utf-8')
    with (T/'README-LINEA-PRIMARIA.md').open('a',encoding='utf-8') as stream:
        stream.write(f'\n## Armados, perfiles y Google Earth\n\nEl expediente integrado tiene {pagination["hojas_expediente"]} páginas: {pagination["hojas_memoria"]} de memoria, {pagination["hojas_anexo"]} de anexo y {pagination["hojas_planos"]} de planos. La memoria tiene portada académica, resumen ejecutivo, índice paginado, capítulos y subtítulos numerados, y párrafos justificados. [Anexo de armados](Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf): 23 láminas A3 exportadas del DXF como vectores, sin imágenes raster, con las piezas, cotas, tablas y rótulos completos.\n\nEl DWG/DXF contiene 42 presentaciones: 19 del proyecto (incluye 7 perfiles ampliados) y 23 referencias DGE completas. La biblioteca general se publica por separado en herramientas/biblioteca_dge, con 102 láminas MT, 21 láminas BT y la 022 aprobada en 2019, y 182 símbolos de la sección 9. Los CAD de detalle son derivados de PDF normativos, no archivos emitidos por MINEM. Las piezas de madera y las variantes angulares no se adoptan automáticamente como armados CAC.\n\n[KMZ para Google Earth](google-earth/LP_Limbani_Huancasayani_R01.kmz), con fichas de 111 postes y 110 vanos, curvas de nivel cada 20 m y principales cada 100 m, relieve y recorrido 3D. Las curvas se derivan del DEM público de aproximadamente 30 m y no acreditan topografía de campo. [Guía del KMZ](google-earth/LEER_PRIMERO.md). QGIS incorpora el DEM y las curvas con rutas relativas; 13 capas verificadas.\n')
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
