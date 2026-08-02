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

## DEC-008 | 2026-08-02 | Auditoria final del anteproyecto

- Verificacion independiente de calculos (MD, reserva, desbalance, I fase,
  dV 3F y grupo de emergencia) contra `resumen-calculos.json`: todos PASS.
- Verificacion de citas CNE-U contra el PDF oficial por coordenadas:
  Tabla 2 (ampacidades XLPE/EPR 90 C, 3 conductores: valores B1/D del script
  coinciden valor a valor) y Tabla 14 (Industrial/Comercial 25 W/m2, fd 100%),
  reglas 050-102, 030-002 y 060-712.
- Verificacion de trazabilidad: sha256 de `cargas.yaml` == sha256 del
  `manifest.json` de planos.
- Veredicto: aceptable como anteproyecto academico; hallazgos menores
  (proyecto.yaml desactualizado - corregido; propietario/ubicacion/suministro
  por confirmar; catalogos referenciales; clasificacion de areas por revisar).
- Estado: ejecutado.

## DEC-009 | 2026-08-02 | Expediente academico completo compilado

- Se crean `expediente/main.tex`, `preambulo.tex` y 9 capitulos
  (portada, memoria descriptiva, calculos, especificaciones, seguridad y
  normativa, cronograma, metrados y presupuesto, planos y conclusiones).
- Datos numericos alimentados desde `generated/datos` (macros + tablas
  CIRCUITOSTAB/ALIMENTADORESSTAB), sin valores duplicados a mano.
- Planos anexados con `\includepdf` al final (6 laminas en orientacion
  horizontal).
- Salida: `build/renzo-industrial/expediente/expediente-renzo-industrial.pdf`
  (23 paginas). Compilacion: 2 pasadas pdflatex; solo overfull benignos
  (< 5 pt).
- Estado: ejecutado; pendiente revision humana antes de publicar.

## DEC-010 | 2026-08-02 | Datos confirmados del estudiante (cuestionario B1-B11)

- El estudiante respondio el cuestionario (`documentacion/cuestionario-estudiante.md`).
- Confirmados: codigo 228447, semestre 2026-II, entrega 2026-08-03,
  propietario Miguel Mamani Chuquicallata, direccion Predio Rustico Reumita
  Parcela B-8 y B-9 Lado Este (comunidad campesina San Francisco de
  Buenavista, carretera Juliaca-Puno), distrito/provincia San Roman,
  departamento Puno, altitud 3830 m s.n.m.
- Delegados al diseno (criterio adoptado, registrado en `criterios-diseno.yaml`
  y `cargas.yaml`): empresa distribuidora Electro Puno (asumida), Icc 10 kA
  (supuesto), estimacion de alumbrado/tomacorrientes/equipos segun planos,
  mantener Cummins C30D6, mantener cargas criticas y UPS.
- Mejoras solicitadas y aplicadas: memoria de calculo con Icc/selectividad y
  tabla de parametros, presupuesto con cantidades y totales, cronograma por
  semanas, mas citas normativas y tabla de parametros de diseno.
- Pendiente para publicar: factibilidad/Icc de la concesionaria, placas reales
  y revision humana competente.
- Estado: aplicado.
