# Comparación y selección de la recuperación

Estado de comparación: main en 3619a7f06e64488628182d915e9d85e87d1515a5.
Todos los paquetes se descargaron y comprobaron contra el SHA Git de origen.
Los ZIP se abrieron y sus miembros se leyeron comprobando CRC; el RAR se
descomprimió mediante libarchive. Cada miembro recibió SHA-256 y SHA Git,
y se buscó coincidencia entre los 1 752 archivos actuales y los miembros de los
tres paquetes actuales examinados.

## Paquetes históricos

| Paquete | Miembros | Coincidencias exactas como archivo actual | Decisión |
| --- | ---: | ---: | --- |
| [Planos_Electricos_Editables_DXF_JSON.zip](https://github.com/gaelrenzo/instalacion-electricas/blob/edd56eb19091fcf32e4b443c452515e946623a17/IMPRIMIR%20YA/Planos_Electricos_Editables_DXF_JSON.zip) | 7 | 0 | Siete salidas/generador de una vivienda antigua. No se reintroducen sus cálculos ni los planos anteriores. |
| [Planos_Editables_AutoCAD.zip](https://github.com/gaelrenzo/instalacion-electricas/blob/edd56eb19091fcf32e4b443c452515e946623a17/proyecto_vivienda_unifamiliar_por_RENZO/3_de_Junio/Editables/Planos_Editables_AutoCAD.zip) | 8 | 1 | Se recupera AVANCE_DEL_PLANO_ELECTRICO1.dwg. CAPACHICA.dwg ya existe idéntico; los seis DXF son entregas anteriores sin necesidad confirmada de volver. |
| [Proyecto_LaTeX_Overleaf.zip](https://github.com/gaelrenzo/instalacion-electricas/blob/edd56eb19091fcf32e4b443c452515e946623a17/proyecto_vivienda_unifamiliar_por_RENZO/3_de_Junio/Overleaf/Proyecto_LaTeX_Overleaf.zip) | 35 | 3 | El proyecto actual mantiene los capítulos y el mecanismo de portada. Se conserva el paquete antiguo como enlace; tres recursos ya existen idénticos. |
| [Paquete_Planos_CAD_Nave_Industrial.zip](https://github.com/gaelrenzo/instalacion-electricas/blob/d9e6a646592e468bf8ed45407a79f1494e66dfdf/proyectos/nave-industrial/planos/Paquete_Planos_CAD_Nave_Industrial.zip) | 51 | 0 | Mezcla modelos industriales con salidas residenciales y rutas de Android. No se restaura este paquete de resultados como una plantilla coherente. |
| [136252v10379207_planocatastraldejuliaca.zip](https://github.com/gaelrenzo/instalacion-electricas/blob/edd56eb19091fcf32e4b443c452515e946623a17/avance-capitulos-1-2/Catastro-Juliaca/136252v10379207_planocatastraldejuliaca.zip) | 1 | 0 | Un único DWG catastral de Juliaca, base de consulta independiente. |
| [simulacion dialux.rar](https://github.com/gaelrenzo/instalacion-electricas/blob/edd56eb19091fcf32e4b443c452515e946623a17/materiales/INSTALACIONES%20ELECTRICAS%20DVD%2028.02-23/Anexo/simulacion%20dialux.rar) | 5 | 0 | Cuatro proyectos DIALux originales ausentes; RAR íntegro, incluido su respaldo interno. |

No se encontró coincidencia exacta entre miembros históricos y miembros de los
tres paquetes actuales. La ausencia de coincidencia no justifica por sí sola
recuperar una entrega antigua: se revisó también su función y utilidad.

## Comparaciones de contenido

- Se inspeccionaron 24 libros modernos de Excel, incluyendo seis fuentes históricas:
  nombres/estados de hojas, celdas, fórmulas, vínculos externos y errores almacenados.
  Ninguno de los seis históricos tuvo una firma semántica idéntica entre los
  comparadores actuales seleccionados.
- Los metrados Rev1 y Rev2 difieren en fórmulas, hojas y otros componentes:
  125 808 y 125 744 celdas de fórmula, respectivamente. Se conservan ambos como
  fuentes históricas con dependencias pendientes.
- Se leyeron 47 DXF de paquetes y comparadores. La comparación del espacio modelo
  excluyó identificadores internos; no demuestra equivalencia completa de bloques
  o referencias externas. No se descartó ningún DWG por esta comparación.
- Se abrieron 57 PDF sin errores de lectura y se revisó visualmente una muestra
  para reconocer su función como guía.
- Se leyeron los dos DOCX del DVD: proyecto modelo de servicios administrativos de
  la UNAP, preservado intacto.
- Se comparó LaTeX del ZIP Overleaf con la fuente actual de Renzo: los nueve
  capítulos originales tienen correspondencia en el proyecto actual, que conserva
  el mecanismo de portada y amplía secciones.
- Se revisaron visualmente las 14 fotografías. Se seleccionaron 12 de formatos
  y revisión, descartando dos tomas parcialmente redundantes.

## Conservación y pendientes

Se recuperan 69 originales: 14 del DVD, 41 del proyecto guía, 12 fotos,
un ZIP catastral y un DWG original. Sus SHA Git son idénticos a los de origen.
Los documentos originales no se corrigen ni se convierten durante la restauración.

Se enlazan las referencias ya presentes y las variantes cuya utilidad no se
confirmó. Los datos, cálculos, programas y entregables actuales permanecen sin
cambios. El único archivo anterior editado es referencias/README.md, al que se
añade un enlace de navegación.
