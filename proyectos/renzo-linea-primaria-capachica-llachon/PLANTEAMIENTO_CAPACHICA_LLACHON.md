# Capachica–Llachón: sustento de ubicación y planteamiento preliminar

**Objeto de este estudio:** evaluar la red de media tensión (MT) publicada entre el entorno de Capachica y el de Llachón, y definir la información necesaria para decidir si corresponde reforzarla, ampliarla o mantenerla. **Estado:** borrador cartográfico para revisión; no es expediente de construcción ni acredita una línea nueva.

Este estudio se limita al corredor **Capachica–Llachón**. Los parámetros de diseño se definirán con evidencia propia de este corredor.

## Ubicación elegida y alcance

| Elemento | Valor y unidad | Procedencia y estado |
|---|---:|---|
| Inicio de referencia, entorno de Capachica | Estructura GISEM `NMT000367723`; longitud −69.830170304°, latitud −15.643135203° | Capa oficial de estructuras MT; `EXTRACTED` como registro GIS. La separación calculada a la geometría de red es **5.02 m**; vínculo físico pendiente de comprobar. |
| Final de referencia, entorno de Llachón | Estructura GISEM `NMT000027963`; longitud −69.784386472°, latitud −15.722124515° | Misma capa; `EXTRACTED` como registro GIS. Separación calculada a la geometría de red **3.48 m**; vínculo físico pendiente de comprobar. |
| Corredor dibujado | **13 834.03 m**, equivalentes a **13.834 km**, en **27 tramos GIS** | `INFERRED`: camino más corto sobre la red publicada, con unión de extremos a ≤1 m; longitud calculada en **UTM zona 19S, EPSG:32719**. No es metrado de obra. |
| Perfil del terreno | **57 muestras**, cotas **3823–3887 m** | `INFERRED` de SRTM30m mediante Open Topo Data, interpolación bilineal; solo orientación territorial. |

