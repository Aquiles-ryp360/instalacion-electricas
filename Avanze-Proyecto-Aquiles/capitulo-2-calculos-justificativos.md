# Capitulo II: Calculos justificativos

## 1. Objetivo del capitulo

Justificar tecnicamente la instalacion electrica mediante el levantamiento de cargas, calculo de potencia instalada, maxima demanda, corriente de diseno, seleccion preliminar de circuitos, conductores, protecciones, tablero y puesta a tierra.

## 2. Estructura propuesta

| Seccion | Contenido a desarrollar | Fuente principal |
|---|---|---|
| 2.1 Normas aplicables | CNE-U, EM.010 y criterios del curso | `normativas/fuentes-oficiales.md` |
| 2.2 Datos electricos del sistema | Tension, frecuencia, factor de potencia, material conductor | `pautas-vivienda-2-pisos.md` |
| 2.3 Levantamiento de cargas | Tabla por ambiente, equipo, cantidad y potencia | `respuestas-cuestionario-aquiles.md` |
| 2.4 Cuadro de cargas por circuito | C1 a C8, potencia instalada, factor y demanda | `respuestas-cuestionario-aquiles.md` |
| 2.5 Calculo de maxima demanda | Formulas y resultado total | `proyecto-casa/02-calculos-justificativos/calculos-justificativos.md` |
| 2.6 Corriente de diseno | Formula `I = P / (V x fp)` | `proyecto-casa/02-calculos-justificativos/calculos-justificativos.md` |
| 2.7 Distribucion de circuitos | Alumbrado, tomacorrientes, cocinas, lavadora y bomba de agua | `respuestas-cuestionario-aquiles.md` |
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

## 4. Resultado preliminar general

Con los datos indicados por el estudiante se adopta una primera base de calculo. Los valores deben ajustarse cuando exista croquis y dimensiones aproximadas.

| Concepto | Valor preliminar |
|---|---:|
| Alumbrado total | 252 W |
| Tomacorrientes generales | 3420 W |
| Cocina y servicio | 4500 W |
| Bomba de agua | 750 W |
| Potencia instalada preliminar | 8922 W |
| Demanda preliminar estimada | 6996 W |
| Corriente preliminar estimada | 35.33 A |

El calculo anterior usa factores academicos preliminares: alumbrado 1.00, tomacorrientes generales 0.70, cocina/servicio 0.80 y bomba 1.00. Deben corregirse si el docente exige usar tabla especifica del CNE-U.

## 5. Circuitos preliminares

| Circuito | Uso | Desarrollo pendiente |
|---|---|---|
| C1 | Alumbrado primer piso | Cuartos, cocina pequena, pasadizo y escalera/plataforma |
| C2 | Tomacorrientes primer piso | Cuarto 1 y cuarto 2 |
| C3 | Cocina primer piso | Licuadora y artefactos pequenos |
| C4 | Alumbrado segundo piso | Sala, cuartos, cocina amplia y bano |
| C5 | Tomacorrientes generales segundo piso | Sala, cuartos, cuarto de uso varios y bano |
| C6 | Cocina amplia segundo piso | Tomacorrientes de cocina, microondas/horno y waflera |
| C7 | Lavadora segundo piso | Carga de servicio dedicada |
| C8 | Bomba de agua exterior | Bomba del pozo |

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
| Confirmar potencias reales de equipos | Revisar placa o potencia comercial de bomba, lavadora, microondas/horno y waflera |
| Definir longitudes de circuitos | Usar croquis o plano preliminar |
| Completar caida de tension | Aplicar formula o calculadora HTML |
| Sustentar protecciones | Relacionar corriente, conductor y termomagnetico |
| Verificar puesta a tierra | Definir conductor, electrodo, caja de registro y barra de tierra |
| Agregar numerales normativos | Revisar CNE-U y EM.010 |
| Confirmar tomacorrientes del segundo piso | Definir sala, cuartos y cuarto de uso varios |
