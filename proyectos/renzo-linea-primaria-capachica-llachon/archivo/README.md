# Archivo: versiones anteriores de Capachica–Llachón

Antecedentes que **no se usan** para los resultados vigentes. La versión vigente es la Rev. 7: ver el [README del proyecto](../README.md).
Se movieron con `git mv`, así que `git log --follow` muestra el historial de cada archivo.

| Carpeta | Contenido |
|---|---|
| `rev6_planos_gabinete/` | Rev. 6: 13 láminas EPIME con 168 postes de una distribución de gabinete (vano máx. 100 m). La Rev. 7 la reemplazó con el plantillado del motor. La regenera `scripts/planos_formato_epime.py` |
| `rev1_a_rev5/` | Rev. 1 a 5: anteproyecto cartográfico, conciliación KML/GIS, auditorías y entregas |

Contenido de `rev1_a_rev5/`:

- `README_anterior.md` y `proyecto_rev3.yaml`: README y configuración del proyecto antes de la reorganización.
- `ENTREGA_ACADEMICA_REV5/` y `ENTREGA_FINAL_CAPACHICA_LLACHON_REV4/`: entregas académicas con manifiestos SHA-256.
- `EXPEDIENTE_TECNICO_CAPACHICA_LLACHON_REV5_COMPILADO.pdf`: expediente preliminar Rev. 5.
- `plans/`: láminas CL-01 a CL-08 (Rev. 1 a 5).
- `scripts/` y `tests/`: generadores de esas revisiones, incluida la planta satelital (`generar_planta_satelital.py`).
- `datos/`, `derived/`, `documentacion/` y `expediente/`: datos, auditorías y borradores de esas revisiones.

Los scripts archivados calculan sus rutas desde su propia carpeta. Para volver a ejecutarlos hay que copiarlos con
`datos/` y `sources/` en una estructura como la original.
