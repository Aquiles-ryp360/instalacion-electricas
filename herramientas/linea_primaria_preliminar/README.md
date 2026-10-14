# Anteproyectos cartográficos de línea primaria

Esta herramienta crea una carpeta independiente por proyecto en `build/linea_primaria_preliminar/`. Sirve para explorar el lugar, un eje propuesto y sitios **geométricos candidatos**. No aprueba estructuras ni genera planos aptos para obra.

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

```powershell
python -m herramientas.linea_primaria_preliminar.generar proyectos/mi-proyecto/datos/anteproyecto.json
```

La ruta se interpreta relativa al JSON. Cada ejecución crea una carpeta nueva con topografía, `sitios_candidatos.csv`, `perfil_dem.csv`, planta DXF/PDF/PNG, perfil PDF/PNG y `manifiesto.json` con origen, estado y huellas SHA-256. El DXF está en metros UTM; las cotas vienen de un **modelo digital de superficie** y se interpolan, no de levantamiento de campo. El perfil no verifica flechas ni gálibos.

Para procesar varios anteproyectos, coloque sus JSON en una carpeta y ejecútela como entrada:

```powershell
python -m herramientas.linea_primaria_preliminar.generar proyectos/anteproyectos/datos
```

Cada JSON produce su propia carpeta. Un error se informa por proyecto y el proceso devuelve código de error al final si alguno falla.

Los sitios `SC-*` solo marcan progresivas exploratorias. Permanecen como `dato requerido` el tipo y armado de poste, y se registran los estudios pendientes: conexión, eje/cruces/servidumbres, topografía de campo, demanda, conductor, cálculo eléctrico y mecánico, despejes, suelo, cimentación y puesta a tierra. Una revisión humana decide si el eje y cada estructura son viables antes de cualquier plano de obra.

El servicio público Nominatim se usa para geocodificar los nombres de lugar; la descarga DEM requiere internet. Por proyecto el recorte DEM admite hasta 30 km por lado. Consulte también [la herramienta de topografía](../topografia/README.md).
