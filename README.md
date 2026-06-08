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
python3 herramientas/calculos-electricos-vivienda/scripts/generar_bom.py \
  --input data/proyecto.json --output output/
```

---

## Herramientas

### `buscador_precios.py` — Buscador de precios en línea

Genera tabla comparativa con enlaces a Sodimac, Promart, MercadoLibre, Maestro, Google.

```bash
# Tabla con enlaces directos
python3 buscador_precios.py --bom output/bom.json --output comparativa

# Asignar precios manuales (se guardan en cache)
python3 buscador_precios.py --precio "cable TW 2.5mm2=12.50" --precio "ITM 2P 20A=45.00"

# Busqueda automatica via Google API
python3 buscador_precios.py --bom output/bom.json \
  --google-api-key AIza... --google-cx 123...

# Actualizar BOM con los precios encontrados
python3 buscador_precios.py --bom output/bom.json --actualizar output/bom.json
```

### `generar_cotizacion.py` — Cotización formal

Genera cotización formateada (HTML imprimible + LaTeX) con subtotal, mano de obra (40%), IGV (18%) y total.

```bash
python3 generar_cotizacion.py --bom output/bom.json --cliente "Juan Perez" --output cotizacion
```

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
│   ├── buscador_precios.py            # Buscador de precios en linea
│   ├── generar_cotizacion.py          # Generador de cotizaciones
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
