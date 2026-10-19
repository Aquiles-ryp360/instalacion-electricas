# LP-R03 — adopción de tensión nominal 22,9 kV

**Proyecto:** línea primaria Limbani–Huancasayani. **Fecha:** 2026-10-19. **Rama:** `aquiles/lp-229kv-profesional-r03`.
**Base:** M01, commit `f7c29c2f2c11fef388141da51e735d352f853daa` de `gaelrenzo/instalacion-electricas`.

## Decisión de ingeniería de diseño
Se adopta **22,9 kV entre fases, trifásico, 60 Hz** como tensión nominal del nuevo diseño de línea primaria aislada MCH Limbani → transformador elevador T1 → línea → transformador reductor T2 → Huancasayani. No se confunde **tensión nominal adoptada** con **tensión de generación ni tensión real de equipos verificadas**. La adopción es firme para la revisión LP-R03, pero **NO constituye aprobación para construcción** ni transforma automáticamente la infraestructura existente.

- Línea MT nominal: 22,9 kV, tres fases, sin derivaciones ni red secundaria.
- T1: `V_generador_real/22,9 kV`, relación, grupo, aislamiento, impedancia, regulación y potencia por verificar con placa y evaluación a altitud.
- T2: `22,9/0,380 kV` **como interfaz de estudio**, relación/tomas y tensión de distribución final sujetas al diseño de la red receptora y verificación real.
- Equipos MT, interruptores, descargadores, TT/TC y aisladores: seleccionar por **tensión máxima de equipo, aislamiento corregido por altitud y coordinación de aislamiento**, no por el rótulo de 22,9 kV.
- Se mantiene provisionalmente AAAC 50 mm² como **hipótesis M01 de comparación**: no reducir sección hasta cerrar criterio térmico, mecánico, cortocircuito, corrosión, disponibilidad y costo.
- Se mantiene la geometría de gabinete de 111 apoyos / 110 vanos sólo para trazabilidad; exige levantamiento topográfico, detalle de cruces y análisis resistente/cimentaciones.

## Cálculo preliminar del caso 22,9 kV (reutiliza la comparación LP-R02)

Valores reportados en el expediente de 72 páginas, sección 3.5. Son escenarios del **mismo modelo idealizado**, NO resultados de un nuevo flujo de carga certificado. La carga máxima original es 171,486 kW / 190,540 kVA, fp 0,90.

| Tensión fuente equivalente | BT calculada (V) | Pérdida de línea (kW) | Fuente requerida (kW) | Desviación BT sobre 380 V |
|---|---:|---:|---:|---:|
| 1,000 pu | 354,634 | 0,439 | 182,027 | -6,675 % |
| 1,025 pu | 364,905 | 0,414 | 181,770 | -3,972 % |
| 1,050 pu | 375,126 | 0,392 | 181,534 | -1,283 % |

**Lectura:** sin regulación equivalente, el caso nominal entrega 354,634 V en BT, por debajo de una banda de estudio ±5 % alrededor de 380 V; **no se debe escoger 1,05 pu arbitrariamente para ocultarlo**. Confirmar tensión en bornes del generador, AVR, taps disponibles, caída real de T1/T2 y variación horaria antes de adoptar ajustes.

La corriente de pérdida implícita para 1,05 pu, usando `R_75 = 5,432569 Ω/fase` del modelo y `ΔP = 3 I²R`, resulta ≈4,904 A; esta magnitud se deduce de valores redondeados, no reemplaza el flujo de carga recalculado.

**Balance:** con oferta nominal supuesta de 200 kW y carga de Limbani de 25 kW en simultáneo, el escenario 1,05 pu tendría déficit de `181,534 + 25 - 200 = 6,534 kW`. La generación de estiaje y el reparto de carga siguen sin medirse.

## Revisión de aislamiento, protección y PAT
- Verificar norma DGE RD 018-2003-EM/DGE, Código Nacional de Electricidad — Suministro 2011, RD 024-2003-EM/DGE, RD 026-2003-EM/DGE y RD 016-2003-EM/DGE en sus alcances aplicables.
- Usar base normalizada para 22,9 kV, corregida por altura y condición de contaminación; no extrapolar aisladores de 10 kV. Definir BIL, tensión soportada a frecuencia industrial, distancia de fuga, descargadores y distancias fase-fase/fase-tierra.
- Redefinir corrientes de falla en T1, MT y T2 con impedancias y conexión de equipos reales. No copiar 51V/27/59/81 ni TC/TT con sus ajustes del caso 10 kV.
- El modelo de neutro de 5 A usado anteriormente **no se conserva como decisión constructiva**: depende de grupo vectorial y puesta a tierra. Como sensibilidad a 22,9 kV: `R_N = 22 900/(√3 · 5) ≈ 2644,0 Ω`, con `P_10s ≈ 66,1 kW` y `E_10s ≈ 661 kJ`. Esta operación aislada NO constituye especificación de resistencia ni diseño térmico.
- Rehacer verificación de distancias mínimas reales, corregidas por altitud y clase de cruce. El gálibo de 7,549 m sobre DEM es una comparación académica, no una certificación.

## Armados y presupuesto
Adoptar un inventario por poste compatible con **CAC**, con detalles oficiales utilizados sólo como referencia documentada y planos de fabricación adaptados. Comprobar herrajes, separación de fases y esfuerzos (en especial P003, P035, P057 y 46 apoyos con reacción ascendente). Aislar el paquete de 23 láminas DGE como biblioteca, sin sustituir planos ejecutivos.
Regenerar **en una única revisión** cálculos, 111 fichas M01, presupuesto, unifilar, perfiles, planos en DWG/DXF y el expediente PDF. Ningún cuadro económico M01 puede presentarse como presupuesto definitivo a 22,9 kV hasta revalorizar equipos.

## Puertas obligatorias antes de declarar «aprobado para ejecución»
1. Placas de generador, T1 y T2; capacidad firme estiaje; curva de demanda y reserva real de Limbani.
2. Topografía y predios/servidumbres; coordenadas y obstáculos medidos; cruces y gálibos revisados.
3. Diseño electromecánico de apoyos y cadenas; capacidad axial, interacción N-M, esfuerzos ascendentes, retenidas y estudio geotécnico.
4. Coordinación de protecciones; puesta a tierra con resistividad medida, tensiones de paso/contacto y prueba de falla.
5. Armados CAC constructivos comprobados; selección de materiales 22,9 kV con fichas de fabricante.
6. APU, cronograma, metrados civiles y costos según oferta validada; control de versiones de todos los editables.

**Estado de LP-R03:** tensión nominal **ADOPTADA PARA DISEÑO**; datos reales pendientes; **NO APROBADO PARA CONSTRUCCIÓN**.

## Fuentes
- MINEM, RD 018-2003-EM/DGE: https://www.gob.pe/institucion/minem/normas-legales/4775002-018-2003-em-dge
- MINEM, RD 024-2003-EM/DGE: https://www.gob.pe/institucion/minem/normas-legales/4775076-024-2003-em-dge
- MINEM, RD 026-2003-EM/DGE: https://www.gob.pe/institucion/minem/normas-legales/4775087-026-2003-em-dge
- MINEM, RD 016-2003-EM/DGE: https://www.gob.pe/institucion/minem/normas-legales/4774974-016-2003-em-dge
- CNE Suministro 2011: https://www.gob.pe/institucion/osinergmin/normas-legales/738581-0214-2011-mem-dm
