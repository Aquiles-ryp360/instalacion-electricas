# Inventario de fuentes de ubicación y catastro

Las imágenes originales recibidas el 2 de agosto de 2026 se guardan sin
modificación en `fuentes/local/ubicacion/`. Por indicación expresa del
estudiante en DEC-019, estas dos capturas son excepciones versionadas para que
un clon de Windows pueda compilar la memoria sin transferencia manual. Este
inventario y `datos/ubicacion.yaml` fijan su nombre, huella y uso.

| ID | Archivo local | SHA-256 | Uso permitido en el proyecto |
|---|---|---|---|
| LOC-CAT-01 | `2026-08-02-captura-catastro-municipal-caracoto.png` | `347c550640c2ccc537bf8a0b5acc72c7e2e7003ba003102c5370507a32a03dc2` | Contexto urbano/catastral, sin afirmar que el predio esté marcado. |
| LOC-MAP-01 | `2026-08-02-captura-google-maps-caracoto.png` | `800cf5a92936dee69398803cbc942433db9758ac52925ab858f2cf80c2aae532` | Contexto distrital y corredor vial, no georreferenciación del predio. |

La referencia espacial más cercana al predio sigue siendo la grilla UTM de la
lámina A-01 del DXF. Se adopta únicamente para la memoria académica un centro
aproximado E 383250 m, N 8272300 m, WGS 84 / UTM 19S. Debe reemplazarse por
levantamiento y documento municipal antes de cualquier uso constructivo.
