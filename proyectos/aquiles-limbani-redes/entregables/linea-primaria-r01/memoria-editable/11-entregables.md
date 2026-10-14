## 11. Planos, QGIS y control de coherencia

El DXF R2018 utiliza unidadesmetros en modelspace y UTM 19 S. Sus bloques de poste representan siempre el círculo CAC de DGE 09-91-20; función S/A/AN/T/ESP mediante atributos y rótulo. Se emplean 09-91-18 para retenida inclinada, 03-31-44 para tierra y09-90-09 para SE en proyección. Geometría de bloque corresponde al poste; el desplazamiento del rótulo es sólo anotación.

El CAD incluye láminas A3: ubicación general, plantas/perfiles por~1 km con cuadrícula UTM y tabla deapoyos, unifilar, estructuras y puesta a tierra/SE. En planta se dibuja UN solo eje con leyenda 3×AAAC 50 mm², según 09-91-03 y04-40-01/03; las tres fases físicas se muestran en detalles de estructuras. Escalas de planta y perfil son explícitas; esquemas eléctricos/constructivos sin escala. PDF renderizado de las propias láminas CAD.

QGIS contiene copias del catastro original, eje, vanos, postes, retenidas, SE y referencias OSM; CRS 32719 y rutas relativas. Ortofoto antecedente disponible como capa opcional sin exigir servicios Google/XYZ. Se verifica guardar/reabrir y se ensaya portabilidad del paquete. No se utiliza el catastro ampliado con viviendas sintéticas como dato censal.

Cada poste y vano procede de resultados.json. Se verifica conteo, coordenadas de bloques CAD, continuidad/longitudes, identificadores en GIS/CSV y metrados; los originales se conservan con manifiestoshash. Verificaciones numéricas no certifican topografía, calidad de montaje ni homologación de símbolos de fabricantes.
