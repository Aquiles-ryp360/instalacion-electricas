# Control de calidad Rev. 2

Fecha: 14-10-2026. Alcance: KML manual, tablas, planos y cálculos condicionados.

- KML original preservado; SHA-256 y conteo verificados. Cuatro segmentos no unidos artificialmente.
- Estaciones y coordenadas UTM 19S calculadas; longitud geodésica y proyectada documentadas.
- Candidatos GIS señalados como inspección pendiente, sin clases, cimentaciones ni vanos definitivos.
- Cruces OSM etiquetados como intersecciones geométricas por confirmar.
- Cinco DXF reabiertos con `ezdxf`: sin errores de auditoría, unidades de modelo en metros, presentación A3.
- Cinco PDF A3 horizontal y cinco PNG generados; inspección visual de CL-02 y CL-04 sin recortes ni superposiciones significativas. No se abrió AutoCAD; ejecutable `acad.exe` no localizado en PATH.
- Pruebas: `python -m pytest tests -q` — 15 aprobadas al 14-10-2026.
- La ingeniería eléctrica/mecánica y la aprobación de obra siguen pendientes; véase `CALCULOS_Y_PENDIENTES_REV2.md`.

El manifiesto de la Rev. 2 registra tamaños y SHA-256. El PDF del expediente Rev. 1 conserva la revisión anterior y no debe confundirse con estas láminas del corredor manual.
