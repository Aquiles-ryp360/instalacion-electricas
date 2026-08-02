# Automatizacion de instalaciones electricas

Repositorio para transformar informacion de viviendas y una nave industrial, idealmente desde croquis o modelos estructurados, en datos canonicos, calculos electricos, planos CAD, metrados, cotizaciones y expedientes tecnicos revisables.

El objetivo es automatizar el trabajo repetitivo con agentes de IA sin presentar resultados preliminares como diseno definitivo. Toda salida tecnica requiere revision humana y contraste con el Codigo Nacional de Electricidad, el RNE y las condiciones reales de obra.

## Estructura

```text
.
├── AGENTS.md                 reglas de trabajo para agentes
├── docs/                     arquitectura, flujo y politica de datos
├── herramientas/             motores reutilizables
├── proyectos/
│   ├── aquiles/              vivienda de dos pisos
│   ├── nave-industrial/      nave industrial trifasica de 20 x 40 m
│   ├── renzo/                vivienda de tres pisos
│   └── unidad-2-industrial/  nuevo proyecto no residencial, tipologia por definir
├── referencias/              normativa versionada y material local ignorado
└── build/                    resultados regenerables, ignorados por Git
```

Los proyectos conservan sus fuentes, datos canonicos, documentacion y entregables. Las herramientas comunes no deben contener nombres, rutas ni datos exclusivos de un alumno.

## Inicio rapido

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
make test
```

Pipeline general de Aquiles:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto aquiles
```

Pipeline nativo y expediente de Renzo:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto renzo
# equivalente: cd proyectos/renzo && python3 scripts/construir_expediente.py
```

Pipeline industrial:

```bash
make nave-industrial
```

Todas las ejecuciones escriben resultados regenerables en `build/<proyecto>/`.
En Renzo, el PDF temporal queda en `build/renzo/expediente/main.pdf`; la
version revisada se publica en `proyectos/renzo/entregables/expediente.pdf`.

## Flujo esperado

1. Conservar el croquis original sin modificarlo.
2. Extraer geometria, ambientes, cotas e incertidumbres a JSON.
3. Validar la planta arquitectonica antes del diseno electrico.
4. Definir cargas, circuitos, protecciones, conductores y canalizaciones.
5. Ejecutar calculos, CAD, BOM y cotizacion.
6. Registrar observaciones y revision humana.
7. Publicar unicamente resultados aprobados en `entregables/`.

Consulta [docs/arquitectura.md](docs/arquitectura.md), [docs/flujo-agentes.md](docs/flujo-agentes.md) y [AGENTS.md](AGENTS.md) antes de modificar datos canonicos.

El proyecto de la segunda unidad se inicia en
[`proyectos/unidad-2-industrial/`](proyectos/unidad-2-industrial/README.md).
Mientras su tipologia siga pendiente, solo se permite investigar, registrar
fuentes y comparar alternativas; no se deben inventar cargas ni generar planos.

## Datos pesados y respaldos

`referencias/local/` y `proyectos/*/fuentes/local/` contienen material pesado o restringido que no se sube a Git. La reorganizacion anterior permanece respaldada en `respaldo/reorganizacion-base-antigua-2026-06-13`.

Las configuraciones locales de asistentes, incluida `.gemini/`, estan ignoradas porque no forman parte del producto ni del pipeline reproducible.
