# Topografía preliminar desde un lugar

Esta herramienta genera una topografía de gabinete, sin Topomagic y sin clave
API. Escribe el nombre del lugar y obtiene un modelo digital de superficie
Copernicus GLO-30 Public desde el catálogo abierto de AWS. Si falta una tesela
GLO-30, intenta GLO-90 y registra qué resolución se utilizó.

## Instalación y uso

Desde la raíz del repositorio:

~~~powershell
python -m pip install -r herramientas/topografia/requirements.txt
python herramientas/topografia/generar_topografia.py "Capachica, Puno, Perú"
~~~

La carpeta nueva se crea en build/topografia/<lugar>-<fecha UTC>/. Opciones:

~~~powershell
python herramientas/topografia/generar_topografia.py "Llachón, Puno, Perú" --radio-km 3 --equidistancia-m 10
python herramientas/topografia/generar_topografia.py "Capachica, Puno, Perú" --salida build/topografia/mi_revision
~~~

--radio-km acepta 0.25 a 5 km; el valor predeterminado es 2 km. La
equidistancia predeterminada es 10 m. La herramienta rechaza sobrescribir una
carpeta existente.

## Archivos generados

| Archivo | Uso |
| --- | --- |
| modelo_elevacion_preliminar.tif | Raster recortado y reproyectado a UTM, con celdas de salida de 30 m. |
| curvas_nivel_preliminares.dxf | Curvas con cota Z y centro del lugar en coordenadas UTM. |
| mapa_topografico_preliminar.pdf y .png | Vista para revisar relieve y curvas. |
| manifiesto.json | Lugar elegido, alternativas de geocodificación, URL y ETag de teselas, resolución real, CRS, datum vertical y SHA-256 de salidas. |

El geocodificador toma la primera coincidencia de OpenStreetMap Nominatim. Si
hay topónimos repetidos, revisa lugar.seleccion y lugar.alternativas en el
manifiesto antes de utilizar el mapa. El centro del lugar define solo un área
circular de estudio. No genera ni aprueba automáticamente un eje de línea.

**No es un levantamiento topográfico de campo.** Copernicus DEM es un modelo
digital de superficie: puede reflejar vegetación e infraestructura. No usar
estas cotas para aprobar estructuras, flechas, gálibos, cimentaciones,
servidumbres o un punto de conexión. Para el perfil longitudinal de un proyecto
se requiere además un eje KML/GIS revisado y, para diseño de obra, cotas de
campo conciliadas.

## Fuentes y uso de servicios

- [Copernicus DEM en AWS](https://registry.opendata.aws/copernicus-dem/):
  GLO-30 Public y GLO-90, GeoTIFF optimizados, acceso público.
- [Manual del producto Copernicus DEM](https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf):
  DSM y referencia vertical EGM2008.
- [Política de Nominatim](https://operations.osmfoundation.org/policies/nominatim/):
  la herramienta hace una consulta por ejecución y se identifica mediante
  User-Agent. No está diseñada para consultas masivas.

Si se publica un mapa derivado, mantener la atribución a Copernicus DEM y
OpenStreetMap. Los datos brutos y las salidas quedan en build/ y no se
publican automáticamente en entregables/.
