# Registro de decisiones

Formato: `DEC-NNN | fecha | decision | estado`.

## DEC-001 | 2026-08-02 | Borrar `proyectos/nave-industrial`

- Motivacion: el estudiante Renzo reemplaza el proyecto industrial previo por
  un proyecto propio de unidad 2.
- Se elimina `proyectos/nave-industrial/` del repositorio.
- Estado: ejecutado en el commit de creacion del proyecto renzo-industrial.

## DEC-002 | 2026-08-02 | Crear proyecto `renzo-industrial`

- El estudiante Renzo Gabriel Mamani Galindo desarrolla la segunda unidad sobre
  una estacion de servicio (grifo).
- Fuentes: `PLANO DE UBICACION.dwg` y `PLANO DE DISTRIBUCION.dwg`.
- El plano electrico y las canalizaciones no existen en la fuente; forman parte
  del diseno a desarrollar.
- Estado: ejecutado.

## DEC-003 | 2026-08-02 | Tipologia: grifo / estacion de servicio

- Confirmado por el estudiante. GLP y GNV excluidos.
- Combustibles liquidos: Diesel B5-S50, Gasohol Regular, Gasohol Premium.
- Estado: vigente.

## DEC-004 | 2026-08-02 | Nivel de tension 380/220 V trifasico 3F+N+PE

- Criterio academico adoptado por el estudiante para el diseno.
- Requiere factibilidad y corriente de cortocircuito de la concesionaria.
- Estado: vigente (criterio adoptado).

## DEC-005 | 2026-08-02 | Sistema de puesta a tierra TN-S

- Conductores N y PE separados aguas abajo del origen de la instalacion.
- Estado: criterio adoptado; configuracion final condicionada a factibilidad.

## DEC-006 | 2026-08-02 | Rotulo de planos propio de Renzo

- Se crea `datos/rotulo-planos.yaml` con datos propios del estudiante (UNAP,
  docente Meza Marocho) y NO se reutilizan los del proyecto hermano.
- Propietario, direccion y distrito/provincia/departamento quedan `por
  confirmar`; no se inventa firma, sello, CIP ni aprobacion profesional.
- Se definen 6 laminas IE-01..IE-06 para el anteproyecto.
- Estado: vigente.

## DEC-007 | 2026-08-02 | Juego de planos de anteproyecto IE-01..IE-06

- Se crea `scripts/generar_planos_grifo_renzo.py`, motor propio que dibuja la
  arquitectura desde `layout-grifo.json` (coordenadas locales) y superpone el
  diseno electrico (alumbrado, fuerza, emergencia, PAT, pararrayo y
  clasificacion de areas como propuesta academica).
- Se excluye el poligono `lote_total` (bounding box aproximado) para no salir
  del marco A1; solo se grafica el lote a ejecutar.
- Salida: DXF + PNG (220 dpi) + PDF vectorial A1 por lamina y un PDF combinado
  (`planos-electricos-grifo-renzo.pdf`), todo en `build/`.
- Estado: ejecutado; pendiente de revision humana antes de publicar en
  `entregables/`.
