# Proyecto de Instalaciones Eléctricas - Vivienda Unifamiliar

Este repositorio contiene el expediente técnico completo y la automatización para el proyecto de instalaciones eléctricas de una vivienda unifamiliar de 3 pisos, diseñado bajo la normativa peruana (**Código Nacional de Electricidad - Utilización (CNE-U)** y **Reglamento Nacional de Edificaciones (RNE)**).

---

## 🏗️ Organización y Estructura del Repositorio

El repositorio ha sido reorganizado y optimizado bajo estándares profesionales de consultoría de ingeniería y oficinas de proyectos (PMO):

### A. Estructura de Git y Eliminación de "Ramas Físicas"
* Se eliminaron las carpetas de trabajo físico redundantes (`rama-*`). El flujo de trabajo colaborativo está documentado en [docs/workflow_git.md](./docs/workflow_git.md).

### B. Segmentación de Planos (Fuentes vs. Entregables)
* **Planos de Entrada:** Ubicados en [planos/fuentes/](./planos/fuentes/), contiene los planos arquitectónicos de fondo e inputs originales.
* **Entregables Finales:** Ubicados en [planos/entregables/](./planos/entregables/), organizados por tipo de archivo (`dwg/`, `dxf/`, `pdf/`, `png/`).

### C. Centralización de Configuraciones (`/config`)
* Se crearon archivos YAML en [config/](./config/) para desacoplar los parámetros del proyecto del código fuente:
  * `proyecto.yaml`: Datos geométricos, cargas y áreas de la vivienda.
  * `normativa.yaml`: Factores de demanda, intensidades máximas admisibles y caída de tensión según CNE-U.
  * `proveedores.yaml`: Base de datos de materiales comerciales y precios de referencia.

### D. Portabilidad y Modularidad de Scripts
* Todos los scripts de automatización de planos y presupuestos se movieron a la carpeta [scripts/](./scripts/) y fueron refactorizados con rutas relativas dinámicas (`pathlib`) para garantizar portabilidad.
* Se creó un paquete Python modular bajo la carpeta [src/electrica_peru/](./src/electrica_peru/) para centralizar cálculos y automatizaciones.

---

## 📄 Compilación del Expediente Técnico (LaTeX)

El documento principal recopila toda la información técnica, cálculos, metrados y presupuestos.

### Compilar el Expediente:
Desde la raíz del proyecto, ejecuta en tu terminal:
```powershell
pdflatex -interaction=nonstopmode -output-directory=build main.tex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```

El PDF generado quedará ubicado en:
```text
build/main.pdf
```

---

## 🗂️ Árbol Completo de Archivos

