# PeruCompras v1

## Metadata

Proposito: consultar el Buscador Publico de Catalogos Electronicos de
PeruCompras desde un BOM JSON y guardar, para cada material, el primer nombre
oficial visible en las tarjetas HTML de resultados.

Ubicacion:

```text
herramientas/cotizacion/v1/homologacion/perucompras.py
```

Dependencias:

```bash
pip install requests beautifulsoup4 rich
```

El sitio objetivo es una aplicacion ASP.NET Core. El script hace un `GET`
inicial para capturar cookies y el campo hidden `__RequestVerificationToken`;
luego ejecuta busquedas con `POST` form-urlencoded contra la ruta principal del
buscador.

## Guia Para IAs

Comando recomendado:

```bash
python3 herramientas/cotizacion/v1/homologacion/perucompras.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/perucompras_resultados.json \
  --key item \
  --limit 5 \
  --delay 2.5 \
  --max-pages 1
```

Flags:

- `--input`: ruta a un JSON de entrada.
- `--output`: ruta de salida. Debe terminar en `.json`.
- `--key`: llave que contiene el texto a buscar dentro de cada item. Por
  defecto usa `item`.
- `--limit`: procesa solo los primeros N items.
- `--delay`: segundos de espera entre busquedas.
- `--max-pages`: paginas de resultados a intentar sin romper el formulario.
- `--save-html [carpeta]`: guarda HTML para depuracion.
- `--verbose`: muestra variantes y detalles de busqueda.

Formato aceptado de entrada:

```json
{
  "materiales": [
    {
      "item": "Cable TW THW 16 mm2",
      "cantidad": 40,
      "unidad": "m"
    }
  ]
}
```

Tambien acepta una lista directa:

```json
[
  {"item": "Interruptor termomagnetico 2 polos 10A"},
  {"item": "Luminaria LED plafon 18 W"}
]
```

Formato de salida:

```json
{
  "metadata": {
    "fuente": "https://buscadorcatalogos.perucompras.gob.pe/",
    "key": "item",
    "delay_seconds": 2.0
  },
  "resumen": {
    "ok": 1,
    "no_encontrado": 0,
    "error": 0
  },
  "resultados": [
    {
      "index": 1,
      "query": "Luminaria LED plafon 18 W",
      "status": "OK",
      "confianza": "MEDIA",
      "score": 68.5,
      "requiere_revision": false,
      "nombre_oficial": "...",
      "bom_item_original": {}
    }
  ]
}
```

Manejo de `NO_ENCONTRADO`:

- Si `status` es `NO_ENCONTRADO`, la IA no debe inventar codigo ni producto.
- Debe conservar el item para revision humana o para una segunda pasada con una
  consulta mas generica.
- El campo `mensaje` guarda el texto detectado en el HTML cuando el sitio indica
  que no hay fichas-producto, o avisa que hubo tarjetas pero ninguna alcanzo el
  score minimo de coincidencia tecnica.

Exit codes:

- `0`: el lote termino y el JSON fue escrito.
- `1`: error critico, por ejemplo JSON invalido, falla de conexion inicial,
  falta de token anti-forgery o salida no `.json`.

Confianza:

- `ALTA`: match fuerte y sin ambiguedad frente al segundo candidato.
- `MEDIA`: match util, pero debe validarse si el item es sensible.
- `BAJA`: score bajo o ambiguo; tratar `requiere_revision=true` como revision
  humana obligatoria.

Regla de seguridad:

- El scraper no intenta "llenar todo". Si PeruCompras devuelve una ficha de otra
  familia, por ejemplo tuberia sanitaria para un tubo SAP electrico, una tijera
  para una curva PVC o un producto vendido por caja para una caja electrica, el
  resultado debe quedar como `NO_ENCONTRADO`.

## Guia Para Humanos

Instalacion rapida:

```bash
python3 -m pip install requests beautifulsoup4 rich
```

Ejecucion:

```bash
python3 herramientas/cotizacion/v1/homologacion/perucompras.py \
  --input herramientas/cotizacion/fixtures/perucompras_bom_test.json \
  --output herramientas/cotizacion/salidas/perucompras_test.json \
  --limit 5 \
  --delay 2.5
```

Lectura de logs:

- `OK`: encontro tarjetas y eligio el mejor candidato por scoring.
- `NO_ENCONTRADO`: PeruCompras no devolvio fichas-producto para esa busqueda.
  Tambien puede aparecer cuando la web devolvio tarjetas irrelevantes con score
  bajo.
- `Advertencia`: fallo un item individual; el script continua con el siguiente.
- `Error critico`: el proceso no puede continuar y termina con exit code `1`.

Notas operativas:

- El script espera 2 segundos entre busquedas para no golpear el servicio.
- PeruCompras se usa para homologar fichas-producto, no como precio final.
- El buscador puede devolver resultados no electricos cuando la consulta es muy
  generica; por eso el scraper calcula score, confianza y `requiere_revision`.
