# Línea primaria Limbani–Huancasayani

**Instalaciones Eléctricas II · Aquiles Taylor Ramos Yapo · 227368 · Metrados M01.**

[Descargar todo en ZIP](entregables/Proyecto_Linea_Primaria_Limbani_Huancasayani.zip) · [Abrir las ocho carpetas](entregables/proyecto-final/)

| Carpeta | Contenido |
| --- | --- |
| [00_Expediente](entregables/proyecto-final/00_Expediente/) | Expediente integrado: 195 páginas; memoria, cálculos, 111 fichas de inventario, presupuesto, ubicación UB-01, 19 planos base y 23 referencias DGE. |
| [01_Memoria_Descriptiva](entregables/proyecto-final/01_Memoria_Descriptiva/) | Memoria independiente de 10 páginas: antecedentes, objetivos, ubicación, coordenadas, condiciones del emplazamiento, instalaciones y alcance; UB-01 en A3. |
| [02_Calculos](entregables/proyecto-final/02_Calculos/) | Cálculo eléctrico/mecánico formulado de LP-R02 y resumen PDF. |
| [03_Metrados](entregables/proyecto-final/03_Metrados/) | Excel de 12 hojas con recetas por armado, inventario por poste, ficha seleccionable, compra global y accesorios incluidos; resumen PDF. |
| [04_Planos](entregables/proyecto-final/04_Planos/) | DWG/DXF base y nuevo plano de ubicación UB-01 en PDF A3 y SVG editable: Perú → Puno → Sandia → Limbani → corredor. |
| [05_Cartografia](entregables/proyecto-final/05_Cartografia/) | QGIS portable, GeoPackage, DEM y Google Earth. |
| [06_Presupuesto](entregables/proyecto-final/06_Presupuesto/) | Cantidades M01, precios referenciales por conjunto y resumen PDF. |
| [07_Recursos](entregables/proyecto-final/07_Recursos/) | Cartografía oficial IGN, normativa DGE, PAC Electro Puno y criterios del metrado con procedencia. |

Para consultar un poste, abre [Metrados.xlsx](entregables/proyecto-final/03_Metrados/Metrados.xlsx), entra a **Ficha_poste** y selecciónalo en **B4**. `Inventario` permite filtrar todos los postes y `Matriz_armados` desarrolla el consumo unitario. Las tuercas, contratuercas y arandelas que ya vienen con pernos o abrazaderas se controlan en `Accesorios_incluidos`, sin duplicar su compra.

El metrado comprende 111 postes, 110 vanos y 160 ramales. Los puentes se calculan por interrupción del conductor: 38 retenciones y 2 terminales, con 240 m auxiliares; el suministro total es **21 131 m**, incluida reserva y redondeo. El presupuesto recalculado es **S/ 2 553 726.92**, de carácter referencial académico.

Los tres libros se recalcularon con LibreOffice y sus fórmulas se comprobaron contra la base. Cada XLSX es autónomo: editar uno no actualiza los otros ni el PDF. Para sincronizar la entrega se regenera desde las entradas canónicas. Las pruebas incluyeron cambios de altura/función, consumo unitario y selector de ficha en una copia del libro.

## Bases y fuentes

Sistema aislado desde T1 en Limbani hasta T2 en Huancasayani, sin derivaciones ni redes de usuarios. La base técnica sigue siendo LP-R02: caso académico de 10 kV y alternativas 20/22/22.9 kV, sin tensión de equipo real confirmada. La geometría es de gabinete y las condiciones resistentes siguen sujetas a los límites del modelo.

La ubicación usa el [servicio oficial de límites referenciales IGN](https://www.idep.gob.pe/geoportal/rest/services/DATOS_GEOESPACIALES/L%C3%8DMITES/MapServer). El plano UB-01 es una elaboración del proyecto; no constituye demarcación ni levantamiento oficial. Los GeoJSON, consultas y SHA256 se conservan junto a las fuentes. Se comprobó la pertenencia del corredor al polígono referencial de Limbani, ubigeo 211203.

El despiece toma las variantes DGE trifásicas sin neutro y declara sus adaptaciones a CAC. El catálogo es académico, sujeto a compatibilidad del suministro. Las masas de accesorios no están certificadas: no se afirma que el despiece nuevo valide la carga tipo de 300 N del modelo previo. Ver [criterios y alcance de la revisión](documentacion/metrados-m01/REVISION.md).

## Continuar en PC u otro equipo

[proyecto.yaml](proyecto.yaml) declara las rutas y entradas activas. Las fuentes editables están en [expediente/final](expediente/final/) y [expediente/memoria-descriptiva](expediente/memoria-descriptiva/). El [informe de verificación](documentacion/metrados-m01/validacion-m01.json), las [pruebas](documentacion/metrados-m01/pruebas.json) y la [guía de reproducción](documentacion/metrados-m01/REVISION.md) conservan la trazabilidad para otras IA.

```bash
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/actualizar_metrados.py verificar-publicado
```

El ZIP anterior de 72 páginas se conserva en `archivo/presentacion-pre-m01/`; las revisiones móviles y P01 siguen intactas. Los comandos de `entrega_final.py` describen la presentación previa; el constructor vigente de presentación M01 es `actualizar_metrados.py`. Los parámetros del curso de Centrales Hidroeléctricas se mantienen independientes.
