# Línea primaria Limbani–Huancasayani · LP-R01

Estudiante: Aquiles Taylor Ramos Yapo, 227368. Curso Instalaciones Eléctricas II.

- [Expediente](Linea_Primaria_Limbani_Huancasayani_R01_expediente.pdf), [cálculos](Linea_Primaria_Limbani_Huancasayani_R01_calculos.pdf) y [19 láminas A3](Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf).
- [DWG nativo](cad/LP_Limbani_Huancasayani_R01_Armados_Perfiles.dwg), [DXF](cad/LP_Limbani_Huancasayani_R01.dxf), [QGIS](qgis/LP-Limbani-Huancasayani.qgz).
- [Resumen](RESUMEN_CORRECCIONES_LP_R01.md), [pendientes](PENDIENTES_LP_R01.md), [fuentes](datos/fuentes.json), [memoria editable](memoria-editable/memoria-completa.md) y [tablas](tablas).

Mantener juntas las capas del directorio qgis. El diseño es académico, aislado y con datos de campo pendientes. La planta usa un único eje para la terna; las funciones de los apoyos se indican por rótulos.

## Armados, perfiles y Google Earth

El expediente integrado tiene 69 páginas: 23 de memoria, 27 de anexo y 19 de planos. La memoria tiene portada académica, resumen ejecutivo, índice paginado, capítulos y subtítulos numerados, y párrafos justificados. [Anexo de armados](Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf): 23 láminas A3 exportadas del DXF como vectores, sin imágenes raster, con las piezas, cotas, tablas y rótulos completos.

El DWG/DXF contiene 42 presentaciones: 19 del proyecto (incluye 7 perfiles ampliados) y 23 referencias DGE completas. La biblioteca general se publica por separado en herramientas/biblioteca_dge, con 102 láminas MT, 21 láminas BT y la 022 aprobada en 2019, y 182 símbolos de la sección 9. Los CAD de detalle son derivados de PDF normativos, no archivos emitidos por MINEM. Las piezas de madera y las variantes angulares no se adoptan automáticamente como armados CAC.

[KMZ para Google Earth](google-earth/LP_Limbani_Huancasayani_R01.kmz), con fichas de 111 postes y 110 vanos, curvas de nivel cada 20 m y principales cada 100 m, relieve y recorrido 3D. Las curvas se derivan del DEM público de aproximadamente 30 m y no acreditan topografía de campo. [Guía del KMZ](google-earth/LEER_PRIMERO.md). QGIS incorpora el DEM y las curvas con rutas relativas; 13 capas verificadas.
