# Cotizador v1

Version activa del flujo de homologacion y cotizacion.

## Flujo

```text
BOM JSON
  -> homologacion/perucompras.py
  -> tiendas/promelsa.py
  -> tiendas/<siguiente_tienda>.py
  -> seleccion/
  -> exportadores/
```

La homologacion con PeruCompras es diagnostica por ahora. Si el catalogo no
cubre una familia, por ejemplo cables, la etapa debe quedar como `SKIPPED` o
`NO_ENCONTRADO` y continuar a tiendas.

## Entradas principales

- `cli/cotizar.py`: orquestador general v1. Actualmente delega a Promelsa.
- `cli/promelsa.py`: entrada CLI para cotizacion directa en Promelsa.
- `tiendas/promelsa.py`: implementacion real del scraper Promelsa.
- `homologacion/perucompras.py`: busqueda de fichas tecnicas PeruCompras.

`cli/` se mantiene como capa de entrada para operadores y agentes externos. La
logica de negocio debe vivir en `tiendas/`, `homologacion/`, `seleccion/`,
`core/` y `exportadores/`.

## Tiendas

Cada tienda debe producir candidatos con:

- nombre comercial
- precio visible
- SKU o codigo de producto
- URL
- stock/disponibilidad cuando exista
- texto tecnico visible
- evidencia de ficha de producto cuando exista

## Salidas

Las salidas deben ser revisables en JSON primero. Luego se agregaran
exportadores Markdown/XLSX para revision humana y comparativas.
