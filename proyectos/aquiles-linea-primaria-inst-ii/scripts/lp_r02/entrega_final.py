"""Entrega de presentación: un expediente y archivos de cálculo/gráficos limpios."""
from pathlib import Path
import hashlib,json,math,re,shutil,subprocess,sys,zipfile
import openpyxl,pymupdf,yaml

P=Path(__file__).resolve().parents[2];ROOT=P.parents[1]
B=ROOT/'build'/P.name/'presentacion-final';O=B/'Proyecto_Linea_Primaria'
S=P/'entregables/linea-primaria-r02-presentacion'
ZIPNAME='Proyecto_Linea_Primaria_Limbani_Huancasayani.zip'


def cartografia():
    out=O/'04_Cartografia';q=out/'QGIS';q.mkdir(parents=True,exist_ok=True)
    for name in ['Catastro-original.gpkg','LP-R02.gpkg','DEM-gabinete-30m.tif']:
        shutil.copy2(S/'04-planos/QGIS'/name,q/name)
    shutil.copy2(S/'04-planos/QGIS/Linea_Primaria_LP_R02.qgz',q/'Linea_Primaria.qgz')
    shutil.copy2(S/'04-planos/QGIS/vista-general.png',out/'Vista_General.png')
    shutil.copy2(S/'04-planos/LP_R02.kmz',out/'Linea_Primaria.kmz')
    (O/'LEEME.txt').write_text('''LÍNEA PRIMARIA LIMBANI - HUANCASAYANI
Instalaciones Eléctricas II
Estudiante: Aquiles Taylor Ramos Yapo - 227368

DOCUMENTO PRINCIPAL: Expediente.pdf
Reúne memoria, ecuaciones, metrados desarrollados, presupuesto y planos.

01_Calculos: libro con fórmulas y resumen de una página.
02_Metrados: conteo de postes/armados, conductor y resumen de una página.
03_Planos: CAD editable DXF/DWG, con láminas LP y referencias DGE.
04_Cartografia: QGIS portable, Google Earth y vista general del corredor.
05_Presupuesto: cantidades, precios referenciales y resumen de una página.

Los planos y armados en PDF están incorporados en Expediente.pdf.
''',encoding='utf-8')
    print('Cartografía y guía de entrega preparadas',flush=True)


