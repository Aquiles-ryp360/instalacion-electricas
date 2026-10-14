## 11. Planos, QGIS y control de coherencia

El DXF R2018 utiliza unidadesmetros en modelspace y UTM19 S. Contiene bloques propios LP_SUSPENSION/ANGULO/ANCLAJE/TERMINAL, atributos ID/estructura/E/N/altura, símbolos de tierra/retenida y SE en proyección basada en09-90-09. Geometría de bloque corresponde a poste; desplazamiento del rótulo es sólo anotación.

El CAD incluye láminas A3: ubicación general, plantas/perfiles por~1 km, unifilar, estructuras y puesta a tierra/SE. Escalas de planta y perfil se calculan por viewport; esquemas eléctricos y constructivos se indican sin escala. El eje de tres fases y retenidas está separado en capas. La presentación PDF se renderiza de las propias láminas CAD para evitar gráficos de distinto trazado.

QGIS contiene copias del catastro original, eje, vanos, postes, retenidas, SE y referencias OSM; CRS32719 y rutas relativas. Ortofoto antecedente disponible como capa opcional sin exigir servicios Google/XYZ. Se verifica guardar/reabrir y se ensaya portabilidad del paquete. No se utiliza el catastro ampliado con viviendas sintéticas como dato censal.

Cada poste y vano procede de resultados.json. Se verifica conteo, coordenadas de bloques CAD, continuidad/longitudes, identificadores en GIS/CSV y metrados; los originales se conservan con manifiestoshash. Verificaciones numéricas no certifican topografía, calidad de montaje ni homologación de símbolos de fabricantes.
