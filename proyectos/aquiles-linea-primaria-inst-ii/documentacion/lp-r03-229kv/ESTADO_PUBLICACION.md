# Estado de publicación R03 — 22,9 kV
**Actualizado:** 19/10/2026 · **Fuente:** fork Aquiles-ryp360/instalacion-electricas, rama `aquiles/lp-229kv-profesional-r03`.

## Publicado y revisable en GitHub
- Decisión técnica de tensión nominal 22,9 kV y parámetros de escenario de diseño.
- Resultados eléctricos de comparación del caso de 22,9 kV con tres valores de regulación equivalente.
- Matriz de 111 postes y ocho observaciones especiales de armados.
- Scripts de cálculo preliminar y presentación CAD A3.
- Auditoría de entrega `scripts/lp_r03/verificar_entrega_229kv.py`.

## Aún no publicado como resultado definitivo
- **No hay un DWG nativo R03 verificado** (PDF y CAD del M01 continúan históricos).
- **No hay expediente PDF integrado R03** consistente con una nueva selección y justificación de 22,9 kV.
- **No hay tres libros XLSX R03 recalculados** desde entradas de los 111 postes ni armados definitivos de 22,9 kV.
- El ZIP minimalista desarrollado en el entorno de trabajo de ChatGPT **no se subió aquí**; una primera maqueta local nació de un ZIP de 72 páginas de la presentación anterior (pre-M01) y conserva cifras antiguas, entre ellas 21 873 m de conductor. **NO usar esa maqueta como metrado M01**. La base actual M01 rectificó ese suministro a **21 131 m**.

## Criterio para cierre de revisión
No se debe señalar `R03 FINAL` ni publicar ese material en `main` hasta que todo el cuadro documental coincida en:
- tensión nominal adoptada de 22,9 kV (no asumir verificación de placa generadora, T1 o T2);
- inventario completo de 111 postes, 110 vanos y 160 ramales;
- conductor M01 de 21 131 m *mientras no cambien las hipótesis de tendido/armado*;
- armados adaptados a postes CAC en 22,9 kV y selección de aislación por altitud;
- comprobaciones de los 46 apoyos de carga vertical ascendente, P003/P035/P057 y R02-P019-2;
- memorias, tablas y planos de una única revisión;
- revisión visual de cada página A3/PDF y apertura CAD por aplicación nativa.

Este registro separa material publicado, material local y elementos aún pendientes. Su finalidad es evitar entregas inconsistentes al docente.
