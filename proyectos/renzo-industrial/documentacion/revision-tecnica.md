# Revision tecnica del anteproyecto - unidad 2 (grifo Renzo)

Fecha: 2026-08-02
Estado: ejecutado por IA; PENDIENTE de revision humana competente antes de
publicar en `entregables/`.

Alcance: verificar la mejora integral solicitada (7 puntos), listar los cambios
realizados y justificar cada modificacion.

## 1. Resumen de verificacion del pipeline

| Etapa | Script | Estado |
| --- | --- | --- |
| Calculos electricos | `scripts/calcular_proyecto.py` | PASS (PI 18,85 kW; MD 15,67 kW / 18,83 kVA; 22 circuitos; 3 alimentadores; servicio 30 kVA; ITM 50 A) |
| Iluminacion | `scripts/calcular_iluminacion.py` | PASS (38 luminarias; 2202 W; LPD prom 3,21 W/m2; todos los ambientes cumplen) |
| Fragmentos expediente | `scripts/generar_fragmentos_expediente.py` | PASS |
| Layout base | `scripts/generar_layout_base.py` | PASS (layout-base.pdf vectorial) |
| Planos electricos | `scripts/generar_planos_grifo_renzo.py` | PASS (6 laminas; entity_counts 143,145,121,102,69,99) |
| Compilacion expediente | pdflatex (2 pasadas) | PASS (44 paginas; ToC completo; sin warnings criticos) |

## 2. Cambios realizados y justificacion tecnica

### 2.1 Planos con jerarquia de espesores y simbolos normalizados

- `generar_planos_grifo_renzo.py`: capas ordenadas por lineweight (MARCO 50,
  ARQ_REFERENCIA 40, IE_TIERRA/IE_ZONA_1 40, IE_FUERZA/IE_EMERGENCIA/IE_RAYO 35,
  IE_ALUMBRADO/IE_CANALIZACION 30, IE_TABLA 18, textos 20). Justificacion:
  jerarquia visual del dibujo (marco > referencia > instalaciones) y trazado
  legible en impresion.
- Se corrigio `lineweight: 22` (invalido en DXF, lanzaba DXFValueError) -> 20.
- Simbolos IEC: `add_luminaire` (circulo + aspa; "E" si emergencia),
  `add_outlet` (semicirculo), `add_panel`. Justificacion: normalizacion segun
  simbologia IEC para lectura universal.
- Arquitectura dibujada desde `layout-grifo.json` (lote, bbox, ambientes
  4x3 m, tanques, surtidores). Justificacion: coherencia geometrica con el
  plano de distribucion fuente.
- Render con `Configuration(lineweight_scaling=2.0, min_lineweight=0.18)`,
  PNG 220 dpi (3638x2571) y PDF A1 vectorial. Justificacion: nitidez en
  impresion A1 y zoom sin perdida.

### 2.2 Seccion "Planos Base u Originales" (trazabilidad)

- Nuevo `expediente/capitulos/07-planos-base.tex`: registro CAD-001 (PLANO DE
  UBICACION.dwg) y CAD-002 (PLANO DE DISTRIBUCION.dwg) con nombre, codigo,
  escala, fecha, version, descripcion, observaciones y huella sha256.
- Justificacion: cumplir trazabilidad de la fuente inmutable y evidenciar que
  el diseno parte de los DWG recibidos.
- Incluye figura `\IlustracionLayout` (reconstruccion vectorial generada por
  `generar_layout_base.py`). Justificacion: presentar el layout base sin
  depender de visor DWG.

### 2.3 Memoria de calculo de iluminacion

- Nuevo `diseno-electrico/datos/iluminacion-ambientes.yaml` (7 ambientes) y
  `scripts/calcular_iluminacion.py`: metodo de lumenes con factor de utilizacion
  interpolado de tablas y FM 0,80/0,70.
- Nuevo `expediente/capitulos/03-iluminacion.tex`: metodologia con ecuaciones,
  ejemplo completo con macros `\IllumEj*`, tabla `\ILLUMTAB` por ambiente,
  verificacion de LPD y criterios normativos (NTP ISO 8995 / EM.010).
- Resultado: 38 luminarias, 2202 W (~2,2 kW), LPD promedio 3,21 W/m2, todos los
  ambientes cumplen. Justificacion: dimensionar alumbrado y verificar densidad
  de potencia permitida.

### 2.4 Verificacion normativa expresa

- `02-calculos.tex`: nueva seccion "Verificacion normativa" con tabla que cita
  CNE-U (Reglas 030-002, 030-004/Tabla 2, 050-104, 050-102, 050-210/Tabla 14,
  060-712/Tabla 16, 120-000/Seccion 110, 050-100) y EM.010 (arts. 6 y 11.1),
  con resumen y evidencia del proyecto. Justificacion: no escribir solo
  "cumple CNE", sino citar norma, seccion, resumen propio y evidencia.

### 2.5 Coherencia memoria-planos

- `05-planos.tex`: nueva seccion "Coherencia entre memoria y planos" con tabla
  de circuitos (F-/L-/A1-/S-), tableros, puesta a tierra y zonas.
- Se verifico que DESP=800 W coincide con lamina L-01 y PAT=640 W <= L-02
  (800 W); total iluminacion 2202 W < capacidad de los circuitos de alumbrado.

### 2.6 Mejora de presentacion

- `main.tex`: capitulos reordenados (III iluminacion, IX planos base) con
  `\documentfootertext` por capitulo y `\clearpage`; `\input` del fragmento
  `generated/iluminacion-datos`.
- `preambulo.tex`: `amssymb` (para \checkmark), macro `\IlustracionLayout`,
  `headheight` 15 -> 22 pt (corrige warning fancyhdr).
- `01-memoria-descriptiva.tex`: seccion "Estructura del documento".
- `06-conclusiones.tex`: 21 items con iluminacion y trazabilidad.

## 3. Hallazgos pendientes (no bloquean el anteproyecto academico)

1. Factibilidad e Icc real de la concesionaria (Electro Puno asumida; Icc 10 kA
   supuesto).
2. Placas reales de equipos (catalogos referenciales).
3. Clasificacion de areas peligrosas: propuesta academica, requiere revision
   competente.
4. Propietario/ubicacion confirmados en cuestionario (DEC-010) pero suministro
   y punto de entrega pendientes.
5. Referencias cruzadas adicionales entre capitulos (opcional).
6. Cotas, alturas y PAT por verificar en campo.

## 4. Veredicto

Aceptable como anteproyecto academico. Los cambios de la mejora integral estan
implementados, compilados (44 paginas) y trazables. Antes de copiar de
`build/` a `entregables/` se requiere revision humana competente conforme a
`AGENTS.md`.
