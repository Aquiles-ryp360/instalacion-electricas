# Scrapers

Scrapers de catalogos externos usados para enriquecer un BOM con codigos,
nombres normalizados o referencias de catalogo.

## catalogo_win.py

Consulta `https://catalogo.win/` y exporta el primer resultado de busqueda por
material a CSV, Excel o JSON. Usa cookie de sesion y token CSRF capturados
desde la pagina inicial.

```bash
python3 herramientas/cotizacion/scrapers/catalogo_win.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/catalogo_win.csv \
  --key item
```

Guia completa:

```text
herramientas/cotizacion/docs/scraper_catalogo_win.md
```
