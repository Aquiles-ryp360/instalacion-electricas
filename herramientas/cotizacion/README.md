# Cotizacion

La carpeta contiene las herramientas de homologacion y cotizacion de materiales
electricos. `v0_legacy/` queda congelado para consulta historica; el desarrollo
activo vive en `v1/`.

## Estructura v1

```text
v1/
  cli/             entradas de consola para humanos/agentes
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

Modo automatico con Gemini:

```bash
GEMINI_API_KEY=... python3 herramientas/cotizacion/v1/cli/promelsa.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles_promelsa_auto.json \
  --modo auto \
  --modelo-gemini gemini-2.5-flash-lite \
  --key item
```

Modo automatico reproducible sin clave externa:

```bash
python3 herramientas/cotizacion/v1/cli/cotizar.py \
  --input build/<proyecto>/cotizaciones/bom-cotizable.json \
  --output build/<proyecto>/cotizaciones/promelsa.json \
  --modo heuristico \
  --key item \
  --no-actualizar-precio \
  --workers 4
```

`heuristico` solo selecciona si coinciden familia y especificacion nominal, el
precio es visible, no hay falta de stock explicita y el puntaje tecnico minimo
se supera. Las demas partidas quedan `SIN_SELECCION` o `NO_ENCONTRADO`. Toda
seleccion conserva `requiere_revision: true`: sirve como evidencia de mercado,
no como autorizacion de compra ni como sustitucion automatica de una partida
instalada del presupuesto.
`--workers 4` reduce el tiempo de lotes grandes usando sesiones HTTP
independientes; el limite admitido es 6 para no sobrecargar la tienda.

Tambien puede usarse `herramientas/cotizacion/.env`; ver `.env.example`.

## Orquestador v1

`v1/cli/cotizar.py` es la entrada general del flujo. Por ahora delega a
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

## Estados

- `OK`: se obtuvo una seleccion/candidato usable.
- `NO_ENCONTRADO`: la fuente no devolvio candidatos confiables.
- `SIN_SELECCION`: hubo candidatos, pero el agente u operador no eligio uno.
- `SKIPPED`: etapa omitida sin bloquear el flujo.
- `ERROR`: fallo de red, parseo, API o entorno; el lote debe continuar.
- `REQUIERE_REVISION`: salida util, pero necesita validacion humana.
