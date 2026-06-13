# Proyecto de Instalaciones Eléctricas - Vivienda Unifamiliar

Este repositorio contiene el expediente técnico completo y la automatización para el proyecto de instalaciones eléctricas de una vivienda unifamiliar de 3 pisos, diseñado bajo la normativa peruana (**Código Nacional de Electricidad - Utilización (CNE-U)** y **Reglamento Nacional de Edificaciones (RNE)**).

---

## 🏗️ Organización y Estructura del Repositorio

El repositorio ha sido reorganizado y optimizado bajo estándares de nivel consultora de ingeniería y oficinas de proyectos (PMO), alcanzando una madurez de arquitectura de **10/10**:

### A. Estructura Oficial del Expediente Técnico
* **`01_memoria_descriptiva/`**: Memoria descriptiva general y ubicación del predio.
* **`02_memoria_calculo/`**: Memorias de cálculo (cargas, demanda y alimentadores).
* **`03_especificaciones/`**: Fichas técnicas generales y especificaciones del proyecto.
* **`04_metrados/`**: Hojas de metrados detallados en formato XLSX y LaTeX.
* **`05_presupuesto/`**: Análisis de costos unitarios y presupuesto estimado general.
* **`06_planos/`**: Archivos de planos unificados en sus tres subcarpetas:
  * `fuentes/`: Planos arquitectónicos base.
  * `diagramas/`: Diagramas unifilares y puestas a tierra.
  * `entregables/`: Planos finales listos para entrega agrupados por formato (`dwg/`, `dxf/`, `pdf/`, `png/`).
* **`07_anexos/`**: Documentación complementaria dividida en `catastro/`, `normativa/`, `fichas_tecnicas/` y `evidencias/`.

### B. Pruebas Unitarias y Configuración Profesional
* **`/tests`**: Pruebas automáticas utilizando `pytest` para validar algoritmos de cálculo:
  * `test_demanda.py`: Validaciones de cargas y áreas.
  * `test_conductores.py`: Validaciones de caída de tensión.
  * `test_circuitos.py`: Dimensionamiento de llaves termomagnéticas.
  * `test_presupuesto.py`: Fórmulas de cálculo de presupuesto total.
* **`pyproject.toml`** y **`requirements.txt`**: Archivos de empaquetado y control de dependencias para reproducibilidad completa del entorno Python.

---

## 📄 Compilación Completa en un Solo Comando

Para compilar todo el expediente técnico (incluyendo renders de planos CAD, generación de tablas de metrados en LaTeX y el PDF final compilado con todas sus referencias cruzadas), ejecuta el script orquestador:

```bash
python scripts/build_project.py
```

Este comando automatiza secuencialmente:
1. La compilación de versiones arquitectónicas en CAD (`scripts/generate_all_versions.py`).
2. La generación de planos eléctricos y diagramas unifilares en PDF, DXF y SVG (`scripts/generate_electrical_drawings.py`).
3. El cálculo de las tablas de metrados y su inyección en LaTeX (`scripts/update_latex_metrados.py`).
4. La compilación doble en LaTeX de la memoria completa (`main.tex`).

El PDF temporal generado quedará ubicado en:
```text
build/main.pdf
```

Después de la revisión técnica, la versión publicada se conserva en
`entregables/expediente.pdf`.

---

## 🗂️ Árbol Completo de Archivos

```text
proyectos/renzo/
├── 01_memoria_descriptiva/
│   └── memoria_descriptiva.md                   # Memoria descriptiva en Markdown
├── 02_memoria_calculo/
│   ├── hojas_excel/
│   │   └── maxima_demanda.xlsx                  # Máxima demanda y cuadro de cargas
│   └── memoria_calculo.md                       # Memoria de cálculo en Markdown
├── 03_especificaciones/
│   └── especificaciones_tecnicas.md             # Especificaciones generales
├── 04_metrados/
│   └── metrados.xlsx                            # Plantilla de metrados detallada
├── 05_presupuesto/
│   └── presupuesto.xlsx                         # Presupuesto general estimado
├── 06_planos/                                   # Carpeta maestra de planos
│   ├── fuentes/                                 # Planos arquitectónicos base
│   ├── diagramas/                               # Diagramas unifilares y puesta a tierra
│   └── entregables/                             # Planos finales generados (dwg, dxf, pdf, png)
├── 07_anexos/                                   # Anexos e información catastral/normativa
│   ├── catastro/
│   ├── evidencias/
│   ├── fichas_tecnicas/
│   └── normativa/
├── config/
│   ├── normativa.yaml                           # Normas y factores de demanda del CNE-U
│   ├── proveedores.yaml                         # Precios unitarios y catálogos comerciales
│   └── proyecto.yaml                            # Parámetros geométricos y datos de carga
├── docs/                                        # Documentación de revisiones y reportes
│   ├── revisiones/
│   │   ├── circuitos/                           # Auditorías por circuitos
│   │   └── pisos/                               # Revisiones por niveles
│   └── workflow_git.md                          # Guía de control de versiones
├── metrados/                                    # Fragmentos de tablas LaTeX para metrados
├── partidas/                                    # Especificaciones técnicas de partidas LaTeX
├── presupuesto/                                 # Tablas de costos y APU en LaTeX
├── scripts/                                     # Scripts de automatización y compilación
│   ├── build_project.py                         # Orquestador del pipeline completo
│   ├── generate_electrical_drawings.py          # Generador de planos eléctricos e imágenes
│   └── ...
├── src/                                         # Código fuente modular en Python
│   └── electrica_peru/
├── tests/                                       # Pruebas unitarias automatizadas
│   ├── test_circuitos.py
│   ├── test_conductores.py
│   ├── test_demanda.py
│   └── test_presupuesto.py
├── build/                                       # Archivos temporales ignorados por Git
├── entregables/
│   └── expediente.pdf                           # Expediente revisado y publicado
├── main.tex                                     # Documento raíz de LaTeX
├── requirements.txt                             # Librerías de Python requeridas
└── pyproject.toml                               # Configuración de empaquetado del proyecto
```
