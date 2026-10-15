# Levantamiento de campo reutilizable para proyectos lineales

Esta herramienta define un intercambio GeoPackage (`.gpkg`) para registrar un eje y observaciones de campo en QGIS/QField. El esquema es común a distintos proyectos y lugares. No fija tensión, tipo de obra, distancia entre estructuras ni umbrales de precisión. Cada dato conserva su proyecto, origen y precisión declarada.

## Crear la plantilla

```powershell
python -m pip install -r herramientas/levantamiento_campo/requirements.txt
python -m herramientas.levantamiento_campo.gpkg crear-plantilla build/plantilla_campo.gpkg
```

El archivo contiene dos capas en WGS84 (`EPSG:4326`):

| Capa | Geometría | Campos principales |
|---|---|---|
| `eje` | `LineString` | `id_proyecto`, `id_eje`, `estado` (`propuesto` o `levantado`), `fuente`, `metodo`, `fecha_registro`, `responsable`, `precision_h_m`, `precision_v_m`, `datum_vertical`, `documento_ref` |
| `observaciones` | `Point` | `id_proyecto`, `id_observacion`, `categoria`, `fuente`, `fecha_registro`, `responsable`, `precision_h_m`, `precision_v_m`, `cota_m`, `datum_vertical`, `foto_ref` |

`categoria` es libre para poder registrar cruces, obstáculos, accesos, posibles apoyos u otra observación sin cambiar el esquema por proyecto. `precision_h_m` y `precision_v_m` son **precisiones informadas por el método/equipo**, no precisiones certificadas por el validador. `fecha_registro` acepta ISO 8601 con zona horaria, por ejemplo `2026-01-15T10:30:00-05:00`. Si se registra `cota_m`, se exige precisión vertical y `datum_vertical`; no se mezclan alturas elipsoidales y ortométricas por omisión.

## Preparar la captura en QGIS/QField

1. Abrir ambas capas del GeoPackage en QGIS y guardar un proyecto QGIS `.qgz` junto al `.gpkg` con rutas relativas.
2. Configurar el formulario de atributos de cada capa: `id_proyecto` y los campos de procedencia como obligatorios; `estado` como lista con `propuesto` y `levantado`; `categoria` como texto o lista propia del proyecto. Conservar los campos de precisión GNSS reportados.
3. Abrir el proyecto QGIS en QField, registrar el eje y las observaciones con fotos y referencias documentales. Un teléfono sin receptor adecuado no da por sí mismo precisión de levantamiento.
4. Conservar el `.gpkg` recibido de campo como evidencia original en `proyectos/<id>/fuentes/`. La validación y los planos se generan en `build/`; la herramienta no edita el archivo de campo.

Esta versión genera el **GeoPackage y su contrato de campos**; la configuración visual del formulario `.qgz` se realiza en QGIS. La creación automática del proyecto QField queda como mejora general futura y requiere probarla con una instalación QGIS disponible.

## Validar e importar

```powershell
python -m herramientas.levantamiento_campo.gpkg validar proyectos/mi-proyecto/fuentes/campo.gpkg --id-proyecto mi-proyecto --informe build/mi-proyecto/validacion_campo.json
```

Se comprueba que exista un solo eje por ID de proyecto, geometría y CRS, continuidad básica, metadatos de procedencia, fechas, precisión horizontal y observaciones con cota trazable. El informe incluye SHA-256 de la evidencia. La validación es **formal**: `apto_para_diseno` permanece `false` hasta incorporar revisión del eje, inventario suficiente de cruces y topografía/cálculos pertinentes. Una fila marcada `levantado` tampoco equivale a aprobación profesional.

El generador de línea primaria puede leer el mismo GeoPackage mediante `levantamiento_campo`; consulte [su README](../linea_primaria_preliminar/README.md). Así, un proyecto usa el esquema compartido sin añadir excepciones con su nombre dentro de la herramienta.
