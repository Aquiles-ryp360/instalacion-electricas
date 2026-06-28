# Requerimientos

Esta carpeta centraliza los documentos de alcance que antes estaban separados
en `RENZO-REQUERIMIENTOS`.

- `requerimiento-renzo.tex`: fuente LaTeX editable del requerimiento
  consolidado.
- `requerimiento-renzo.pdf`: version compilada del requerimiento.
- `terminos-referencia.tex`: fuente LaTeX editable de los terminos de
  referencia.
- `terminos-referencia.pdf`: version compilada de los terminos de referencia.
- `requerimiento-insumos-electricos-renzo.docx`: requerimiento formal de
  adquisicion de insumos electricos, armado desde las plantillas del curso y
  los datos del Proyecto Renzo.
- `cuadro-insumos-requerimiento-renzo.xlsx`: cuadro de insumos con cantidades,
  especificaciones, valores referenciales, codigos SIGA validados y matriz de
  evidencia de `catalogo.win`. Incluye la hoja `SIMILARES CATALOGO WIN` para
  candidatos no exactos de los items pendientes.
- `guia-catalogo-win-renzo.md`: guia breve para usar `https://catalogo.win/`
  como apoyo en la validacion de codigos SIGA.

Estos documentos sirven como insumo de alcance y trazabilidad. No reemplazan a
`../../expediente/main.tex`, que sigue siendo la fuente del expediente tecnico
publicable.

Si se actualiza un archivo `.tex`, recompilar su PDF correspondiente y revisar
que el cambio siga alineado con `../../proyecto.yaml` y
`../coordinacion.md`.

Antes de presentar el requerimiento de insumos, revisar los items que quedaron
marcados como `SIN COINCIDENCIA EXACTA` o `SIN CODIGO UNICO` en la matriz
`VALIDACION CATALOGO WIN`, contrastar los candidatos de `SIMILARES CATALOGO WIN`
y actualizar precios con una cotizacion vigente.
