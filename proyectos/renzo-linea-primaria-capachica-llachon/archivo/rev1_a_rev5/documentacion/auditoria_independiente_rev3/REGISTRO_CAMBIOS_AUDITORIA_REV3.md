# Registro de cambios de la auditoría independiente

| Fecha | Revisión | Cambio | Motivo y verificación |
|---|---|---|---|
| 14-10-2026 | AI-Rev3.0 | Carpeta nueva `documentacion/auditoria_independiente_rev3/` con estado inicial, informe, matrices, validación geométrica, auditorías eléctrica y de planos, pruebas y plan Rev. 4. | Mantener intactos los documentos y planos Rev. 2/3; dar trazabilidad a hallazgos comprobados y bloqueos externos. |
| 14-10-2026 | AI-Rev3.1 | Nueva prueba `tests/test_auditoria_independiente_rev3.py`. | Recalcula KML desde la fuente y marca con `xfail(strict=True)` los defectos reproducidos de finitud y paridad CL-04, sin alterar el código Rev. 3. Resultado: 27 passed, 5 xfailed. |
| 14-10-2026 | AI-Rev3.2 | `scripts/calculos_condicionales_rev4_propuesta.py` y `tests/test_calculos_condicionales_rev4_propuesta.py`. | Corrige de forma aislada AI-08: rechaza entradas/resultados no finitos y desbordamiento. Ensayo intermedio encontró un `OverflowError` del módulo heredado; se diagnosticó y cubrió. Resultado final de toda la suite: 38 passed, 5 xfailed. El flujo Rev. 3 aún usa el módulo original. |

No se modificaron KML, GISEM, OSM, `derived/route.json`, salidas Rev. 2/3, scripts activos ni archivos ajenos. Se efectuaron correcciones **documentales de interpretación** en estos nuevos archivos: la resta 40,405 m se identifica como aritmética sin tramo, PN se separa de postes instalables, PC de estructuras existentes verificadas, y la equivalencia entre DXF/PDF se somete a contraste. Los defectos del software y de los planos quedan abiertos hasta revisión separada. No hubo respuestas de Electro Puno, campo, AutoCAD, push, merge ni conformidad externa.
