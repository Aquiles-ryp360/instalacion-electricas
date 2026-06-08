# Cotización Automatizada — Instalaciones Eléctricas

Pipeline para generar cotizaciones formales de materiales eléctricos con precios reales de proveedores peruanos.

```
BOM (JSON) → Buscar precios → Cotización (HTML / LaTeX)
```

---

## Flujo Completo

```bash
# 1. GENERAR BOM desde cálculos eléctricos
python3 ../calculos-electricos-vivienda/scripts/generar_bom.py \
  --input ../calculos-electricos-vivienda/data/proyecto_aquiles_base.json \
  --output ../../output/mi_proyecto

# 2. ASIGNAR PRECIOS (3 formas)

# 2a. Manual — precios conocidos
python3 buscador_precios.py \
  --precio "Cable TW 2.5mm2=12.50" \
  --precio "ITM 2P 20A=89.00" \
  --precio "tubo PVC SAP 20mm=3.20"

# 2b. Automático — Google Custom Search API
export GOOGLE_API_KEY="AIza..."
export GOOGLE_CX="tu_cx"
python3 buscador_precios.py \
  --bom ../../output/mi_proyecto/bom.json \
  --output ../../output/comparativa

# 2c. Cache — los precios se guardan en ~/.cache_precios_electricos.json

# Ver precios guardados en cache:
python3 buscador_precios.py --precio ""

# 3. ACTUALIZAR BOM con los precios
python3 buscador_precios.py \
  --bom ../../output/mi_proyecto/bom.json \
  --actualizar ../../output/mi_proyecto/bom.json

# 4. GENERAR COTIZACION
python3 generar_cotizacion.py \
  --bom ../../output/mi_proyecto/bom.json \
  --cliente "Juan Perez" \
  --empresa "Mi Empresa SRL" \
  --output ../../output/mi_proyecto/cotizacion
```

---

## Herramientas

### `buscador_precios.py` — Búsqueda y asignación de precios

```bash
# Buscar un material (genera enlaces a proveedores)
python3 buscador_precios.py --item "interruptor diferencial 2P 40A"

# Buscar todos los materiales de un BOM
python3 buscador_precios.py --bom bom.json --output comparativa

# Solo enlaces (sin scraping)
python3 buscador_precios.py --item "cable TW 2.5mm2" --solo-enlaces

# Asignar precio manual y guardar en cache
python3 buscador_precios.py --precio "cable TW 2.5mm2=12.50"

# Busqueda con Google API
python3 buscador_precios.py --item "ITM 2P 20A" \
  --google-api-key AIza... --google-cx 123...
```

El cache se guarda en `~/.cache_precios_electricos.json` y se reusa automáticamente.
El matching de nombres es flexible (case-insensitive, ignora THW/TW/SAP/NH-90).

### `generar_cotizacion.py` — Generación de cotización formal

```bash
# Cotización básica
python3 generar_cotizacion.py --bom bom.json --output cotizacion

# Con datos del cliente y empresa
python3 generar_cotizacion.py --bom bom.json \
  --cliente "Juan Perez" --empresa "Mi Empresa SRL" \
  --output cotizacion

# Con precios personalizados (JSON)
python3 generar_cotizacion.py --bom bom.json \
  --precios mis_precios.json --output cotizacion
```

Genera:
- `cotizacion.html` — Formato HTML imprimible (Ctrl+P → PDF)
- `../latex/cotizacion.tex` — Formato LaTeX para incluir en informes

La cotización incluye:
- Tabla de materiales con cantidades, precios unitarios y totales
- Mano de obra (40% de materiales)
- IGV (18%)
- Total general

---

## Flujo con Pipeline Automatizado

El pipeline unificado integra todo el proceso:

```bash
python3 ../pipeline_automatizado.py \
  --config proyecto.yaml \
  --output-dir ../../resultados/
```

Esto ejecuta: cálculos → JSON → DXF/PDF → BOM → cotización, todo en un solo comando.

Ver `../pipeline_automatizado.py` para la configuración YAML y opciones.
