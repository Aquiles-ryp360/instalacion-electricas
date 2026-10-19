# Expediente técnico completo — LP 22,9 kV Capachica–Llachón

Paquete: [`expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip`](../expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip), 30 MB.
Contiene 53 PDF, más los Word, los Excel con fórmulas, los DWG/DXF y los archivos de Google Earth.

Lo generó el motor [expediente-lp-22.9kv](https://github.com/dilmar231gabriel-ops/expediente-lp-22.9kv) (D. H. Ccora), con los 15 pasos
y la entrada `datos/motor_lp229/entrada/proyecto.yaml`. Sobre lo que produjo el motor se agregó:

- En el Vol. VII, la carpeta **PLANOS FORMATO EPIME – AUTOCAD (REV. 7)**: `LP_REV7.dwg`, `.dxf`, `.pdf` y la guía de AutoCAD.
- En el Vol. VII, carpetas **DWG (AutoCAD)** junto a los DXF de planos, láminas de detalle y plano georreferenciado (29 DWG, revisados con AUDIT al convertir).

## Volúmenes

| Volumen | Contenido |
|---|---|
| Carátula y separadores | — |
| I Ficha técnica · II Resumen ejecutivo · III Memoria descriptiva | Word + PDF |
| IV Especificaciones técnicas | Suministro (ETS-LP-01…13) y montaje |
| V Metrado y presupuesto | Excel con fórmulas, APU, gastos generales, cronogramas y fórmula polinómica |
| VI Cálculos justificativos | Anexos 1–9: aislamiento, pararrayos, PAT, cálculo mecánico de conductores, cimentación, cálculo mecánico de estructuras, retenidas, caída de tensión, planilla |
| VII Planos y láminas | Ubicación, planta, perfil y planimetría, unifilar, cruce, 14 armados, coordenadas, KML/KMZ y **Rev. 7 EPIME** |
| VIII Geología y geotecnia | De gabinete, más los términos de referencia del estudio de mecánica de suelos |
| IX Flujo, cortocircuito y protecciones | — |
| X Requerimientos de ejecutor y supervisor | — |
| XI Anexos | Riesgos, panel fotográfico, cotizaciones y datos pendientes |
| 00 Informe de generación y verificación | Resultado de las comprobaciones cruzadas |

## Resultados principales

| Concepto | Valor |
|---|---|
| Longitud / estructuras | 13,89 km / 122 (PS1-3 78, PA1-3 28, PA2-3 8, TS-3 5, PSER-3, PR3-3, PTH-3) |
| Conductor | AAAC 70 mm² (el económico sería 35 mm²; el motor usa el de su kit) |
| Máxima demanda 2047 | 143 kW; caída de tensión 0,29 % (límite 5 %) |
| Cota de la línea | 3 813 – 3 867 m s.n.m. (diseño a 3 900 m) |
| Valor referencial | **S/ 1 359 760,11** con IGV |
| Verificación cruzada | **17 de 17 CONFORME** |

## Supuestos que hay que reemplazar antes de presentarlo como estudio definitivo

Están marcados como SUPUESTO en el `proyecto.yaml` y en el Vol. XI:

- Punto de diseño, tensión y Scc: solicitar la factibilidad a Electro Puno.
- Población: 1 500 hab., pendiente de confirmar con INEI 2017.
- Clima: SENAMHI Puno.
- Resistividad del terreno: 100 Ω·m; medir en campo.
- Topografía: se usó el DEM de 30 m; hace falta levantamiento.
- Mecánica de suelos y cotizaciones.
- Tipo de cambio: 3,453, tomado del ejemplo del motor; actualizar con el BCRP.
- Plazo: 90 días.
- Proyectista: Renzo Gabriel Mamani Galindo. El expediente no lleva CIP, firma ni sello.

## Regenerar

LibreOffice no estaba instalado. Se aplicó al motor el parche [`oficina_microsoft_office.patch`](../datos/motor_lp229/oficina_microsoft_office.patch):
sin LibreOffice, usa Microsoft Excel y Word (pywin32) para recalcular y convertir a PDF.

En Windows, la carpeta de salida debe tener una ruta corta; Word no abre rutas de más de 259 caracteres:

```powershell
python generar.py proyectos/capachica-llachon/proyecto.yaml --salida C:\Users\renzo\EXP_LP
```
