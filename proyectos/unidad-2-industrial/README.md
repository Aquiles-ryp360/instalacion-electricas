# Unidad 2: instalacion electrica no residencial

## Estado actual

Carpeta preparada para iniciar el nuevo proyecto del curso. La tipologia aun no
esta elegida y no existen datos suficientes para calcular o dibujar una
instalacion.

Opciones abiertas:

- hospital o clinica;
- laboratorio educativo, sanitario o industrial;
- taller;
- grifo o estacion de servicio.

La guia comparativa esta en
[`referencias/normativa/documentacion/guia-tipologias-no-residenciales.md`](../../referencias/normativa/documentacion/guia-tipologias-no-residenciales.md).

## Como debe empezar una nueva sesion de IA

1. Leer el [`AGENTS.md`](AGENTS.md) de esta carpeta y el de la raiz.
2. Leer [`proyecto.yaml`](proyecto.yaml); no deducir el estado por otros
   archivos.
3. Revisar [`documentacion/checklist-arranque.md`](documentacion/checklist-arranque.md).
4. Pedir o localizar la consigna, rubrica, plano y fichas de equipos.
5. Registrar decisiones en
   [`documentacion/registro-decisiones.md`](documentacion/registro-decisiones.md).
6. Mantener `null` o `por confirmar` donde no exista evidencia.

## Estructura

```text
unidad-2-industrial/
├── AGENTS.md
├── proyecto.yaml
├── fuentes/                    documentos recibidos, sin modificar
├── arquitectura/datos/         geometria aprobada
├── diseno-electrico/datos/     cargas y circuitos aprobados
├── datos/                      criterios y parametros
├── documentacion/              decisiones, guias y matriz normativa
├── expediente/                 fuentes editables del informe
├── entregables/                solo resultados revisados
├── tests/                      validaciones especificas futuras
└── archivo/                    antecedentes fuera del flujo activo
```

## Estado de automatizacion

El pipeline esta deshabilitado intencionalmente. Se habilitara despues de
confirmar la tipologia, validar la arquitectura, completar cargas y decidir si
se reutiliza el motor comun o se necesita una extension especifica.

El proyecto existente `nave-industrial` puede consultarse para entender la
estructura de un flujo industrial, pero sus dimensiones, tensiones, cargas,
circuitos y factores no son datos de este proyecto.
