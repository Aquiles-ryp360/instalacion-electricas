# Mini Proyecto: Instalaciones Eléctricas Domiciliarias

Repositorio grupal para la organización, cálculo, diseño y compilación del informe académico de instalaciones eléctricas domiciliarias interiores, desarrollado para el curso de **Instalaciones Eléctricas I** (UNAP).

---

## 👥 Integrantes y Proyectos

El repositorio alberga el avance y desarrollo de las propuestas de instalación eléctrica domiciliaria de los dos integrantes:

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
* **Estado:** Avances y borradores del capítulo I y II en desarrollo.
* **Archivos clave (Carpeta de Aporte):**
  * [avance-capitulos-1-2/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/avance-capitulos-1-2): Directorio principal de aportes del proyecto de 2 pisos.
  * [avance-capitulos-1-2/capitulo-1-memoria-descriptiva.md](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/avance-capitulos-1-2/capitulo-1-memoria-descriptiva.md): Borrador de la memoria descriptiva.
  * [avance-capitulos-1-2/capitulo-2-calculos-justificativos.md](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/avance-capitulos-1-2/capitulo-2-calculos-justificativos.md): Borrador de los cálculos justificativos (demanda eléctrica).
  * [avance-capitulos-1-2/respuestas-cuestionario-aquiles.md](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/avance-capitulos-1-2/respuestas-cuestionario-aquiles.md): Cuestionario de datos y parámetros técnicos consolidado.
  * [avance-capitulos-1-2/latex/planificacion-vivienda-aquiles.tex](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/avance-capitulos-1-2/latex/planificacion-vivienda-aquiles.tex): Documento de planificación inicial compilable en LaTeX.

---

## 📂 Estructura General del Repositorio

```text
instalacion-electricas/
├── avance-capitulos-1-2/         # Carpeta de aportes para el proyecto de 2 pisos (Aquiles)
│   ├── Capturas-de-medidas-de-la-casa/ # Evidencias del catastro y medidas de la vivienda
│   ├── latex/                    # Documentación LaTeX del avance de 2 pisos
│   ├── capitulo-1-memoria-descriptiva.md
│   ├── capitulo-2-calculos-justificativos.md
│   └── respuestas-cuestionario-aquiles.md
│
├── latex/                        # Compilación LaTeX del proyecto de 3 pisos (Gael Renzo)
│   ├── build/                    # PDF generado final (main.pdf)
│   ├── capitulos/                # Archivos .tex de cada capítulo (Portada, Memoria, Criterios, etc.)
│   ├── planos/                   # Planos y esquemas eléctricos en formato PDF y CAD (.dwg)
│   └── main.tex                  # Archivo principal de compilación LaTeX
│
├── materiales/                   # Normativas e información de referencia técnica
│   ├── normas/                   # Normativas nacionales en PDF (CNE-U, RNE, etc.)
│   ├── proyecto-guia-red-primaria/ # Ejemplos de formato de proyectos guía
│   └── INSTALACIONES ELECTRICAS DVD 28.02-23/ # Material didáctico de referencia, simulaciones y planos modelo
│
├── herramientas/                 # Utilidades de desarrollo
│   └── calculadora-instalacion-casa.html # Calculadora HTML interactiva de cargas eléctricas domiciliarias
│
├── normativas/                   # Resúmenes técnicos y fichas normativas base (CNE-U, RNE EM.010)
├── proyecto-casa/                # Estructura de plantilla inicial del proyecto
└── README.md                     # Este archivo informativo
```

---

## 🛠️ Herramientas y Compilación

### Compilación del Informe LaTeX (Proyecto 3 Pisos)
Para compilar el informe y regenerar el documento final en PDF (`latex/build/main.pdf`), ejecuta los siguientes comandos desde la terminal dentro de la carpeta `latex/`:

```bash
pdflatex -interaction=nonstopmode -output-directory=build main.tex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```

### Calculadora de Cargas
La calculadora interactiva está en [calculadora-instalacion-casa.html](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/calculadora-instalacion-casa.html). Puedes abrirla en tu navegador para realizar estimaciones rápidas de demanda máxima por áreas y circuitos.

---

## 📚 Normativa de Respaldo
El proyecto se rige y fundamenta técnicamente en las siguientes normativas peruanas:
1. **Código Nacional de Electricidad - Utilización (CNE-U)**: Define las reglas para el cálculo de demanda máxima, circuitos mínimos y calibre de conductores en unidades de vivienda.
2. **Reglamento Nacional de Edificaciones (RNE), Norma EM.010**: Establece el alcance general y requerimientos técnicos exigibles para instalaciones eléctricas interiores.
