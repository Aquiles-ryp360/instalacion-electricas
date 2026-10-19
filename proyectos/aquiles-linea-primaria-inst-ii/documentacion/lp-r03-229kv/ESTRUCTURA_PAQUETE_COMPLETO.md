# Paquete R03/A03 reorganizado con base del primer ZIP

**Fecha:** 19/10/2026. **Estado:** entrega académica para revisión, NO expediente aprobado para construir.

La reorganización se entregó al usuario como un **nuevo ZIP local** en la conversación. El binario no se ha subido al repositorio GitHub. En esta rama están los criterios, el control M01/R03 y los scripts.

## Estructura del ZIP entregado
```text
Proyecto_Linea_Primaria_Limbani_Huancasayani_R03/
  00_Expediente/        Índice, dossier y expediente integrado de 101 páginas
  01_Memoria_Descriptiva/ 3 páginas extractadas del dossier R03
  02_Calculos/          Libro XLSX de 22,9 kV + resumen PDF
  03_Metrados/          Libro XLSX con 111 postes, 110 vanos + planilla CSV
  04_Planos/            20 láminas A3, DXF editable, DWG original histórico
  05_Cartografia/       QGIS, DEM/GPKG/QGZ, KMZ y vista general
  06_Presupuesto/       Control de presupuesto M01/R03 y valoración pendiente
  07_Recursos/          ZIP original de 16 archivos, normas enlazadas, manifiesto SHA-256
```

## Controles del ZIP
- 8 carpetas principales; 32 archivos.
- 111 postes del modelo CAD con identificadores únicos; 20 láminas LP y 23 referencias DGE.
- ZIP original de 16 archivos preservado con SHA-256 `40ac386a8f663c69823e4ec931fb2fc8b5a70268acdc1708cdbf9c0f234fa824`.
- Libro de metrado M01 con fórmula para conductor: 20 274,360891 m + 240 m + 616 m = 21 131 m.
- Referencia de presupuesto M01 S/ 2 553 726,92 (todavía no existe costo ejecutivo R03).
- Expediente integrado de 101 páginas contiene una advertencia explícita antes del anexo R02 de 72 páginas. **Esas páginas históricas aún describen 10 kV y 21 873 m**, no se presentan como cálculos definitivos de 22,9 kV.

## Limitación material
El ZIP M01 de 31 archivos y el expediente M01 de 195 páginas publicados en el upstream no estaban entre los insumos físicos entregados al modelo; por tanto **no se afirma haberlos incluido**. Para reemplazar íntegramente los 16 archivos históricos por la revisión M01 actualizada se requiere obtener esos binarios, regenerar los CAD/XLSX/PDF desde la base canónica y auditarlos.

El libro R03 es un control estructurado de cantidades, no el libro M01 original de 12 hojas; el DXF de presentación no constituye DWG nativo rediseñado a 22,9 kV ni un armado certificado.
