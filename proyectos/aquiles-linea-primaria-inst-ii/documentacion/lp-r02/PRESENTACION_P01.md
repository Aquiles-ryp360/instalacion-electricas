# Presentación P01 de la línea primaria — 18/10/2026

Se sincronizó `origin/main` en 1819362f278c5fffd88498e156200d34eeedc134 antes de continuar la revisión móvil LP-R02. La presentación se desarrolla únicamente para Instalaciones Eléctricas II; el proyecto Michell-Banki queda fuera de esta entrega.

## Entrega y cambios

La carpeta compartida es `entregables/linea-primaria-r02-presentacion/`, con diez secciones, capítulos Markdown/LaTeX, XLSX, CSV, fuentes y planos. El PDF integrado tiene 59 páginas. El formato adapta la vivienda Aquiles de `proyectos/aquiles/entregables/expediente.pdf`: carátula, azul RGB 91/155/213, rojo RGB 220/0/0, Helvetica y encabezados. No copia su docente ni sus parámetros. Los rótulos CAD propios se conservan.

DWG nativo R2018 AC1032, generado y reabierto con AutoCAD 2027: 111 postes, tipos coincidentes, diferencia XY máxima 1.87×10⁻⁹ m y auditoría sin errores. Se mantienen los 19 planos LP-R02 y se añaden 23 referencias DGE en pestañas `REF-DGE-*`, con comparación de contornos tras la conversión. Son reproducciones vectorizadas documentales, no armados CAC aprobados.

QGIS 3.44.15: eje, postes, vanos, retenidas ideales y T1/T2 obtenidos de LP-R02. Catastro original sin alterar, curvas heredadas y DEM público de gabinete. Longitud horizontal 6696.368693 m. Proyecto nativo guardado, reabierto y trasladado con once capas válidas y cero rutas externas. CRS EPSG:32719. La geometría y los tipos de los 111 postes coinciden con los cálculos; no se reutilizan los apoyos de diseño R01.

## Conservación y validación

151 entradas del manifiesto móvil y 81 fuentes recuperadas cotejadas. Se repararon únicamente EOL de 78 textos de la copia congelada para recuperar las huellas del ZIP publicado; `.gitattributes` evita otra transformación de Windows. El JSON R01 asociado a la huella de geometría se conserva con los bytes Git usados por el cálculo, sin cambio de valores. Las fuentes normativas y los archivos recuperados conservan sus blobs originales.

Los resultados, CSV y XLSX técnicos son idénticos a LP-R02 móvil. Los espacios/unidades de redacción se ajustan sin alterar la secuencia numérica. Los DOCX originales móviles quedan separados; el formato P01 se edita en LaTeX/Markdown.

15 pruebas unitarias del motor aprobadas; 70 controles del paquete aprobados. Revisión visual de los tres documentos maquetados, los 19 planos y las referencias adjuntas. La compilación rechaza desbordamientos y caracteres ausentes. Los informes CAD, QGIS y `validacion-presentacion-p01.json` se incluyen en la entrega.

El ZIP completo, de aproximadamente 129 MB, supera el límite de archivos individuales del árbol GitHub y se distribuye como adjunto de la versión `lp-r02-p01-20261018`. Las carpetas del proyecto se versionan normalmente; no se retiran fuentes para reducir artificialmente el paquete. Cada archivo tiene tamaño y SHA-256 en `manifest-p01.json`.

## Pendientes conservados

Tensión confirmada y potencia firme siguen sin cerrar; se comparan 10/20/22/22.9 kV. Mantener 46 apoyos con carga ascendente, 16 cambios funcionales propuestos, 160 retenidas ideales de mínimo 60 kN y el conflicto de R02-P019-2. Topografía, predios, axial/interacción N–M, geotecnia, resistividad, herrajes y protecciones necesitan datos reales. Precios no cotizados vacíos. El nombre del ZIP de entrega no supone aprobación constructiva.

El siguiente modelo que aporte el estudiante podrá modificar la presentación. Las referencias normativas conservan la fecha y el alcance de LP-R02; no se afirma una nueva auditoría normativa completa por haber cambiado el formato.
