# Capitulo II: Calculos justificativos

## 1. Objetivo del capitulo

Justificar tecnicamente la instalacion electrica mediante el levantamiento de cargas, calculo de potencia instalada, maxima demanda, corriente de diseno, seleccion preliminar de circuitos, conductores, protecciones, tablero y puesta a tierra.

## 2. Estructura propuesta

| Seccion | Contenido a desarrollar | Fuente principal |
|---|---|---|
| 2.1 Normas aplicables | CNE-U, EM.010 y criterios del curso | `normativas/fuentes-oficiales.md` |
| 2.2 Datos electricos del sistema | Tension, frecuencia, factor de potencia, material conductor | `pautas-vivienda-2-pisos.md` |
| 2.3 Levantamiento de cargas | Tabla por ambiente, equipo, cantidad y potencia | `pautas-vivienda-2-pisos.md` |
| 2.4 Cuadro de cargas por circuito | C1 a C5, potencia instalada, factor y demanda | `pautas-vivienda-2-pisos.md` |
| 2.5 Calculo de maxima demanda | Formulas y resultado total | `proyecto-casa/02-calculos-justificativos/calculos-justificativos.md` |
| 2.6 Corriente de diseno | Formula `I = P / (V x fp)` | `proyecto-casa/02-calculos-justificativos/calculos-justificativos.md` |
| 2.7 Distribucion de circuitos | Alumbrado primer piso, tomacorrientes primer piso, cocina, alumbrado segundo piso y tomacorrientes segundo piso | `pautas-vivienda-2-pisos.md` |
| 2.8 Seleccion de conductores | Secciones preliminares segun corriente y uso | `proyecto-casa/02-calculos-justificativos/calculos-justificativos.md` |
| 2.9 Protecciones | Interruptores termomagneticos y diferencial | `proyecto-casa/02-calculos-justificativos/calculos-justificativos.md` |
| 2.10 Caida de tension | Verificacion con longitud estimada | `herramientas/calculadora-instalacion-casa.html` |
| 2.11 Puesta a tierra | Componentes y criterio preliminar | `latex/capitulos/02-calculos-justificativos.tex` |

## 3. Datos de calculo actuales

| Parametro | Valor |
|---|---:|
| Tension nominal | 220 V |
| Frecuencia | 60 Hz |
| Factor de potencia | 0.90 |
| Sistema | Monofasico |
| Material conductor | Cobre |
| Resistividad referencial del cobre | 0.0175 ohm mm2/m |

## 4. Resultado preliminar del primer piso

Con los datos indicados para el primer piso se tiene este avance inicial:

| Concepto | Valor preliminar |
|---|---:|
| Alumbrado primer piso | 72 W |
| Tomacorrientes generales primer piso | 1440 W |
| Cocina primer piso | 300 W |
| Potencia instalada primer piso | 1812 W |

El resultado total de la vivienda queda pendiente hasta definir la cantidad final de focos y tomacorrientes en las 4 habitaciones del segundo piso.

## 5. Circuitos preliminares

| Circuito | Uso | Desarrollo pendiente |
|---|---|---|
| C1 | Alumbrado primer piso | Verificar cantidad de luminarias y potencia total |
| C2 | Tomacorrientes primer piso | Verificar cantidad por ambiente |
| C3 | Cocina | Confirmar si solo considera licuadora y pequenos artefactos o tambien refrigeradora |
| C4 | Alumbrado segundo piso | Definir 1 o 2 focos por habitacion |
| C5 | Tomacorrientes segundo piso | Definir 3 o 4 tomacorrientes por habitacion |

## 6. Calculos que deben quedar completos

- Potencia total por carga: `cantidad x potencia unitaria`.
- Potencia instalada por circuito.
- Factor de demanda por tipo de carga.
- Maxima demanda por circuito.
- Corriente por circuito.
- Corriente total estimada.
- Seleccion de conductor por circuito.
- Seleccion de proteccion por circuito.
- Verificacion de caida de tension.
- Criterio de puesta a tierra.
- Tabla final de tablero o diagrama unifilar preliminar.

## 7. Pendientes del capitulo

| Pendiente | Accion |
|---|---|
| Confirmar cargas reales o estimadas | Revisar ambientes y equipos con el grupo |
| Definir longitudes de circuitos | Usar croquis o plano preliminar |
| Completar caida de tension | Aplicar formula o calculadora HTML |
| Sustentar protecciones | Relacionar corriente, conductor y termomagnetico |
| Verificar puesta a tierra | Definir conductor, electrodo, caja de registro y barra de tierra |
| Agregar numerales normativos | Revisar CNE-U y EM.010 |
