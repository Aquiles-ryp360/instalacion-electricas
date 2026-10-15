## 11. Planos, QGIS y control de coherencia

### 11.1 Planos y armados vectoriales

La entrega incorpora 19 planos A3, incluidos siete perfiles longitudinales ampliados con identificadores, longitudes, alturas de amarre, flechas y separación respecto al DEM. El anexo añade 23 hojas de armados y componentes exportadas del CAD como PDF vectorial, con sus vistas, cotas, tablas y rótulos completos. La conversión utiliza Potrace sobre las copias normativas y conserva los PDF originales para contraste; no es un redibujo por IA ni un CAD emitido por MINEM. La adaptación de las variantes de madera y de sujeción PIN a las estructuras CAC estudiadas requiere diseño específico.

### 11.2 Visualización en Google Earth

El archivo KMZ permite consultar 111 postes y 110 vanos, sus fichas y los perfiles de cada tramo. Incluye 208 curvas derivadas del DEM, con equidistancia de 20 m y curvas principales cada 100 m, relieve sombreado y recorrido en tres dimensiones. La resolución aproximada de 30 m del DEM limita esta representación: la equidistancia no equivale a exactitud vertical. Las alturas relativas al terreno de Google Earth y las cotas absolutas del DEM se muestran como modos distintos y no acreditan un levantamiento de campo.

### 11.3 Unidades y simbología del CAD

El DXF R2018 utiliza unidades en metros en espacio modelo y UTM zona 19 Sur. Sus bloques de poste representan siempre el círculo CAC de DGE 09-91-20; función S/A/AN/T/ESP mediante atributos y rótulo. Se emplean 09-91-18 para retenida inclinada, 03-31-44 para tierra y 09-90-09 para SE en proyección. Geometría de bloque corresponde al poste; el desplazamiento del rótulo es sólo anotación.

### 11.4 Contenido de los planos

El CAD incluye láminas A3: ubicación general, plantas/perfiles por~1 km con cuadrícula UTM y tabla de apoyos, unifilar, estructuras y puesta a tierra/SE. En planta se dibuja UN solo eje con leyenda 3×AAAC 50 mm², según 09-91-03 y 04-40-01/03; las tres fases físicas se muestran en detalles de estructuras. Escalas de planta y perfil son explícitas; esquemas eléctricos/constructivos sin escala. PDF renderizado de las propias láminas CAD.

### 11.5 QGIS y control de coherencia

QGIS reúne copias del catastro original, el eje, los vanos, los postes, las retenidas, las subestaciones, las referencias OSM, el DEM y las curvas derivadas. Sus 13 capas se guardan con rutas relativas y se verifican al reabrir una copia del paquete. Los identificadores, las coordenadas y las longitudes proceden de una fuente de resultados común al CAD, las tablas y los metrados. Se conservan los archivos originales con sus hashes. Los 53 controles de coherencia de la entrega comprueban esa concordancia documental y la ausencia de imágenes raster en el anexo de armados; no certifican topografía ni calidad de montaje.

