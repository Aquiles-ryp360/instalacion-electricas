# Instalaciones Eléctricas Domiciliarias — Automatización

Pipeline completo de cálculo → CAD → diagrama unifilar → BOM → cotización para proyectos de instalaciones eléctricas residenciales en Perú.

---

## 🏗️ Estructura del Repositorio

El repositorio está organizado de la siguiente manera:

* **`herramientas/`**: Contiene los motores generales de cálculo y utilidades de automatización:
  * `pipeline_automatizado.py`: Orquestador maestro para automatizar diseño y cálculos.
  * `calculadora-instalacion-casa.html`: Calculadora interactiva web para estimar demandas.
  * `calculos-electricos-vivienda/`: Motor en Python para dimensionamiento bajo el CNE-U.
  * `ia-cad-casas/`: Scripts para generación de diagramas unifilares y ruteo ortogonal de tuberías.
  * `cotizacion/`: Scripts para búsqueda de precios de mercado y generación de presupuestos formales.
* **`proyecto_vivienda_unifamiliar_por_RENZO/`**: Expediente técnico profesional de 3 pisos (LaTeX, cálculos, planos, metrados, presupuestos y pruebas unitarias de Renzo Gabriel Mamani Galindo).
* **`Avanze-Proyecto-Aquiles/`**: Proyecto académico de vivienda unifamiliar de 2 pisos (Aquiles Ramos).

---

## 🚀 Expediente Técnico - Vivienda Unifamiliar 3 Pisos (Renzo)

El proyecto ubicado en [proyecto_vivienda_unifamiliar_por_RENZO/](./proyecto_vivienda_unifamiliar_por_RENZO/) cuenta con una arquitectura de nivel profesional (10/10) que incluye un pipeline automatizado, pruebas unitarias y flujos de CI/CD.

### Ejecución del Pipeline:
Para construir todo el expediente de forma automatizada (generar planos DXF de cada piso, diagramas unifilares, metrados, presupuestos y compilar el documento LaTeX a PDF), ejecuta:

```powershell
# Ir al proyecto
cd proyecto_vivienda_unifamiliar_por_RENZO/

# Ejecutar la compilación del expediente completo
python scripts/build_project.py
```

El PDF final compilado quedará en:
`proyecto_vivienda_unifamiliar_por_RENZO/build/main.pdf`

Para más detalles, consulta el [README específico del proyecto de Renzo](./proyecto_vivienda_unifamiliar_por_RENZO/README.md).

---

## ⚙️ Pipeline General de Herramientas

Puedes utilizar las herramientas de cálculo y cotización ubicadas en `herramientas/` de la siguiente manera:

### Motor de Cálculo:
Calcula demanda máxima, conductores y protecciones según el CNE-U:
```bash
python herramientas/calculos-electricos-vivienda/scripts/calcular_instalacion.py \
  --input herramientas/calculos-electricos-vivienda/data/proyecto.json --output output/
```

### Generación de Diagrama Unifilar:
Genera diagramas unifilares en formato DXF/PDF a partir del JSON de circuitos:
```bash
python herramientas/ia-cad-casas/scripts/generar_unifilar.py \
  --json output/instalacion_electrica.json \
  --output planos/unifilar
```

### Buscador de Precios y Cotización:
Permite asignar y buscar precios en base a listados de materiales (BOM) y generar presupuestos formales:
```bash
# Buscar precios a partir de un BOM generado
python herramientas/cotizacion/buscador_precios.py --bom output/bom.json --output output/comparativa.json
```

Ver detalles completos en [herramientas/cotizacion/README.md](./herramientas/cotizacion/README.md).

---

## 📦 Requisitos de Instalación

Para ejecutar los scripts de automatización y cálculos, instala las dependencias necesarias:
```bash
pip install -r proyecto_vivienda_unifamiliar_por_RENZO/requirements.txt
```
O de forma manual:
```bash
pip install pyyaml beautifulsoup4 ezdxf matplotlib pytest
```

---

## ⚖️ Normativa de Referencia

* **Código Nacional de Electricidad - Utilización (CNE-U)**: Criterios de demanda máxima, conductores, caídas de tensión y factores de simultaneidad.
* **Reglamento Nacional de Edificaciones (RNE EM.010)**: Parámetros técnicos mínimos de seguridad para instalaciones eléctricas residenciales interiores.
