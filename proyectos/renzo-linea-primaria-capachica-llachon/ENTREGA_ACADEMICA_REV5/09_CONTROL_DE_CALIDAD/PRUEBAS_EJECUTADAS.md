# Pruebas ejecutadas en la preparación Rev. 5 (14-10-2026)

Comando: `python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests/test_rev5_modelos.py proyectos/renzo-linea-primaria-capachica-llachon/tests/test_entrega_rev5.py -q` → **13 passed**. Tras añadir el norte y coordenadas de extremos a CL-06/tabla de segmentos, se repitió la prueba de integración afectada: **4 passed**. `--verify` se ejecuta al generar el paquete; reabre seis PDF y seis DXF, coteja la geometría KML/las tres brechas, hashes y 21 entradas pendientes. Las 42 pruebas Rev. 4 con 5 xfail históricos habían pasado en la revisión precedente y no se repitieron porque sus fuentes y código no cambiaron.

Se inspeccionó visualmente el PNG renderizado de CL-06. No se realizó inspección física, revisión profesional ni apertura en AutoCAD. Las pruebas sintéticas no son cálculos del alimentador real.
