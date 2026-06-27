---
title: "Requerimiento de servicio: puesta a tierra, electrobomba y grupo electrogeno"
subtitle: "Proyecto Aquiles - Instalaciones electricas interiores de vivienda unifamiliar"
author: "Aquiles Taylor Ramos Yapo"
date: "22 de junio de 2026"
lang: es-PE
geometry: margin=2.2cm
fontsize: 11pt
---

# REQUERIMIENTO DE SERVICIO PARA ADQUISICION DE MATERIALES, INSTALACION Y PUESTA EN SERVICIO DE SISTEMA DE PUESTA A TIERRA, ELECTROBOMBA Y GRUPO ELECTROGENO

## Datos generales

| Concepto | Dato |
|---|---|
| Proyecto | Instalaciones electricas interiores - vivienda unifamiliar de 2 pisos |
| Propietario / integrante | Aquiles Taylor Ramos Yapo |
| Docente del curso | Ing. Richar Renzo Julio Amachi Quispe |
| Ubicacion | Av. Horacio con Jr. Marineros, Mz. F7, lotes 11 y 12 |
| Distrito / provincia / departamento | San Miguel / San Roman / Puno |
| Sistema electrico de referencia | Monofasico, 220 V, 60 Hz |
| Tipo de requerimiento | Adquisicion de materiales, instalacion y puesta en servicio |
| Base de calculo | Maxima demanda del proyecto, actualizada con electrobomba de 2 HP |

Este documento se emite como requerimiento tecnico academico para el Proyecto Aquiles. Los valores finales deben ser verificados en obra por profesional competente antes de una ejecucion real.

## 1. Finalidad

El presente requerimiento tiene por finalidad garantizar la seguridad electrica, continuidad operativa y disponibilidad de servicios auxiliares de la vivienda unifamiliar del Proyecto Aquiles, mediante la contratacion integral de los siguientes servicios:

- Sistema de puesta a tierra de la instalacion electrica interior.
- Electrobomba de 2 HP, con sus accesorios de conexion, proteccion, instalacion y prueba de funcionamiento.
- Grupo electrogeno dimensionado segun la maxima demanda adoptada del proyecto.

La puesta a tierra busca reducir el riesgo de choque electrico, asegurar continuidad del conductor de proteccion y permitir la operacion adecuada de las protecciones. La electrobomba forma parte de las cargas especiales de la vivienda y debe quedar conectada de manera segura. El grupo electrogeno debe permitir respaldo electrico de la vivienda segun la demanda calculada.

## 2. Descripcion general del requerimiento

El servicio sera ejecutado bajo modalidad integral o a todo costo, incluyendo suministro de materiales, equipos, herramientas, mano de obra, montaje, pruebas, mediciones, informe tecnico, puesta en servicio y garantia.

El alcance comprende tres items principales:

| Item | Servicio requerido | Cantidad | Alcance |
|---|---|---:|---|
| 1 | Sistema de puesta a tierra residencial | 1 sistema | Materiales, instalacion, medicion con telurometro, conexion al tablero y puesta en servicio |
| 2 | Electrobomba 2 HP | 1 equipo | Adquisicion, conexion electrica, protecciones, accesorios necesarios, prueba hidraulica/electrica y puesta en servicio |
| 3 | Grupo electrogeno para maxima demanda | 1 equipo | Adquisicion, instalacion, tablero/llave de transferencia, pruebas con carga y puesta en servicio |

## 3. Base tecnica de dimensionamiento

La base del calculo se toma del expediente del Proyecto Aquiles. El calculo anterior consideraba una bomba de 1 HP, equivalente a 746 W. Por indicacion del docente, para este requerimiento se actualiza la electrobomba a 2 HP:

$$
P_{bomba}=2 \times 746\ W=1\,492\ W
$$

Con este cambio, la maxima demanda conservadora del proyecto queda:

| Concepto | Valor |
|---|---:|
| Potencia instalada anterior del escenario conservador | 11,658 W |
| Potencia instalada adicional por cambio de bomba 1 HP a 2 HP | 746 W |
| Potencia instalada ajustada | 12,404 W |
| Maxima demanda anterior | 10,358 W |
| Maxima demanda ajustada con electrobomba 2 HP | 11,104 W |
| Tension de servicio | 220 V |
| Factor de potencia adoptado | 0.90 |
| Corriente de empleo del alimentador | 56.08 A |
| Corriente de diseno referencial, 1.25 x Ib | 70.10 A |
| Potencia aparente para respaldo | 12.34 kVA |
| Capacidad minima recomendada del grupo electrogeno | 15 kVA, monofasico, 220 V, 60 Hz |

Para el grupo electrogeno se adopta una reserva aproximada del 20 % sobre la potencia aparente de la maxima demanda:

