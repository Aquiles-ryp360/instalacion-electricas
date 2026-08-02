# Cuestionario de confirmacion - Proyecto renzo-industrial (unidad 2)

El objetivo es recolectar los datos que estan `por confirmar` en el repositorio
para elevar el anteproyecto a su mejor version y poder publicarlo en
`entregables/`. Cada respuesta se aplicara a los archivos canonicos indicados.

> Formato: responde por bloques o por numeros. Usa `no se / verificar en campo`
> cuando no dispongas del dato; quedara registrado como pendiente, no inventado.

**Estado: respondido por el estudiante el 2026-08-02.** Las respuestas
confirmadas se aplicaron a los archivos canonicos; las delegadas ("tu asumes",
"estimalo") se adoptaron como criterio de diseno y quedan registradas en
`criterios-diseno.yaml` y `cargas.yaml`.

---

## B1. Identificacion academica (aplica a `datos/rotulo-planos.yaml` y portada)

1. Codigo de estudiante (UNAP): **228447**
2. Semestre academico (ej. 2026-II): **2026-II**
3. Fecha de entrega prevista: **03 de agosto 2026**
4. Numero de laminas esperado por el docente (6 IE-01..IE-06 es lo actual):
   **las que hay (6)**
5. Ademas de los planos y el expediente, el curso exige algun otro entregable
   (memoria de calculo aparte, presentacion, maqueta)? **no; solo el
   expediente del proyecto**

## B2. Ubicacion y propietario (aplica a `rotulo-planos.yaml`, `proyecto.yaml`, memoria)

6. Departamento: **Puno**  Provincia: **San Roman**  Distrito: **San Roman**
7. Direccion o referencia del grifo: **Predio Rustico Reumita Parcela B-8 y
   B-9 Lado Este, comunidad campesina San Francisco de Buenavista, carretera
   Juliaca-Puno**
8. Propietario / razon social: **MIGUEL MAMANI CHUQUICALLATA**
9. Altitud real del terreno (el diseno usa 3830 m s.n.m. de Puno):
   **3830 m**
10. El DWG de ubicacion tiene rotulo con datos (urbanizacion, lote, numero)?
    **si**

## B3. Suministro y concesionaria (aplica a `cargas.yaml`, `criterios-diseno.yaml`)

11. Empresa distribuidora (se asume Electro Puno): **asumida: Electro Puno**
12. Numero de suministro o factura de luz del grifo (si existe): **no dispone**
13. Potencia contratada actual (kVA o kW): **delegado: se propone 30 kVA**
14. Corriente de cortocircuito Icc en el punto de entrega (dato de la
    concesionaria): **delegado: se asume 10 kA**
15. Existe factibilidad o carta de la concesionaria? Adjuntala en
    `fuentes/local/` si la tienes: **no**

## B4. Cargas reales de playa (aplica a `diseno-electrico/datos/cargas.yaml`)

Estas cargas hoy se dimensionan con familias de catalogo; con placas reales el
diseno gana exactitud.

16. Surtidores/dispensadores: **delegado; se mantiene el criterio de catalogo
    (Gilbarco 220 V, 103 VA por cabeza), 2 posiciones de islas**
17. Bombas sumergibles de tanque (STP): **delegado; se mantiene Franklin FE
    1,5 hp por tanque (una por TK-1, TK-2 y TK-3)**
18. Control de playa / ATG: **delegado; se estima 0,40 kVA (controlador ATG e
    interfaces)**
19. Compresor de aire: **delegado; se mantiene Atlas Copco 2,2 kW**
20. Bombas de agua y de efluentes: **delegado; se mantienen Grundfos 1,5 kW**

## B5. Cargas de edificio administrativo (aplica a `cargas.yaml`)

21. Alumbrado interior: **estimado segun planos generados: LED interior
    administrativo 0,80 kW (A1-01) y SS.HH/sala de maquinas 0,40 kW (A1-02)**
22. Alumbrado exterior: **estimado segun planos IE-01: marquesina y despacho
    0,80 kW (L-01), postes 0,80 kW (L-02), letrero/totem 0,40 kW (L-03)**
23. Tomacorrientes: **estimado: oficina/admin 1,20 kVA (A1-03), sala de
    maquinas/SS.HH 1,00 kVA (A1-04), criticos de caja/POS 0,80 kVA (A1-05)**
24. Equipos de oficina (POS, impresora, caja, PC, CCTV): **estimado 1,20 kVA
    en UPS-IT (S-01)**
25. Aire acondicionado o equipo adicional no considerado: **delegado; no se
    adiciona (fuera del alcance del curso)**

## B6. Tableros y configuracion electrica (aplica a `cargas.yaml`)

26. El plano muestra TG y TG2. El diseno interpreta: TG = acometida y TG2 =
    tablero del edificio administrativo (TD-A1). Confirma o corrige:
    **esta bien**
