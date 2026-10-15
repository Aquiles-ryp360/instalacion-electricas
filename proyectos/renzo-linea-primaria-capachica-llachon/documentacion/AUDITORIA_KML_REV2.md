# Auditoría del levantamiento manual y estado inicial — Rev. 2

**Fecha:** 14-10-2026. **Estado:** anteproyecto cartográfico, no diseño aprobado.

## Estado inicial protegido

- Repositorio local `C:\Users\renzo\instalacion-electricas`; remoto `https://github.com/gaelrenzo/instalacion-electricas.git`; rama predeterminada remota `main`; HEAD inicial `0e79dea`.
- Antes de editar: rama `main`; el directorio completo `proyectos/renzo-linea-primaria-capachica-llachon/` estaba sin seguimiento. Había cambios de usuario en `README.md` raíz y en `proyectos/renzo-linea-primaria-capachica/`; se dejaron intactos.
- Rama creada: `feature/diseno-preliminar-postes-capachica-llachon`. Fuentes originales sin modificación. Archivos nuevos de la primera ejecución se respaldaron en `documentacion/respaldo_generacion_inicial_20261014/` antes de regenerar.
- Se inspeccionaron README, `proyecto.yaml`, manifiesto de fuentes, memorias, auditoría Rev. 0, parámetros, KML, GeoJSON, corredor derivado, scripts, pruebas, expediente y láminas existentes. Los dos planos anteriores siguen como antecedente del trazado GIS.

## KML original

| Atributo | Resultado | Clase |
|---|---:|---|
| Archivo SHA-256 | `d68db8f50d3408e93612471acdc5db59ccaddb37bdbf08fa4c5e764fff082ec8` | A |
| Estructura | 1 carpeta, 4 Placemark LineString, 0 Point, 187 vértices | A |
| CRS de coordenadas KML | WGS84, longitud/latitud; elevación `0` no tomada como cota | A |
| Proyección métrica | WGS84 / UTM zona 19 Sur, EPSG:32719 | B |
| Longitud geodésica | 13 943,736 m, `pyproj.Geod` WGS84 | B |
| Suma de polilíneas proyectadas | 13 939,512 m, sin unir empalmes | B |
| Brechas entre segmentos | 14,133; 43,965; 6,979 m | B |
| Comparación con corredor GIS | +105,482 m respecto de 13 834,030 m GIS | B |
| Desviación vértices KML → eje GIS | mediana 121,067 m; máximo 269,289 m | B |
| Puntos GIS cercanos para inspección | 40 a un máximo de 25 m del KML | C |
| Intersecciones geométricas con vías OSM | 44; hay que distinguir cruces reales, coincidencias y duplicados | C |

Las cuatro líneas están ordenadas desde Capachica hacia Llachón. No presentan vértices consecutivos idénticos ni autointersección por segmento. El último empalme cruza geométricamente; los dos primeros no conectan. La suma de brechas (65,077 m) no se agrega a la longitud de polilínea porque no hay eje verificado entre ellas. El corredor manual difiere sensiblemente del trazado GIS previo: el primer apoyo GIS de referencia queda a 122,3 m del primer segmento y el último a 107,9 m del cuarto. No corresponde heredar automáticamente sus extremos.

El punto candidato del usuario está a **0,561 m** del primer vértice KML. En la instantánea GISEM, `TMT001868169` pertenece a la capa de **tramos** (`CODTRAMOMT`), con geometría aproximada de 0,962 m y atributos `ELPU`, `A`, `D`, `CT`, puesta en servicio `16/11/2024`, `LONGITUD=0.99` (unidad del atributo sin verificar). La coincidencia espacial apoya la identificación cartográfica del tramo, pero no confirma capacidad, tensión, titularidad contractual ni punto de conexión aprobado. Las claves `NMT...` proceden de la capa de estructuras y no identifican este tramo.

## Método y límites

`scripts/auditar_corredor_manual.py` lee las cuatro líneas originales, transforma con `pyproj`, calcula distancias y estaciones independientes por segmento, proyecta estructuras GISEM a cada eje y selecciona las ubicadas a 25 m o menos **solo como puntos de inspección**. No introduce vanos por separación convencional. La tolerancia de 25 m es un filtro de búsqueda cartográfica, no una tolerancia de replanteo. Las coordenadas de esos puntos permanecen en su posición GIS; no se desplazan al eje KML.

Las vías OSM son una instantánea colaborativa y sus 44 intersecciones geométricas no prueban un cruce eléctrico en terreno. No hay fuente de cauces, edificios, servidumbres, inventario de apoyos ni topografía de detalle. Las 57 cotas SRTM previas corresponden al corredor GIS diferente; se omiten del perfil manual Rev. 2. La exactitud nominal del KML y de GISEM no consta en los archivos. Solicitar metadatos y verificar en campo.

**Fuentes locales:** KML manual sin fecha ni precisión declarada; instantáneas GISEM y OSM con URL, fecha y SHA-256 en `sources/manifest.json`; `derived/route.json` para comparación GIS. Todos los datos observados son cartográficos, no as-built.
