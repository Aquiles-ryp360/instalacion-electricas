# Proyecto Renzo

Expediente de instalaciones electricas interiores para una vivienda
unifamiliar de tres pisos en Capachica, Puno. El punto de entrada del proyecto
es `proyecto.yaml`; no se debe elegir una entrada por nombres como `v1`,
`nuevo` o `final`.

El proyecto conserva fuentes, datos canonicos, documentacion de trabajo y
entregables revisados en carpetas separadas. La carpeta antigua
`RENZO-REQUERIMIENTOS` fue integrada en
`documentacion/requerimientos/`.

## Estructura activa

```text
fuentes/             archivos originales recibidos; no se sobrescriben
arquitectura/        tres layouts JSON canonicos y su interpretacion
diseno-electrico/    modelo electrico canonico y fuente editable del unifilar
datos/               parametros del proyecto, normativa y proveedores
expediente/          fuentes LaTeX del documento tecnico
documentacion/       borradores, reportes y decisiones de coordinacion
  requerimientos/    requerimientos y terminos de referencia integrados
scripts/             automatizacion exclusiva de este proyecto
tests/               comprobaciones de calculo
entregables/         archivos revisados y publicados
archivo/             iteraciones historicas fuera del flujo activo
```

Los archivos regenerables se escriben en `build/renzo/`, fuera de esta
carpeta y sin seguimiento de Git.

## Entradas canonicas

- Arquitectura: `arquitectura/datos/piso-1.json`, `piso-2.json` y
  `piso-3.json`.
- Diseno electrico: `diseno-electrico/datos/modelo-electrico.json`.
- Parametros: `datos/parametros-proyecto.yaml`.
- Requerimientos: `documentacion/requerimientos/`.
- Expediente: `expediente/main.tex`.

Las versiones anteriores se conservan en `archivo/` solo como referencia. No
son entradas validas para el pipeline.

## Flujo de trabajo

1. Actualizar entradas canonicas en `arquitectura/`, `diseno-electrico/` o
   `datos/`.
2. Registrar contexto, acuerdos o documentos recibidos en `documentacion/`.
3. Ejecutar pruebas del proyecto antes de regenerar entregables.
4. Ejecutar el pipeline y revisar los resultados generados en `build/renzo/`.
5. Copiar a `entregables/` solo archivos revisados tecnica y visualmente.

## Ejecucion

Desde la raiz del repositorio:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto renzo
python3 -m pytest -q proyectos/renzo/tests
```

El pipeline genera arquitectura, planos electricos, diagramas y el PDF del
expediente en `build/renzo/`. Copiar resultados a `entregables/` requiere una
revision tecnica y visual previa.

## Documentos clave

- `documentacion/requerimientos/requerimiento-renzo.pdf`: requerimiento
  consolidado del proyecto.
- `documentacion/requerimientos/terminos-referencia.pdf`: terminos de
  referencia.
- `entregables/expediente.pdf`: expediente publicado, cuando exista una
  version revisada.
- `documentacion/coordinacion.md`: acuerdos y cambios relevantes del proceso.

## Alcance actual

La estructura de datos ya tiene una unica version activa. Los requerimientos
estan centralizados dentro de `documentacion/requerimientos/`. Los generadores
CAD siguen siendo especificos de Renzo y se depuraran en una fase posterior
para extraer logica reutilizable hacia `herramientas/`.
