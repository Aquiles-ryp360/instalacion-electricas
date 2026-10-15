# Herramientas

Motores reutilizables del repositorio. Los parámetros y decisiones particulares pertenecen a cada proyecto. Consultar los requisitos del módulo antes de ejecutarlo; no todas las herramientas comparten dependencias ni estado de validación.

| Herramienta | Finalidad |
| --- | --- |
| [pipeline_automatizado.py](pipeline_automatizado.py) | Ejecutar el flujo habilitado por `proyecto.yaml`. |
| [verificar_organizacion.py](verificar_organizacion.py) | Revisar catálogo, navegación y rutas activas después de reorganizar. |
| [calculos/](calculos/README.md) | Cálculos de instalaciones interiores y tablas. |
| [cad/](cad/README.md) | DXF arquitectónico, superposición eléctrica y [QElectroTech](cad/QELECTROTECH.md). |
| [simbologia/](simbologia/README.md) | Símbolos y referencias para representación CAD. |
| [biblioteca_dge/](biblioteca_dge/README.md) | Armados y símbolos derivados de fuentes DGE; PDFs, CAD y trazabilidad. |
| [cotizacion/](cotizacion/README.md) | Metrados, BOM, comparación de precios y documentos de compra; versiones separadas. |
| [calculadora/](calculadora/) | Calculadora HTML local. |
| [hidroelectricas/](hidroelectricas/README.md) | Hidráulica, cuencas y transitorios para proyectos hidroeléctricos. |
| [lineas_primarias/](lineas_primarias/) | Cálculos mecánicos y eléctricos de líneas. |
| [red_mt/](red_mt/) | Utilidades de representación de media tensión. |
| [linea_primaria_preliminar/](linea_primaria_preliminar/README.md) | Preparación cartográfica preliminar de corredores y láminas. |
| [topografia/](topografia/README.md) | Datos de elevación y productos de topografía de gabinete. |
| [levantamiento_campo/](levantamiento_campo/README.md) | Capas y GeoPackage para comprobación de campo. |

Las salidas de trabajo deben dirigirse a `build/` o a la ruta de trabajo declarada por el proyecto. Los scripts específicos de la minicentral y de la línea Limbani–Huancasayani permanecen en las carpetas de esos proyectos. [Catálogo de proyectos](../proyectos/README.md).
