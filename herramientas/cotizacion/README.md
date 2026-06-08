# Cotizacion automatizada de instalaciones electricas

Herramientas para convertir el BOM de materiales electricos del proyecto en una cotizacion formal, verificable y lista para integrarse al informe.

El directorio mantiene dos flujos:

- **Flujo simple legacy:** conserva `buscador_precios.py` y `generar_cotizacion.py`.
- **Flujo multi-proveedor nuevo:** usa `cotizador_multi_proveedor.py` para buscar, comparar, recomendar y generar evidencias.

## Flujo legacy existente

El flujo anterior sigue disponible y no fue eliminado:

```text
BOM JSON -> buscador_precios.py -> cache/enlaces/precios -> generar_cotizacion.py -> HTML/LaTeX/PDF
```

Archivos principales:

- `bom.json`: BOM actual del proyecto de Aquiles.
- `buscador_precios.py`: genera enlaces, usa cache local legacy y opcionalmente Google Custom Search API.
- `generar_cotizacion.py`: genera cotizacion formal HTML/LaTeX usando precios del BOM.
- `generar_bom.py`: generador de BOM base.
- `process_bom_workflow.py`: script historico con rutas Windows y precios de referencia; se conserva como legacy.

Ejemplos legacy:

```bash
python3 herramientas/cotizacion/buscador_precios.py \
  --bom herramientas/cotizacion/bom.json \
  --output herramientas/cotizacion/salidas/comparativa_legacy

python3 herramientas/cotizacion/generar_cotizacion.py \
  --bom herramientas/cotizacion/bom.json \
  --output herramientas/cotizacion/salidas/cotizacion_legacy
```

## Flujo multi-proveedor nuevo

El nuevo cotizador:

1. Lee el BOM actual.
2. Normaliza los nombres tecnicos de los materiales.
3. Detecta categoria y especificaciones: seccion en mm2, diametro, amperaje, polos, sensibilidad, etc.
4. Consulta proveedores peruanos con HTTP headless y rate limit.
5. Extrae producto, marca, precio, URL, disponibilidad, fecha, metodo y confianza cuando el sitio lo permite.
6. Guarda evidencia por consulta en `evidencias/`.
7. Compara alternativas por material.
8. Recomienda una opcion por balance tecnico/economico, no solo por precio.
9. Genera JSON, CSV, XLSX, HTML, LaTeX y resumen Markdown.

Proveedores principales:

- Promart Peru
- Sodimac Peru
- Maestro
- Mercado Libre Peru

Proveedor opcional:

- Ventas Peru

Google Shopping queda documentado como apoyo de descubrimiento, pero no se usa como proveedor ganador porque no es proveedor directo.

## Instalacion de dependencias

En este equipo ya estaban disponibles las dependencias principales. Para un entorno limpio:

```bash
cd /home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas
python3 -m venv .venv
source .venv/bin/activate
pip install -r herramientas/cotizacion/requirements.txt
```

Playwright no es obligatorio. Si en el futuro se habilita un fallback headless:

```bash
pip install playwright
python3 -m playwright install chromium
```

No se debe usar navegador visible ni escritorio grafico para el flujo normal.

## Comandos de uso

Modo rapido:

```bash
python3 herramientas/cotizacion/cotizador_multi_proveedor.py \
  --bom herramientas/cotizacion/bom.json \
  --output herramientas/cotizacion/salidas/aquiles
```

Modo con proveedores especificos y cache:

```bash
python3 herramientas/cotizacion/cotizador_multi_proveedor.py \
  --bom herramientas/cotizacion/bom.json \
  --proveedores promart,sodimac,maestro,mercadolibre \
  --output herramientas/cotizacion/salidas/aquiles \
  --max-resultados 5 \
  --usar-cache
```

Modo refrescando cache:

