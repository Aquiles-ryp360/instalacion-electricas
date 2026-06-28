# Cotización de materiales

Herramientas para convertir un BOM de instalaciones electricas en busquedas,
codigos de catalogo, cotizaciones por proveedor, comparativas y reportes.

## Mapa para agentes

```text
herramientas/cotizacion/
├── README.md                         mapa de navegacion
├── docs/                             guias operativas para agentes/humanos
│   └── scraper_catalogo_win.md       uso del scraper de catalogo.win
├── scrapers/                         scrapers de catalogos externos
│   └── catalogo_win.py               busca codigo/nombre en catalogo.win
├── exportadores/                     reportes Excel/CSV listos para revision
│   └── formato_docente.py            Excel con formato de requerimiento docente
├── proveedores/                      conectores de precios por tienda
├── data/                             reglas de matching, unidades y proveedores
├── tests/                            pruebas unitarias y fixtures offline
├── cotizador_multi_proveedor.py      orquestador principal de cotizacion
├── normalizador_materiales.py        normalizacion y scoring tecnico
├── conversor_unidades.py             rollos, tubos, paquetes y conversiones
├── modelos.py                        dataclasses del cotizador
└── scraper_catalogo.py               wrapper compatible hacia scrapers/catalogo_win.py
```

## Entradas recomendadas

Usa un BOM JSON con una lista `materiales`, `items`, `data` o `rows`. Cada item
debe tener al menos una descripcion en `item`, `nombre` o `descripcion`.

Ejemplo vigente:

```text
proyectos/aquiles/presupuesto/bom_final_aquiles.json
```

## Scraper de catalogo.win

Busca el primer resultado del catalogo SIGA/MEF para cada material y exporta
`codigo`, `nombre`, `status` y `error`.

```bash
python3 herramientas/cotizacion/scrapers/catalogo_win.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/catalogo_win.csv \
  --key item
```

Ruta compatible:

```bash
python3 herramientas/cotizacion/scraper_catalogo.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/catalogo_win.csv \
  --key item
```

Documentacion detallada:

```text
herramientas/cotizacion/docs/scraper_catalogo_win.md
```

## Exportador formato docente

Genera un Excel con una hoja de presentacion y otra con la salida tecnica
completa del scraper.

```bash
python3 herramientas/cotizacion/exportadores/formato_docente.py \
  --input build/aquiles/catalogo_win_aquiles_v3.xlsx \
  --bom proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/requerimiento_docente_catalogo_win.xlsx
```

## Cotizador multi-proveedor

```bash
python3 herramientas/cotizacion/cotizador_multi_proveedor.py \
  --bom proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/cotizacion \
  --proveedores promart,sodimac,maestro,mercadolibre
```

Modo de prueba sin red:

```bash
python3 herramientas/cotizacion/cotizador_multi_proveedor.py \
  --bom proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/prueba-cotizacion \
  --offline --usar-fixtures --max-materiales 3
```

## Reglas tecnicas

- conservar URL, fecha, proveedor y evidencia;
- distinguir precio verificado de estimado;
- convertir rollos, tubos y paquetes a la unidad del diseño;
- no seleccionar solo por precio si la coincidencia tecnica es insuficiente;
- no usar PDFs como fuente primaria de BOM si existe JSON estructurado.

## Pruebas

```bash
python3 -m pytest -q herramientas/cotizacion/tests
python3 -m py_compile herramientas/cotizacion/scrapers/catalogo_win.py
```
