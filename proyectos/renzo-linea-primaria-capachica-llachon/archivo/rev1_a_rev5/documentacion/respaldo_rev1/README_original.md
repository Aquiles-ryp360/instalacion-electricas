# Capachica–Llachón: anteproyecto y planos AutoCAD

**Este es el estudio de Capachica a Llachón.** Todos los datos y planos activos de este proyecto corresponden a ese corredor.

**Expediente integrado Rev. 1:** [abrir capítulos editables](expediente/README.md). El [informe de auditoría correctiva](documentacion/AUDITORIA_REV0.md) explica los hallazgos previos. La copia PDF y el ZIP **Rev. 1** para revisión están en `build/renzo-linea-primaria-capachica-llachon/` de esta máquina. Incluyen los dos planos A3; mantienen visible que faltan datos esenciales para ingeniería de construcción.

## Abrir los dos planos en AutoCAD

| Lámina | DXF con presentación A3 para AutoCAD | Vista del DXF | PDF cartográfico complementario |
|---|---|---|---|
| **CL-01 · Ubicación y corredor** | [CL-01 A3 DXF](plans/CL-01_A3_AUTOCAD_PRELIMINAR.dxf) | [PDF renderizado](plans/CL-01_A3_AUTOCAD_PRELIMINAR_vista.pdf) · [PNG](plans/CL-01_A3_AUTOCAD_PRELIMINAR_vista.png) | [PDF de ubicación](plans/CL-01_ubicacion_corredor.pdf) |
| **CL-02 · Perfil referencial del terreno** | [CL-02 A3 DXF](plans/CL-02_A3_AUTOCAD_PRELIMINAR.dxf) | [PDF renderizado](plans/CL-02_A3_AUTOCAD_PRELIMINAR_vista.pdf) · [PNG](plans/CL-02_A3_AUTOCAD_PRELIMINAR_vista.png) | [PDF de perfil](plans/CL-02_perfil_referencial.pdf) |

En AutoCAD, abre la pestaña **`CL-01_A3`** o **`CL-02_A3`** y selecciona A3 horizontal, escala de papel 1:1. La geometría en modelo está en metros. También se conservan los [DXF iniciales georreferenciados](plans/CL-01_corredor_utm19s.dxf) y [del perfil en metros](plans/CL-02_perfil_srtm_metros.dxf).

El origen de referencia es la estructura GIS `NMT000367723` próxima a Capachica y el final elegido es `NMT000027963` próximo a Llachón. La longitud calculada sobre el corredor GIS es **13,834 km**. Las coordenadas, los 27 tramos utilizados, las fuentes y las limitaciones están en el [planteamiento técnico](PLANTEAMIENTO_CAPACHICA_LLACHON.md), la [memoria del anteproyecto](documentacion/MEMORIA_ANTEPROYECTO.md) y el [control de calidad](documentacion/CONTROL_CALIDAD.md).

**Estado: borrador cartográfico.** La ruta azul del CL-01 sigue una red de media tensión publicada; no representa una línea nueva aprobada. El CL-02 usa terreno SRTM30m y no sirve para definir postes, flechas ni distancias de seguridad. Falta validar en campo y con Electro Puno el punto de conexión, la tensión, la capacidad y la necesidad de obra.

Las fuentes originales están en [`sources/`](sources/), con URL, fecha y SHA-256 en [`manifest.json`](sources/manifest.json). La geometría derivada está en [`route.json`](derived/route.json). El [cuadro GIS de tramos](datos/cuadro_tramos_gisem.csv) y el [reporte CAD](datos/reporte_generacion_cad.json) permiten comprobar el origen de las láminas. Los parámetros de diseño aún no validados se registran como `null` en [parametros_diseno_pendientes.json](datos/parametros_diseno_pendientes.json).

Los DXF A3 fueron generados por [`scripts/generar_anteproyecto_cad.py`](scripts/generar_anteproyecto_cad.py), reabiertos con `ezdxf` y renderizados por [`scripts/render_verificacion_cad.py`](scripts/render_verificacion_cad.py). Los scripts no sobrescriben las salidas existentes. Para reproducirlos, prepara una copia del proyecto sin los archivos de salida y ejecuta desde la raíz del repositorio:

```powershell
python -m pip install -r proyectos/renzo-linea-primaria-capachica-llachon/requirements.txt
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/generar_anteproyecto_cad.py
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/render_verificacion_cad.py
python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests -q
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/compilar_expediente.py
```

El compilador genera la Rev. 1 y rechaza la sobrescritura de una salida existente. Los paquetes anteriores se conservan como historial local; la revisión activa es la indicada en `proyecto.yaml`.

La extracción cartográfica inicial se hizo en el repositorio local `workspace/seace-cad-intelligence/studies/capachica_llachon`; sus archivos fuente y derivados necesarios están copiados aquí. **AutoCAD no se ejecutó en esta máquina**: el control realizado fue apertura y auditoría estructural con `ezdxf` más render de las presentaciones mediante su motor de dibujo.
