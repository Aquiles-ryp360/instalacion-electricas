# Expediente Técnico - Línea Primaria 22.9 kV Capachica - Chifrón

> **Revisión activa:** [dictamen auditado](documentacion/DICTAMEN_PRESENTACION_AUDITADA_REV1.md). La [carpeta de presentación local](../../build/renzo-linea-primaria-capachica/presentacion_auditada_rev3/) contiene un dossier PDF, un plano LP-00 DXF/PDF y una imagen georreferenciada PNG+PGW+PRJ. La conexión E-01 a la red citada queda pendiente de confirmar; los seis planos anteriores son referenciales. Estado: revisión académica, no apto para obra.

Para regenerar la carpeta en una copia sin salida existente: `python scripts/preparar_presentacion_auditada.py` desde este directorio. Requiere conexión al servicio público GISEM y las dependencias Python `requests`, `Pillow`, `pyproj`, `ezdxf`, `PyMuPDF`, `reportlab` y `pypdf`. El script rehúsa sobrescribir una carpeta Rev. 3 ya generada.

> **Este expediente corresponde a Chifrón.** Para el recorrido **Capachica–Llachón** y sus dos planos nuevos, abre el [proyecto separado de Llachón](../renzo-linea-primaria-capachica-llachon/README.md).

**Proyecto:** Instalación de línea primaria en media tensión 22.9 kV y subestación biposte SAB-1 100 kVA para el sector Chifrón, distrito de Capachica, Puno.  
**Alcance final:** Línea primaria, subestación de distribución, protecciones MT, retenidas, cimentaciones y puesta a tierra.  
**No incluido en esta entrega:** redes secundarias, acometidas domiciliarias ni alumbrado público.  

**Estudiante:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Curso:** MEC330 - Instalaciones Eléctricas II  
**Institución:** Universidad Nacional del Altiplano - FIME  
**Docentes:** Ing. Leonidas Vilca Callata / Ing. Marcos José Villanueva Cornejo  

---

## 1. Entrega Principal Para Presentar

| Orden | Archivo | Uso recomendado |
| ---: | --- | --- |
| 1 | [`REVISION_FINAL_SUPERVISOR.md`](REVISION_FINAL_SUPERVISOR.md) | Auto-revisión final y guía de defensa. |
| 2 | [`expediente/expediente_linea_primaria_22_9kv_compilado.pdf`](expediente/expediente_linea_primaria_22_9kv_compilado.pdf) | Expediente técnico compilado para revisión del ingeniero. |
| 3 | [`entregables/planos/plano_LP01_planta_linea_primaria.pdf`](entregables/planos/plano_LP01_planta_linea_primaria.pdf) | Plano de planta, traza, servidumbre y estructuras. |
| 4 | [`entregables/planos/plano_PL01_perfil_longitudinal.pdf`](entregables/planos/plano_PL01_perfil_longitudinal.pdf) | Perfil longitudinal, catenaria, spotting y gálibos. |
| 5 | [`entregables/planos/plano_U01_diagrama_unifilar_detalles.pdf`](entregables/planos/plano_U01_diagrama_unifilar_detalles.pdf) | Diagrama unifilar de media tensión y límite de alcance. |
| 6 | [`entregables/planos/plano_D01_armados_dge_ps1_pa1.pdf`](entregables/planos/plano_D01_armados_dge_ps1_pa1.pdf) | Armados DGE PS-1 y PA-1. |
| 7 | [`entregables/planos/plano_D02_armados_dge_pr1_sab1.pdf`](entregables/planos/plano_D02_armados_dge_pr1_sab1.pdf) | Armados DGE PR-1 y SAB-1. |
| 8 | [`entregables/planos/plano_D03_detalles_cimentacion_retenida_pat.pdf`](entregables/planos/plano_D03_detalles_cimentacion_retenida_pat.pdf) | Cimentación Sulzberger, retenida R-1 y PAT-3. |
| 9 | [`entregables/planos/planos_autocad_linea_primaria_capachica.zip`](entregables/planos/planos_autocad_linea_primaria_capachica.zip) | Paquete DXF A3 para AutoCAD. |

> Para una presentación limpia, abrir primero el expediente compilado y luego sustentar los planos en el orden LP-01, PL-01, U-01, D-01, D-02 y D-03.

---

## 2. Datos Técnicos Clave

| Parámetro | Valor |
| --- | --- |
| Nivel de tensión | 22.9 kV, trifásico, 3 hilos, 60 Hz |
| Longitud de eje | 0.8166 km |
| Número de estructuras | 9 estructuras MT, E-01 a E-09 |
| Conductor | AAAC 35 mm² |
| Vano crítico | E-05 a E-06, 115.59 m |
| Punto de derivación | E-01, Cerro Chifrón, cota 3924.17 msnm |
| Punto de llegada | E-04, SED SAB-1 100 kVA, cota 3839.56 msnm |
| Estructura terminal | E-09, progresiva 0+816.60 m |
| Puesta a tierra | PAT-3, resistencia objetivo R <= 10 ohm |

---

## 3. Planos AutoCAD

El paquete AutoCAD está en:

[`entregables/planos/autocad_lp/`](entregables/planos/autocad_lp/)

Incluye 6 archivos DXF A3:

- `LP-01_PLANTA_LINEA_PRIMARIA_A3_AUTOCAD.dxf`
- `PL-01_PERFIL_LONGITUDINAL_A3_AUTOCAD.dxf`
- `U-01_DIAGRAMA_UNIFILAR_MT_A3_AUTOCAD.dxf`
- `D-01_ARMADOS_PS1_PA1_A3_AUTOCAD.dxf`
- `D-02_ARMADOS_PR1_SAB1_A3_AUTOCAD.dxf`
- `D-03_CIMENTACION_RETENIDA_PAT3_A3_AUTOCAD.dxf`

Recomendación de ploteo: abrir cada DXF en AutoCAD, ejecutar `ZOOM EXTENTS`, configurar hoja A3 horizontal y plotear con CTB monocromo o por color según indique el docente.

---

## 4. Archivos Que No Deben Sustentar La Entrega Final

No usar como entrega principal:

- `plano_P01_redes_planta.pdf`
- `PLANO_PLANTA_REDES_Y_ACOMETIDAS_CAPACHICA.dxf`
- `TABLA_CUADRO_DE_CARGAS.dxf`
- archivos antiguos con prefijo `#` o `##`

Se conservan en el repositorio por trazabilidad, pero el paquete final defendible es el de línea primaria indicado arriba.

---

## 5. Automatización Reproducible

Scripts principales:

- [`scripts/generar_planos_ejecutivos_lp_capachica.py`](scripts/generar_planos_ejecutivos_lp_capachica.py): genera las láminas PDF, PNG y DXF base.
- [`scripts/generar_planos_autocad_lp.py`](scripts/generar_planos_autocad_lp.py): genera el paquete AutoCAD A3 y el ZIP final.
- [`scripts/compilar_expediente_lp.py`](scripts/compilar_expediente_lp.py): compila el expediente PDF final.

Validación:

```bash
pytest proyectos/renzo-linea-primaria-capachica/tests -q
```

Estado actual de pruebas: **17 passed**.
