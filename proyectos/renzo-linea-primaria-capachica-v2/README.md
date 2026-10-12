# Proyecto v2: Variante de Línea Primaria 22.9 kV — Chifrón, Capachica

**Propósito:** nueva versión del diseño de la línea primaria 22.9 kV que
**no dañe la infraestructura existente** de Electro Puno S.A.A.
(tramos `TMT000012389` / `TMT001847370` y estructura de derivación E-01).

**Estado:** variante en definición — pendiente de traza, coordenadas y criterios
de no daño. Ver `proyecto.yaml`.

## Reglas

- No modificar `fuentes/` ni `entregables/` de la v1.
- Los datos nuevos (traza, coordenadas, cargas) entran por `fuentes/` de este
  proyecto y se estructuran en `datos/`.
- Todo resultado se genera primero en `build/` y se revisa antes de pasar a
  `entregables/` (regla 5 del repo).
- Pipeline: `extraer_red` → `escribir_modelo_dss` → `ejecutar_flujo_opendss`
  → `analizar_nodos_criticos` → `generar_reportes`
  (toolkit genérico en `herramientas/red_mt/`, sin nombres de proyecto).

## Toolchain

```text
python -m pip install dss-python geopandas networkx pandas openpyxl pyogrio pyyaml
```

## Estado del toolchain (validado 2026-10-11)

- dss-python 0.15.7 (motor OpenDSS nativo, sin win32com) — OK
- geopandas 1.2.0 — OK
- Advertencia: numpy 2.4.6 muestra warnings de compatibilidad con
  opencv-python/pandapower instalados en el ambiente; no afecta a
  dss-python ni geopandas.