$$
S_{grupo}=\frac{11.104\ kW}{0.90}=12.34\ kVA
$$

$$
S_{grupo,recomendada}=12.34\ kVA \times 1.20=14.81\ kVA
$$

Por disponibilidad comercial y margen de arranque del motor de la electrobomba, se solicita grupo electrogeno no menor a 15 kVA. Si el proveedor no garantiza el arranque de la electrobomba de 2 HP con la carga de vivienda conectada, debera ofertar una capacidad superior dentro del rango comercial de 16 kVA a 18 kVA.

## 4. Normativa tecnica aplicable

La ejecucion debera tomar como referencia minima:

- Codigo Nacional de Electricidad - Utilizacion, aprobado por R.M. N. 0037-2006-MEM, y su modificatoria R.M. N. 0175-2008-MEM.
- Reglamento Nacional de Edificaciones, Norma Tecnica EM.010 Instalaciones Electricas Interiores, modificada por R.M. N. 083-2019-VIVIENDA.
- Ley N. 29783, Ley de Seguridad y Salud en el Trabajo, para las condiciones de ejecucion segura.
- Manuales tecnicos del fabricante de la electrobomba, grupo electrogeno, protecciones, tablero y accesorios.

Aplicacion al proyecto:

- La EM.010 define que las instalaciones electricas interiores comprenden alimentadores, tableros, circuitos derivados, protecciones, medicion y puesta a tierra; ademas exige analizar potencia instalada y maxima demanda.
- El CNE-Utilizacion, Seccion 050, se usa como base para cargas y factores de demanda en vivienda.
- El CNE-Utilizacion, Seccion 060, se usa para el sistema de puesta a tierra y enlace equipotencial. La resistencia final de puesta a tierra no debe superar 25 ohmios; como criterio de mejor desempeno para vivienda se propone una meta de 10 ohmios o menor si las condiciones del suelo lo permiten.
- La EM.010 indica que los equipos para suministro de energia por emergencia deben cumplir el Codigo Nacional de Electricidad, por lo que el grupo electrogeno debe instalarse con proteccion, transferencia segura y puesta a tierra.

Fuentes oficiales consultadas:

- MINEM, R.M. N. 0037-2006-MEM - Codigo Nacional de Electricidad Utilizacion: https://www.gob.pe/institucion/minem/normas-legales/108855-0037-2006-mem
- MINEM, R.M. N. 0175-2008-MEM - Modificacion del CNE Utilizacion: https://www.gob.pe/institucion/minem/normas-legales/108110-0175-2008-mem
- MVCS, Reglamento Nacional de Edificaciones - EM.010: https://www.gob.pe/institucion/vivienda/informes-publicaciones/2309793-reglamento-nacional-de-edificaciones-rne
- Congreso de la Republica, Ley N. 29783: https://www.gob.pe/institucion/congreso-de-la-republica/normas-legales/462576-29783

## 5. Condiciones de contratacion y ejecucion

### 5.1 Modalidad

El servicio se solicita bajo modalidad a todo costo, con entrega llave en mano. El proveedor debe incluir materiales, equipos, herramientas, transporte, mano de obra, pruebas, mediciones, documentacion tecnica y puesta en servicio.

### 5.2 Lugar de prestacion

El servicio se ejecutara en la vivienda ubicada en Av. Horacio con Jr. Marineros, Mz. F7, lotes 11 y 12, distrito de San Miguel, provincia de San Roman, departamento de Puno.

### 5.3 Plazo referencial

El plazo referencial de ejecucion sera de 10 dias calendario desde la aprobacion del requerimiento y disponibilidad del area de trabajo. El plazo puede ajustarse si el proveedor justifica tiempos de adquisicion de equipos o condiciones de obra.

### 5.4 Seguridad y salud en el trabajo

El proveedor sera responsable de ejecutar los trabajos con personal calificado, herramientas adecuadas, equipos de proteccion personal y procedimientos seguros. Debe evitar energizacion accidental, retroalimentacion hacia la red publica, excavaciones sin senalizacion y manipulacion de equipos sin bloqueo o aislamiento.

### 5.5 Recepcion y conformidad

La conformidad se otorgara despues de verificar:

- Instalacion fisica completa de los tres items.
- Pruebas electricas y mecanicas satisfactorias.
- Medicion de resistencia de puesta a tierra.
- Funcionamiento de electrobomba.
- Funcionamiento del grupo electrogeno y transferencia.
- Entrega de informe tecnico, fichas de equipos, garantias y recomendaciones de mantenimiento.

### 5.6 Garantia

La garantia minima sera de 12 meses para mano de obra y materiales instalados, sin perjuicio de la garantia mayor que otorgue el fabricante de los equipos principales.

## 6. Especificaciones tecnicas minimas por item

### 6.1 Item 1: Sistema de puesta a tierra residencial

