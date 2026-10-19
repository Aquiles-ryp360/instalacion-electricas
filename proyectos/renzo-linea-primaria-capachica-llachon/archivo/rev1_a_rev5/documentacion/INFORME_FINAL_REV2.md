# Informe de cierre técnico local — Rev. 2

**14-10-2026.** Rama `feature/diseno-preliminar-postes-capachica-llachon` desde `main` (`0e79dea`). El proyecto estaba íntegramente sin seguimiento; otros cambios locales ajenos se excluyeron. El estado de publicación se comprueba por separado en GitHub; este informe documenta el contenido técnico local.

Se inspeccionaron el árbol del proyecto, README, configuración, manifiestos, fuentes KML/GISEM/OSM/SRTM, corredor GIS derivado, scripts, pruebas, documentos y láminas Rev. 1. Las fuentes originales permanecen intactas. Hay respaldos de los archivos modificados en `documentacion/respaldo_rev1/`; las generaciones previas de Rev. 2 están en `build/renzo-linea-primaria-capachica-llachon/archive_rev2/` local.

**A/B:** El KML tiene cuatro segmentos, 187 vértices y 13 939,512 m UTM 19S (13 943,736 m geodésicos); brechas 14,133, 43,965 y 6,979 m. Supera en 105,482 m al corredor GIS de 13 834,030 m. La mediana de distancia de vértices manuales al eje GIS es 121,067 m. El candidato de conexión está a 0,561 m del inicio KML y coincide con un pequeño tramo `TMT001868169` de la capa GISEM de líneas.

**C:** Se listaron 40 estructuras GIS a hasta 25 m del KML como puntos de inspección. Son inventario candidato, no diseño de nuevos postes. Hay 44 intersecciones geométricas con vías OSM por validar. Las láminas CL-01 a CL-05 Rev. 2 se entregan en DXF/PDF/PNG. CL-03 carece de cotas de este corredor y CL-05 es un esquema conceptual.

**D:** Tensión, demanda, fases, conductor, capacidad, protecciones, mecánica, gálibos, servidumbres y aprobación del titular. No se calcularon corriente ni flecha del proyecto ni se cuantificaron materiales de obra. Véanse `CALCULOS_Y_PENDIENTES_REV2.md`, `PLAN_REVISION_CAMPO_REV2.md` y `MATRIZ_NORMATIVA_REV2.md`.

**Verificación:** pipeline `python proyectos/renzo-linea-primaria-capachica-llachon/scripts/reproducir_rev2.py --archive-existing` desde la raíz; 15 pruebas aprobadas; cinco DXF auditados con ezdxf, cinco PDF A3 abiertos y cinco PNG generados. `acad.exe` no se encontró en PATH. El paquete PDF Rev. 1 permanece histórico y no integra la nueva geometría. Este resultado no es apto para construcción.
