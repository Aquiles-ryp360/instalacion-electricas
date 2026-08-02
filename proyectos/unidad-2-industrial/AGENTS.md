# Reglas del proyecto Unidad 2 industrial

Estas reglas complementan el `AGENTS.md` de la raiz. Antes de trabajar, leer
ambos archivos y `proyecto.yaml`.

## Fase actual

El proyecto esta en **preparacion** y la tipologia esta **por confirmar**.
Hospital, laboratorio, taller y grifo son alternativas, no decisiones.

## Acciones permitidas ahora

- Registrar la consigna, rubrica y acuerdos del docente.
- Guardar fuentes originales sin modificarlas.
- Verificar normativa en sitios oficiales y anotar fecha de consulta.
- Comparar tipologias y preparar cuestionarios.
- Crear plantillas vacias o con valores `null` / `por confirmar`.

## Acciones bloqueadas hasta elegir el caso

- Inventar dimensiones, ambientes, equipos, potencias, tension o fases.
- Crear cuadro de cargas, circuitos, conductores o protecciones como si fueran
  definitivos.
- Copiar los 380 V, 20 x 40 m, motores, factores o circuitos de
  `proyectos/nave-industrial/`.
- Clasificar un laboratorio, taller o grifo como lugar peligroso sin evidencia
  del proceso y sustancias.
- Generar planos o publicar archivos en `entregables/`.
- Activar el pipeline en `proyecto.yaml`.

## Fuentes de verdad

1. `proyecto.yaml`: estado, alcance y rutas canonicas.
2. `fuentes/`: consigna, croquis, arquitectura y fichas recibidas.
3. `datos/criterios-diseno.yaml`: parametros confirmados, siempre con fuente y
   estado.
4. `arquitectura/datos/`: geometria aprobada.
5. `diseno-electrico/datos/`: cargas y circuitos aprobados.
6. `documentacion/registro-decisiones.md`: acuerdos y supuestos autorizados.

Los otros proyectos sirven para aprender el flujo y las herramientas, no como
fuente de datos tecnicos.

## Norma y trazabilidad

- No escribir solo "cumple CNE". Citar norma, seccion/regla, resumen propio y
  evidencia del proyecto.
- Distinguir requisito obligatorio, guia facultativa y criterio de ingenieria.
- Verificar el CNE-U junto con sus modificaciones y el RNE vigente antes del
  expediente final.
- Si se elige hospital o grifo, detener el diseno hasta completar la normativa
  sectorial y la clasificacion de areas/cargas criticas.
- Toda decision tecnica requiere revision humana competente antes de pasar a
  `entregables/`.

## Cambio de fase

Solo despues de recibir la consigna y elegir el caso se debe:

1. Actualizar `tipologia.seleccionada` y `estado` en `proyecto.yaml`.
2. Registrar la decision y su evidencia.
3. Crear la arquitectura canonica.
4. Levantar equipos y cargas con fichas o supuestos aprobados.
5. Seleccionar las secciones del CNE-U y normas sectoriales aplicables.
6. Habilitar calculos; CAD continua bloqueado hasta validar arquitectura y
   clasificacion de riesgos.
