# Control de calidad del paquete Capachica–Llachón

**Fecha:** 14-10-2026 UTC. **Alcance:** integridad de fuentes, cuadro GIS y dos planos CAD A3 preliminares. No acredita aptitud para construcción.

| Control | Resultado comprobado | Límite |
|---|---|---|
| Pruebas automatizadas | `python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests -q`; comprobar resultado después de compilar Rev. 1 | Las pruebas no sustituyen la revisión de campo ni AutoCAD |
| Fuentes | 3 instantáneas del manifiesto con SHA-256 coincidente | Información GIS/DEM, sin visita de campo |
| Ruta | 27 códigos GISEM; suma geométrica UTM y progresiva final **13 834,03 m** | No es metrado de obra |
| Diferencia de longitudes | Atributo GISEM `LONGITUD`: suma numérica **14 248,94**, unidad no confirmada | No usar el campo para presupuesto hasta aclararlo |
| DXF A3 | Ambos R2010, `$INSUNITS=6` en modelo, papel **420 × 297 mm**, cero errores del auditor `ezdxf` | No se probó con AutoCAD instalado |
| Vista de CAD | Se renderizaron las pestañas `CL-01_A3` y `CL-02_A3` a PDF/PNG y se inspeccionaron | El render de `ezdxf` puede diferir de AutoCAD en fuentes y estilos |
| Ingeniería | Campos de diseño y resultados aún desconocidos están en `null` | No hay cálculo de corriente, flecha, protección, PAT ni presupuesto |
| Expediente Rev. 1 | PDF integrado previsto con capítulos A4 y 2 planos A3; ZIP con huellas por archivo | Documento de revisión local, sin aprobación para obra |

## Estado de las tareas

| Tarea | Estado | Evidencia | Pendiente |
|---|---|---|---|
| Ubicación | Cartografía preliminar completada | CL-01 y registro GISEM | Replanteo y confirmación de conexión |
| Perfil | Referencia territorial completada | CL-02 y 57 muestras SRTM | Perfil topográfico de ingeniería |
| Anteproyecto | Documento de evaluación preparado | `MEMORIA_ANTEPROYECTO.md` y matriz de datos | Operador, demanda, alternativas y decisión |
| Diseño eléctrico y mecánico | Bloqueado por datos esenciales | Parámetros `null` | Datos de campo, normas aplicables y cálculos |
| Expediente de construcción | No iniciado | Sin planos de vanos, apoyos ni equipos aprobados | Ingeniería de detalle y firma profesional |

La compilación usa los siete capítulos de `expediente/`, comprueba 27 tramos y resultados de diseño `null`, agrega los dos planos A3 al PDF y genera un ZIP local. El manifiesto en `build/renzo-linea-primaria-capachica-llachon/MANIFIESTO_PAQUETE_REV1.json` registra SHA-256, tamaños de página y huellas de los archivos incluidos. La compilación usa **ReportLab** y `pandoc`.

La [auditoría correctiva](AUDITORIA_REV0.md) detectó que un paquete anterior había quedado desactualizado. La revisión activa se indica en `proyecto.yaml` y sus archivos se comprueban contra el manifiesto correspondiente.

## Archivos de control

El [reporte de generación](../datos/reporte_generacion_cad.json) contiene SHA-256 de los tres archivos de entrada principales y de los dos DXF A3 más el cuadro CSV. Las [pruebas locales](../tests/test_anteproyecto_cad.py) vuelven a verificar esas huellas, el estado preliminar, la estructura de los DXF, las presentaciones y la correspondencia de las polilíneas de modelo con las fuentes.
