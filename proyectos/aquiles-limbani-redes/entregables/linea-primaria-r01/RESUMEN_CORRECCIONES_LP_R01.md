# Entrega revisada LP-R01 · 14/10/2026

Se reformuló el proyecto como **línea primaria Limbani–Huancasayani**, curso Instalaciones Eléctricas II, estudiante Aquiles Taylor Ramos Yapo, 227368. Se preservaron originales y no se modificó la memoria hidroeléctrica de otro curso.

- Se retiró del alcance activo la distribución urbana de Limbani, las tres SED y la asignación de764 lotes del expediente anterior.
- Se usaron tres registros INEI2017 de Huancasayani, sin sumar la población distrital ni Limbani. Proyección1% y tipificación propuesta:353 usuarios potenciales y171,486kW al pico.
- Se reconstruyó el corredor desde vías OSM, evitando casas del catastro disponible. La versión final tiene6696,369m,111 postes,110 vanos,64 cantones y128 retenidas. Los cinco cruces cartográficos se listan enCSV.
- Se calcularon estados de viento/hielo CNE a3000–4000m, catenarias inclinadas, temperatura75°C y fluencia de sensibilidad. Alturas:72 apoyos13m,30 apoyos15m y9 apoyos17m. El margen mínimo frente a envolventeDEM es7,54m, sin certificado de campo.
- Se calculó flujoPQ con ambosTX y línea, toma efectiva+5% propuesta: llegada371,1V y generación requerida183,31kW. La corriente de falla sostenida resulta menor a carga; se propuso51V/diferencial/tierra sensible.
- Se corrigió RM del CNE a214-2011, se distinguieron Suministro/Utilización, RD024 primarios y RD023 secundarios, y se registraron límites de acceso a RD018.
- Se cambió la planta a un solo eje de terna3×AAAC50mm². CírculoCAC09-91-20 en todas las funciones, retenida09-91-18, tierra03-31-44, SE09-90-09 y unifilar06/07: figuras leídas y renderizadas antes de dibujar.
- Se consultó documentación de una instalación construida, CH Ingenio(SINIA), para organización gráfica. No se utilizó un proyecto de otro estudiante como expediente terminado.
- Se produjeron13páginas de expediente,16de cálculo y12láminasA3, CADeditableDXF yDWGnativoR2018, QGIS3.44.15 con11capas/rutas relativas, tablas, fuentes y presupuesto.

**Presupuesto de orden de magnitud:** S/3,43millones conIGV; todos los precios son estimaciones, no ofertas verificadas. No incluye reforzar generación ni redes posteriores de Huancasayani.

**Verificación:**46 controles de coherencia aprobados, cuatro pruebas de catenaria y41páginas inspeccionadas visualmente. AutoCAD abrió elDWG y exportó unDXF de comprobación: diferencia máxima de coordenadas de postes1,86e-9m, sin errores de auditoría. QGIS se reabrió y comprobó desde una copia en otro directorio.

La entrega académica permite revisión del diseño. Permanecen verificaciones de campo, placas, potencia disponible, armados especiales, geotecnia/resistividad, permisos y cotizaciones; se detallan en [PENDIENTES_LP_R01.md](PENDIENTES_LP_R01.md).
