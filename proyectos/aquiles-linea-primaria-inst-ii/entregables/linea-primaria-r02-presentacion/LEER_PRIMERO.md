# Proyecto académico de línea primaria Limbani–Huancasayani

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