27. Numero de circuitos por tablero que esperas (hoy: 22 circuitos, 3
    subalimentadores TDE/TDF/TD-A1): **perfecto; concuerda con los planos**
28. Ubicacion real de TG, TG2, interruptor general y pulsador de emergencia
    (el plano los marca cerca de [10,5] local): **todo segun el plano**

## B7. Respaldo de emergencia (aplica a `cargas.yaml` -> `generator`, `ups`)

29. Grupo electrogeno: se propone Cummins C30D6 (37,5 kVA standby). Tienes
    placa/cotizacion real de algun equipo? Confirma o sustituye:
    **aun tengo la cotizacion; se mantiene Cummins C30D6**
30. Cargas criticas a respaldar (hoy: STP, cabezas de surtidor, ATG, POS/CCTV,
    alumbrado de emergencia): **delegado; se mantienen las cargas criticas
    existentes**
31. UPS:
    - Para combustible/control: 1,5 kVA, 15 min (se propone): **delegado
      (mantener)**
    - Para POS/CCTV/comunicaciones: 2,0 kVA, 15 min (se propone): **delegado
      (mantener)**
32. El grifo tiene tarifa con doble suministro o contrato de reserva? **no
    indicado; fuera del alcance**

## B8. Seguridad, areas peligrosas y normativa (aplica a `04-seguridad-normativa.tex`, IE-06)

33. Zonas peligrosas: el anteproyecto delimita zonas 1 y 2 alrededor de
    tanques, venteos y surtidores (lamina IE-06). Tienes referencia oficial de
    distancias de clasificacion (p. ej. NPT o reglamento OSINERGMIN)? **no
    dispone; se mantiene la propuesta academica con revision competente**
34. Alarma contra incendio y bomba contra incendio: el grifo las tiene? Estan
    dentro de tu alcance o las dejas fuera (hoy fuera)? **delegado; fuera del
    alcance electrico del curso**
35. Pararrayo: se incluye uno de h=12 m con radio de 20 m (observado en DWG).
    Confirma altura real: **delegado; se mantiene h=12 m, radio 20 m**
36. Extintores: cantidad y ubicacion (el plano muestra 2): **delegado; se
    mantiene lo observado (2)**
37. Reglamento sectorial vigente a citar (OSINERGMIN / D.S. N.°xxx): consulta
    y anota numero/fecha: **pendiente de consulta oficial**

## B9. Geometria y arquitectura (aplica a `arquitectura/datos/layout-grifo.json`)

38. Cotas exactas de cada ambiente (hoy derivadas de bounding boxes, confianza
    media): **delegado; se mantienen las cotas extraidas del DWG**
39. Alturas de techo, de tableros y de luminarias: **pendiente de verificacion
    en campo**
40. Puntos "PM A1/R1, PM A2/R2" del plano: que representan (puntos de
    monitoreo de areas)? Confirma o descarta: **delegado; se interpretan como
    puntos de monitoreo de areas (S-05)**
41. Area del lote a ejecutar (hoy 435 m2, poligono aproximado) y del lote
    total (hoy 1517 m2): confirma o corrige: **delegado; se mantienen los
    valores extraidos**
42. Hay zonas adicionales (baño publico, cafeterin, tienda) no graficadas? **no
    indicado**

## B10. Presupuesto y cronograma (aplica a `06-metrados-presupuesto.tex`)

43. Cotizaciones reales de los equipos principales (grupo, tableros,
    luminarias) para llenar P.U. del presupuesto: **delegado; se usan P.U.
    referenciales de mercado (2026) y totales llenos**
44. Plazo real de ejecucion (hoy 8 semanas referencial): **delegado; se
    mantiene 8 semanas**
45. Fecha de inicio / fin prevista para el cronograma: **delegado; el
    cronograma se expresa por semanas (inicio condicionado a permisos)**

## B11. Mejoras que quieres aplicar

46. Marca las areas a reforzar (puedes elegir varias):
    - [x] Memoria de calculo mas detallada (selectividad, Icc) -- APLICADO
    - [x] Diagrama unifilar completo con protecciones -- APLICADO (IE-05)
    - [x] Planos con cotas y alturas exactas -- APLICADO (rotulo confirmado)
    - [x] Presupuesto con cantidades llenas y totales -- APLICADO
    - [x] Cronograma con fechas reales -- APLICADO (expresado por semanas)
    - [x] Mas citas normativas con seccion y evidencia -- APLICADO
    - [x] Tabla de parametros de diseno (factor de potencia, demandas) -- APLICADO
    - [x] Detalles constructivos (pozo a tierra, sellado de paso) -- APLICADO (IE-04/IE-06)
    - [ ] Otro: ___________________

47. Prioridad final: que es lo mas importante para tu nota (rigor tecnico,
    cantidad de planos, presupuesto, normativa)? **normativa, planos y
    calculos**
