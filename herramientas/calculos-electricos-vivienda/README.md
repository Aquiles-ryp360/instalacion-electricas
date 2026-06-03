# Motor de Cálculo de Instalaciones Eléctricas Domiciliarias

Este directorio contiene una herramienta en Python desarrollada para automatizar y verificar de manera reproducible los cálculos justificativos del expediente técnico residencial de Aquiles Taylor Ramos Yapo, evitando discrepancias manuales y asegurando la trazabilidad de los resultados frente al Código Nacional de Electricidad (CNE).

## Estructura del Directorio

```text
calculos-electricos-vivienda/
├── README.md                          # Este archivo explicativo
├── data/
│   └── proyecto_aquiles_base.json     # Parámetros y circuitos de entrada (JSON)
├── scripts/
│   └── calcular_instalacion.py        # Script ejecutable de cálculo (Python)
├── output/                            # Directorio de salida (generado automáticamente)
│   ├── resultados_aquiles.json        # Resultados detallados en JSON
│   ├── tabla_cargas.tex              # Tabla de cargas formateada para LaTeX
│   ├── tabla_conductores.tex         # Tabla de conductores y llaves para LaTeX
│   └── reporte_calculos.md            # Reporte técnico en formato Markdown
└── docs/
    └── notas_formulas.md              # Resumen normativo de fórmulas y parámetros
```

## Requisitos

El script es compatible con Python 3 estándar y no requiere de librerías externas complejas.

## Ejecución del Motor de Cálculo

Para ejecutar el script y regenerar las tablas de LaTeX y el reporte en Markdown, corra el siguiente comando desde la raíz de este directorio o de la carpeta contenedora:

```bash
python3 scripts/calcular_instalacion.py
```

## Edición de Datos de Entrada

Si el propietario realiza cambios en la potencia de la cocina, añade nuevas habitaciones, modifica las longitudes de los tramos o cambia las secciones de los conductores, puede hacerlo directamente editando el archivo `data/proyecto_aquiles_base.json` y volviendo a ejecutar el script. Esto actualizará los archivos de salida del directorio `output/` de forma instantánea.
