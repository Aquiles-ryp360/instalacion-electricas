# Entrega académica Rev. 5 — línea primaria Capachica–Llachón

**Estado: anteproyecto académico documentado, no apto para construcción.** La Rev. 5 incorpora modelos eléctricos/mecánicos condicionados, sensibilidad adimensional, tabla maestra de entradas y planos CL-06 a CL-08. CL-01 a CL-05 son copias identificadas **Rev. 4**, conservadas como planos de referencia, no reemitidas como diseño Rev. 5.

Resultado geométrico: KML original de cuatro segmentos, 13939.512 m UTM sin uniones; eje GIS alternativo 13834.029 m; diferencia 105.483 m entre ejes, no metrado. El KML tiene 187 vértices. PC=40 referencias GIS, PN=27 sitios por replantear y CV=44 alertas OSM. Ninguno es una estructura nueva aprobada.

**Sin resultados de dimensionamiento del proyecto:** no constan punto oficial, tensión, fases, demanda, conductor, parámetros de red, topografía de vanos, clima/terreno o permisos. Los factores de `ESCENARIOS_ADIMENSIONALES.csv` son hipótesis matemáticas, no voltajes, cargas ni materiales asignados.

CL-07-S1..S4 separa los cuatro segmentos KML y representa PC GISEM sin confirmar su existencia, PN como sitios candidatos de replanteo y CV como alertas OSM. CL-08 resume 57 muestras SRTM30m interpoladas cada 250 m sobre el eje GIS alternativo; no corresponde al KML y no sirve para gálibos. El KML `02_DATOS_Y_CRITERIOS/fuentes/GIS_REV5_ABRIR_EN_GOOGLE_EARTH.kml` se puede abrir en Google Earth Pro para inspección de gabinete.

Desde raíz del repositorio: `python proyectos/renzo-linea-primaria-capachica-llachon/scripts/generar_entrega_rev5.py --output RUTA_NUEVA`. No sobrescribe rutas existentes. Verificar con `--verify RUTA_EXISTENTE`. Dependencias en `00_INDICE_Y_RESUMEN/requirements.txt`; usar un entorno virtual. La copia del generador en el paquete es de referencia: requiere las fuentes originales y Rev. 4 en este repositorio. `manifest_rev5.json` da SHA-256 por archivo y la huella del manifiesto Rev. 4 de partida.
