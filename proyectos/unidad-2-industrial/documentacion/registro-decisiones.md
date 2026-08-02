# Registro de decisiones

Agregar una entrada por decision. No reescribir el pasado; si una decision
cambia, registrar una nueva entrada que sustituya a la anterior.

## Plantilla

### DEC-000 - Titulo

- Fecha: AAAA-MM-DD
- Estado: propuesta | aprobada | reemplazada | rechazada
- Decide: por confirmar
- Fuente o evidencia: ruta, enlace o reunion
- Decision:
- Motivo:
- Alternativas consideradas:
- Impacto en arquitectura, calculos, planos y normativa:
- Supuestos autorizados:
- Pendientes:

## Decisiones registradas

### DEC-001 - Seleccion de tipologia

- Fecha: 2026-08-01
- Estado: aprobada por el estudiante; validacion docente pendiente
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: decision directa en conversacion con Codex
- Decision: desarrollar un proyecto de instalaciones electricas interiores para un grifo
- Alternativas consideradas: hospital/clinica, laboratorio, taller y grifo
- Impacto: define normativa especial, arquitectura, cargas, riesgos y alcance
- Supuestos autorizados: ninguno; no se han definido productos, arquitectura ni cargas
- Pendientes: confirmar alcance exacto y validar la alternativa con el docente

### DEC-002 - Tratamiento de las fuentes de WhatsApp

- Fecha: 2026-08-01
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: archivos entregados en la raiz y capturas indicadas por el estudiante
- Decision: organizar las fuentes en `fuentes/local/whatsapp/` y eliminar el ZIP original solo despues de verificar la copia
- Motivo: conservar evidencia del curso sin versionar material pesado o privado
- Alternativas consideradas: mantener el ZIP sin clasificar
- Impacto: la evidencia binaria permanece local; Git conserva inventario y transcripcion
- Supuestos autorizados: ninguno
- Pendientes: confirmar rubrica detallada

### DEC-003 - Actualizacion del docente

- Fecha: 2026-08-01
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: confirmacion directa y separatas del curso 2026
- Decision: registrar como docente actual al Mg. Gregorio Meza Marocho
- Motivo: hubo cambio de docente durante el curso
- Alternativas consideradas: conservar al docente de la primera etapa
- Impacto: portada, cuestionario, expediente y presentacion deben usar al docente actual
- Supuestos autorizados: ninguno
- Pendientes: ninguno

### DEC-004 - Autoria, propietario y caracter del trabajo

- Fecha: 2026-08-01
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: indicacion directa del estudiante y rotulo del DXF de referencia
- Decision: Aquiles Taylor Ramos Yapo es el unico autor del nuevo proyecto academico; Miguel Mamani Chuquicallata se consigna como propietario indicado en la documentacion tecnica de referencia facilitada por la DREM
- Motivo: distinguir el trabajo nuevo del estudiante de la procedencia del levantamiento arquitectonico
- Alternativas consideradas: presentar el DXF como proyecto electrico existente o atribuirle autoria al propietario
- Impacto: la portada mostrara autor, propietario, ubicacion y naturaleza academica en campos separados; no se afirmara que la DREM aprobo este proyecto electrico
- Supuestos autorizados: la escritura del nombre y la ubicacion se transcriben literalmente del plano fuente
- Pendientes: una constancia registral del propietario no forma parte de las fuentes recibidas

### DEC-005 - Alcance de combustibles

- Fecha: 2026-08-01
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: indicacion directa del estudiante y rotulos de los cuatro tanques del DXF
- Decision: incluir Diesel B5 S-50, Gasohol Regular y Gasohol Premium; excluir completamente GLP y GNV
- Motivo: el establecimiento representado almacena combustibles liquidos y el estudiante descarto expresamente GLP/GNV
- Alternativas consideradas: estacion mixta con GLP o GNV
- Impacto: cargas, areas clasificadas, detalles y normativa se desarrollaran solo para combustibles liquidos; se eliminaran textos genericos de GLP de los nuevos planos
- Supuestos autorizados: ninguno respecto de GLP/GNV
- Pendientes: fichas definitivas de surtidores y bombas

### DEC-006 - Uso del plano arquitectonico de referencia

- Fecha: 2026-08-01
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: `/home/kimdokja/Downloads/DISTRIBUCION Y CIRCULACION MIGUEL.dxf`
- Decision: conservar una copia inmutable del DXF y generar de ella bases derivadas; el nuevo diseno electrico no modificara ni se presentara como parte del expediente original
- Motivo: mantener trazabilidad y permitir un proyecto electrico nuevo sobre una arquitectura existente
- Alternativas consideradas: editar directamente el original
- Impacto: las laminas A-01, S-01 y M-01 se separaran en `build/`; toda interpretacion geometrica llevara fuente, estado y confianza
- Supuestos autorizados: interpretar la geometria en metros conforme a cotas y escala impresas, pese a que `$INSUNITS` declara milimetros
- Pendientes: comprobar cotas sensibles contra una copia acotada o medicion de campo si estuviera disponible

