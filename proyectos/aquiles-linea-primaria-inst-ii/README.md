# Línea primaria Limbani–Huancasayani · LP-R02 / P01

Instalaciones Eléctricas II · Aquiles Taylor Ramos Yapo · 227368. Una terna principal sin ramales, con MCH aislada como hipótesis del manifiesto. La tensión y potencia reales requieren placas y verificación.

## Entrega ordenada con formato de Aquiles

- [Descargar ZIP completo](https://github.com/gaelrenzo/instalacion-electricas/releases/download/lp-r02-p01-20261018/Proyecto_Final_Linea_Primaria_Limbani_Huancasayani_LP_R02_P01.zip).
- [Expediente integrado: 59 páginas](entregables/linea-primaria-r02-presentacion/00-expediente-integrado/Expediente_integral_Linea_Primaria_LP_R02_P01.pdf).
- [Índice de carpetas y edición por capítulos](entregables/linea-primaria-r02-presentacion/LEER_PRIMERO.md).
- [Memoria de cálculo](entregables/linea-primaria-r02-presentacion/03-calculos/Memoria_calculo_explicita_LP_R02.pdf) · [Metrados](entregables/linea-primaria-r02-presentacion/02-metrados/Metrados_trazables_LP_R02.xlsx) · [Especificaciones](entregables/linea-primaria-r02-presentacion/05-especificaciones/Especificaciones_y_montaje_R02.pdf).
- [19 planos A3](entregables/linea-primaria-r02-presentacion/04-planos/Planos_LP_R02_A3.pdf) · [DWG nativo](entregables/linea-primaria-r02-presentacion/04-planos/LP_Limbani_Huancasayani_R02.dwg) · [DXF](entregables/linea-primaria-r02-presentacion/04-planos/LP_Limbani_Huancasayani_R02.dxf) · [QGIS portable](entregables/linea-primaria-r02-presentacion/04-planos/QGIS/) · [Google Earth KMZ](entregables/linea-primaria-r02-presentacion/04-planos/LP_R02.kmz).

P01 mantiene los cálculos de la última revisión móvil y adapta carátula, azul, escudo UNAP, encabezados y títulos rojos del expediente de vivienda de Aquiles. Los rótulos rectos de planos se conservan. Incluye diez secciones, capítulos Markdown/LaTeX y los Word originales del móvil separados. El ZIP completo se publica como archivo de una versión de GitHub por superar 100 MiB; las carpetas se consultan también directamente en el repositorio.

El DWG se guardó y reabrió con AutoCAD: 111 postes y 19 láminas, más 23 referencias DGE vectorizadas en pestañas separadas. Son reproducciones documentales, no DWG oficiales ni armados CAC aprobados. QGIS 3.44.15 se guardó, reabrió y trasladó con once capas válidas, rutas relativas y geometría coincidente. Se aprobaron 15 pruebas del motor y 70 controles del paquete. [Registro P01 y pendientes](documentacion/lp-r02/PRESENTACION_P01.md).

El proyecto conserva sus observaciones de ingeniería. La minicentral del otro curso no se modifica en esta entrega. Para editar los nuevos documentos, usar sus carpetas `LaTeX/` con `main.tex`, plantilla y logo. El motor del ZIP se restaura con `08-recursos/codigo/restaurar.py`; las conversiones de PC requieren AutoCAD o PyQGIS reales.

## Copia móvil conservada

Los archivos originales de LP-R02 se conservan en [ocho carpetas](revisiones/lp-r02/LEER_PRIMERO.md). La [guía de sincronización](revisiones/README.md) y el [ZIP móvil original](revisiones/Limbani_Huancasayani_LP_R02.zip) mantienen su procedencia. Los enlaces siguientes corresponden a esa copia anterior a la presentación P01.

1. [ExpedientePDF](revisiones/lp-r02/01-expediente/Expediente_revisado_LP_R02.pdf), DOCX yMarkdown.
2. [MetradosXLSX](revisiones/lp-r02/02-metrados/Metrados_trazables_LP_R02.xlsx), conreferencia a cada poste/vano.
3. [Memoria de cálculo explícita](revisiones/lp-r02/03-calculos/Memoria_calculo_explicita_LP_R02.pdf) y [libro de cálculo](revisiones/lp-r02/03-calculos/Calculos_explicitos_LP_R02.xlsx).
4. [PlanosA3](revisiones/lp-r02/04-planos/Planos_LP_R02_A3.pdf), [DXF](revisiones/lp-r02/04-planos/LP_Limbani_Huancasayani_R02.dxf), GeoJSON yKMZ.
5. [Especificaciones ymontaje](revisiones/lp-r02/05-especificaciones/Especificaciones_y_montaje_R02.pdf).
6. [Presupuesto yplanificación abiertos](revisiones/lp-r02/06-presupuesto-y-cronograma/Presupuesto_y_planificacion_R02.xlsx).
7. [Cuestionario de autoevaluación](revisiones/lp-r02/07-evaluacion-y-pendientes/Cuestionario_autoevaluacion.pdf), [evaluación](revisiones/lp-r02/07-evaluacion-y-pendientes/Evaluacion_tecnica_LP_R02.pdf) ypendientes.
8. [Fuentes y recursos](revisiones/lp-r02/08-recursos/fuentes.json):MINEM, SEACE, Electro Puno, SINIA yreferencias del repositorio.

Se comparan10/20/22/22.9 kV, conMTde salida fija yconambos transformadores, pérdidas ybalance de generación150/200 kW. Se calculan fuerzas deextremo porvano rígido, condesnivel, viento ysigno vertical. El diagnósticoidentifica46apoyos concarga ascendente,16cambiosfuncionales propuestos yunanclaje conconflicto cartográfico. Sonobservaciones de estudio; topografía real, placas, capacidadN-M, geotecnia, protecciones y predios siguenpendientes.

La salida pasó la revisión informática y se revisaron susláminas, pero noestá aprobada paraconstrucción. Losprecios sincotización yvolúmenes civiles definitivos permanecenvacíos. La presencia de undocumentoSEACE no reemplaza su evaluación técnica ni acredita las condiciones de Limbani.

[Continuidad paraotraIA](documentacion/lp-r02/CONTINUIDAD_IA.md) · [Plan de trabajo](documentacion/lp-r02/PLANEACION.md) · [Hallazgos del repositorio](documentacion/lp-r02/OBSERVACIONES_REPOSITORIO.md) · [ReferenciaR01 conservada](entregables/linea-primaria-r01/LEER_PRIMERO.md).

Las entradas, generadores y copia de revisión se versionan juntos. `build/` sigue destinado a resultados regenerables y está ignorado por Git. Para leer los PDF y editar los archivos ya exportados no hace falta reconstruir. Los originales R01 se conservan. Las [fuentes recuperadas del DVD y de Aricato–Phara](documentacion/lp-r02/FUENTES_RECUPERADAS_GITHUB.md) se incorporan sin alterar sus bytes. El [proyecto hidroeléctrico](../aquiles-central-michell-banki/README.md) mantiene suspropios parámetros.