| Componente / actividad | Requerimiento minimo |
|---|---|
| Estudio preliminar | Verificar ubicacion del pozo, distancia al tablero general, accesibilidad para mantenimiento y condicion del terreno. |
| Electrodo | Varilla de cobre o acero recubierto de cobre, minimo 5/8 pulg y 2.40 m comercial, compatible con el CNE; debe alcanzar profundidad efectiva conforme instalacion. |
| Caja de registro | Caja de concreto o polipropileno resistente, con tapa removible para inspeccion. |
| Conductor de puesta a tierra | Cobre aislado verde/amarillo o desnudo, seccion minima segun calculo del proyecto; referencial 10 mm2 para conexion al tablero, o mayor si la verificacion normativa/final lo exige. |
| Conector | Abrazadera de cobre, conector certificado o soldadura exotermica; debe asegurar baja resistencia de contacto. |
| Tratamiento de suelo | Bentonita, cemento conductivo, gel reductor u otro material tecnico no corrosivo, segun condicion del terreno. |
| Excavacion y relleno | Excavacion, instalacion de electrodo, tratamiento, relleno y compactacion. |
| Conexion al tablero | Conexion a barra de tierra del Tablero General; continuidad hacia tableros y circuitos con conductor PE. |
| Medicion | Medicion con telurometro antes/despues del tratamiento, registrando metodo usado, condiciones y resultado. |
| Valor de aceptacion | Resistencia final no mayor a 25 ohmios; meta recomendada para el proyecto: 10 ohmios o menor. |
| Entregable | Informe de medicion, fotos, croquis de ubicacion, materiales instalados y recomendaciones de mantenimiento. |

### 6.2 Item 2: Electrobomba de 2 HP

| Componente / actividad | Requerimiento minimo |
|---|---|
| Equipo | Electrobomba monofasica 220 V, 60 Hz, potencia nominal 2 HP, adecuada para el uso hidraulico real de la vivienda. |
| Potencia de calculo | 1,492 W para el cuadro de cargas del proyecto. |
| Corriente referencial | 7.54 A con 220 V y fp 0.90; verificar con corriente nominal de placa. |
| Circuito electrico | Circuito dedicado C8 desde tablero, con conductor de cobre 2.5 mm2 como minimo y conductor de proteccion PE. |
| Canalizacion | Tuberia PVC SAP 20 mm o equivalente, con accesorios y sellos adecuados para zona exterior. |
| Caja de conexion | Caja estanca IP55 o superior, borneras y prensaestopas si corresponde. |
| Proteccion | ITM bipolar recomendado 16 A curva C o dimensionado segun placa; interruptor diferencial 30 mA; guardamotor o proteccion termica regulada a la corriente nominal del equipo. |
| Accesorios de control | Interruptor de mando, flotador/presostato si corresponde, contactor si el fabricante o corriente de arranque lo exige. |
| Accesorios hidraulicos | Acoples, union, valvula check y accesorios necesarios para dejar el equipo operativo, segun condicion real de pozo/cisterna/tanque. |
| Pruebas | Arranque, parada, sentido/flujo, consumo de corriente, ausencia de fugas, estabilidad de presion y verificacion de protecciones. |
| Entregable | Ficha tecnica, manual, registro de prueba, garantia y recomendaciones de operacion. |

### 6.3 Item 3: Grupo electrogeno segun maxima demanda

| Componente / actividad | Requerimiento minimo |
|---|---|
| Capacidad | No menor a 15 kVA monofasico, 220 V, 60 Hz. Recomendar 16 kVA a 18 kVA si el proveedor no garantiza arranque de electrobomba de 2 HP con carga conectada. |
| Potencia base | Maxima demanda ajustada: 11.104 kW; potencia aparente base: 12.34 kVA. |
| Regulacion | AVR o sistema de regulacion de tension compatible con cargas residenciales. |
| Proteccion | Interruptor termomagnetico de salida y proteccion contra sobrecarga/cortocircuito segun fabricante. |
| Transferencia | Tablero o llave de transferencia manual/automatica 2P, capacidad recomendada 80 A, con enclavamiento para impedir retroalimentacion hacia la red publica. |
| Conexion | Alimentacion al tablero general o tablero de emergencia definido, con conductores dimensionados por corriente, longitud y caida de tension. |
| Puesta a tierra | Conexion del chasis y tablero del grupo al sistema de puesta a tierra, respetando continuidad y enlace equipotencial. |
| Ubicacion | Zona ventilada, accesible para mantenimiento, protegida de lluvia directa, gases de escape y manipulacion no autorizada. |
| Combustible | Gasolina o diesel segun oferta; debe indicarse autonomia, consumo estimado y plan de mantenimiento. |
| Pruebas | Prueba en vacio, prueba con carga parcial, prueba de transferencia, verificacion de tension/frecuencia y arranque de electrobomba. |
| Entregable | Ficha tecnica, manual, garantia, registro de pruebas y esquema de conexion. |

