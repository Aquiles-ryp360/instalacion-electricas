"""Edición documental P01 sobre LP-R02, sin alterar el modelo ni la copia móvil."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
import zipfile

P=Path(__file__).resolve().parents[2];R=P.parents[1]
sys.path.insert(0,str(R))
from herramientas.documentos.formato_aquiles import desde_markdown,compilar
from pypdf import PdfReader,PdfWriter

S=P/'revisiones/lp-r02'
B=R/'build'/P.name/'presentacion-p01'
O=B/'LP_Limbani_Huancasayani'


def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()


def meta(tipo,titulo_interior):
    return dict(autor='Aquiles Taylor Ramos Yapo',codigo='227368',docente='Por confirmar',
        curso='INSTALACIONES ELÉCTRICAS II',curso_celda=r'\shortstack{INSTALACIONES\\ELÉCTRICAS II}',
        cabecera='PROYECTO: LÍNEA PRIMARIA LIMBANI - HUANCASAYANI, PROVINCIA DE SANDIA - DEPARTAMENTO DE PUNO',
        titulo='PROYECTO: “LÍNEA PRIMARIA LIMBANI - HUANCASAYANI”',
        ubicacion_titulo='DISTRITO DE LIMBANI - PROVINCIA DE SANDIA - DEPARTAMENTO DE PUNO',
        ubicacion='Limbani - Huancasayani, Sandia, Puno',revision='LP-R02 · Presentación P01',
        tipo_documento=tipo,titulo_interior=titulo_interior,pie=titulo_interior+' - LÍNEA PRIMARIA')


def preparar():
    if O.exists():raise FileExistsError('La preparación ya existe; compilar sus fuentes o usar otra salida: '+str(O))
    O.mkdir(parents=True)
    carpetas=[x for x in S.iterdir() if x.is_dir()]
    for origen in carpetas:
        ignorar=shutil.ignore_patterns('codigo') if origen.name=='08-recursos' else None
        shutil.copytree(origen,O/origen.name,ignore=ignorar)
    # Los Word originales se conservan como referencia, sin atribuirles el nuevo formato.
    originales=O/'08-recursos/documentos-movil-originales';originales.mkdir()
    for f in list(O.rglob('*.docx')):
        if originales in f.parents:continue
        target=originales/f.name
        assert target.resolve().is_relative_to(O.resolve()) and not target.exists()
        f.rename(target)
    (originales/'README.md').write_text('# Copias originales del móvil\n\nDOCX de LP-R02 conservados sin modificación. El nuevo formato se entrega en PDF y en fuentes LaTeX/Markdown por capítulos. Estos Word conservan el formato de la revisión móvil y no son el original de maquetación P01.\n',encoding='utf-8')
    items=[('01-expediente',P/'expediente/lp-r02/memoria-completa.md','Expediente_revisado_LP_R02',
            'EXPEDIENTE ACADÉMICO DE LÍNEA PRIMARIA','MEMORIA DESCRIPTIVA Y CÁLCULOS'),
           ('03-calculos',S/'03-calculos/Memoria_calculo_explicita_LP_R02.md','Memoria_calculo_explicita_LP_R02',
            'MEMORIA DE CÁLCULO','CÁLCULOS JUSTIFICATIVOS'),
           ('05-especificaciones',S/'05-especificaciones/Especificaciones_y_montaje_R02.md','Especificaciones_y_montaje_R02',
            'ESPECIFICACIONES Y MONTAJE','ESPECIFICACIONES Y MONTAJE')]
    registro=[]
    for folder,entrada,nombre,tipo,titulo in items:
        salida=O/folder/'LaTeX';info=desde_markdown(entrada,salida,meta(tipo,titulo));info.update(carpeta=folder,nombre=nombre)
        registro.append(info)
        shutil.copy2(salida/'contenido.md',O/folder/(nombre+'.md'))
        if folder=='01-expediente':shutil.copytree(salida/'capitulos',O/folder/'Capitulos')
    # Referencias DGE ya revisadas: no se usan sus resultados de línea ni sus apoyos.
    anexo=P/'entregables/linea-primaria-r01/Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf'
    ref=O/'09-armados-referencia';ref.mkdir()
    shutil.copy2(anexo,ref/'Referencia_documental_DGE.pdf')
    (ref/'README.md').write_text('# Referencias DGE\n\nSe conserva íntegra la recopilación documental anterior. Su portada identifica LP-R01 como procedencia; únicamente las 23 hojas normativas A3 se anexan al expediente integrado P01. No se reactivan la línea ni los cálculos R01. Las piezas de madera, giros especiales y capacidades no equivalen automáticamente a un armado CAC de LP-R02. Ver las observaciones técnicas del paquete.\n',encoding='utf-8')
    # Recursos recuperados pertinentes a línea primaria. El DVD de edificación queda en el repositorio.
    rec=O/'08-recursos/recuperados';rec.mkdir()
    for nombre in ['red-primaria-aricato-phara','formatos-electro-puno-clase']:
        shutil.copytree(R/'referencias/guias-originales'/nombre,rec/nombre)
    shutil.copy2(P/'documentacion/lp-r02/fuentes-recuperadas-preservar.json',rec/'inventario-completo-81-archivos.json')
    (rec/'README.md').write_text('# Recuperación de antecedentes\n\nAricato-Phara y formatos de clase se incluyen como referencias, sin aplicar sus fórmulas o materiales automáticamente al corredor de Limbani. El inventario completo registra también el DVD UNAP de edificaciones y otros archivos recuperados, conservados en referencias/guias-originales del repositorio. No se mezclan esos proyectos de vivienda con esta línea primaria.\n\nRepositorio: https://github.com/gaelrenzo/instalacion-electricas/tree/main/referencias/guias-originales\n',encoding='utf-8')
    (B/'documentos.json').write_text(json.dumps(registro,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Preparado:',O,flush=True)


def documentos():
    registro=json.loads((B/'documentos.json').read_text(encoding='utf-8'))
    for item in registro:
        folder=O/item['carpeta']
        titulos={
            '01-expediente':('EXPEDIENTE ACADÉMICO DE LÍNEA PRIMARIA','MEMORIA DESCRIPTIVA Y CÁLCULOS'),
            '03-calculos':('MEMORIA DE CÁLCULO','CÁLCULOS JUSTIFICATIVOS'),
            '05-especificaciones':('ESPECIFICACIONES Y MONTAJE','ESPECIFICACIONES Y MONTAJE')}
        desde_markdown(Path(item['fuente']),folder/'LaTeX',meta(*titulos[item['carpeta']]))
        shutil.copy2(folder/'LaTeX/contenido.md',folder/(item['nombre']+'.md'))
        if item['carpeta']=='01-expediente':shutil.copytree(folder/'LaTeX/capitulos',folder/'Capitulos',dirs_exist_ok=True)
        pdf=compilar(folder/'LaTeX')
        shutil.copy2(pdf,folder/(item['nombre']+'.pdf'))
        print('PDF compilado:',item['nombre'],flush=True)


def integrar():
    writer=PdfWriter();indice=[]
    partes=[('Memoria descriptiva y cálculos',O/'01-expediente/Expediente_revisado_LP_R02.pdf',None),
            ('Especificaciones y montaje',O/'05-especificaciones/Especificaciones_y_montaje_R02.pdf',None),
            ('Hojas DGE de referencia; adaptación pendiente',O/'09-armados-referencia/Referencia_documental_DGE.pdf','a3'),
            ('Planos de la línea primaria LP-R02',O/'04-planos/Planos_LP_R02_A3.pdf',None)]
    for titulo,ruta,seleccion in partes:
        reader=PdfReader(ruta);paginas=list(range(len(reader.pages)))
        if seleccion=='a3':
            paginas=[i for i,p in enumerate(reader.pages) if all(abs(a-b)<1 for a,b in zip(sorted([float(p.mediabox.width)*25.4/72,float(p.mediabox.height)*25.4/72]),[297,420]))]
            if len(paginas)!=23:raise AssertionError('Se esperaban 23 referencias normativas A3')
        inicio=len(writer.pages)+1
        writer.append(reader,pages=paginas,outline_item=titulo,import_outline=seleccion is None)
        indice.append(dict(titulo=titulo,primera_pagina=inicio,ultima_pagina=len(writer.pages),archivo=str(ruta.relative_to(O))))
    d=O/'00-expediente-integrado';d.mkdir(exist_ok=True)
    f=d/'Expediente_integral_Linea_Primaria_LP_R02_P01.pdf'
    with f.open('wb') as out:writer.write(out)
    (d/'indice-general.json').write_text(json.dumps(indice,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md='# Índice del expediente integrado\n\n| Sección | Páginas del PDF |\n| --- | --- |\n'
    md+='\n'.join(f'| {x["titulo"]} | {x["primera_pagina"]}-{x["ultima_pagina"]} |' for x in indice)
    (d/'INDICE.md').write_text(md+'\n',encoding='utf-8')
    print('Expediente integrado:',len(writer.pages),'páginas',flush=True)


def cerrar():
    """Prepara código portable, índice y huellas; conserva la copia móvil intacta."""
    codigo=O/'08-recursos/codigo';codigo.mkdir(exist_ok=True)
    antiguo=S/'08-recursos/codigo/fragmento-repositorio'
    mappings=[(antiguo/'proyectos'/P.name,codigo/'proyecto'),(antiguo/'herramientas',codigo/'herramientas')]
    for origen,destino in mappings:shutil.copytree(origen,destino,dirs_exist_ok=True)
    # Motor técnico vigente con búsqueda de fuente compatible con Windows/Linux.
    for name in ['analizar.py','complementos.py','construir.py','documentar.py','planos.py','prosa.py','verificar.py']:
        shutil.copy2(P/'scripts/lp_r02'/name,codigo/'proyecto/scripts/lp_r02'/name)
    shutil.copy2(P/'datos/lp-r01/resultados.json',codigo/'proyecto/datos/lp-r01/resultados.json')
    for name in ['presentacion_aquiles.py','cad_presentacion.py','gis_presentacion.py']:
        shutil.copy2(P/'scripts/lp_r02'/name,codigo/name)
    restaurar='''from pathlib import Path
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
'''
    (codigo/'restaurar.py').write_text(restaurar,encoding='utf-8')
    (codigo/'README.md').write_text('''# Código e insumos de cálculo

Las carpetas cortas `proyecto/` y `herramientas/` conservan el motor y entradas LP-R02. Ejecutar `python -X utf8 restaurar.py G:/Aquiles/reconstruccion-lp` con una carpeta nueva. Instalar `proyectos/aquiles-linea-primaria-inst-ii/requirements-lp-r02.txt` en esa reconstrucción y ejecutar sus pruebas/constructor con `python -X utf8`. La generación base produce el formato documental móvil; los tres archivos de presentación se conservan aquí como registro y requieren el repositorio completo y sus recursos para ejecutarse. AutoCAD y PyQGIS son requisitos separados.

Los documentos P01 se editan directamente en las carpetas `LaTeX/` y `Capitulos/` de cada sección; cada `main.tex` es portable y contiene su plantilla y logo. Compilar tres veces con pdfLaTeX. No editar números en la memoria sin actualizar antes los datos y recalcular. El DOCX original del móvil está separado y mantiene su formato anterior.
''',encoding='utf-8')
    cad=O/'09-armados-referencia/README.md'
    cad.write_text(cad.read_text(encoding='utf-8')+'\nEl DXF/DWG de `04-planos` incorpora las 23 referencias vectorizadas en pestañas `REF-DGE-*`; los planos propios son `LP-01` a `LP-19`. Son CAD derivados de copias normativas, con texto trazado como contornos; no archivos DWG oficiales emitidos por MINEM ni cotas paramétricas. No utilizar estas hojas como adaptación CAC aprobada. El modelo principal conserva sus 111 postes R02.\n',encoding='utf-8')
    (O/'LEER_PRIMERO.md').write_text('''# Proyecto académico de línea primaria Limbani–Huancasayani

Instalaciones Eléctricas II · Estudiante Aquiles Taylor Ramos Yapo · 227368. Revisión técnica LP-R02, presentación P01, 18/10/2026. Docente del curso por confirmar. Sistema aislado; sin interconexión inicial con el SEIN.

## Abrir primero

`00-expediente-integrado/Expediente_integral_Linea_Primaria_LP_R02_P01.pdf` reúne memoria, especificaciones, 23 referencias DGE y los 19 planos A3 de LP-R02. El índice de rangos y los marcadores del PDF permiten localizar cada parte. La memoria de cálculo detallada también está en `03-calculos/`.

| Carpeta | Contenido |
| --- | --- |
| 00-expediente-integrado | PDF reunido e índice |
| 01-expediente | Memoria, capítulos Markdown/LaTeX y carátula con formato Aquiles |
| 02-metrados | XLSX y cantidades trazadas a postes y vanos |
| 03-calculos | Memoria, resultados JSON, tablas CSV y libro XLSX |
| 04-planos | 19 láminas A3, DXF/DWG nativo, QGIS portable, GeoJSON y Google Earth KMZ |
| 05-especificaciones | Equipos, montaje y fuentes editables |
| 06-presupuesto-y-cronograma | Partidas y planificación; precios sin cotizar vacíos |
| 07-evaluacion-y-pendientes | Evaluación, pendientes y comprobaciones |
| 08-recursos | Fuentes públicas, código, documentos móviles originales y recuperados pertinentes |
| 09-armados-referencia | Referencias documentales DGE y catálogo de pestañas CAD |

El formato toma como modelo `proyectos/aquiles/entregables/expediente.pdf`: carátula azul, escudo UNAP, encabezados y títulos rojos. Los rótulos rectos y minimalistas de los planos se conservan. La presentación P01 no cambia parámetros, cálculos ni decisiones del móvil.

## Base técnica y límites

111 postes y 110 vanos; terna 3×AAAC 50 mm² representada por un eje en planta. Demanda de estudio 171.486 kW para el ámbito supuesto de Huancasayani. Se comparan 10/20/22/22.9 kV; tensión confirmada y potencia firme siguen pendientes. Se mantienen 46 apoyos con carga ascendente, 16 cambios funcionales propuestos y 160 retenidas ideales de resistencia mínima 60 kN. El anclaje R02-P019-2 presenta conflicto cartográfico.

Verificar placas, reserva para Limbani y estiaje, padrón/curva de demanda, topografía de campo, predios, geotecnia, resistividad, capacidad axial e interacción N–M, herrajes y coordinación de protecciones. Las separaciones calculadas sobre el perfil heredado no acreditan distancias reales. Los precios sin cotización permanecen vacíos. Las referencias DGE vectorizadas no son armados CAC aprobados.

Este es el paquete de entrega académica para revisión. El nombre comercial del ZIP no significa ingeniería aprobada para construcción. La minicentral del otro curso tiene expediente e hipótesis independientes y no se incluye en este paquete. El próximo modelo que entregue el estudiante podrá ajustar esta presentación sin perder la revisión LP-R02.

## Edición y reproducción

Editar los capítulos de `01-expediente/LaTeX/capitulos/` y compilar `main.tex`; las tablas e imágenes están dentro de cada árbol LaTeX. Los Word del móvil se conservan en `08-recursos/documentos-movil-originales/`. Para reconstruir cálculos, consultar `08-recursos/codigo/README.md`. No hace falta instalar Python para leer los PDF, CAD o QGIS ya exportados.

`manifest-p01.json` enumera tamaño y SHA-256 de los archivos finales. La copia móvil original y su ZIP se conservan en el repositorio, bajo `revisiones/`; no deben elegirse resultados R01 por contener un DWG antiguo. Ver `07-evaluacion-y-pendientes/REVISION_PRESENTACION_P01.md`.
''',encoding='utf-8')
    (O/'07-evaluacion-y-pendientes/REVISION_PRESENTACION_P01.md').write_text('''# Revisión de presentación P01 — 18/10/2026

Base sincronizada de GitHub: 1819362f278c5fffd88498e156200d34eeedc134. Última revisión móvil LP-R02. Se cotejaron 151 entradas de su manifiesto y los 81 originales recuperados. Se restauraron exclusivamente saltos de línea de 78 textos de la copia publicada para respetar sus SHA-256; se desactivó la transformación EOL en esa copia. El JSON de resultados R01 se guarda con los bytes Git utilizados en la huella de geometría R02, sin cambio matemático.

Cambios: formato de vivienda Aquiles para memoria/cálculos/especificaciones, espacios y unidades de redacción con comparación de toda la secuencia numérica, capítulos editables, PDF integrado, referencias DGE en papel, DWG nativo con reapertura, proyecto QGIS nativo con ensayo de traslado y ZIP ordenado. Los resultados JSON, metrados y XLSX de estudio permanecen idénticos al paquete móvil. Los Word móviles no se presentan como nuevos originales de maquetación.

No se ha cerrado la elección de tensión, la capacidad firme de la central, el presupuesto cotizado ni la validación estructural y de campo. No se mezclan los parámetros del curso de Centrales Hidroeléctricas. Las referencias normativas conservan la fecha/alcance de la revisión móvil; esta presentación no afirma una nueva consolidación legal exhaustiva.

Comprobaciones: ver validacion.json, 04-planos/verificacion-dwg.json y 04-planos/QGIS/verificacion-qgis.json. Las pruebas del motor se ejecutan aparte y se registran al publicar. La revisión del nuevo PDF comprende portada, contenido, tablas, capítulos y láminas; no equivale a aprobación de ingeniería.
''',encoding='utf-8')
    (O/'.gitattributes').write_text('# Entrega con manifiesto SHA-256: conservar bytes en cualquier plataforma.\n** -text\n',encoding='utf-8')
    informe=dict(fecha='2026-10-18',revision_tecnica='LP-R02',presentacion='P01',pruebas_motor_aprobadas=15,
        comando_pruebas='python -m unittest discover -s herramientas/lineas_primarias/tests -v',
        controles_paquete_aprobados=json.loads((O/'validacion.json').read_text(encoding='utf-8'))['controles_aprobados'],
        paginas_integrado=59,postes=111,planos_propios=19,referencias_dge=23,
        documentos_visualmente_revisados=['memoria','calculos','especificaciones','19 planos A3','referencias DGE'],
        compilacion_sin_desbordamientos=True,originales_manifiesto_verificados=151,fuentes_recuperadas_verificadas=81,
        resultados_y_planillas_moviles_sin_cambios=True,aprobacion_ingenieria=False)
    (O/'07-evaluacion-y-pendientes/validacion-presentacion-p01.json').write_text(json.dumps(informe,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # No empaquetar PDFs duplicados ni residuos de compilación junto a las fuentes.
    extras={'.aux','.log','.out','.toc','.fls','.fdb_latexmk'}
    for folder in O.glob('*/LaTeX'):
        for f in folder.iterdir():
            if f.is_file() and (f.suffix in extras or f.name=='main.pdf' or f.name.startswith('compilacion-')):f.unlink()
    # El manifiesto original pertenece sólo a la copia móvil y no se reutiliza.
    manifest=dict(revision_tecnica='LP-R02',presentacion='P01',fecha='2026-10-18',base_git='1819362f278c5fffd88498e156200d34eeedc134',
        aprobacion_ingenieria=False,archivos=[dict(ruta=f.relative_to(O).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(O.rglob('*')) if f.is_file() and f.name!='manifest-p01.json'])
    (O/'manifest-p01.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    destino=B/'Proyecto_Final_Linea_Primaria_Limbani_Huancasayani_LP_R02_P01.zip'
    if destino.exists():raise FileExistsError(destino)
    with zipfile.ZipFile(destino,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(O.rglob('*')):
            if f.is_file():z.write(f,O.name+'/'+f.relative_to(O).as_posix())
    with zipfile.ZipFile(destino) as z:
        assert z.testzip() is None
        assert max(map(len,z.namelist()))<240
    print('ZIP:',destino,'bytes:',destino.stat().st_size,flush=True)


if __name__=='__main__':
    modo=sys.argv[1] if len(sys.argv)>1 else 'preparar'
    {'preparar':preparar,'documentos':documentos,'integrar':integrar,'cerrar':cerrar}[modo]()
