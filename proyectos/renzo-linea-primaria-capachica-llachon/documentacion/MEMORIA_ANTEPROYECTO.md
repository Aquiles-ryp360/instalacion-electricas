# Memoria de sustento del anteproyecto Capachica–Llachón

**Estado: anteproyecto para investigación y revisión profesional. No es expediente técnico aprobado ni plano para construcción.** Fecha de consulta de fuentes públicas: 14-10-2026 UTC. Esta memoria se aplica únicamente al corredor **Capachica–Llachón**.

## 1. Objeto y decisión de planteamiento

El objetivo preliminar es **determinar si la red de media tensión que figura entre Capachica y Llachón requiere intervención** para atender una necesidad eléctrica que aún debe definirse con datos de demanda y calidad de servicio. El planteamiento inicial es estudiar el **aprovechamiento y eventual reforzamiento de la red publicada**, pues [GISEM/Osinergmin](https://gisem.osinergmin.gob.pe/serverosih/rest/services/OGC/PeruOsinergmin019RedesMediaTension/MapServer) representa tramos de MT en ese recorrido. La existencia cartográfica no confirma su continuidad física, estado, capacidad disponible o aptitud para conectarse.

Esta elección evita presuponer una línea paralela nueva. La alternativa final se decidirá tras conocer el problema real, la condición del circuito y la respuesta del operador.

| Alternativa a evaluar | Cuándo tendría sentido | Evidencia que falta |
|---|---|---|
| A. Mantener u operar mejor la red actual | La red ya cubre la demanda y el problema es de operación o mantenimiento | Demanda, interrupciones, tensiones, inventario y diagnóstico de fallas |
| B. Reforzar/rehabilitar tramos existentes | La red presenta límite térmico, de tensión, protección, confiabilidad o condición física comprobado | Flujo de carga, cortocircuito, inspección de estructuras y conductor, compatibilidad de equipos |
| C. Nueva derivación o trazo | El servicio requerido no está cubierto o las alternativas A y B son técnica o económicamente insuficientes | Punto de conexión, servidumbres, topografía, comparación de rutas, evaluación ambiental y presupuesto |

**No se elige todavía conductor, tensión, subestación, estructuras ni potencia.** La [matriz de parámetros pendientes](../datos/parametros_diseno_pendientes.json) representa estos datos con `null` hasta que exista evidencia propia del corredor.

## 2. Área, extremos y geometría de referencia

El inicio elegido es el registro de estructura `NMT000367723` (**−69.830170304°, −15.643135203°**) próximo a Capachica. El final elegido es `NMT000027963` (**−69.784386472°, −15.722124515°**) próximo a Llachón. Ambos son datos `EXTRACTED_GIS` de la capa de estructuras de GISEM, no puntos de conexión aprobados. La geometría de red queda a **5,02 m** y **3,48 m**, respectivamente, de esos registros; las asociaciones requieren comprobación en campo.

El camino de menor longitud dentro de la instantánea GISEM enlaza **27 códigos de tramo**. Su longitud en UTM 19S (EPSG:32719) es **13 834,03 m** (`INFERRED_GIS`). La longitud es de la polilínea digital y no puede convertirse directamente en metrado de suministro o montaje. La suma de las longitudes geométricas de los 27 tramos coincide con la ruta dentro del redondeo. Sin embargo, la suma numérica del atributo GISEM `LONGITUD` es **14 248,94**; el esquema consultado no declara su unidad. La diferencia numérica frente a los 13 834,03 m es **414,91**, pero no puede interpretarse físicamente sin confirmar la unidad y método de ese atributo. Esta discrepancia debe aclararse con el titular antes de presupuestar. El [cuadro de 27 tramos](../datos/cuadro_tramos_gisem.csv) conserva ambos valores y los códigos de origen.

El perfil se trazó con **57 cotas** del conjunto SRTM30m consultado mediante [Open Topo Data](https://www.opentopodata.org/datasets/srtm/), con rango **3823–3887 m**. Es una aproximación territorial; la escala vertical de CL-02 se amplía para leer la forma del relieve. No hay conductor ni vanos dibujados.

## 3. Planos CAD y lectura correcta

| Lámina | Archivo para AutoCAD | Visualización | Estado |
|---|---|---|---|
| CL-01, ubicación y corredor | [DXF A3 con layout](../plans/CL-01_A3_AUTOCAD_PRELIMINAR.dxf) | [PDF A3](../plans/CL-01_ubicacion_corredor.pdf) | Ruta GIS y estructuras extremas de referencia, sin replanteo |
| CL-02, perfil de terreno | [DXF A3 con layout](../plans/CL-02_A3_AUTOCAD_PRELIMINAR.dxf) | [PDF A3](../plans/CL-02_perfil_referencial.pdf) | Cotas SRTM, sin conductores ni gálibos |

Cada DXF contiene una pestaña de presentación `CL-01_A3` o `CL-02_A3` de **420 × 297 mm**. Para inspección CAD, abrir esa pestaña e imprimir A3 horizontal a escala de papel 1:1. El modelo CL-01 usa coordenadas UTM 19S en **metros**; el modelo CL-02 usa progresiva y cota en **metros**. Los PDF fueron preparados como vistas legibles del mismo conjunto de datos, pero el layout DXF debe verificarse visualmente en AutoCAD antes de imprimir para entrega. El [reporte de generación](../datos/reporte_generacion_cad.json) conserva las huellas de entradas y salidas.

## 4. Bases normativas identificadas

Se identificaron las siguientes fuentes **oficiales** para desarrollar la ingeniería posterior. El ámbito de las normas DGE de electrificación rural depende de que el proyecto se formule bajo ese régimen; aún no se ha establecido. La consulta de páginas de aprobación no constituye una revisión exhaustiva de modificatorias ni una certificación de cumplimiento.

| Documento oficial | Relevancia a revisar | Estado de aplicación al proyecto |
|---|---|---|
| [R.M. 0214-2011-MEM, Código Nacional de Electricidad Suministro 2011](https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem) | Seguridad de líneas de suministro, distancias, instalaciones y mantenimiento | Referencia identificada; reglas concretas y posibles modificatorias pendientes de verificar sobre diseño final |
| [R.D. 018-2003-EM/DGE, Bases para diseño de líneas y redes primarias rurales](https://www.gob.pe/institucion/minem/normas-legales/4775002-018-2003-em-dge) | Criterios de diseño de líneas y redes primarias dentro de su ámbito | Aplicabilidad condicionada a régimen de electrificación rural y alcance aprobado |
| [R.D. 030-2003-EM/DGE, levantamientos topográficos rurales](https://www.gob.pe/institucion/minem/normas-legales/4775130-030-2003-em-dge) | Levantamiento del eje, apoyos, cruces y perfil | Debe definirse plan de levantamiento y su ámbito |
| [R.D. 026-2003-EM/DGE, suministro de materiales y equipos](https://www.gob.pe/institucion/minem/normas-legales/4775087-026-2003-em-dge) | Especificaciones de componentes seleccionados | Se usará cuando exista alternativa y lista de materiales aprobadas; comprobar actualizaciones por componente |
| [R.D. 016-2003-EM/DGE, montaje de líneas y redes primarias](https://www.gob.pe/institucion/minem/normas-legales/4774974-016-2003-em-dge) | Especificación de construcción y pruebas | Pendiente de definición de obra |

No se han asignado aquí valores normativos de gálibo, viento, hielo, puesta a tierra o aislamiento; dependen de clasificación de cruces, configuración, altitud, condiciones de sitio y edición aplicable. Cada valor deberá sustentarse con datos y normas aplicables a Llachón.

## 5. Cadena de estudios y verificaciones necesaria

| Disciplina | Información de entrada | Verificación que debe producirse | Estado |
|---|---|---|---|
| Necesidad y operación | Demanda actual y futura por sectores, interrupciones, tensión medida, inventario de alimentador | Definir problema y comparar alternativas A/B/C | Sin datos del operador |
| Topografía y ocupación | Eje medido, coordenadas de estructuras, terreno, vías, cruces, predios, servidumbres | Planta/perfil medidos, puntos críticos y permisos | Solo GIS/SRTM de referencia |
| Eléctrica | Tensión, fases, cargas, conductor y longitudes reales, impedancias, nivel de cortocircuito, dispositivos | Corriente de diseño, caída de tensión, pérdidas, capacidad, cortocircuito, coordinación, aislamiento | No calculable de forma válida |
| Mecánica | Vanos, cotas, conductor, herrajes, apoyos, suelo, clima y casos de carga | Flecha/tensión, cargas, fundaciones y distancias en cada cruce | No calculable de forma válida |
| Puesta a tierra | Esquema de neutro, corrientes de falla, resistividad medida, equipos | Seguridad de contacto/paso y diseño de PAT | No calculable de forma válida |
| Costos y permisos | Alternativa aprobada, metrados medidos, análisis de precios y derechos | Presupuesto, cronograma, autorizaciones | No cuantificable |

Las ecuaciones de uso posterior deben aplicarse mediante funciones deterministas con sus unidades y condiciones. Por ejemplo, en sistema trifásico equilibrado la corriente a partir de potencia aparente sería `I = S / (sqrt(3)·V_LL)`, siempre que `S` y `V_LL` estén confirmados. No se ejecuta un cálculo de corriente porque ambos valores son `null` para este corredor. Asimismo, no se calcula flecha con SRTM: faltan vanos reales y propiedades mecánicas.

## 6. Trabajo de campo y solicitud al operador

1. Confirmar con el operador el titular y estado de los tramos que GISEM codifica `ELPU`; solicitar a Electro Puno, si corresponde, unifilar vigente, códigos de alimentador y activos, tensión/fases, características de conductor y equipos, historial de fallas y calidad, niveles de cortocircuito, capacidad disponible y condiciones de conexión.
2. Definir usuarios/cargas a atender y horizonte de demanda; registrar ubicación de cargas y objetivos medibles del proyecto.
3. Verificar en campo ambos extremos y los tramos candidatos: continuidad, apoyos, propiedad, conductor, aisladores, protecciones, cruces y puntos de riesgo. Reconciliar los códigos GIS con el inventario patrimonial.
4. Levantar topografía de precisión del eje y alternativas, terreno en cruces, edificaciones, vías y cursos de agua; establecer sistema de referencia y puntos de control.
5. Levantar predios, servidumbres, restricciones ambientales, culturales y de accesibilidad; solicitar autorizaciones pertinentes.
6. Medir resistividad de suelo y condiciones geotécnicas donde se propongan nuevas estructuras o PAT.

**Puerta de decisión:** con esos datos se aprueba una alternativa y recién entonces se desarrollan unifilar eléctrico, selección de conductor, cálculo de protecciones, cuadro de estructuras, planta/perfil de diseño, detalles de armados, metrados, presupuesto y expediente para firma. Hasta ese punto, los planos CL-01 y CL-02 son anexos de investigación.
