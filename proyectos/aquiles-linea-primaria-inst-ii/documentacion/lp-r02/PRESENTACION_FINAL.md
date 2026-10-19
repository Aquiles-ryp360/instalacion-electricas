# Consolidación de entrega — 19/10/2026

> Registro histórico de la presentación de 72 páginas. La entrega activa posterior es M01: consultar `../metrados-m01/REVISION.md` y `proyecto.yaml`.

Base inicial sincronizada: 6dbfd3aaed6c224049870aebe11f2e1ec9898455. Antes de publicar se incorporaron también los avances paralelos del repositorio hasta e81f214. Proyecto exclusivo de línea primaria, Instalaciones Eléctricas II. La minicentral del otro curso no se modifica.

## Cambios

Un único Expediente.pdf, 72 páginas: 30 de memoria, cálculos, metrados, presupuesto e índice; 19 láminas de línea; 23 hojas DGE documentales. Las ecuaciones se compusieron en LaTeX con fracciones, índices, integrales y numeración, sustituyendo el texto plano de la presentación anterior. Se desarrollan la demanda, impedancias, barrido radial, cortocircuito, catenaria, cambio de estado, flexión tipo y retenidas.

El capítulo de metrados incluye los 110 vanos y 111 apoyos, los conteos por altura y función y el desarrollo de terna, puentes y reserva. Los libros de cálculo son tres archivos con fórmulas: Calculos.xlsx (10 216), Metrados.xlsx (1672) y Presupuesto.xlsx (1705). Se recalcularon en Microsoft Excel y se exportaron sus tres resúmenes de una página. Los ensayos de cambio de altura, función, factor de potencia y precio actualizaron sus dependencias sin guardar las modificaciones de ensayo. Las 660 combinaciones de vano/estado y las 110 longitudes EDS se contrastaron con el modelo.

El presupuesto se completa como estimación académica usando los precios del parámetro costos del proyecto, no como cotizaciones. Los postes 15/17 m se escalan por longitud respecto al de 13 m. Los precios y partidas se redondean a céntimos antes de sumar. Montaje/cimentación tipo se incluyen en los conjuntos instalados, sin sumar volúmenes geotécnicos inexistentes. El costo referencial es S/ 2 559 924.11; esa precisión corresponde a la conciliación aritmética, no a exactitud comercial.

Las notas de CAD se redactaron como condiciones técnicas, conservando geometría, cargas ascendentes y el conflicto R02-P019-2. Se verificó el DWG nativo por reapertura y comparación de contornos y postes. QGIS se reabrió tras traslado, con once capas válidas, rutas relativas y 111 posiciones coincidentes. El GeoPackage adopta el nombre estable Linea_Primaria.gpkg.

## Empaquetado

El ZIP tiene 16 archivos: un expediente, tres libros y sus tres resúmenes, dos CAD, cartografía nativa y una guía breve. No contiene cuestionarios, pendientes de trabajo, plantillas, código, PDFs anteriores ni recursos de otros proyectos. Las fuentes y observaciones técnicas se conservan en el repositorio. El diseño sigue siendo académico, con geometría de gabinete y datos tipo; se mantienen en la memoria las condiciones que limitan la interpretación estructural y de equipos.

Evidencia detallada, fórmulas, huellas de archivos, resultados CAD y QGIS: VALIDACION_ENTREGA_FINAL.json. Los originales LP-R02 móvil y P01 se conservan; la entrega activa es entregables/proyecto-final.
