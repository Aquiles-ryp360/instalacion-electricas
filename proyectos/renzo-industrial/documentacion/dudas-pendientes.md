# Dudas pendientes

Preguntas que no deben detener el avance del anteproyecto, pero deben
responderse antes de publicar entregables.

Estado 2026-08-02: el anteproyecto (calculos, planos y expediente) esta
compilado y auditado en `build/`. El estudiante respondio el cuestionario;
quedan pendientes solo los datos que requieren la concesionaria, placas reales
o verificacion de campo.

## Ubicacion y propietario (CONFIRMADO el 2026-08-02)

- [x] Confirmar distrito (San Roman), provincia (San Roman), departamento
      (Puno) y direccion (Predio Rustico Reumita Parcela B-8 y B-9 Lado Este,
      comunidad campesina San Francisco de Buenavista, carretera Juliaca-Puno).
- [x] Confirmar propietario / razon social: Miguel Mamani Chuquicallata.
- [x] Codigo de estudiante: 228447; semestre 2026-II; entrega 2026-08-03.
- [x] Altitud: 3830 m s.n.m.

## Suministro

- [ ] Empresa distribuidora y punto de entrega (se asume Electro Puno).
- [ ] Factibilidad y corriente de cortocircuito (Icc) en el punto de entrega
      (se asume 10 kA para el anteproyecto).
- [ ] Potencia contratada / demanda prevista de la concesionaria (se propone
      30 kVA).

## Plano electrico y canalizaciones

- [x] No existen en la fuente; se confirmo el alcance: el curso pide el
      expediente con los planos del anteproyecto (6 laminas IE-01..IE-06).

## Cargas y equipos

- [ ] Potencia nominal real de dispensadores/surtidores (placas o fichas);
      el diseno usa Gilbarco 220 V, 103 VA por cabeza (familia de catalogo).
- [ ] Cantidad y ubicacion exacta de dispensadores (islas D, M, V): el plano
      muestra 2 posiciones; se mantiene para el anteproyecto.
- [ ] Cargas del POS/CCTV/comunicaciones: estimadas (1,2 kVA en UPS-IT).
- [x] Cargas de alumbrado (interior, exterior, de emergencia): estimadas por
      el diseno segun los planos generados (LED interior/exterior, marquesina,
      postes y totem).
- [ ] Cargas de la sala de maquinas (bomba de transferencia, compresor, etc.):
      se usan familias de catalogo (Atlas Copco 2,2 kW, Grundfos 1,5 kW).
- [ ] Alumbrado y fuerza de la zona de despacho y del area de tanques:
      estimado segun planos IE-01..IE-03.

## Seguridad y clasificacion de areas

- [ ] Clasificacion de areas peligrosas (zonas 0/1/2 o divisiones) segun CNE-U;
      propuesta academica en IE-06; pendiente revision competente.
- [ ] Alarma contra incendio y bomba contra incendio: fuera del alcance
      electrico del anteproyecto (no solicitado por el curso).
- [ ] Pararrayo: se mantiene h=12 m con radio 20 m (observado en DWG).

## Geometria y arquitectura

- [ ] Cotas exactas de ambientes (la extraccion preliminar uso bounding boxes).
- [ ] Alturas de techos, tableros y luminarias.
- [ ] Significado de los puntos PM A1/R1, PM A2/R2 en el plano fuente.
