# Guia rapida: catalogo.win para Proyecto Renzo

El enlace enviado por el docente (`https://catalogo.win/`) es un buscador de items del Catalogo SIGA MEF. Segun la pagina, permite buscar por nombre o codigo, verificar clasificadores/cuentas contables y generar archivos `.rar` para importar al SIGA MEF.

## Como usarlo con este requerimiento

1. Abrir `https://catalogo.win/`.
2. Usar la busqueda individual con el texto de la columna `Busqueda sugerida en catalogo.win` del archivo `cuadro-insumos-requerimiento-renzo.xlsx`.
3. Elegir el item que mejor coincida con la descripcion tecnica, unidad y presentacion comercial.
4. Copiar el codigo en la columna `Codigo del bien`.
5. Revisar clasificador y cuenta contable desde el detalle del item.
6. Si el docente pide importacion SIGA, usar la busqueda masiva con los codigos ya validados.

## Criterio aplicado

- Validacion ejecutada el 2026-06-28 contra `https://catalogo.win/`.
- No se inventaron codigos SIGA: los items sin coincidencia exacta quedan marcados como pendientes o por desagregar.
- El codigo `969800030540` se conserva porque aparece en la plantilla del curso y fue validado en catalogo.win como tuberia PVC SAP 3/4 in x 3 m.
- Las cantidades salen del modelo y metrados del Proyecto Renzo.
- Los precios son referenciales, tomados de los presupuestos/cotizaciones existentes del proyecto; deben actualizarse antes de comprar.
- Quedaron pendientes de cierre formal:
  - Item 20, tomacorriente protegido tipo GFCI/diferencial: catalogo.win no devolvio coincidencia exacta de tomacorriente GFCI.
  - Item 22, kit de pozo de puesta a tierra: no existe codigo unico para el kit completo; debe desagregarse por componentes si el docente exige codificacion SIGA itemizada.
- Los candidatos cercanos para esos pendientes quedaron registrados en la hoja
  `SIMILARES CATALOGO WIN` del Excel.

## Archivos generados

- `requerimiento-insumos-electricos-renzo.docx`
- `cuadro-insumos-requerimiento-renzo.xlsx`

Fecha de preparacion: 2026-06-27
