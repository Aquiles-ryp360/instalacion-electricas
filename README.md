# Instalaciones Eléctricas Domiciliarias — Automatización

Pipeline completo de cálculo → CAD → diagrama unifilar → BOM → cotización para proyectos de instalaciones eléctricas residenciales en Perú.

---

## Pipeline Automatizado

```
YAML config → Cálculos eléctricos → JSON → DXF/PDF (planos + unifilar) → BOM → Cotización
```

```bash
# Pipeline completo de un solo paso
python3 herramientas/pipeline_automatizado.py \
  --config proyecto.yaml \
  --output-dir resultados/

# O paso a paso:
python3 herramientas/calculos-electricos-vivienda/scripts/calcular_instalacion.py \
  --input data/proyecto.json --output output/
```

---

## Cotización

Todas las herramientas de cotización están en `herramientas/cotizacion/`:

| Herramienta | Descripción |
|-------------|-------------|
| `buscador_precios.py` | Busca y asigna precios de materiales (enlaces + cache + Google API) |
| `generar_cotizacion.py` | Genera cotización formal HTML/LaTeX |

```bash
# Ir al directorio de cotización
cd herramientas/cotizacion/

# 1. Asignar precios manuales
python3 buscador_precios.py --precio "cable TW 2.5mm2=12.50" --precio "ITM 2P 20A=89.00"

# 2. Buscar precios para todo el BOM
python3 buscador_precios.py --bom ../../output/bom.json --output ../../output/comparativa

# 3. Actualizar BOM con los precios
python3 buscador_precios.py --bom ../../output/bom.json --actualizar ../../output/bom.json

# 4. Generar cotización
python3 generar_cotizacion.py --bom ../../output/bom.json \
  --cliente "Juan Perez" --empresa "Mi Empresa" \
  --output ../../output/cotizacion
```

Ver `herramientas/cotizacion/README.md` para el flujo completo y todas las opciones.

### `generar_unifilar.py` — Diagrama unifilar

Genera diagrama unifilar en DXF + PDF a partir del JSON de circuitos.

```bash
python3 ia-cad-casas/scripts/generar_unifilar.py \
  --json output/instalacion_electrica.json \
  --output planos/unifilar
```

### `auto_routing.py` — Enrutamiento ortogonal de tuberías

Calcula rutas ortogonales (en L) entre grupos de circuitos y el tablero general.

```bash
python3 ia-cad-casas/scripts/auto_routing.py \
  --json output/instalacion_electrica.json \
  --output planos/ruteo.dxf
```

### `calcular_instalacion.py` — Motor de cálculo

Calcula demanda máxima, conductores, protecciones según CNE-U.

```bash
python3 calculos-electricos-vivienda/scripts/calcular_instalacion.py \
  --input data/proyecto.json --output output/
```

---

## Instalación

```bash
pip install pyyaml beautifulsoup4    # pipeline + busqueda
pip install ezdxf matplotlib         # CAD / unifilar / PDF
```

---

## Proyectos Académicos

El repositorio también contiene los expedientes técnicos completos de:

- **Renzo Mamani** — Vivienda unifamiliar 3 pisos, Capachica, Puno (LaTeX en `latex/`)
- **Aquiles Ramos** — Vivienda unifamiliar 2 pisos, San Miguel, Puno (LaTeX en `Avanze-Proyecto-Aquiles/`)

Ver secciones abajo para compilación LaTeX y detalles de cada proyecto.

---

## 📂 Estructura

```
├── herramientas/
│   ├── pipeline_automatizado.py       # Orquestador maestro
│   ├── cotizacion/
│   │   ├── README.md                  # Documentacion de cotizacion
│   │   ├── buscador_precios.py        # Buscador de precios en linea
│   │   └── generar_cotizacion.py      # Generador de cotizaciones
│   ├── calculadora-instalacion-casa.html  # Calculadora HTML interactiva
│   ├── ia-cad-casas/scripts/
│   │   ├── generar_unifilar.py        # Diagrama unifilar DXF/PDF
│   │   └── auto_routing.py            # Enrutamiento de tuberias
│   └── calculos-electricos-vivienda/scripts/
│       ├── calcular_instalacion.py    # Motor de calculo de cargas
│       └── generar_bom.py             # Generador de BOM + costos
├── Avanze-Proyecto-Aquiles/           # Proyecto 2 pisos (Aquiles)
├── latex/                             # Proyecto 3 pisos (Renzo)
└── README.md
```

---

## Normativa

- **CNE-U**: Cálculo de demanda máxima, circuitos mínimos, conductores
- **RNE EM.010**: Requisitos técnicos para instalaciones eléctricas interiores