### DEC-007 - Suministro electrico de diseno

- Fecha: 2026-08-01
- Estado: propuesta academica adoptada
- Decide: criterio tecnico para continuar; pendiente de concesionaria
- Fuente o evidencia: sistemas de baja tension publicados por Electro Puno y ubicacion del predio en Caracoto
- Decision: desarrollar el anteproyecto en baja tension, 3 x 380/220 V, 60 Hz, 3F+N+PE, sin subestacion propia
- Motivo: es una configuracion local tecnicamente plausible y permite dimensionar el caso academico sin fingir una factibilidad inexistente
- Alternativas consideradas: 3 x 220 V o suministro en media tension con subestacion
- Impacto: todos los cuadros y unifilares indicaran que potencia disponible, punto de entrega y corriente de cortocircuito deben validarse antes de construir
- Supuestos autorizados: suministro directo en BT y separacion de N/PE aguas abajo del origen
- Pendientes: factibilidad, calibre de acometida, sistema exacto de la red y corriente de cortocircuito disponible

### DEC-008 - Respaldo de cargas criticas

- Fecha: 2026-08-01
- Estado: propuesta academica adoptada
- Decide: criterio tecnico para continuar
- Fuente o evidencia: presencia del rotulo `G.E.` en el DXF y necesidad operativa del caso
- Decision: incluir grupo electrogeno con transferencia y UPS para control, POS, CCTV, comunicaciones, alarma y alumbrado critico; su potencia se calculara a partir de esas cargas
- Motivo: mejorar continuidad y seguridad operativa
- Alternativas consideradas: solo alumbrado autonomo de emergencia o respaldo total del establecimiento
- Impacto: se definira un tablero de emergencia separado y se verificara que el equipo quede fuera de areas clasificadas
- Supuestos autorizados: el respaldo es una decision de diseno, no una obligacion general atribuida por EM.010 a todo grifo
- Pendientes: fichas finales, autonomia y ubicacion revisada

### DEC-009 - Gestion de indicaciones y dudas

- Fecha: 2026-08-01
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: indicacion directa del estudiante
- Decision: tratar los comentarios esporadicos como pautas acumulativas y continuar el trabajo; registrar dudas no criticas en `documentacion/dudas-pendientes.md`
- Motivo: evitar interrupciones y conservar temas para una revision posterior del estudiante
- Alternativas consideradas: detener el avance ante cada dato faltante
- Impacto: los supuestos continuaran identificados y ninguna duda no resuelta se ocultara en el expediente
- Supuestos autorizados: usar criterios tecnicos prudentes cuando no alteren el alcance definido
- Pendientes: el estudiante revisara el archivo de dudas cuando regrese

### DEC-010 - Rotulo institucional de los planos

- Fecha: 2026-08-01
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: indicacion directa del estudiante y portadas del proyecto Aquiles de la primera unidad
- Decision: adaptar todos los rotulos al formato academico de la Universidad Nacional del Altiplano, Facultad de Ingenieria Mecanica Electrica, Electronica y Sistemas, Escuela Profesional de Ingenieria Mecanica Electrica
- Motivo: identificar correctamente la institucion, el curso y la autoria del nuevo trabajo
- Alternativas consideradas: conservar el rotulo empresarial del DXF fuente o usar un cajetin generico
- Impacto: cada lamina mostrara UNAP, curso, docente actual, estudiante, titulo, propietario de referencia, ubicacion, codigo, escala, fecha y advertencia academica
- Supuestos autorizados: usar el nombre institucional ya confirmado en las portadas de la primera unidad
- Pendientes: codigo de estudiante y semestre academico, si el docente exige esos campos; no se inventaran firma, sello ni CIP

### DEC-011 - Dimensionamiento electrico base del anteproyecto

- Fecha: 2026-08-01
- Estado: propuesta academica calculada
- Decide: criterio tecnico reproducible para continuar
- Fuente o evidencia: `diseno-electrico/datos/cargas.yaml`, catalogos listados en `documentacion/catalogo-equipos-diseno.md` y `scripts/calcular_proyecto.py`
- Decision: proponer suministro de 50 kVA con interruptor principal 80 A, alimentador Cu 4 x 35 mm2 + PE 16 mm2 y grupo electrogeno standby de 37.5 kVA corregido por altitud
- Motivo: despues de verificar el alumbrado interior con la EM.010, la maxima demanda es 33.31 kVA y 39.97 kVA con 20 % de reserva; la corriente maxima de fase es 61.88 A y el escenario de arranque de emergencia exige 27.69 kVA disponibles en sitio
- Alternativas consideradas: suministro de 40 kVA sin reserva y respaldo total del establecimiento
- Impacto: fija la base del unifilar, cuadros de carga y planos IE-01 a IE-05
- Supuestos autorizados: arranque secuencial de bombas sumergibles, altitud de referencia de Caracoto 3830 m y potencias de familias comerciales comparables
- Pendientes: reemplazar por placas, factibilidad de Electro Puno, Icc, selectividad y confirmacion del fabricante del grupo antes de construir

