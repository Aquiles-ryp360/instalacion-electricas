# Cotizacion

La carpeta contiene las herramientas de homologacion y cotizacion de materiales
electricos. `v0_legacy/` queda congelado para consulta historica; el desarrollo
activo vive en `v1/`.

## Estructura v1

```text
v1/
  cli/             comandos de entrada
  core/            BOM, normalizacion, matching y modelos comunes
  homologacion/    fuentes tecnicas previas a la compra, como PeruCompras
  tiendas/         scrapers comerciales por tienda/proveedor
  seleccion/       seleccion automatica o asistida entre candidatos
  exportadores/    salidas JSON, Markdown, XLSX, etc.
  formatos/        esquemas de datos
  fixtures/        datos minimos de prueba
  tests/           pruebas de v1
  salidas/         resultados regenerables locales
```

## Flujo previsto

```text
BOM JSON
  -> homologacion/perucompras.py   # diagnostico opcional; puede quedar SKIPPED
  -> tiendas/promelsa.py           # primera tienda comercial activa
  -> tiendas/<siguiente_tienda>.py
  -> seleccion/
  -> exportadores/
```

PeruCompras se mantiene como fuente de homologacion tecnica, pero no debe
bloquear la cotizacion comercial cuando su catalogo no cubre cables u otros
materiales. En esos casos el resultado debe quedar como `SKIPPED` o
`NO_ENCONTRADO` y continuar hacia tiendas.

## Promelsa

Comando principal de tienda:

```bash
python3 herramientas/cotizacion/v1/cli/promelsa.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles_promelsa.json \
  --modo cli \
  --key item
```

Wrapper compatible:

```bash
python3 herramientas/cotizacion/agente_compras.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles_promelsa.json \
  --modo cli \
  --key item
```

Modo automatico con Gemini:

```bash
GEMINI_API_KEY=... python3 herramientas/cotizacion/v1/cli/promelsa.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles_promelsa_auto.json \
  --modo auto \
  --modelo-gemini gemini-2.5-flash-lite \
  --key item
```

Tambien puede usarse `herramientas/cotizacion/.env`; ver `.env.example`.

## Orquestador v1

`v1/cli/cotizar.py` existe como punto de entrada general. Por ahora delega a
Promelsa; cuando agreguemos mas tiendas, este archivo coordinara PeruCompras,
tiendas, seleccion y exportadores.

```bash
python3 herramientas/cotizacion/v1/cli/cotizar.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles_cotizacion_v1.json \
  --modo cli \
  --key item
```

## PeruCompras

Comando v1:

```bash
python3 herramientas/cotizacion/v1/homologacion/perucompras.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles_perucompras.json \
  --key item
```

Wrappers compatibles:

```bash
python3 herramientas/cotizacion/scraper_perucompras.py --input ... --output ...
python3 herramientas/cotizacion/fuentes/perucompras_fichas.py --input ... --output ...
```

## Estados

- `OK`: se obtuvo una seleccion/candidato usable.
- `NO_ENCONTRADO`: la fuente no devolvio candidatos confiables.
- `SIN_SELECCION`: hubo candidatos, pero el agente u operador no eligio uno.
- `SKIPPED`: etapa omitida sin bloquear el flujo.
- `ERROR`: fallo de red, parseo, API o entorno; el lote debe continuar.
- `REQUIERE_REVISION`: salida util, pero necesita validacion humana.
