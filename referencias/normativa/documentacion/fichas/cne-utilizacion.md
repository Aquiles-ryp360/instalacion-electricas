# Ficha de norma: Codigo Nacional de Electricidad - Utilizacion

## Identificacion

- Codigo interno: CNE-U.
- Nombre: Codigo Nacional de Electricidad - Utilizacion.
- Entidad emisora: Ministerio de Energia y Minas.
- Aprobacion: R.M. N.° 037-2006-MEM/DM.
- Modificacion identificada: R.M. N.° 175-2008-MEM/DM.
- Texto oficial: <https://www.gob.pe/institucion/osinergmin/normas-legales/738607-037-2006-mem-dm>.
- Modificacion oficial: <https://www.gob.pe/institucion/minem/normas-legales/4778939-175-2008-mem-dm>.
- Fecha de comprobacion de enlaces: 2026-08-01.

El texto base y sus modificaciones deben consultarse conjuntamente. El Manual
de Sustentacion publicado por MINEM es apoyo interpretativo de cumplimiento
facultativo y no reemplaza la norma.

## Funcion dentro de un proyecto

El CNE-U es la norma tecnica base para las instalaciones de utilizacion. No
define por si solo toda la solucion: se complementa con el RNE, la EM.010, la
regulacion del uso elegido, las condiciones de la distribuidora, las NTP de
producto y las decisiones justificadas del proyectista.

## Mapa de secciones relevante para la segunda unidad

| Seccion | Titulo | Pregunta que ayuda a resolver |
|---|---|---|
| 010 | Introduccion | Alcance, terminologia y principios de aplicacion |
| 020 | Prescripciones generales | Condiciones generales de seguridad y aprobacion de equipos |
| 030 | Conductores | Tipos, capacidad y condiciones de los conductores |
| 040 | Conexiones y equipo de conexion | Punto de conexion y equipos asociados |
| 050 | Cargas de circuitos y factores de demanda | Potencia instalada, demanda y dimensionamiento inicial |
| 060 | Puesta a tierra y enlace equipotencial | Proteccion de personas, masas y continuidad de tierra |
| 070 | Metodos de alambrado | Canalizaciones y forma de instalar los conductores |
| 080 | Proteccion y control | Sobrecorriente, desconexion y control |
| 100 | Equipos e instalaciones especiales | Reglas adicionales para equipos especiales |
| 110 | Lugares peligrosos | Clasificacion por gases, polvos o fibras combustibles |
| 120 | Lugares de manipulacion de combustibles | Grifos, estaciones, talleres de reparacion, almacenamiento y acabados |
| 130 | Lugares con liquidos o vapores corrosivos o muy humedos | Laboratorios, procesos de lavado y ambientes agresivos, si aplican |
| 140 | Hospitales, clinicas y similares | Areas de pacientes, sistemas aislados y sistemas esenciales |
| 150 | Instalacion de equipo electrico | Requisitos generales de montaje de equipos |
| 160 | Motores y generadores | Motores, alimentadores, proteccion, control y generacion |
| 170 | Instalacion de equipos de alumbrado | Luminarias y alumbrado |
| 210 | Gruas y polipastos electricos | Equipos de izaje en talleres o industria |
| 220 | Soldadoras electricas | Alimentacion y proteccion de soldadoras |
| 240 | Sistemas de emergencia y senales de salida | Respaldo, iluminacion y transferencia de emergencia |
| 260 | Instalaciones de diagnostico por imagenes | Rayos X, tomografia y equipos similares |
| 370 | Alarma y bombas contra incendio | Circuitos dedicados y alimentacion de seguridad |

## Alcances especiales comprobados

- La Regla 110-000 hace que la Seccion 110 complemente o modifique las reglas
  generales cuando existe un lugar peligroso. La clasificacion debe realizarse
  antes de escoger equipo o alambrado.
- La Regla 120-000 incluye puestos de venta de combustibles, estaciones de
  servicio, talleres de reparacion, garajes, almacenamiento y procesos de
  acabado. Por eso un grifo o un taller con combustibles/pintura no puede
  tratarse como un local ordinario.
- La Regla 130-000 cubre lugares con liquidos o vapores corrosivos o niveles
  muy altos de humedad. La presencia real de estas condiciones debe quedar
  documentada.
- La Regla 140-000 cubre areas hospitalarias de cuidado de pacientes y partes
  esenciales. Las Reglas 140-300 en adelante tratan los sistemas electricos
  esenciales.
- La Regla 160-000 cubre instalacion, alambrado, conductores, proteccion y
  control de motores y generadores.
- La Regla 220-000 agrega requisitos para soldadoras electricas.
- La Regla 240-000 cubre energia e iluminacion de emergencia y senales de
  salida.
- La Regla 260-000 cubre rayos X y otros equipos de diagnostico por imagenes,
  pero no sustituye las medidas de proteccion radiologica.
- La Regla 370-000 cubre sistemas locales de alarma y bombas contra incendio.

## Metodo de uso por una IA

1. Leer `proyecto.yaml` y confirmar el uso, proceso, ambientes y alcance.
2. Identificar las secciones generales y especiales posiblemente aplicables.
3. Abrir el PDF oficial y leer la regla completa, sus excepciones, tablas y
   anexos relacionados.
4. Registrar en la matriz: norma, regla, resumen propio, dato de entrada,
   decision, evidencia y estado de verificacion.
5. No convertir un ejemplo del CNE-U o de otro proyecto en dato de diseno.
6. Marcar `por confirmar` si falta clasificar un ambiente o verificar una
   condicion de operacion.
7. Someter los criterios tecnicos a revision de un ingeniero electricista o
   mecanico-electricista colegiado antes de publicar entregables.

## Errores que deben evitarse

- Citar solo "segun CNE" sin seccion o regla.
- Aplicar factores de demanda residenciales a una instalacion no residencial.
- Dimensionar un motor solo con kW sin corriente de placa, servicio, arranque,
  eficiencia y factor de potencia.
- Suponer que todo laboratorio es un lugar peligroso o, en el extremo opuesto,
  ignorar gases, solventes, polvos, humedad o corrosion.
- Seleccionar equipo "antiexplosivo" sin clasificacion de area y certificacion
  compatible.
- Tratar un hospital como un edificio comercial ordinario.
- Confundir el CNE-U con el CNE-Suministro o usar indistintamente sus alcances.