### DEC-012 - Formato del documento de entrega

- Fecha: 2026-08-02
- Estado: aprobada
- Decide: Aquiles Taylor Ramos Yapo
- Fuente o evidencia: indicacion directa del estudiante y expediente Aquiles de la primera unidad
- Decision: usar para el informe el formato grafico del expediente Aquiles de la primera unidad: papel carta, portada azul/verde, encabezado enmarcado, titulos rojos y pie tecnico
- Motivo: mantener continuidad entre las dos unidades del curso sin imponer un formato institucional distinto al ya utilizado
- Alternativas consideradas: formato A4 institucional nuevo
- Impacto: `expediente/preambulo.tex` y la portada reproducen el lenguaje visual de la primera unidad con los datos y contenido del grifo
- Supuestos autorizados: el rotulo de las laminas conserva la identidad UNAP y los datos ya confirmados
- Pendientes: el docente puede pedir ajustes de formato finales

### DEC-013 - Calidad vectorial de planos y expediente

- Fecha: 2026-08-02
- Estado: aprobada y verificada
- Decide: correccion solicitada por Aquiles Taylor Ramos Yapo
- Fuente o evidencia: los primeros PDF contenian una sola imagen JPEG de 2150 x 1519 px a 130 dpi y se veian borrosos al ampliar
- Decision: generar cada plano directamente como PDF vectorial A1 y unirlos sin rasterizacion; reservar PNG de 220 dpi solo para vista previa
- Motivo: preservar lineas y textos nitidos en pantalla, ampliacion e impresion
- Alternativas consideradas: aumentar solamente la resolucion del PNG
- Impacto: las seis laminas tienen tamano A1, cero imagenes raster incrustadas y el expediente incorpora esas paginas vectoriales
- Supuestos autorizados: ninguno
- Pendientes: comprobar la impresion fisica con el ploteador que se vaya a usar

### DEC-014 - Metrados y presupuesto referencial

- Fecha: 2026-08-02
- Estado: propuesta academica calculada
- Decide: criterio tecnico reproducible para completar la consigna
- Fuente o evidencia: longitudes de `diseno-electrico/datos/cargas.yaml`, cantidades de `diseno-electrico/datos/alumbrado.yaml`, planos IE-01 a IE-06 y referencias registradas en `presupuesto/datos/partidas.yaml`
- Decision: metrar rutas, conductores, tableros, protecciones, alumbrado, dispositivos, PAT/rayo, respaldo y pruebas; excluir la compra de tanques, surtidores y STP, pero incluir sus conexiones electricas
- Motivo: la pizarra exige metrados y presupuesto; los equipos de proceso no cuentan con modelo ni cotizacion definitiva
- Alternativas consideradas: omitir el presupuesto o inventar costos definitivos de equipos de hidrocarburos
- Impacto: se genera un presupuesto con 46 partidas, costo directo de S/ 283,442.76 y total referencial con IGV de S/ 394,665.70
- Supuestos autorizados: 10 % de holgura en rutas/conductores y costos instalados de anteproyecto, todos etiquetados por tipo de precio
- Pendientes: proformas vigentes, recorrido de campo, flete, marcas/certificados y cantidades conforme a obra antes de una compra real

### DEC-015 - Cierre y paquete academico de revision

- Fecha: 2026-08-02
- Estado: aprobada para revision academica; no constructiva
- Decide: cumplimiento de la consigna y preparacion para sustentacion
- Fuente o evidencia: `documentacion/auditoria-cierre-academico.md`
- Decision: cerrar en `build/` un paquete con expediente en formato Aquiles, guia personal, seis planos vectoriales A1/DXF, cuadro de cargas, metrados/presupuesto y dudas pendientes
- Motivo: disponer de una entrega coherente e imprimible sin ocultar datos que requieren campo o profesional competente
- Alternativas consideradas: copiar prematuramente a `entregables/` o declarar el anteproyecto como expediente de obra
- Impacto: el paquete se puede revisar e imprimir; el pipeline de publicacion permanece deshabilitado
- Supuestos autorizados: ninguno adicional
- Pendientes: revision del estudiante, rubrica final e impresion de prueba; para obra siguen pendientes factibilidad, placas, campo y revision profesional
