# 5. Relación de planos y anexos

## 5.1 Láminas disponibles

| Código | Título | Archivo AutoCAD compatible | Vista PDF | Fuente y condición |
|---|---|---|---|---|
| CL-01 | Ubicación y corredor de MT publicado | `plans/CL-01_A3_AUTOCAD_PRELIMINAR.dxf` | `plans/CL-01_A3_AUTOCAD_PRELIMINAR_vista.pdf` | GISEM/Osinergmin; A3, coordenadas UTM 19S en modelo, referencias GIS |
| CL-02 | Perfil referencial del terreno | `plans/CL-02_A3_AUTOCAD_PRELIMINAR.dxf` | `plans/CL-02_A3_AUTOCAD_PRELIMINAR_vista.pdf` | SRTM30m; A3, progresiva y cota en modelo, sin postes ni conductor |

El [servicio oficial GISEM](https://gisem.osinergmin.gob.pe/serverosih/rest/services/OGC/PeruOsinergmin019RedesMediaTension/MapServer) tiene las capas 22 (tramos) y 24 (estructuras) utilizadas. Las instantáneas, consultas, fecha y SHA-256 están en `sources/manifest.json`. El perfil proviene de [Open Topo Data - SRTM30m](https://www.opentopodata.org/datasets/srtm/) y se interpoló de forma bilineal aproximadamente cada 250 m. Las cotas no permiten verificar distancias eléctricas.

Los DXF se guardaron en versión R2010 (`AC1024`) con modelo en metros (`$INSUNITS=6`) y presentación A3 de 420 × 297 mm. La apertura y auditoría estructural se verificaron con `ezdxf`; se renderizaron las presentaciones a PDF/PNG. **No se ejecutó AutoCAD** en esta máquina; el responsable debe comprobar impresión, fuentes y estilos en su instalación.

## 5.2 Láminas exigibles para expediente de obra, aún no disponibles

| Plano | Por qué no puede emitirse en Rev. 1 |
|---|---|
| Unifilar de la instalación proyectada | Faltan unifilar vigente, punto de conexión, cargas, tensión y equipos aprobados |
| Planta y perfil de diseño por tramos | Falta topografía de precisión, definición de intervención y servidumbres |
| Cuadro de apoyos/vanos | Faltan inventario en campo, cálculo mecánico, fundaciones y alternativa elegida |
| Cruces y distancias de seguridad | Faltan cotas y clasificación de cada cruce; SRTM no es apto |
| Detalles de armados, retenidas, cimentación y PAT | Faltan materiales, cálculo estructural, suelo y resistividad |
| Plano de subestaciones y protecciones, si aplica | No se ha definido su necesidad ni su capacidad |

Los detalles constructivos se desarrollarán con las condiciones verificadas del corredor, sus cargas y el diseño aprobado.

## 5.3 Anexos digitales del paquete

- `proyecto.yaml`: identidad, estado, extremos y pendientes críticos.
- `sources/manifest.json`: URL, fecha y huella de las fuentes cartográficas.
- `derived/route.json`: camino GIS calculado y advertencias.
- `datos/cuadro_tramos_gisem.csv`: 27 códigos de tramo y progresivas/longitudes.
- `datos/parametros_diseno_pendientes.json`: datos de ingeniería desconocidos en `null`.
- `datos/matriz_metrados_pendientes.csv`: partidas potenciales sin cantidad ni precio.
- `datos/reporte_generacion_cad.json`: entradas/salidas SHA-256 y validación CAD.
- `documentacion/MEMORIA_ANTEPROYECTO.md` y `documentacion/CONTROL_CALIDAD.md`: método y comprobaciones.
