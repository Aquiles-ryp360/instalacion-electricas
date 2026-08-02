# Presupuesto y cotización automática

La fuente canónica de metrados y precios referenciales es
`datos/partidas.yaml`. El cálculo genera dos productos distintos:

1. `build/unidad-2-industrial/presupuesto/`: presupuesto académico instalado,
   con gastos generales, utilidad e IGV.
2. `build/unidad-2-industrial/cotizaciones/`: evidencia comercial de suministros
   comparables; no reemplaza automáticamente los precios instalados.

Flujo reproducible para cualquier IA o instalación de Codex:

```bash
.venv/bin/python proyectos/unidad-2-industrial/scripts/calcular_metrados_presupuesto.py
.venv/bin/python herramientas/cotizacion/v1/cli/cotizar.py \
  --input build/unidad-2-industrial/cotizaciones/bom-cotizable.json \
  --output build/unidad-2-industrial/cotizaciones/promelsa.json \
  --modo heuristico --key item --no-actualizar-precio --workers 4
.venv/bin/python proyectos/unidad-2-industrial/scripts/revalidar_cotizacion_automatica.py
.venv/bin/python proyectos/unidad-2-industrial/scripts/resumir_cotizacion_automatica.py
```

Estados esperados:

- `OK`: existe candidato trazable, pero mantiene revisión humana.
- `SIN_SELECCION`: hubo candidatos y ninguno superó todos los filtros.
- `NO_ENCONTRADO`: la tienda no devolvió candidatos.
- `ERROR`: falló red, parseo o ficha; el lote continúa.

No copiar un precio comercial unitario sobre una partida que incluye montaje,
mano de obra, cajas, accesorios o pruebas. Primero debe prepararse un análisis
de precio unitario que separe suministro e instalación.