def verificar():
    r=json.loads((P/'revisiones/lp-r02/03-calculos/resultados.json').read_text(encoding='utf-8'))
    report=dict(fecha='2026-10-19',revision_tecnica='LP-R02',entrega='presentacion consolidada',aprobacion_ingenieria=False,libros={})
    def cerca(a,b,tol=1e-6):assert isinstance(a,(int,float)) and abs(a-b)<tol,(a,b)
    for name,folder in [('Calculos','01_Calculos'),('Metrados','02_Metrados'),('Presupuesto','05_Presupuesto')]:
        f=O/folder/(name+'.xlsx');a=openpyxl.load_workbook(f,data_only=False,read_only=True);v=openpyxl.load_workbook(f,data_only=True,read_only=True)
        formulas=0;errors=[]
        for s in a:
            for row in s:
                for x in row:
                    if x.data_type=='f':
                        formulas+=1;assert '[' not in x.value,'Referencia externa no permitida: '+x.value
        for s in v:
            for row in s:
                errors.extend((s.title,x.coordinate,x.value) for x in row if x.data_type=='e')
        assert not errors,errors
        if name in ['Metrados','Presupuesto']:
            s=v['Resumen'];cerca(s['E10'].value,111);cerca(s['E17'].value,111);cerca(s['E19'].value,160);cerca(s['E27'].value,21873)
            for row,expected in [(7,72),(8,30),(9,9),(12,30),(13,41),(14,22),(15,16),(16,2)]:cerca(s[f'E{row}'].value,expected)
        if name=='Calculos':
            f0=next(x for x in r['comparacion_tensiones'] if x['kV']==10 and x['toma_pu']==1.05)
            cerca(v['Resumen']['D8'].value,r['demanda_kW']);cerca(v['Resumen']['D16'].value,f0['BT_llegada_V']);cerca(v['Resumen']['D18'].value,f0['P_generacion_kW']);cerca(v['Resumen']['D19'].value,f0['S_generador_kVA'])
            for i,x in enumerate(r['vanos']):cerca(v['Vanos'][f'M{i+7}'].value,x['estados']['EDS']['longitud_cable_m'])
            rows=list(v['Estados'].iter_rows(min_row=7,max_row=666,values_only=True));original=[x for vano in r['vanos'] for x in vano['estados'].values()]
            for row,x in zip(rows,original):
                assert row[0]==x['vano'] and row[1]==x['estado'];cerca(row[14],x['longitud_cable_m']);cerca(row[15],x['T_izq_N']);cerca(row[16],x['T_der_N'])
        if name=='Presupuesto':
            s=v['Presupuesto']
            for row in range(7,21):cerca(s[f'F{row}'].value,round(s[f'D{row}'].value*s[f'E{row}'].value+1e-8,2))
            cerca(s['F28'].value,sum(s[f'F{row}'].value for row in [22,24,25,26]),1e-5)
            report['presupuesto_referencial_pen']=s['F28'].value
        report['libros'][name]=dict(hojas=a.sheetnames,formulas=formulas,errores=errors,recalculado_con_excel=True)
        a.close();v.close()
    doc=pymupdf.open(O/'Expediente.pdf');alltext='\n'.join(p.get_text() for p in doc)
    assert not re.search(r'\b(cuestionario|pendientes?|plantilla|por completar)\b',alltext,re.I)
    assert len(doc)>50 and 'METRADOS DESARROLLADOS' in alltext and 'CÁLCULOS ELÉCTRICOS' in alltext
    report['paginas_expediente']=len(doc);report['expedientes_principales']=1;report['resumenes_pdf']=[]
    for folder,name in [('01_Calculos','Resumen_Calculos'),('02_Metrados','Resumen_Metrados'),('05_Presupuesto','Resumen_Presupuesto')]:
        d=pymupdf.open(O/folder/(name+'.pdf'));assert len(d)==1
        assert 'Ã' not in d[0].get_text();report['resumenes_pdf'].append(name)
    report['cad']=json.loads((B/'verificacion-cad.json').read_text(encoding='utf-8'))
    report['qgis']=json.loads((B/'verificacion-qgis-final.json').read_text(encoding='utf-8'))
    report['ensayos_dinamicos_excel']=json.loads((B/'verificacion-excel-nativo.json').read_text(encoding='utf-8'))
    assert report['cad']['postes']==111 and report['cad']['dwg_nativo']
    report['geometria_datos']=dict(postes=111,vanos=110,longitud_horizontal_m=r['longitud_horizontal_m'],suministro_conductor_m=21873)
    (B/'validacion-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['libros','ensayos_dinamicos_excel']},ensure_ascii=False,indent=2),flush=True)
    return report


def empaquetar():
    report=verificar();files=archivos();zipfile_path=B/ZIPNAME
    assert len([x for x in files if x.suffix=='.pdf'])==4
    assert sum(x.name.lower()=='expediente.pdf' for x in files)==1
    with zipfile.ZipFile(zipfile_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:z.write(f,'Proyecto_Linea_Primaria/'+f.relative_to(O).as_posix())
    with zipfile.ZipFile(zipfile_path) as z:
        assert z.testzip() is None
        assert not any(re.search(r'(cuestionario|pendiente|plantilla|p01|r01|r02|inspect|codigo|recursos)',x,re.I) for x in z.namelist())
    report['zip']=dict(nombre=ZIPNAME,bytes=zipfile_path.stat().st_size,sha256=sha(zipfile_path),archivos=len(files))
    report['archivos_entrega']=[dict(ruta=f.relative_to(O).as_posix(),sha256=sha(f),bytes=f.stat().st_size) for f in files]
    (B/'validacion-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('ZIP limpio:',zipfile_path,zipfile_path.stat().st_size,'bytes;',len(files),'archivos',flush=True)


def archivos():
    valid={'.pdf','.xlsx','.dxf','.dwg','.kmz','.qgz','.gpkg','.tif','.png','.txt'}
    return sorted(f for f in O.rglob('*') if f.is_file() and f.suffix.lower() in valid and not f.name.startswith('~'))


def publicar():
    report=json.loads((B/'validacion-final.json').read_text(encoding='utf-8'));target=P/'entregables/proyecto-final'
    if target.exists():raise FileExistsError('Conservar la entrega anterior antes de publicar otra: '+str(target))
    for f in archivos():
        out=target/f.relative_to(O);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,out)
    (target/'.gitattributes').write_text('# Entrega revisada: conservar bytes de los archivos.\n** -text\n',encoding='utf-8')
    shutil.copy2(B/ZIPNAME,P/'entregables'/ZIPNAME)
    local=Path('G:/Aquiles')/ZIPNAME
    if local.exists():raise FileExistsError(local)
    shutil.copy2(B/ZIPNAME,local)
    fuentes=P/'expediente/final'
    if fuentes.exists():raise FileExistsError(fuentes)
    shutil.copytree(TEX(),fuentes,ignore=shutil.ignore_patterns('*.aux','*.log','*.out','*.toc','main.pdf','compilacion-*.txt'))
    (P/'documentacion/lp-r02/VALIDACION_ENTREGA_FINAL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pdfout=ROOT/'output/pdf';pdfout.mkdir(exist_ok=True)
    for f in archivos():
        if f.suffix=='.pdf':shutil.copy2(f,pdfout/f.name)
    registrar_navegacion(report)
    print('Entrega publicada localmente:',target,'ZIP:',local,flush=True)


def registrar_navegacion(report):
    manifest=yaml.safe_load((P/'proyecto.yaml').read_text(encoding='utf-8'))
    manifest.update(estado='Proyecto académico de diseño; entrega consolidada para presentación',
        documentos='expediente/final',paquete_revision='entregables/proyecto-final',paquete_revision_movil='revisiones/lp-r02',
        paquete_zip='entregables/'+ZIPNAME,paquete_zip_movil='revisiones/Limbani_Huancasayani_LP_R02.zip',guia_pc='README.md',
        cad_dxf_activo='entregables/proyecto-final/03_Planos/Linea_Primaria.dxf',cad_dwg_activo='entregables/proyecto-final/03_Planos/Linea_Primaria.dwg',
        google_earth='entregables/proyecto-final/04_Cartografia/Linea_Primaria.kmz')
    manifest['presentacion']=dict(estado='Entrega consolidada',fecha='2026-10-19',base_tecnica='LP-R02',
        carpeta='entregables/proyecto-final',expediente='entregables/proyecto-final/Expediente.pdf',paginas=report['paginas_expediente'],
        capitulos_editables='expediente/final/capitulos',qgis='entregables/proyecto-final/04_Cartografia/QGIS/Linea_Primaria.qgz',
        verificacion='documentacion/lp-r02/VALIDACION_ENTREGA_FINAL.json',aprobacion_ingenieria=False)
    manifest['presentacion_anterior_conservada']='entregables/linea-primaria-r02-presentacion'
    (P/'proyecto.yaml').write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding='utf-8')
    (P/'README.md').write_text('''# Línea primaria Limbani–Huancasayani

**Instalaciones Eléctricas II · Estudiante Aquiles Taylor Ramos Yapo · 227368.**

## Entrega para presentación

- [Descargar el proyecto completo en ZIP](entregables/Proyecto_Linea_Primaria_Limbani_Huancasayani.zip).
- [Abrir el único expediente principal](entregables/proyecto-final/Expediente.pdf): 72 páginas con memoria, ecuaciones LaTeX, metrados desarrollados, presupuesto, 19 planos y 23 referencias DGE.
- [Ver las carpetas de la entrega](entregables/proyecto-final/).

| Carpeta | Contenido |
| --- | --- |
| [01_Calculos](entregables/proyecto-final/01_Calculos/) | Libro Excel con demanda, balance radial, cortocircuito, mecánica y estados; resumen PDF de una página. |
| [02_Metrados](entregables/proyecto-final/02_Metrados/) | Conteo por altura/función, catenaria de 110 vanos, ramales, puentes y reserva; Excel con fórmulas y resumen PDF. |
| [03_Planos](entregables/proyecto-final/03_Planos/) | DXF y DWG nativo; sus láminas PDF están incorporadas en el expediente principal. |
| [04_Cartografia](entregables/proyecto-final/04_Cartografia/) | QGIS portable, GeoPackage, DEM, Google Earth y vista del corredor. |
| [05_Presupuesto](entregables/proyecto-final/05_Presupuesto/) | Cantidades vinculadas al metrado, precios referenciales y costos calculados; resumen PDF. |

El ZIP contiene 16 archivos. El documento principal se llama **Expediente.pdf**. Los otros tres PDF son resúmenes de una página en las carpetas de cálculo, metrados y presupuesto; no son expedientes alternativos. La entrega excluye cuestionarios, listas de trabajo, plantillas, código, fuentes de otros proyectos y copias anteriores.

Los libros contienen fórmulas editables y valores recalculados con Microsoft Excel. Se verificó que los cambios de altura/función actualizan los conteos, retenidas y conductor; el factor de potencia actualiza el balance; y los precios actualizan el presupuesto. El metrado mantiene 111 postes, 110 vanos, 160 ramales y 21 873 m de conductor de suministro. La memoria incluye las planillas por vano y por apoyo.

## Bases del diseño

Sistema aislado, desde T1 en Limbani hasta T2 en Huancasayani, sin redes secundarias. Caso de cálculo de 10 kV, con comparación 20/22/22.9 kV. Demanda académica 171.486 kW. La geometría es de gabinete y los equipos se modelan con datos tipo; las condiciones de interpretación están explicadas dentro del expediente. El presupuesto es una estimación académica, sin cotizaciones comerciales. Los parámetros del curso de Centrales Hidroeléctricas se mantienen independientes.

## Fuentes editables y trazabilidad

La memoria LaTeX está en [expediente/final](expediente/final/), fuera del ZIP de presentación. El [registro de revisión](documentacion/lp-r02/PRESENTACION_FINAL.md) y la [verificación](documentacion/lp-r02/VALIDACION_ENTREGA_FINAL.json) documentan cálculos, recálculo nativo, CAD y QGIS. Los archivos móviles originales y la presentación anterior se conservan en el historial; no forman parte del ZIP actual. La base de cálculo sigue siendo LP-R02 según [proyecto.yaml](proyecto.yaml).

Para recalcular el motor se conserva `scripts/lp_r02/construir.py`; para esta presentación se utilizan `excel_final.mjs`, `excel_recalcular.ps1`, `planos_final.py`, `expediente_final.py`, `gis_final.py` y `entrega_final.py`. Los cálculos y originales previos no se sobrescriben.
''',encoding='utf-8')
    (P/'entregables/README.md').write_text('''# Entrega de línea primaria

La entrega vigente para presentación está en [proyecto-final](proyecto-final/). Su documento principal es [Expediente.pdf](proyecto-final/Expediente.pdf) y el [ZIP completo](Proyecto_Linea_Primaria_Limbani_Huancasayani.zip) reúne los 16 archivos.

Las carpetas `linea-primaria-r01` y `linea-primaria-r02-presentacion` conservan entregas anteriores. No forman parte del ZIP vigente.
''',encoding='utf-8')
    (P/'documentacion/lp-r02/PRESENTACION_FINAL.md').write_text('''# Consolidación de entrega — 19/10/2026

Base sincronizada: 6dbfd3aaed6c224049870aebe11f2e1ec9898455. Proyecto exclusivo de línea primaria, Instalaciones Eléctricas II. La minicentral del otro curso no se modifica.

## Cambios

Un único Expediente.pdf, 72 páginas: 30 de memoria, cálculos, metrados, presupuesto e índice; 19 láminas de línea; 23 hojas DGE documentales. Las ecuaciones se compusieron en LaTeX con fracciones, índices, integrales y numeración, sustituyendo el texto plano de la presentación anterior. Se desarrollan la demanda, impedancias, barrido radial, cortocircuito, catenaria, cambio de estado, flexión tipo y retenidas.

El capítulo de metrados incluye los 110 vanos y 111 apoyos, los conteos por altura y función y el desarrollo de terna, puentes y reserva. Los libros de cálculo son tres archivos con fórmulas: Calculos.xlsx (10 216), Metrados.xlsx (1672) y Presupuesto.xlsx (1705). Se recalcularon en Microsoft Excel y se exportaron sus tres resúmenes de una página. Los ensayos de cambio de altura, función, factor de potencia y precio actualizaron sus dependencias sin guardar las modificaciones de ensayo. Las 660 combinaciones de vano/estado y las 110 longitudes EDS se contrastaron con el modelo.

El presupuesto se completa como estimación académica usando los precios del parámetro costos del proyecto, no como cotizaciones. Los postes 15/17 m se escalan por longitud respecto al de 13 m. Los precios y partidas se redondean a céntimos antes de sumar. Montaje/cimentación tipo se incluyen en los conjuntos instalados, sin sumar volúmenes geotécnicos inexistentes. El costo referencial es S/ 2 559 924.11; esa precisión corresponde a la conciliación aritmética, no a exactitud comercial.

Las notas de CAD se redactaron como condiciones técnicas, conservando geometría, cargas ascendentes y el conflicto R02-P019-2. Se verificó el DWG nativo por reapertura y comparación de contornos y postes. QGIS se reabrió tras traslado, con once capas válidas, rutas relativas y 111 posiciones coincidentes. El GeoPackage adopta el nombre estable Linea_Primaria.gpkg.

## Empaquetado

El ZIP tiene 16 archivos: un expediente, tres libros y sus tres resúmenes, dos CAD, cartografía nativa y una guía breve. No contiene cuestionarios, pendientes de trabajo, plantillas, código, PDFs anteriores ni recursos de otros proyectos. Las fuentes y observaciones técnicas se conservan en el repositorio. El diseño sigue siendo académico, con geometría de gabinete y datos tipo; se mantienen en la memoria las condiciones que limitan la interpretación estructural y de equipos.

Evidencia detallada, fórmulas, huellas de archivos, resultados CAD y QGIS: VALIDACION_ENTREGA_FINAL.json. Los originales LP-R02 móvil y P01 se conservan; la entrega activa es entregables/proyecto-final.
''',encoding='utf-8')


def TEX():return B/'latex'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()


if __name__=='__main__':
    {'cartografia':cartografia,'verificar':verificar,'empaquetar':empaquetar,'publicar':publicar}[sys.argv[1]]()