## 7. Experiencia minima del proveedor y personal

El proveedor debera acreditar capacidad tecnica para ejecutar instalaciones electricas y puesta en servicio de equipos.

| Perfil | Requerimiento minimo |
|---|---|
| Proveedor | Haber ejecutado al menos 2 servicios similares de instalaciones electricas, puesta a tierra, bombas o grupos electrogenos en los ultimos 3 anos. |
| Tecnico responsable | Experiencia minima de 2 anos en instalaciones electricas residenciales, tableros, puesta a tierra o equipos electromecanicos. |
| Profesional certificador | Ingeniero Electricista o Ingeniero Mecanico Electricista colegiado y habilitado para validar mediciones, protocolos y recomendaciones finales, si el servicio se ejecuta de manera real. |

La experiencia puede sustentarse con ordenes de servicio, constancias, conformidades, facturas, fotografias de trabajos similares o declaracion jurada tecnica.

## 8. Entregables tecnicos

Al concluir el servicio, el proveedor debera entregar:

- Informe tecnico general del servicio ejecutado.
- Relacion de materiales y equipos instalados.
- Fichas tecnicas y manuales de electrobomba, grupo electrogeno, protecciones y tablero de transferencia.
- Protocolo de medicion de puesta a tierra con resultado en ohmios.
- Registro de pruebas de continuidad del conductor de proteccion.
- Registro de prueba de arranque y operacion de electrobomba.
- Registro de prueba de grupo electrogeno, tension, frecuencia y transferencia.
- Croquis o esquema unifilar actualizado de conexion.
- Garantias de equipos y mano de obra.
- Recomendaciones de mantenimiento preventivo.

## 9. Criterios de aceptacion

La instalacion se considerara conforme cuando cumpla como minimo:

| Criterio | Condicion de aceptacion |
|---|---|
| Puesta a tierra | Resistencia medida no mayor a 25 ohmios; continuidad PE hacia tablero y circuitos. |
| Electrobomba | Arranque y parada normales, corriente dentro del valor de placa, protecciones operativas y sin fugas visibles. |
| Grupo electrogeno | Tension y frecuencia estables, soporte de carga de prueba, arranque de electrobomba y transferencia sin retorno hacia red publica. |
| Seguridad | Tableros cerrados, conductores protegidos, identificacion de circuitos, conexion a tierra y ausencia de partes energizadas expuestas. |
| Documentacion | Informe, mediciones, fichas tecnicas, garantias y esquema de conexion entregados. |

## 10. Observaciones tecnicas

- El calculo adopta el escenario conservador del Proyecto Aquiles, que considera cocina electrica preliminar. Si finalmente se confirma cocina a gas y ausencia de cargas electricas de alta potencia, la maxima demanda y el grupo electrogeno podrian recalcularse.
- La electrobomba se actualiza obligatoriamente a 2 HP por indicacion docente.
- La capacidad de 15 kVA del grupo electrogeno se justifica por maxima demanda y reserva. El proveedor debe confirmar capacidad de arranque del motor de 2 HP.
- El cambio de bomba de 1 HP a 2 HP incrementa la corriente de diseno referencial del alimentador. Antes de una ejecucion real debe revisarse la coordinacion final de alimentador, interruptor general, transferencia y tablero.
- La puesta a tierra debe medirse en obra. No basta con instalar la varilla; la conformidad depende del valor medido y de la continuidad del conductor de proteccion.

## 11. Anexo: cuadro de cargas ajustado para el requerimiento

| Circuito | Descripcion | P.I. (W) | F.D. | M.D. (W) |
|---|---|---:|---:|---:|
| C1 | Alumbrado primer piso | 80 | 1.00 | 80 |
| C2 | Tomacorrientes primer piso | 1,260 | 0.70 | 882 |
| C3 | Cocina primer piso, auxiliar | 300 | 0.80 | 240 |
| C4 | Alumbrado segundo piso | 132 | 1.00 | 132 |
| C5 | Tomacorrientes segundo piso | 2,340 | 0.70 | 1,638 |
| C6 | Cocina electrica segundo piso, escenario conservador | 6,000 | 1.00 | 6,000 |
| C7 | Lavadora segundo piso | 800 | 0.80 | 640 |
| C8 | Electrobomba exterior 2 HP | 1,492 | 1.00 | 1,492 |
| **Total** |  | **12,404** |  | **11,104** |

## 12. Fecha y firma

San Miguel, San Roman, Puno, 22 de junio de 2026.

| Elaborado por | Revisado por |
|---|---|
| Proyecto Aquiles - Instalaciones Electricas I | Ing. Richar Renzo Julio Amachi Quispe |
