# Validación independiente de geometría — Rev. 3

## Método y procedencia

Se leyó el XML KML original con `lxml`; sus coordenadas son longitud, latitud WGS84 (KML 2.2, EPSG:4326). Se transformaron con `pyproj.Transformer(always_xy=True)` a WGS84/UTM zona 19 sur (EPSG:32719). La longitud se sumó en `shapely.LineString.length`; se calculó además `pyproj.Geod(ellps="WGS84").line_length`. El eje GIS alternativo se reconstruyó de los 152 pares UTM de `derived/route.json`. La proyección es adecuada para comparación métrica local; los seis decimales son reproducibilidad numérica, no precisión topográfica.

SHA-256 KML: `d68db8f50d3408e93612471acdc5db59ccaddb37bdbf08fa4c5e764fff082ec8`, idéntico al `derived/reconciliacion_corredores_rev3.json` y al archivo original en Git. El KML tiene una carpeta, cuatro placemarks/LineString y 187 vértices distribuidos 122, 24, 12 y 29. El KML no contiene un eje continuo único. Los valores de altitud cero del KML no son cotas utilizables.

| Magnitud | Reportado Rev. 3 (m) | Recalculado (m) | Diferencia (m) | Evidencia |
|---|---:|---:|---:|---|
| KML, cuatro segmentos UTM | 13 939,511910 | 13 939,511909681 | <0,000001 | KML original, EPSG:32719 |
| KML geodésico | 13 943,735685 | 13 943,735685372 | <0,000001 | KML original, Geod WGS84 |
| GIS alternativo UTM | 13 834,028618 | 13 834,028617954 | <0,000001 | `derived/route.json` |
| Diferencia entre ejes UTM | 105,483292 | 105,483291727 | <0,000001 | Resta de dos ejes diferentes |
| Brecha GAP-1 | 14,132854 | 14,132853515 | <0,000001 | Extremo S1/inicio S2 |
| Brecha GAP-2 | 43,965184 | 43,965183846 | <0,000001 | Extremo S2/inicio S3 |
| Brecha GAP-3 | 6,979239 | 6,979239370 | <0,000001 | Extremo S3/inicio S4 |
| Suma cuerdas | 65,077277 | 65,077276730 | <0,000001 | Tres distancias rectas |

La cifra histórica **105,482 m** resulta de restar `13 939,512 − 13 834,030` (GIS publicado/redondeado). Con geometrías completas resulta **105,483292 m**. La cifra histórica **40,405 m** es `105,482 − 65,077`; con precisión completa resulta `40,406015 m`. Ninguna representa un tramo espacial: las tres brechas no forman parte de la longitud inicial del KML, y el GIS sigue otro eje. Añadir cuerdas hipotéticas da 14 004,589187 m, que tampoco es obra medida.

## Localización y continuidad

| Empalme | Extremo anterior lon, lat | Inicio siguiente lon, lat | Separación UTM | Observación |
|---|---|---|---:|---|
| GAP-1 | -69,832422736; -15,643710441 | -69,832309130; -15,643645600 | 14,132854 m | Extremos distintos; no se conoce trayectoria de enlace. |
| GAP-2 | -69,849281259; -15,673366521 | -69,849530400; -15,673682260 | 43,965184 m | Extremos distintos; avance proyectado GIS 33,488926 m, sin equivalencia garantizada. |
| GAP-3 | -69,821339509; -15,702327509 | -69,821389327; -15,702286870 | 6,979239 m | Las polilíneas se intersecan antes de sus extremos. Sobrantes calculados: 1,781217 m del S3 y 5,270941 m desde inicio S4; decidir en campo si hay solape/retorno. |

La intersección S3/S4 calculada en UTM es E 411 991,038 m, N 8 263 821,758 m. No se recortó ni modificó el KML. La línea GIS inferida inicia y termina en lugares distintos del KML; `route.json` declara separaciones de 5,02 m y 3,48 m entre sus extremos de ruta y las estructuras NMT respectivas. Por tanto tampoco debe asumirse conexión exacta a esas estructuras. Las 40 referencias PC proceden de estructuras GIS dentro de 25 m del KML; los 27 PN son vértices retenidos mediante filtros de 10 m y 20°, no apoyos nuevos aprobados. El intervalo de progresiva más largo entre PN consecutivos del mismo segmento es 2 143,351 m (PN-014 a PN-015), prueba de que la lista no constituye una distribución de vanos.

Se verificaron 44 intersecciones geométricas CV de 10 vías OSM diferentes. Falta depurar su realidad física, categoría, anchura, cotas, permisos y despejes. La unidad del atributo GISEM `LONGITUD=0.99` del tramo TMT001868169 no está acreditada; no se equiparó a la longitud geométrica ni a capacidad eléctrica. La huella de las tres fuentes descargadas coincide con `sources/manifest.json`; las fuentes cartográficas no sustituyen as-built ni levantamiento.

## Reproducción mínima

Desde la raíz del repositorio: `python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests -q`. Para las magnitudes independientes, parsear `//k:LineString/k:coordinates` del KML y sumar `LineString([Transformer.from_crs(4326,32719,always_xy=True).transform(lon,lat), ...]).length` por segmento; calcular cada separación con la distancia entre último y primer par UTM consecutivos. La tabla anterior registra los números no redondeados necesarios para comprobarlo.
