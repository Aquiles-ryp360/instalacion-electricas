# Proyecto: Instalaciones Eléctricas Domiciliarias Interiores

Repositorio grupal para la organización, cálculo, diseño y compilación del expediente técnico-académico de instalaciones eléctricas domiciliarias interiores, desarrollado para el curso de **Instalaciones Eléctricas I** (UNAP).

---

## 👥 Integrantes y Proyectos

El repositorio alberga el desarrollo de las propuestas de instalación eléctrica domiciliaria de los dos integrantes:

### 1. Renzo Gabriel Mamani Galindo (Proyecto 3 Pisos)
* **Vivienda:** Unifamiliar de 3 pisos, área construida de 40 m² por piso.
* **Ubicación:** Jr. Lima S/N, Capachica, Puno (Zona Urbana).
* **Estado:** Informe unificado y compilable en LaTeX.
* **Archivos clave:**
  * [informe_instalaciones_electricas.md](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/informe_instalaciones_electricas.md): Informe consolidado en formato Markdown.
  * [latex/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/latex): Código fuente de LaTeX para el informe completo y planos vinculados.
  * [latex/build/main.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/latex/build/main.pdf): PDF final compilado del informe de 3 pisos.

### 2. Aquiles Taylor Ramos Yapo (Proyecto 2 Pisos)
* **Vivienda:** Unifamiliar (casa grande) de 2 pisos, terreno de 134.18 m² (segundo piso de aprox. 42.56 m² construidos, primer piso con menor área construida).
* **Ubicación:** Av. Horacio con Jr. Marineros, Mz F7, Lotes 11 y 12, San Miguel, San Román, Puno (Zona Urbana).
* **Estado:** Expediente y planos sincronizados en la versión **v4**.
* **Archivos clave (Carpeta de Aporte):**
  * [Avanze-Proyecto-Aquiles/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles): Directorio principal de aportes.
  * [proyecto-latex-instalaciones/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/proyecto-latex-instalaciones): Directorio del proyecto LaTeX aislado.
  * [proyecto-latex-instalaciones/build/main.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/proyecto-latex-instalaciones/build/main.pdf): PDF del expediente técnico de 2 pisos compilado (Memoria descriptiva y cálculos).
  * [herramientas/calculos-electricos-vivienda/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/calculos-electricos-vivienda): Motor de cálculo de cargas en Python.
  * [trabajo-cad-casa/electricos/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos): Planos DXF/PDF y documentación de revisiones del primer y segundo piso.

---

## 📂 Estructura General del Repositorio

```text
instalacion-electricas/
├── Avanze-Proyecto-Aquiles/       # Carpeta de aportes para el proyecto de 2 pisos (Aquiles)
│   ├── Full-Imagenes/            # Croquis originales y plantillas visuales CAD
│   ├── trabajo-cad-casa/         # Modelación CAD de la vivienda (layouts y salidas)
│   │   └── electricos/           # Datos JSON, planos finales DXF/PDF y revisiones
│   └── proyecto-latex-instalaciones/ # Expediente técnico en LaTeX (2 pisos)
│
├── herramientas/                 # Utilidades y automatizaciones del proyecto
│   ├── ia-cad-casas/             # Motor de generación automática de planos DXF/PDF
│   ├── calculos-electricos-vivienda/ # Motor de cálculo de cargas y demanda máxima
│   └── calculadora-instalacion-casa.html # Calculadora HTML interactiva de cargas
│
├── latex/                        # Compilación LaTeX del proyecto de 3 pisos (Gael Renzo)
│   ├── build/                    # PDF generado final (main.pdf)
│   ├── capitulos/                # Archivos .tex de cada capítulo (Portada, Memoria, etc.)
│   ├── planos/                   # Planos y esquemas eléctricos en formato PDF y CAD (.dwg)
│   └── main.tex                  # Archivo principal de compilación LaTeX
│
├── materiales/                   # Normativas e información de referencia técnica
│   ├── normas/                   # Normativas nacionales en PDF (CNE-U, RNE, etc.)
│   ├── proyecto-guia-red-primaria/ # Ejemplos de formato de proyectos guía
│   └── INSTALACIONES ELECTRICAS DVD 28.02-23/ # Planos modelo y material didáctico
│
├── normativas/                   # Resúmenes técnicos y fichas normativas base (CNE-U, RNE EM.010)
├── proyecto-casa/                # Estructura del proyecto final domiciliario (07-planos)
└── README.md                     # Este archivo informativo
```

---

## 🛠️ Herramientas y Compilación

### Compilación del Informe LaTeX

#### 1. Proyecto 3 Pisos (Renzo Mamani)
Ejecuta desde el directorio `latex/`:
```bash
pdflatex -interaction=nonstopmode -output-directory=build main.tex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```
El PDF final se genera en `latex/build/main.pdf`.

#### 2. Proyecto 2 Pisos (Aquiles Ramos)
Ejecuta desde el directorio `Avanze-Proyecto-Aquiles/proyecto-latex-instalaciones/`:
```bash
pdflatex -interaction=nonstopmode -output-directory=build main.tex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```
El PDF final se genera en `Avanze-Proyecto-Aquiles/proyecto-latex-instalaciones/build/main.pdf`.

### Motor de Cálculo de Cargas y Demanda Máxima
Para actualizar los cálculos justificativos y regenerar las tablas LaTeX para el proyecto de 2 pisos, edite el JSON [proyecto_aquiles_base.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/calculos-electricos-vivienda/data/proyecto_aquiles_base.json) y luego ejecute desde la raíz del repositorio:
```bash
python3 herramientas/calculos-electricos-vivienda/scripts/calcular_instalacion.py
```
Esto actualizará los archivos de salida en `herramientas/calculos-electricos-vivienda/output/` automáticamente.

### Superposición Eléctrica y Planos CAD
Para aplicar la simbología y circuitos eléctricos sobre la arquitectura base, ejecute desde la raíz:
```bash
herramientas/ia-cad-casas/.venv/bin/python \
  herramientas/ia-cad-casas/scripts/electrical_overlay.py \
  --base Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.dxf \
  --electrical Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/data/electrico_piso1_v4.json \
  --output Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v4.dxf
```
Para exportarlo a PDF usando QCAD en modo headless:
```bash
qcad -no-gui -platform offscreen -quit \
  -autostart "$(realpath herramientas/ia-cad-casas/cad-scripts/dxf2pdf.js)" \
  -input "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v4.dxf)" \
  -output "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v4.pdf)"
```

### Calculadora de Cargas Interactiva
La calculadora interactiva está en [calculadora-instalacion-casa.html](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/calculadora-instalacion-casa.html). Puedes abrirla en tu navegador para realizar estimaciones rápidas de demanda máxima.

---

## 📚 Normativa de Respaldo
El proyecto se rige y fundamenta técnicamente en las siguientes normativas peruanas:
1. **Código Nacional de Electricidad - Utilización (CNE-U)**: Define las reglas para el cálculo de demanda máxima, circuitos mínimos y calibre de conductores en unidades de vivienda.
2. **Reglamento Nacional de Edificaciones (RNE), Norma EM.010**: Establece el alcance general y requerimientos técnicos exigibles para instalaciones eléctricas interiores.
