# Datos electricos canonicos

La entrada de calculo inicial es [`cargas.yaml`](cargas.yaml). Cada circuito distingue dato de
catalogo, criterio adoptado y funcion obligatoria, ademas de fase, demanda,
longitud, conductor y proteccion.

Las cargas sin placa se sustentan en
[`catalogo-equipos-diseno.md`](../../documentacion/catalogo-equipos-diseno.md) y
deben reemplazarse si aparecen fichas definitivas. Los resultados se regeneran
en `build/unidad-2-industrial/calculos/`.

El alumbrado se define en [`alumbrado.yaml`](alumbrado.yaml). Su comprobacion
por el metodo de lumenes se ejecuta con `scripts/calcular_alumbrado.py`; no
sustituye una simulacion punto por punto con fotometrias IES/LDT.