```bash
python3 herramientas/cotizacion/cotizador_multi_proveedor.py \
  --bom herramientas/cotizacion/bom.json \
  --output herramientas/cotizacion/salidas/aquiles \
  --max-resultados 5 \
  --refrescar-cache
```

Modo offline con fixtures:

```bash
python3 herramientas/cotizacion/cotizador_multi_proveedor.py \
  --bom herramientas/cotizacion/bom.json \
  --output herramientas/cotizacion/salidas/test \
  --offline \
  --usar-fixtures
```

Prueba real limitada:

```bash
python3 herramientas/cotizacion/cotizador_multi_proveedor.py \
  --bom herramientas/cotizacion/bom.json \
  --output herramientas/cotizacion/salidas/test_real \
  --max-materiales 3 \
  --max-resultados 3 \
  --refrescar-cache
```

## Salidas generadas

Para `--output herramientas/cotizacion/salidas/aquiles`, se generan:

- `comparativa_precios.json`
- `comparativa_precios.csv`
- `comparativa_precios.xlsx`
- `cotizacion_recomendada.html`
- `cotizacion_recomendada.tex`
- `resumen_cotizacion.md`
- `evidencias/manifest.json`
- `evidencias/*.html` o `evidencias/*.json`

El Excel contiene hojas:

- `BOM original`
- `Materiales normalizados`
- `Comparativa por proveedor`
- `Mejor opcion por material`
- `Resumen por proveedor`
- `Evidencias`

## Cache

La cache nueva se guarda en:

```text
herramientas/cotizacion/.cache/precios_multi_proveedor.json
```

Cada entrada conserva:

- consulta normalizada
- proveedor
- fecha
- hash del BOM
- resultados extraidos

Usa `--no-cache` para ignorarla y `--refrescar-cache` para consultar de nuevo y actualizarla.

## Evidencias y limites de scraping

La herramienta no intenta saltar captchas, verificaciones de trafico, bloqueos ni medidas anti-bot.

Si un proveedor no entrega HTML util o no expone precio de forma confiable:

- `precio` queda en `null`
- `metodo_extraccion` queda como `fallback`, `html`, `cache` o `json`
- `observaciones` explica la razon
- se guarda URL o evidencia de la consulta

En pruebas reales se observaron estos comportamientos:

- Promart puede entregar HTML y datos embebidos, pero su estructura puede cambiar.
- Sodimac puede redirigir busquedas a portada y no entregar resultados parseables.
- Maestro puede responder lento o con timeout.
- Mercado Libre puede mostrar verificacion de trafico; en ese caso se registra como bloqueado y no se extrae precio.

## Matching y recomendacion

El sistema asigna puntajes:

```text
score_total =
0.50 * score_precio +
0.30 * score_tecnico +
0.10 * score_proveedor +
0.10 * score_disponibilidad
```

No siempre gana la opcion mas barata. Se penaliza:

- falta de amperaje, polos, seccion o diametro
- producto de categoria dudosa
- precio fuera de rango referencial
- ausencia de precio o URL
- baja confianza de extraccion

Los materiales sin precio o con baja confianza quedan listados en `resumen_cotizacion.md`.

## Pruebas

```bash
python3 -m py_compile herramientas/cotizacion/*.py
python3 -m py_compile herramientas/cotizacion/proveedores/*.py
pytest herramientas/cotizacion/tests -q
```

## Revision manual antes de entregar

Antes de presentar al ingeniero:

1. Abrir `cotizacion_recomendada.html` y revisar productos recomendados.
2. Revisar `resumen_cotizacion.md` para materiales sin precio o baja confianza.
3. Verificar URLs de productos con precio.
4. Confirmar que los productos coincidan con especificaciones CNE/RNE: seccion, polos, amperaje, sensibilidad y tipo de material.
5. Ajustar manualmente cualquier item pendiente si el proveedor no permitio extraccion automatica.

La herramienta prioriza trazabilidad sobre apariencia: no inventa precios.
