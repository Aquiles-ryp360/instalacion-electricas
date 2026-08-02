# Datos arquitectonicos canonicos

La entrada activa es [`grifo.json`](grifo.json). Se deriva del DXF CAD-001 y
distingue datos observados, calculados y criterios adoptados. Los campos con
coordenadas `null` deben completarse por extraccion reproducible; no deben
rellenarse visualmente sin indicar tolerancia y fuente.

Los DXF recortados y sus vistas se generan con:

```bash
.venv/bin/python proyectos/unidad-2-industrial/scripts/preparar_base_cad.py
```

Las salidas quedan en `build/unidad-2-industrial/cad/base/` y no sustituyen a
la fuente inmutable.
