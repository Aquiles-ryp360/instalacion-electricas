# Hito de presentación A03 — LP-R03 22,9 kV

**Fecha:** 19/10/2026. **Base activa M01:** commit `f7c29c2f2c11fef388141da51e735d352f853daa` de `gaelrenzo/instalacion-electricas`. **Rama de trabajo:** `aquiles/lp-229kv-profesional-r03`.

## Correcciones obligatorias de la revisión
- Suministro canónico M01 **21 131 m** de AAAC 50 mm². Despiece: 20 274,360891 m de tendido, 240 m de puentes/colas, 616 m de reserva y redondeo final a 21 131 m.
- El valor **21 873 m** pertenece a una entrega pre-M01 (puentes erróneamente asociados a 160 ramales mecánicos) y debe quedar fuera de los documentos R03 vigentes.
- Inventario M01: 111 apoyos, 110 vanos, 160 ramales; 30 CAC-S, 41 CAC-A, 38 CAC-R (22 anclajes + 16 adicionales), 2 CAC-T.
- Presupuesto M01: **S/ 2 553 726,92**; únicamente referencial, no recotizado a 22,9 kV.
- Decisión LP-R03: 22,9 kV trifásico, aislado; no implica placa real ni aprobación para construcción.

## Archivos A03 preparados en entorno de trabajo, NO subidos a GitHub
Se preparó un dossier A03 de 7 páginas A4, más 20 hojas A3 del CAD previo en calidad de *referencia histórica* (27 páginas combinadas), y un nuevo XLSX de control de 111 apoyos y tres escenarios eléctricos.

Esos archivos binarios existen en el entorno de ChatGPT, pero **no se han insertado en este commit ni en esta rama**. La carpeta histórica de planos de M01 tampoco fue modificada; no presentar su archivo DXF o DWG como un diseño de 22,9 kV terminado. En el PDF de 27 páginas las láminas de referencia se identifican expresamente como no constructivas.

## Auditoría automatizable en el repositorio

```bash
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r03/control_m01_229kv.py \
  --salida build/aquiles-linea-primaria-inst-ii/a03-m01-229kv-control
```

El script valida desde las **entradas canónicas M01**, sin reemplazarlas: metrado del conductor, cuatro tipos de armado, 111 postes/110 vanos/160 retenidas y correspondencia numérica de los tres escenarios de 22,9 kV con el CSV LP-R02. Exige salida nueva para evitar sobrescritura. Se escribió y publicó; ejecutar la herramienta en un checkout completo del repositorio para obtener su registro de pruebas antes de dar visto bueno.

## Condiciones para la revisión final R04
1. Actualizar el origen de cálculo eléctrico a 22,9 kV, con grupos vectoriales reales/estudio justificado y 3F/2F/1F, AVR/taps, protecciones/puesta a tierra; descartar encabezados vigentes que aún indiquen caso nominal 10 kV.
2. Definir armados CAC 22,9 kV con selección de cadenas, aisladores, herrajes, separación y detalle dimensional; resolver P003/P035/P057 y 46 apoyos con carga ascendente.
3. Recalcular cimentación, tensado, gálibos y replanteo con topografía, geotecnia y predios reales.
4. Generar Metrados.xlsx **de 12 hojas** con Inventario, Matriz_armados, Ficha_poste y Resumen_materiales a partir de datos únicos; recalcular presupuesto sin duplicar componentes incluidos.
5. Generar PDF/planos DWG verdaderamente coherentes; auditoría visual página por página en A3, con legibilidad y cajetines unificados; no atribuir conversión DWG sin reapertura por AutoCAD/ODA.
6. Obtener revisión y aprobación competente antes de calificar documentación como expediente ejecutable.

**Resultado A03:** control editorial y metrado histórico M01 conciliado; el expediente definitivo a 22,9 kV continúa abierto.
