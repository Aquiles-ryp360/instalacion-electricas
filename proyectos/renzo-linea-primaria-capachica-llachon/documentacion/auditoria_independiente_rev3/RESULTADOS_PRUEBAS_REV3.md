# Resultados de pruebas y reproducción — auditoría Rev. 3

Fecha: 14-10-2026. Plataforma: Windows, Python 3.11. Dependencias observadas: ezdxf 1.4.4, pyproj 3.7.2, shapely 2.2.0, lxml 6.1.1, PyMuPDF 1.27.2.3, pytest 9.1.1, matplotlib 3.10.9 y PyYAML 6.0.3. `Get-Command acad.exe` no devolvió ejecutable en PATH; no se abrió AutoCAD. La disponibilidad en otras ubicaciones no fue comprobada.

## Comandos ejecutados y resultado

| Entorno/comando | Resultado |
|---|---|
| Original: `python -m pytest tests -q -rs` desde el proyecto | **25 passed**, 0 omitidas, 0,72 s. Las pruebas existentes validan geometría, presencia, formato, referencias y valores nulos; no validan seguridad eléctrica ni estructura. |
| Tras añadir `tests/test_auditoria_independiente_rev3.py`: `python -m pytest tests -q -rx` | **27 passed, 5 xfailed**, 1,79 s. Dos pruebas independientes verifican KML y condición PN; cuatro `xfail(strict=True)` documentan AI-08 y una documenta la diferencia CL-04 AI-06. Las cinco fallas esperadas son defectos **abiertos**, no conformidades corregidas. Un eventual XPASS estricto fallará hasta actualizar el control al corregir la revisión. |
| Propuesta separada `scripts/calculos_condicionales_rev4_propuesta.py`: `python -m pytest tests/test_calculos_condicionales_rev4_propuesta.py -q` | Ensayo intermedio: **10 passed, 1 failed**. La prueba de desbordamiento mostró que `vano_m**2` del módulo original lanza `OverflowError`, antes de la validación del resultado. Se añadió conversión explícita a `ValueError` en el adaptador. |
| Estado final: `python -m pytest tests -q -rx` | **38 passed, 5 xfailed**, 1,78 s. El módulo propuesto rechaza no finitos de entrada y resultado, y desbordamiento; los cinco `xfail` siguen señalando defectos de los artefactos originales Rev. 2/3. |
| Copia aislada de 106 archivos rastreados en `%TEMP%\capachica_rev3_audit_2q1fq6ma\repo\...`: `python proyectos/renzo-linea-primaria-capachica-llachon/scripts/reproducir_rev3.py --archive-existing` desde raíz de la copia | Exit 0, 24 passed, 1 skipped, 0,94 s. Regeneró cinco CSV/JSON y `derived/manifest_rev3.json` tras archivar seis salidas **solo de la copia**. |
| Segunda ejecución del mismo pipeline en la copia | Exit 0, 24 passed, 1 skipped, 0,66 s. Los SHA-256 de las seis salidas coinciden entre ambas ejecuciones y con el árbol original. |
| Copia: `python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests -q -rs` | 24 passed, 1 skipped. La omisión está en `tests/test_expediente_preliminar.py:36`: «PDF local de build no presente en este clon». El test adicional del árbol original usa un paquete histórico local ajeno al flujo Rev. 3. |
| Lectura de los cinco `CL-0x_REV2_MANUAL.dxf` con `ezdxf.readfile().audit()` | 5 leídos, 0 errores reportados, `$INSUNITS=6`; no prueba equivalencia con vistas PDF ni validez de ingeniería. |
| Apertura PDF con PyMuPDF y PNG con Pillow | 5 PDF A3 horizontal de una página y 5 PNG 2481×1753; inspección visual de los 5 PNG. |
| Comprobación de SHA-256 frente a `sources/manifest.json` | Coinciden GISEM tramos, GISEM estructuras y OSM. KML coincide con `derived/reconciliacion_corredores_rev3.json` y objeto Git HEAD. |
| Ensayo sintético adverso con `scripts/calculos_condicionales.py` | `I(inf,20)=inf`, `I(nan,20)=nan`, `ΔU(nan,1,.2,.1,.9)=nan`, `f(1,100,inf)=0.0`; defecto AI-08 reproducido. |

La copia se construyó con `git ls-files` del proyecto y `shutil.copy2` a una ruta temporal inexistente; no se copiaron los dos elementos no rastreados ni cambios ajenos. El script fue leído antes de ejecutarse: `--archive-existing` mueve los seis archivos de salida Rev. 3 a `build/.../archive_rev3/`; por ello **no se ejecutó en el árbol original**. La comparación determinista cubre las seis salidas del pipeline, no los planos Rev. 2 ni documentos, que el script no regenera.

## Alcance de software frente a ingeniería

Pruebas positivas: identidad de fuentes, conteos, longitudes geométricas, transformación de coordenadas, progresivas, IDs, integridad DXF y formato PDF. Las nuevas pruebas exponen finitud y paridad CL-04 como fallas esperadas; el adaptador Rev. 4 propuesto pasa ensayos sintéticos y **no está integrado** al pipeline actual. No se cubren todavía todas las hojas ni todas las referencias cruzadas. Pruebas ausentes o insuficientes: cálculo por vano, cargas y distancias reales, selección de equipo, alcance normativo artículo por artículo, factibilidad y permisos. La ruta del pipeline no reconstruye CAD ni compila el expediente. Cualquier futura puerta de diseño exige además ensayos, estudios y revisión firmada.
