# Mejora técnica de la minicentral Michell-Banki

Revisión del 16/10/2026. **Propuesta de trabajo y contraste inicial; no es todavía un nuevo expediente R04.** La memoria, los cálculos y los tres PDF de presentación R03 se conservan. El propósito de la siguiente revisión es explicar qué se propone construir, con qué dimensiones y qué potencia puede entregar.

## Diagnóstico concreto

1. La memoria tiene 55 páginas, pero la selección de turbina no desarrolla álabes, inyector, eje, apoyos ni un plano de conjunto. Su diámetro y ancho de chorro son predimensionamientos.
2. Las ocho láminas mezclan cartografía, gráficas de cálculo y esquemas funcionales. PL-03, PL-06 y PL-07 no son planos de disposición o fabricación. Las gráficas de transitorios son útiles en la memoria de cálculo; no sustituyen el detalle de una tubería y sus soportes.
3. El perfil no es una rasante topográfica: faltan posiciones comprobadas de cámara y restitución. Las dos casas de máquinas candidatas difieren unos 152 m. Se debe mostrar esa discrepancia en el mapa, sin seleccionar silenciosamente una.
4. Los 600 kW son una envolvente de cobertura de demanda supuesta. No deben convertirse en una potencia obligatoria ni en un resultado que se fuerce aumentando caudal o salto.
5. Se repiten condiciones académicas y verificaciones pendientes. Deben concentrarse en una ficha de bases y una matriz de pendientes, manteniendo una nota específica donde cambia un resultado.

## Planteamiento recomendado

El objeto sigue siendo una **central hidroeléctrica de pasada en sistema aislado**, con suministro de estudio a Limbani y Huancasayani. La turbina forma parte del proyecto; no es necesario convertir el encargo en una fábrica de turbinas.

Se recomienda desarrollar **una unidad de 200 kW como módulo de estudio mecánico** y contrastar después cuántas unidades tienen sentido. Eso no aprueba una central de 200, 400 o 600 kW: la selección de planta debe conservar el balance estacional, el déficit de demanda y la comparación económica. El diseño de la línea primaria de Instalaciones II permanece separado.

La siguiente memoria debe responder, en este orden: recurso y salto disponibles; demanda y déficit; tamaño de planta propuesto; dimensiones hidráulicas; selección y diseño del grupo; operación aislada; costos; comprobaciones pendientes. Cada apartado debe mostrar **entrada con unidad y fuente → cálculo → resultado → plano asociado**.

## Primer contraste calculado: T12 y rendimiento

Se recuperó del editor SKAT el manual *Cross Flow Turbine Design and Equipment Engineering*, 1993, volumen 3, de Krishna Nakarmi, Alex Arter, Rolf Widmer y Markus Eisenring. Su lectura gráfica distingue:

- Páginas impresas 19 y 35-37: T12 de diámetro exterior 0.30 m, rendimiento de cálculo 0.70, velocidad unitaria 40 y caudal unitario 0.92.
- Página 30: ancho de entrada `b0 = 3.623 Q / sqrt(Hn)`, con Q en L/s, Hn en m y b0 en mm. No es una ecuación universal para cualquier Banki.
- Páginas 20-29 y 32: selección mediante campo conjunto H-Q, discos intermedios y línea d-d. Estar dentro de límites individuales de salto y caudal no basta.
- Página 32: por encima de la línea d-d no se admite la carga adicional de una polea montada directamente sobre el eje del rodete. La transmisión necesita una solución compatible.
- El archivo descargado tiene 44 páginas de manual. **No se recuperó el juego íntegro de planos de taller descrito en la ficha editorial.** No se declara disponer de CAD del fabricante ni se inventa un despiece a partir de estas páginas.

R03 supone rendimiento de turbina 0.84, mecánico 0.985 y de generador 0.925. El 0.84 puede ser una hipótesis para una máquina comercial distinta, pero no se puede atribuir automáticamente al T12. Para comparar se mantiene la geometría R03: salto bruto 45.30 m, tubería 350 m y diámetro interior 1.00 m. **Esta tubería no queda optimizada para una sola unidad.**

| Objetivo eléctrico en bornes | Caudal total requerido con ηt=0.70 | Salto neto calculado | Comparación con Qmáx R03 = 1.90 m³/s |
| --- | ---: | ---: | --- |
| 1 × 200 kW | 0.7094 m³/s | 45.06 m | Dentro del límite de caudal; selección T12 y mecánica pendientes. |
| 2 × 200 kW | 1.4408 m³/s | 44.37 m | Dentro del límite de caudal; no demuestra disponibilidad en estiaje. |
| 3 × 200 kW | 2.2219 m³/s | 43.16 m | Supera el límite adoptado. No se aumenta el caudal para forzar 600 kW. |

Al caudal límite de 1.90 m³/s, ese contraste entrega **519.72 kW en bornes**, antes de auxiliares y pérdidas hasta usuarios. No son 600 kW. Tampoco es potencia firme: sigue dependiendo del agua disponible cada día.

Para la unidad de 200 kW, las relaciones del T12 dan `b0 ≈ 383 mm`, diámetro exterior 300 mm, velocidad de referencia `≈ 895 rpm` y potencia en eje de turbina `≈ 219.51 kW`. La velocidad del generador R03 es 900 rpm: hay que comprobar operación conjunta y transmisión; no modificar el salto para hacer coincidir velocidades. El número de discos, la línea d-d y la geometría de taller deben verificarse antes de dibujar piezas definitivas. No se confunde el ancho b0 con el espesor del chorro ni con el ancho total del equipo.

