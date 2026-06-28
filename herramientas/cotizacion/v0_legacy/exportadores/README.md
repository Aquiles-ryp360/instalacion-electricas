# Exportadores

Scripts que transforman resultados de scraping/cotizacion en archivos listos
para revision humana.

## formato_docente.py

Genera un Excel con dos hojas:

- `presentacion_docente`: cuadro resumido con columnas tipo requerimiento:
  item, cantidad, unidad, codigo del bien, descripcion y observaciones.
- `catalogo_win`: salida tecnica completa del scraper para auditoria.

Uso recomendado con Aquiles:

```bash
python3 herramientas/cotizacion/exportadores/formato_docente.py \
  --input build/aquiles/catalogo_win_aquiles_v3.xlsx \
  --bom proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/requerimiento_docente_catalogo_win.xlsx \
  --proyecto "Instalaciones electricas interiores - vivienda Aquiles" \
  --titulo "REQUERIMIENTO DE INSUMOS PARA INSTALACIONES ELECTRICAS"
```
