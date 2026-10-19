# Auditoría correctiva del anteproyecto Capachica–Llachón

**Fecha:** 14-10-2026. **Alcance:** archivos locales del proyecto, trazabilidad GIS/DEM, láminas DXF/PDF, memoria y paquete de revisión. La auditoría no constituye aprobación de diseño ni inspección de campo.

| Hallazgo | Evidencia local | Corrección o estado |
|---|---|---|
| El ZIP Rev. 0 no reproducía el árbol actual | Comparación SHA-256 entre miembros del ZIP y archivos locales: `README.md`, `documentacion/CONTROL_CALIDAD.md` y `proyecto.yaml` estaban desactualizados. Faltaban `requirements.txt`, `expediente/README.md` y una prueba. | Se conserva Rev. 0 y se genera paquete Rev. 0A con inventario y SHA-256 por archivo. |
| El empaquetador omitía dependencias | `package_files()` no incluía `requirements.txt`. | Se añadió a la lista de inclusión. |
| La rotulación CAD fijaba los códigos de extremos en el código | `scripts/generar_anteproyecto_cad.py` tenía ambos códigos como literales. | La rotulación toma los identificadores de `derived/route.json`. Los DXF actuales mantienen los mismos extremos. |
| Longitudes de dos fuentes no coinciden | Geometría UTM de 27 tramos: **13 834,03 m**; suma numérica de `LONGITUD` en GISEM: **14 248,94** con unidad no confirmada. | Se mantiene la geometría como longitud **cartográfica**; ninguna cifra se considera metrado de obra. La discrepancia queda pendiente de cotejo con titular de red y levantamiento. |
| La red existente no equivale a un proyecto nuevo aprobado | CL-01 representa un recorrido sobre la red MT publicada. Los extremos GIS se separan 5,02 m y 3,48 m de la geometría seleccionada. | Se mantienen los avisos en plano y memoria. No se define punto de conexión, tensión, apoyos ni necesidad de construir línea sin confirmación de Electro Puno y campo. |
| El perfil carece de resolución para ingeniería de detalle | CL-02 usa 57 muestras SRTM30m, sin levantamiento topográfico de apoyos, cruces ni vanos. | Se conserva como perfil referencial; no se derivan flechas, alturas o distancias de seguridad. |
| No hay validación de AutoCAD ni de seguridad eléctrica | Se reabrieron DXF con `ezdxf`; no hay AutoCAD instalado ni cálculos de protecciones, PAT, mecánica o capacidad. | Los dos DXF siguen como borradores para revisión. La validación final requiere CAD en AutoCAD, datos del operador, topografía y firma profesional. |

## Estado de los entregables

Las láminas **CL-01** (ubicación/corredor) y **CL-02** (perfil de terreno) son visualizables en PDF y editables en DXF. El PDF integrado Rev. 0 contiene 10 páginas A4 y dos anexos A3. El paquete Rev. 0A incorpora el árbol actual y un manifiesto externo de huellas; el PDF integrado no cambió porque los siete capítulos de su memoria conservan las mismas huellas del manifiesto Rev. 0.

## Datos indispensables antes de un expediente de construcción

1. Pronunciamiento del titular de la red sobre necesidad de obra, tensión, capacidad y punto de conexión.
2. Levantamiento topográfico de precisión, inventario de apoyos, cruces, servidumbres y accesos.
3. Demanda actual/proyectada y criterio de diseño aprobado.
4. Características certificadas de conductor, estructuras, aisladores, equipos, protecciones y puesta a tierra.
5. Cálculos eléctricos y mecánicos, metrados y presupuesto basados en el diseño aprobado, además de revisión profesional y normativa vigente aplicable.

No se asignaron valores a esas variables ni se declara cumplimiento normativo. El expediente entregado es un **anteproyecto cartográfico para revisión**.
