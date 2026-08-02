# Reglas del proyecto Unidad 2 industrial

Estas reglas complementan el `AGENTS.md` de la raiz. Antes de trabajar, leer
ambos archivos y `proyecto.yaml`.

## Fase actual

El proyecto esta en **revision del paquete academico completo**. Los calculos
electrico, de alumbrado y de metrados/presupuesto estan en PASS; existen seis
laminas A1 vectoriales, expediente con el formato grafico Aquiles, cronograma y
guia de sustentacion en `build/`. GLP y GNV estan excluidos. Para una eventual
obra siguen faltando fichas definitivas, factibilidad de Electro Puno,
verificacion de campo y revision profesional de areas clasificadas.

## Acciones permitidas ahora

- Registrar la consigna, rubrica y acuerdos del docente.
- Guardar fuentes originales sin modificarlas.
- Verificar normativa en sitios oficiales y anotar fecha de consulta.
- Preparar y completar el cuestionario y el archivo de dudas del grifo.
- Separar, limpiar, renderizar y medir copias derivadas del DXF en `build/`.
- Crear la arquitectura canonica con trazabilidad al DXF.
- Desarrollar calculos, cuadros y planos de anteproyecto con datos observados,
  calculados o criterios adoptados claramente identificados.
- Seleccionar potencias de catalogos comparables cuando no exista placa,
  registrando fabricante/familia, fecha y margen usado.
- Regenerar calculos, planos PDF/DXF y expediente desde las entradas canonicas.
- Corregir observaciones visuales sin rasterizar los PDF de planos.

## Acciones bloqueadas o condicionadas

- Presentar como observado cualquier dimension, equipo, potencia, tension o
  fase que en realidad sea un criterio adoptado.
- Crear cuadro de cargas, circuitos, conductores o protecciones como si fueran
  definitivos.
- Copiar los 380 V, 20 x 40 m, motores, factores o circuitos de
  `proyectos/nave-industrial/`.
- Dibujar limites definitivos de zonas peligrosas sin trazar su regla normativa
  y sin advertir la necesidad de revision competente. Se permite una propuesta
  academica basada en las fuentes geometricas disponibles.
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
- Verificar el CNE-U junto con sus modificaciones y el RNE vigente antes del
  expediente final.
- Por tratarse de un grifo, no cerrar ni publicar el diseno sin completar la
  normativa sectorial y revisar la clasificacion de areas/cargas criticas.
- Toda decision tecnica requiere revision humana competente antes de pasar a
  `entregables/`.

## Siguiente cambio de fase

Antes de activar el pipeline de entregables se debe:

1. Revisar `documentacion/dudas-pendientes.md` con el estudiante.
2. Sustituir familias de catalogo por placas cuando se reciban.
3. Obtener factibilidad, punto de entrega e Icc de Electro Puno.
4. Verificar cotas, alturas, PAT y areas clasificadas en campo.
5. Ejecutar revision humana competente de calculos, CAD y expediente.
6. Solo despues de esa revision copiar desde `build/` a `entregables/`.
