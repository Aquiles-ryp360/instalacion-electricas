# Cotización de Materiales - Proyecto Aquiles

Este directorio contiene los entregables formales de la cotización multi-proveedor de materiales del proyecto de instalaciones eléctricas de Aquiles Ramos.

## Estructura de Salidas

- `comparativa_precios.json`: Base de datos completa en JSON.
- `comparativa_precios.csv`: Tabla de comparativas en formato CSV.
- `comparativa_precios.xlsx`: Hoja de cálculo Excel organizada con pestañas por tienda.
- `cotizacion_recomendada.html`: Cotización recomendada en HTML interactivo.
- `cotizacion_recomendada.tex`: Tabla LaTeX lista para insertar en el capítulo II del expediente.
- `resumen_cotizacion.md`: Resumen general de la cotización y totales.
- `pendientes_revision.md`: Reporte detallado de materiales que requieren validación manual.
- `evidencias/`: Carpeta con evidencias de scraping y enlaces de verificación.
  - `enlaces_productos.md`: Listado ordenado con los enlaces directos a las tiendas.
- `por_tienda/`: Carpeta con los presupuestos individuales de cada tienda.
  - `promart.md`: Presupuesto y cobertura en Promart.
  - `sodimac_maestro.md`: Presupuesto y cobertura en Sodimac/Maestro.
  - `mercado_libre.md`: Presupuesto y cobertura en Mercado Libre.
  - `recomendada_mixta.md`: Presupuesto optimizado mixto.

## Resumen de la Cotización Mixta Recomendada

- **Total de compra real mixta (unidades comerciales):** S/ 1682.03
- **Total recomendado neto de materiales (BOM):** S/ 1600.30
- **Cobertura del BOM:** 33/46
- **Materiales sin precio:** 13
- **Materiales baja confianza:** 13
