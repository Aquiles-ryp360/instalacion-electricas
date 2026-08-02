# Renzo industrial - unidad 2: estacion de servicio (grifo)

Anteproyecto academico nuevo de instalaciones electricas interiores para una
estacion de servicio de combustibles liquidos. Autor: Renzo Gabriel Mamani
Galindo. Docente: Gregorio Meza Marocho.

## Fuentes

- `fuentes/local/cad/PLANO DE UBICACION.dwg` (CAD-001)
- `fuentes/local/cad/PLANO DE DISTRIBUCION.dwg` (CAD-002)

Los archivos DWG son la evidencia original y no se modifican. El plano
electrico y las canalizaciones no existen en la fuente: forman parte del
diseno a desarrollar.

## Estado

- Anteproyecto desarrollado y auditado (2026-08-02).
- Fuente CAD incorporada con huella verificada.
- Arquitectura extraida en `arquitectura/datos/layout-grifo.json`.
- Diseno electrico completo: cargas, calculos (PASS), 22 circuitos y
  3 alimentadores en `diseno-electrico/datos/cargas.yaml`.
- Planos de anteproyecto IE-01..IE-06 generados en `build/renzo-industrial/cad/planos/`
  con `manifest.json` (trazabilidad sha256 a cargas.yaml).
- Expediente academico compilado en `build/renzo-industrial/expediente/expediente-renzo-industrial.pdf`
  (23 paginas: portada, indice, 8 capitulos y planos anexados).
- No publicado en `entregables/`: pendiente confirmacion de ubicacion,
  propietario, suministro, factibilidad e Icc, y revision humana competente
  (incluye clasificacion de areas peligrosas como propuesta academica).

## Entregables pendientes

Ver `documentacion/dudas-pendientes.md` para la lista completa de confirmaciones
requeridas antes de copiar `build/` a `entregables/`.

## Como empezar una nueva sesion

1. Leer el `AGENTS.md` de esta carpeta y el de la raiz.
2. Leer `proyecto.yaml`; no deducir el estado por otros archivos.
3. Revisar `documentacion/registro-decisiones.md` y `documentacion/dudas-pendientes.md`.
4. Registrar decisiones nuevas en el registro de decisiones.
5. Mantener `null`/`por confirmar` o un criterio adoptado explicito donde no
   exista evidencia; nunca presentarlo como dato observado.