Las cuentas se reproducen con [contrastar_t12.py](../scripts/contrastar_t12.py); el [JSON del contraste](../datos/turbina/contraste-t12-r04.json) conserva entradas, resultados y limitaciones. No se modifican las series de caudal, las cotas ni los resultados R03.

## Planos concretos para desarrollar

**Primer avance preparado:** [lámina UG-02 de revisión geográfica](../entregables/r04-avance/README.md), con PDF A3, DXF editable, SVG, GeoJSON y KMZ. Usa relieve DEM, curvas, catastro y las tres referencias de emplazamiento. Las coordenadas se cotejan entre archivos; todavía no fija una traza hidráulica ni resuelve la ubicación de las obras.

| Lámina propuesta | Contenido mínimo | Base y límite |
| --- | --- | --- |
| UG-01 · Ubicación | Perú/Puno/Sandia/Limbani, cuenca, localidades, norte, escala y referencias. | Cartografía pública y antecedentes; diferenciar ámbito de abastecimiento de trazado real. |
| UG-02 · Emplazamiento | Relieve DEM, curvas, cauce, catastro y las dos CM candidatas, con coordenadas y procedencia. | UTM WGS84 19S; cotas DEM identificadas. No presentar un modelo de elevación como levantamiento. |
| HI-01 · Disposición hidráulica | Captación, desarenador, canal, cámara, tubería y restitución, numerados y relacionados. | Separar ubicación comprobada de implantación funcional todavía sin coordenadas. |
| HI-02 · Perfil | Progresivas, terreno de gabinete, niveles hidráulicos, línea piezométrica y pérdidas por tramo. | No trazar una rasante exacta ni empalmar cotas de fuentes distintas sin resolver su compatibilidad. |
| HI-03 · Obras | Planta y cortes de canal, desarenador y cámara con dimensiones, flujos y niveles. | Geometría hidráulica calculada; cimentación y refuerzo condicionados a geotecnia. |
| TU-01 · Tubería | Válvula, derivación a grupos, juntas, silletas y anclajes numerados; secciones y cargas. | Pérdidas, presiones y transitorios compatibles; no inventar capacidad del terreno. |
| CM-01 · Casa de máquinas | Planta y dos cortes, eje de grupos, acceso, drenaje, tableros y mantenimiento. | Envolventes de fabricante o dimensiones académicas identificadas. |
| ME-01 · Grupo Banki | Conjunto y corte con inyector, rodete, eje, cojinetes, regulación y generador. | Modelo de referencia explícito y números de parte comunes con la memoria. |
| ME-02 · Rodete e inyector | Perfil y número de álabes, diámetros, ancho, admisión, paso del agua y discos. | Recuperar geometría técnica completa; verificar triángulos de velocidad y cargas. |
| ME-03 · Eje y apoyos | Luz, cargas, torque, flexión, fatiga, deflexión, cojinetes y transmisión. | Datos de material y cargas trazables; tolerancias y fabricación solo cuando se sustenten. |
| EL-01 · Unifilar | Generación aislada, interruptores, transformación, auxiliares y salidas. | Símbolos técnicos y parámetros concordantes, sin ampliar el expediente de Instalaciones II. |
| EL-02 · Protección y tierra | Funciones de disparo, neutros, equipotencialidad y geometría de malla. | Ajustes y seguridad a comprobar con impedancias y resistividad. |

Entregar PDF vectorial y DXF editable; DWG únicamente si se convierte y se verifica como archivo real. Los rótulos siguen siendo rectos y minimalistas. Conservar el norte, la escala y la leyenda en cada mapa. Un esquema funcional se rotula expresamente sin escala. Google Earth/QGIS deben mostrar las mismas coordenadas y estados; un recorrido visual no valida topografía.

## Redacción y presentación

Reducir introducciones generales y párrafos repetidos. La memoria principal debe mostrar decisiones y resultados; el desarrollo extenso, las series, la matriz normativa y las fuentes se conservan en anexos. No borrar advertencias que afectan disponibilidad, seguridad o alcance.

Formato propuesto: ficha inicial de una página con Q, H, potencia, energía y estado de datos; capítulos cortos; ecuaciones con sustitución numérica; tablas de resultados; figuras vectoriales grandes; referencias cruzadas entre cálculo, equipo y lámina. Evitar páginas de texto que solo anuncian estudios futuros.

Orden de trabajo: **cerrar base de diseño → contraste turbina/rendimiento → cálculo del grupo → planos hidráulicos y mecánicos → memoria sintetizada → exposición**. El cambio de rendimiento puede modificar caudal, energía, tamaño de planta y presupuesto; esos resultados se actualizan juntos antes de declarar una entrega R04.

## Fuentes del contraste

- [Editor SKAT, volumen 3](https://skat.ch/publications/cross-flow-turbine-design-volume-3).
- [Manual público enlazado por el editor](https://cdn.prod.website-files.com/68cbdceb38167ec697105235/68cd25f3b73c4e5c197cbe0e_03-T12-Manual.pdf). Copia original local `fuentes/local/investigacion-r04/SKAT_1993_T12_Manual.pdf`, SHA-256 `fc6bfd89c8a33bae6234f5a314cede69f1c4d255d17bb1684b87585c3162cc1f`.
- [OSSBERGER, campo de aplicación y admisión por celdas](https://www.ossberger.de/en/hydropower-technology/ossbergerr-crossflow-turbine). Sustenta aplicabilidad comercial general; no garantiza el rendimiento del equipo de Limbani ni del T12.

SKAT y OSSBERGER son referencias técnicas, no normas peruanas ni certificados de las máquinas existentes.
