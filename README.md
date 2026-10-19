# Proyectos académicos de ingeniería eléctrica

Repositorio de expedientes, cálculos, CAD y cartografía de estudiantes de la Universidad Nacional del Altiplano, Puno. Los proyectos se organizan por alcance y autor; las herramientas y referencias comunes tienen sus propias carpetas.

## Proyectos de Aquiles: dos cursos independientes

| Curso | Proyecto | Documentos para revisar |
| --- | --- | --- |
| **Centrales Hidroeléctricas** | [Minicentral Limbani · Michell-Banki](proyectos/aquiles-central-michell-banki/README.md) | [Memoria PDF](proyectos/aquiles-central-michell-banki/entregables/r03/Minicentral_Limbani_R03_proyecto_academico.pdf) · [Planos PDF](proyectos/aquiles-central-michell-banki/entregables/r03/Minicentral_Limbani_R03_planos_academicos.pdf) · [Exposición](proyectos/aquiles-central-michell-banki/entregables/r03/Minicentral_Limbani_R03_exposicion.pdf) |
| **Instalaciones Eléctricas II** | [Línea primaria Limbani–Huancasayani](proyectos/aquiles-linea-primaria-inst-ii/README.md) | [Expediente único](proyectos/aquiles-linea-primaria-inst-ii/entregables/proyecto-final/Expediente.pdf) · [ZIP de presentación](proyectos/aquiles-linea-primaria-inst-ii/entregables/Proyecto_Linea_Primaria_Limbani_Huancasayani.zip) · [Excel, CAD y cartografía](proyectos/aquiles-linea-primaria-inst-ii/entregables/proyecto-final/) |

La minicentral estudia generación hidroeléctrica. La línea primaria estudia el transporte desde la transformación de salida hasta la subestación de llegada en Huancasayani. Cada una conserva sus parámetros, cálculos, memoria y entregables; compartir antecedentes de Limbani no hace equivalentes sus hipótesis de diseño.

## Todos los proyectos

El **[catálogo por curso y autor](proyectos/README.md)** reúne los once proyectos: centrales, líneas primarias, estaciones de servicio y viviendas de Aquiles, Renzo y Diego. Incluye Capachica–Chifrón y Capachica–Llachón, con enlaces a sus revisiones y estados propios.

Los documentos son trabajos académicos revisables. El estado y las entradas de cada proyecto se consultan en su `proyecto.yaml`; los pendientes técnicos permanecen en la documentación correspondiente. La presencia de un archivo en GitHub no supone aprobación para ejecutar una obra.

## Organización

| Carpeta | Contenido |
| --- | --- |
| [proyectos/](proyectos/README.md) | Un expediente independiente por proyecto, con identificación de curso y autor. |
| [herramientas/](herramientas/README.md) | Motores de cálculo, CAD, presupuestos, topografía y levantamiento. |
| [herramientas/biblioteca_dge/](herramientas/biblioteca_dge/README.md) | Referencias DGE y biblioteca vectorizada, con procedencia y limitaciones. |
| [recursos/](recursos/README.md) | Identidad gráfica e imágenes de ubicación compartidas. |
| [referencias/](referencias/README.md) | Normativa y documentos de consulta; material local identificado. |
| [docs/](docs/README.md) | Guías de trabajo, política de datos y registro de organización. |
| `build/`, `output/` | Resultados locales regenerables; ignorados por Git. |

Dentro de cada proyecto se distinguen `fuentes/` (originales), `datos/` (entradas), `expediente/` (memoria editable), `documentacion/` (decisiones y pendientes), `entregables/` (archivos compartidos con su estado declarado) y `archivo/` (antecedentes). Las variantes históricas de otros estudiantes mantienen su ubicación y estado declarado; no se elige una revisión solo por su nombre.

## Uso de las herramientas

Desde la raíz del repositorio, con Python y las dependencias instaladas:

```powershell
python -m pip install -r requirements.txt
python herramientas/verificar_organizacion.py
python -m pytest -q herramientas/cotizacion/v0_legacy/tests herramientas/cotizacion/v1/tests proyectos/renzo/tests proyectos/unidad-2-industrial/tests
```

Cada proyecto documenta su constructor y sus requisitos adicionales. El pipeline residencial se conserva para los proyectos que lo habilitan:

```powershell
python herramientas/pipeline_automatizado.py --proyecto aquiles
python herramientas/pipeline_automatizado.py --proyecto renzo
```

La minicentral y la línea primaria utilizan sus **constructores específicos**, enlazados en sus README. Los programas escriben resultados de trabajo que deben revisarse antes de compartirlos. Algunas investigaciones requieren fuentes pesadas locales, LaTeX, QGIS o AutoCAD; no se presupone que estén instalados en otro equipo.

La [guía de organización](docs/organizacion-repositorio.md) registra las rutas anteriores y actuales, los archivos históricos y el alcance de esta reorganización. Antes de modificar entradas técnicas, consultar [AGENTS.md](AGENTS.md) y la [política de datos](docs/politica-datos.md).

La [entrega consolidada de la línea primaria](proyectos/aquiles-linea-primaria-inst-ii/entregables/proyecto-final/) reúne un expediente con ecuaciones LaTeX y metrados desarrollados, tres Excel con fórmulas, CAD y cartografía. El [historial móvil](proyectos/aquiles-linea-primaria-inst-ii/revisiones/README.md) y las [fuentes recuperadas](referencias/guias-originales/README.md) se conservan aparte del ZIP de presentación.
