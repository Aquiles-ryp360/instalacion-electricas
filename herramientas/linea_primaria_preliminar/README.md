# Anteproyectos cartográficos de línea primaria

Esta herramienta crea una carpeta independiente por proyecto en `build/linea_primaria_preliminar/`. Sirve para explorar el lugar, un eje propuesto y sitios **geométricos candidatos**. No aprueba estructuras ni genera planos aptos para obra.

> **Regla estricta de mantenimiento:** modificar este README o el código de `herramientas/` únicamente para una mejora reutilizable por múltiples proyectos. Los nombres, coordenadas, criterios particulares, fuentes y decisiones de un proyecto pertenecen a `proyectos/<id>/`. Antes de cambiar el flujo común, comprobar que el caso se resuelve mediante datos/configuración del proyecto; documentar la capacidad general que agrega cualquier cambio compartido.

## Entrada mínima: solo el lugar

```powershell
python -m pip install -r herramientas/topografia/requirements.txt
python -m herramientas.linea_primaria_preliminar.generar herramientas/linea_primaria_preliminar/ejemplo_solo_lugar.json
```

Produce modelo de elevación Copernicus DEM, curvas de nivel DXF, mapa PDF/PNG y manifiesto. Registra `dato requerido: eje o extremos`; con un nombre de lugar no hay una ubicación defendible para postes.

## Entrada con eje preliminar

Prepare un JSON propio por proyecto. Use una ruta GeoJSON `LineString` (EPSG:4326) o un KML con un solo `LineString`:

```json
{
  "id": "mi-linea-primaria",
  "lugar": "Capachica, Puno, Perú",
  "ruta": "ruta_preliminar.geojson",
  "separacion_exploratoria_m": 100
}
```

También puede sustituir `ruta` por `origen` y `destino`; cada extremo lleva `{ "lon": ..., "lat": ... }` o `{ "lugar": "..." }`. Entre extremos se traza una **recta hipotética**. La separación de 100 m del ejemplo es solo un parámetro que debe fijar el usuario; la herramienta distribuye los sitios uniformemente y registra la separación resultante. Acepta de 20 a 500 m para exploración, sin convertir ese intervalo en criterio de diseño.

Puede usar un eje registrado en QGIS/QField con la [plantilla genérica de campo](../levantamiento_campo/README.md):

```powershell
python -m pip install -r herramientas/levantamiento_campo/requirements.txt
```

```json
{
  "id": "mi-proyecto",
  "lugar": "Nombre del lugar",
  "levantamiento_campo": "../fuentes/campo.gpkg",
  "separacion_exploratoria_m": 100
}
```

La ruta al GeoPackage es relativa al JSON. `id` debe coincidir con `id_proyecto` del eje. El importador comprueba geometría y metadatos, registra el SHA-256 del archivo de campo en el manifiesto y **no modifica** el original. La planta y el perfil siguen siendo preliminares: las cotas del perfil todavía provienen del DEM, y los sitios siguen siendo candidatos geométricos.

```powershell
python -m herramientas.linea_primaria_preliminar.generar proyectos/mi-proyecto/datos/anteproyecto.json
```

La ruta se interpreta relativa al JSON. Cada ejecución crea una carpeta nueva con topografía, `sitios_candidatos.csv`, `perfil_dem.csv`, planta DXF/PDF/PNG, perfil DXF/PDF/PNG y `manifiesto.json` con origen, estado y huellas SHA-256. Los DXF incluyen una presentación A3 editable con escala y aviso de anteproyecto. El modelo de planta está en metros UTM; el modelo de perfil utiliza progresiva y cota en metros. Las cotas vienen de un **modelo digital de superficie** y se interpolan, no de levantamiento de campo. El perfil no verifica flechas ni gálibos.

Para procesar varios anteproyectos, coloque sus JSON en una carpeta y ejecútela como entrada:

```powershell
python -m herramientas.linea_primaria_preliminar.generar proyectos/anteproyectos/datos
```

Cada JSON produce su propia carpeta. Un error se informa por proyecto y el proceso devuelve código de error al final si alguno falla.

Los sitios `SC-*` solo marcan progresivas exploratorias. Permanecen como `dato requerido` el tipo y armado de poste, y se registran los estudios pendientes: conexión, eje/cruces/servidumbres, topografía de campo, demanda, conductor, cálculo eléctrico y mecánico, despejes, suelo, cimentación y puesta a tierra. Una revisión humana decide si el eje y cada estructura son viables antes de cualquier plano de obra.

El servicio público Nominatim se usa para geocodificar los nombres de lugar; la descarga DEM requiere internet. Por proyecto el recorte DEM admite hasta 30 km por lado. Consulte también [la herramienta de topografía](../topografia/README.md).