Las coordenadas anteriores son referencias de la base cartográfica, no puntos de conexión aprobados. Se eligió el extremo de Llachón próximo al núcleo indicado en OpenStreetMap y a una estructura incluida en GISEM. No se ha demostrado que sea el mejor punto eléctrico de entrega. El [inventario turístico de MINCETUR](https://consultasenlinea.mincetur.gob.pe/fichaInventario/index.aspx?cod_Ficha=1449) menciona aproximadamente **14 km por carretera** desde Capachica a Llachón; sirve para ubicar la escala regional, sin validar los 13.834 km de red.

## Dos planos para revisar

| Plano | Visualización | Archivo editable | Qué representa |
|---|---|---|---|
| **CL-01 — Ubicación del corredor**, A3 horizontal | [PDF](plans/CL-01_ubicacion_corredor.pdf) · [PNG](plans/CL-01_ubicacion_corredor.png) | [DXF UTM 19S](plans/CL-01_corredor_utm19s.dxf) | Red MT publicada por GISEM, camino seleccionado, estructuras terminales de referencia y caminos OSM. La ruta azul representa un corredor **existente según GIS**, no una obra nueva aprobada. |
| **CL-02 — Perfil longitudinal referencial**, A3 horizontal | [PDF](plans/CL-02_perfil_referencial.pdf) · [PNG](plans/CL-02_perfil_referencial.png) | [DXF en metros](plans/CL-02_perfil_srtm_metros.dxf) | Cota de terreno SRTM30m contra progresiva a lo largo del corredor. **No** representa conductor, postes, flecha ni distancias de seguridad. |

Para AutoCAD se añadieron [CL-01 A3](plans/CL-01_A3_AUTOCAD_PRELIMINAR.dxf) y [CL-02 A3](plans/CL-02_A3_AUTOCAD_PRELIMINAR.dxf), cada uno con pestaña de presentación y rótulo. El [README](README.md) enlaza sus vistas PDF/PNG renderizadas y la [memoria de anteproyecto](documentacion/MEMORIA_ANTEPROYECTO.md) presenta la evaluación técnica y normativa.

Ambos PDF fueron renderizados para revisión visual y los DXF se reabrieron con `ezdxf`. Las geometrías DXF están en metros; el perfil usa progresiva y cota en metros. Véanse los [resultados de inspección CL-01](plans/CL-01_corredor_utm19s_inspection.json) y [CL-02](plans/CL-02_perfil_srtm_metros_inspection.json).

## Fuentes y método

Las descargas y sus fechas UTC, URL exacta, tamaño y SHA-256 constan en [manifest.json](sources/manifest.json). La copia local permite reproducir la revisión sin consultas nuevas.

| Fuente | Uso | Límite de interpretación |
|---|---|---|
| [Osinergmin GISEM, servicio Redes Media Tensión](https://gisem.osinergmin.gob.pe/serverosih/rest/services/OGC/PeruOsinergmin019RedesMediaTension/MapServer), capas 22 y 24; consultado **14-10-2026 UTC** | 208 tramos y 440 estructuras dentro del recorte territorial; se seleccionaron 27 tramos continuos entre dos estructuras. | La ubicación GIS no confirma estado en campo, titularidad legal, tensión exacta por tramo, capacidad libre, sección del conductor o disponibilidad de conexión. |
| © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0; consulta Overpass **14-10-2026 UTC** | Caminos como contexto del plano CL-01 y referencia poblacional. | La cartografía vial no define el trazo eléctrico. |
| [Open Topo Data, SRTM30m](https://www.opentopodata.org/datasets/srtm/); consulta **14-10-2026 UTC** | Cotas interpoladas cada 250 m aproximadamente y en el extremo final. | Resolución y exactitud insuficientes para gálibos, vanos, implantación de postes o cálculo mecánico. |

La ruta se obtuvo transformando la geometría GISEM de WGS84 a UTM 19S, formando un grafo de tramos y uniendo extremos cuya distancia calculada es ≤1 m. El camino de menor longitud conecta dos extremos cercanos a las estructuras elegidas. El resultado, sus 27 códigos de tramo y las coordenadas UTM de cada vértice se conservan en [route.json](derived/route.json). La continuidad calculada es una **inferencia GIS**, no una verificación en terreno.

El [informe técnico 092-2024-GRT de Osinergmin](https://www.osinergmin.gob.pe/Resoluciones/pdf/2024/Informe-Tecnico-092-2024-GRT.pdf) se usó únicamente como contexto documental sobre redes de la zona. No proporciona por sí solo aprobación ni datos de diseño de este corredor seleccionado.

## Planteamiento técnico a comprobar

1. **Diagnóstico de necesidad:** pedir a Electro Puno el unifilar vigente, inventario de equipos, registros de demanda, capacidad y calidad de servicio del alimentador que atiende Llachón. Con ello definir si existe un problema y su solución: operación, reforzamiento, ampliación o una alternativa distinta.
2. **Puntos extremos:** confirmar en campo la identidad, posición, condición y conectividad de `NMT000367723` y `NMT000027963`; acordar con el operador el punto de conexión y la carga o usuarios que se atenderían.
3. **Levantamiento:** obtener topografía de precisión, cruces, servidumbres, predios, restricciones ambientales y accesos. El perfil SRTM no sustituye este levantamiento.
4. **Ingeniería:** una vez fijados demanda, tensión, conductor, estructuras, equipos y condiciones ambientales, calcular flujo/caída de tensión, cortocircuito y protección, flecha y tensión, cargas estructurales, distancias, aislamiento y puesta a tierra con criterios y normas aplicables documentados.
5. **Planos de proyecto:** desarrollar planta y perfil topográfico con vanos, estructuras, cruces, cotas y detalles; contrastarlos con memoria, metrados y presupuesto. Requieren revisión y firma profesional.

**Datos críticos ausentes:** tensión nominal confirmada para cada tramo, estado operativo, capacidad del alimentador, cargas actuales y futuras, conductor instalado, coordenadas medidas en campo, topografía apta para diseño, permisos/servidumbres y aprobación de conexión. Por ello los dos planos entregados muestran **ubicación y terreno referenciales**; no sustentan aún un diseño eléctrico o mecánico definitivo ni un cumplimiento normativo.

## Reproducción y control

El [README del estudio](README.md) enlaza los planos de esta carpeta. Los archivos derivados se conservan junto a sus fuentes. El código de generación está en el repositorio local `workspace/seace-cad-intelligence/studies/capachica_llachon`; para regenerar, utilice una copia de trabajo o un destino nuevo, ya que los scripts evitan sobrescrituras. Las pruebas fuera de línea comprueban la procedencia, la longitud, las 57 muestras y que los cuatro archivos finales se abren con las unidades esperadas.

**Verificación ejecutada el 13-10-2026 (hora de Perú):** `python -m pytest -q` → **20 pruebas superadas**, incluidas 6 específicas de este estudio. Los dos PDF abren como una página A3, se renderizaron y revisaron visualmente; los dos DXF abren con unidades declaradas en metros. La suma independiente de distancias entre vértices UTM coincide con la longitud almacenada dentro de 0.01 m. Estas verificaciones son de integridad documental y geométrica, no de validez eléctrica en campo.

| Tarea | Estado | Evidencia | Pendiente principal |
|---|---|---|---|
| Ubicación y corredor | Cartografía preliminar comprobada | CL-01, GISEM, 27 tramos y pruebas de trazabilidad | Confirmar continuidad y extremos en campo |
| Perfil del terreno | Referencial comprobado | CL-02, 57 cotas SRTM y pruebas de apertura | Levantamiento topográfico para diseño |
| Ingeniería eléctrica y mecánica | Pendiente | Datos críticos enumerados arriba | Operador, cargas, materiales, protecciones y cálculos |
| Plano para construcción | Pendiente | Los dos planos llevan aviso de borrador | Proyecto detallado y revisión profesional |