```text
proyecto_vivienda_unifamiliar_por_RENZO/
├── 02_memoria_calculo/
│   ├── hojas_excel/
│   │   └── maxima_demanda.xlsx                  # Cálculo de cargas y máxima demanda general
│   └── memoria_calculo.md                       # Memoria descriptiva en formato Markdown
├── 03_especificaciones/
│   └── especificaciones_tecnicas.md             # Especificaciones generales del proyecto
├── 04_metrados_y_presupuesto/
│   ├── metrados.xlsx                            # Cuadro general de metrados por partidas
│   └── presupuesto.xlsx                         # Presupuesto general estimado
├── config/
│   ├── normativa.yaml                           # Parámetros y tablas del CNE-U
│   ├── proveedores.yaml                         # Listas de materiales y proveedores
│   └── proyecto.yaml                            # Parámetros específicos de la vivienda
├── docs/
│   ├── auditorias/
│   │   └── revision_inicial.md                  # Auditoría de organización inicial
│   ├── reportes/
│   │   ├── bom/                                 # Bill of Materials generados
│   │   │   ├── bom_consolidada.md
│   │   │   ├── bom_piso1.md
│   │   │   ├── bom_piso2.md
│   │   │   ├── bom_piso3.md
│   │   │   └── bom_proyecto_completo.md
│   │   ├── memoria-tecnica/                     # Memorias y validaciones normativas
│   │   │   ├── memoria_descriptiva.md
│   │   │   ├── memoria_tecnica.md
│   │   │   ├── memoria_tecnica_proyecto.md
│   │   │   ├── reporte_analisis_inicial.md
│   │   │   ├── reporte_nec_aplicado.md
│   │   │   └── reporte_validacion.md
│   │   └── reportes/
│   │       ├── diagramas_unifilares.md
│   │       └── informe_validacion_inicial.md
│   ├── revisiones/                              # Revisiones de diseño por pisos y versiones
│   │   ├── revision_piso1_v1.md
│   │   ├── revision_piso1_v2.md
│   │   ├── revision_piso1_v3.md
│   │   ├── revision_piso2_v1.md
│   │   ├── ... (v2, v3 de cada piso)
│   │   └── revisiones/
│   │       ├── revision_ie_02_alumbrado_v1.md
│   │       ├── revision_ie_03_tomacorrientes_v1.md
│   │       └── revision_ie_04_circuitos_canalizaciones_v1.md
│   └── workflow_git.md                          # Guía del flujo de trabajo y ramas de Git
├── datos_diseno/                                # Modelos de datos del diseño
│   ├── layouts/                                 # Layouts JSON por piso y versión
│   │   ├── primer_piso_nuevo.json
│   │   ├── primer_piso_v1.json
│   │   ├── ... (segundo y tercer piso, versiones v1-v3)
│   └── modelo_electrico/                        # Modelos de cableado y canalización
│       ├── ie_02_alumbrado_v1.json
│       ├── ie_03_tomacorrientes_v1.json
│       ├── ie_04_circuitos_canalizaciones_v1.json
│       └── instalaciones_electricas_nueva.json
├── diagramas/                                   # Diagramas unifilares y de puesta a tierra
│   ├── diagrama_unifilar.drawio
│   ├── diagrama_unifilar.dxf
│   ├── diagrama_unifilar.pdf
│   ├── diagrama_unifilar.svg
│   ├── puesta_a_tierra.dxf
│   └── puesta_a_tierra.pdf
├── cotizaciones/                                # Análisis de mercado y cotización final
│   ├── cotizacion_comparativa_renzo.pdf
│   ├── cotizacion_comparativa_renzo.tex
│   ├── cotizacion_comparativa_renzo.xlsx
│   └── resultados_renzo_general.json
├── figuras/                                     # Figuras de soporte del documento
│   ├── plano_catastral.png
│   └── ubicacion_satelital.png
├── metrados/                                    # Hojas de metrados parciales en LaTeX
│   ├── metrado_accesorios.tex
│   ├── metrado_cajas.tex
│   ├── metrado_conductores.tex
│   ├── metrado_puesta_tierra.tex
│   ├── metrado_tableros.tex
│   ├── metrado_tuberias.tex
│   ├── puntos_por_circuito.tex
│   └── resumen_metrados.tex
├── partidas/                                    # Especificaciones por partida en LaTeX
│   ├── 01-conexion-red-externa.tex
│   ├── 02-salidas-alumbrado-tomacorrientes.tex
│   ├── 03-canalizaciones-tuberias.tex
│   ├── 04-conductores-cables.tex
│   ├── 05-cajas-tableros-protecciones.tex
│   └── 08-puesta-tierra.tex
├── presupuesto/                                 # Precios y análisis de costos en LaTeX
│   ├── precios_unitarios.tex
│   └── presupuesto_general.tex
├── planos/                                      # Directorio maestro de planos
│   ├── fuentes/                                 # Archivos arquitectónicos base
│   │   ├── plano arquitectonico.png
│   │   ├── primer piso.png
│   │   ├── primer_piso_nuevo.dxf
│   │   ├── primer_piso_v1.dxf
│   │   └── ... (segundo y tercer piso, versiones v1-v3)
│   └── entregables/                             # Planos generados listos para entregar
│       ├── dwg/                                 # Formato CAD DWG/DXF
│       ├── dxf/                                 # Formato vectorial DXF
│       ├── pdf/                                 # Planos en PDF a escala
│       └── png/                                 # Vistas en imagen de alta resolución
├── scripts/                                     # Scripts de Python para automatización
│   ├── copy_final_architectural.py
│   ├── create_folders.py
│   ├── create_layouts.py
│   ├── create_revision_files.py
│   ├── generate_all_versions.py
│   ├── generate_electrical_drawings.py
│   ├── generate_individual_floors_nuevo.py
│   ├── generate_spreadsheets.py
│   ├── process_renzo_comparative.py
│   ├── split_latex_tables.py
│   └── update_latex_metrados.py
├── src/                                         # Código fuente modular reutilizable
│   └── electrica_peru/
│       ├── __init__.py
│       ├── calculos/
│       ├── cotizacion/
│       ├── planos/
│       └── reportes/
├── build/                                       # Archivos de compilación intermedia de LaTeX
│   ├── main.pdf                                 # Documento final del expediente compilado
│   └── ... (aux, log, out, toc, lof, lot)
├── main.tex                                     # Archivo maestro del expediente LaTeX
├── README.md                                    # Presentación general del proyecto
└── .gitignore                                   # Filtro de archivos temporales de diseño
```
