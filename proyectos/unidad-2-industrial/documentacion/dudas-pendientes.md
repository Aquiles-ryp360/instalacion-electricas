# Dudas pendientes para revision de Aquiles

Este archivo concentra preguntas no bloqueantes. Codex debe continuar con criterios
tecnicos trazables y actualizar aqui el efecto de cada respuesta. Una duda de
seguridad que impida continuar no debe disfrazarse como supuesto.

Estados: `ABIERTA`, `RESPONDIDA`, `SUPERADA POR EVIDENCIA`, `REQUIERE CAMPO`.

## Datos administrativos y entrega

| ID | Estado | Duda | Criterio usado mientras tanto | Efecto de una respuesta distinta |
|---|---|---|---|---|
| D-001 | ABIERTA | ¿El docente aprobo formalmente el tema del grifo y existe rubrica final? | Se desarrolla el expediente completo con los cinco componentes vistos en clase y formato inspirado en el proyecto Aquiles. | Puede cambiar indice, numero de laminas o profundidad de calculos. |
| D-002 | ABIERTA | ¿Cual es la hora, modalidad y medio definitivo de entrega del 2026-08-03? | El informe usa el formato grafico del expediente Aquiles de la primera unidad; se preparan fuentes editables, PDF y planos PDF/DXF vectoriales. | Solo afecta empaquetado y cronograma. |
| D-003 | ABIERTA | ¿El rotulo/portada requiere codigo de estudiante y semestre academico? | La universidad, facultad, escuela, curso, autor y docente ya quedaron definidos en `datos/rotulo-planos.yaml`; codigo y semestre se dejan vacios. | Afecta rotulo y portada, no el diseno. |

## Fuente arquitectonica y operacion

| ID | Estado | Duda | Criterio usado mientras tanto | Efecto de una respuesta distinta |
|---|---|---|---|---|
| D-004 | REQUIERE CAMPO | ¿Las cotas y alturas del DXF coinciden con el predio y existe una version PDF/DWG aprobada? | Se adopta el DXF recibido como referencia geometrica; sus laminas y textos se preservan. | Puede obligar a recalcular longitudes y metrados. |
| D-005 | ABIERTA | ¿El grifo operara 24 horas y cual sera su aforo/personal? | Para demanda, alumbrado exterior y respaldo se usara operacion continua conservadora. | Puede reducir horas de uso y consumo, no la seguridad electrica. |
| D-006 | ABIERTA | ¿Habra equipos de lavado, lubricentro o taller no representados? | Quedan fuera del alcance; solo se incluye servicio de aire/agua visible en el plano. | Agregaria cargas y posiblemente ambientes. |
| D-007 | ABIERTA | ¿La sigla `G.E.` del plano confirma ubicacion prevista para grupo electrogeno? | Se considera una ubicacion candidata y se verificara su distancia a las areas clasificadas. | Puede mover el grupo y sus canalizaciones. |

## Equipos y suministro

| ID | Estado | Duda | Criterio usado mientras tanto | Efecto de una respuesta distinta |
|---|---|---|---|---|
| D-008 | ABIERTA | ¿Existen fichas de los seis surtidores, bombas sumergibles, compresor, refrigeracion y HVAC? | Se usaran potencias de diseno tomadas de familias comerciales comparables, identificadas como criterio adoptado. | Cambia demanda, circuitos, arranque y protecciones. |
| D-009 | REQUIERE CAMPO | ¿Electro Puno otorgo factibilidad, potencia, punto de entrega y corriente de cortocircuito? | Se proyecta 3 x 380/220 V, 60 Hz, suministro directo BT, con reservas y poderes de corte conservadores. | Puede cambiar acometida, protecciones generales o exigir subestacion. |
| D-010 | REQUIERE CAMPO | ¿Existe medicion de resistividad y puesta a tierra instalada? | Se disena una red equipotencial nueva y se exigira medicion antes de puesta en servicio. | Cambia numero/longitud de electrodos y tratamiento del suelo. |

## Seguridad y areas clasificadas

| ID | Estado | Duda | Criterio usado mientras tanto | Efecto de una respuesta distinta |
|---|---|---|---|---|
| D-011 | ABIERTA | ¿Modelos, alturas y posiciones exactas de venteos, bocas de llenado y bombas coinciden con los simbolos del DXF? | Se extraeran las posiciones visibles y se aplicaran los envolventes del CNE-U 120 como propuesta academica. | Puede desplazar limites de Zona 0/1/2. |
| D-012 | ABIERTA | ¿Un profesional competente revisara la clasificacion de areas antes de una eventual construccion? | Todos los planos se marcaran como proyecto academico y requeriran revision especializada. | Es requisito para convertir el anteproyecto en expediente constructivo. |
| D-013 | ABIERTA | ¿El sistema contra incendio cuenta con bomba electrica o solo equipos portatiles/alarma? | Se incluye alarma; la bomba queda condicionada al proyecto sanitario/contra incendio. | Puede crear una carga esencial y cambiar el grupo electrogeno. |

## Decisiones ya cerradas

- Proyecto individual; autor: Aquiles Taylor Ramos Yapo.
- Docente actual: Mg. Gregorio Meza Marocho.
- Propietario consignado en la fuente: Miguel Mamani Chuquicallata.
- Ubicacion: predio Reumita B-8/B-9, Caracoto, San Roman, Puno.
- Combustibles incluidos: Diesel B5 S-50, Gasohol Regular y Gasohol Premium.
- GLP y GNV: excluidos.
- El proyecto electrico es nuevo; el DXF es solo fuente arquitectonica/documental.
