# Línea primaria Limbani–Huancasayani

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
