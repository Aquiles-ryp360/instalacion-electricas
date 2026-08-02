# Reglas del proyecto Renzo industrial (unidad 2)

Estas reglas complementan el `AGENTS.md` de la raiz. Antes de trabajar, leer
ambos archivos y `proyecto.yaml`.

## Fase actual

El proyecto esta en **etapa inicial de diseno**. Se incorporaron los dos DWG
(ubicacion y distribucion) como fuentes inmutables en `fuentes/local/cad/` y se
extrajo una arquitectura preliminar en `arquitectura/datos/layout-grifo.json`.
El plano electrico y las canalizaciones no existen en la fuente: son parte del
diseno a desarrollar. GLP y GNV estan excluidos.

## Acciones permitidas ahora

- Guardar fuentes originales sin modificarlas.
- Registrar decisiones, supuestos y consigna en `documentacion/`.
- Confirmar ubicacion, propietario y parametros de suministro con el estudiante.
- Verificar normativa (CNE-U, RNE, normativa sectorial de combustibles) en
  sitios oficiales y anotar fecha de consulta.
- Extraer y validar la arquitectura canonica con trazabilidad al DWG.
- Definir cargas por ambiente y por equipo con datos observados o criterios
  adoptados claramente identificados.
- Clasificar areas peligrosas como propuesta academica con su regla normativa
  y advertencia de revision competente.
- Desarrollar calculos, cuadros, canalizaciones y planos de anteproyecto en
  `build/`.
- Seleccionar potencias de catalogos comparables cuando no exista placa,
  registrando fabricante/familia, fecha y margen usado.

## Acciones bloqueadas o condicionadas

- Presentar como observado cualquier dato que en realidad sea un criterio
  adoptado o un supuesto.
- Crear cuadro de cargas, circuitos, conductores o protecciones como si fueran
  definitivos.
- Copiar tensiones, cargas, factores, circuitos o planos de
  `proyectos/unidad-2-industrial/` (proyecto de otro estudiante) ni de
  `proyectos/nave-industrial/` (eliminado).
- Dibujar limites definitivos de zonas peligrosas sin trazar su regla normativa
  y sin advertir la necesidad de revision competente.
- Publicar archivos en `entregables/` antes de compilarlos y revisarlos en
  `build/`.
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
- Por tratarse de un grifo, no cerrar ni publicar el diseno sin completar la
  normativa sectorial y revisar la clasificacion de areas/cargas criticas.
- Toda decision tecnica requiere revision humana competente antes de pasar a
  `entregables/`.

## Siguiente cambio de fase

Antes de activar el pipeline de entregables se debe:

1. Confirmar ubicacion, propietario, suministro y empresa distribuidora.
2. Revisar `documentacion/dudas-pendientes.md` con el estudiante.
3. Sustituir familias de catalogo por placas cuando se reciban.
4. Obtener factibilidad, punto de entrega e Icc de la concesionaria.
5. Verificar cotas, alturas, PAT y areas clasificadas en campo.
6. Ejecutar revision humana competente de calculos, CAD y expediente.
7. Solo despues de esa revision copiar desde `build/` a `entregables/`.
