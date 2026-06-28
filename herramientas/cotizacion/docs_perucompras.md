# scraper_perucompras.py

## Metadata

Proposito: consultar el Buscador Publico de Catalogos Electronicos de
PeruCompras desde un BOM JSON y guardar, para cada material, el primer nombre
oficial visible en las tarjetas HTML de resultados.

Ubicacion:

```text
herramientas/cotizacion/scraper_perucompras.py
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
python3 herramientas/cotizacion/scraper_perucompras.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/perucompras_resultados.json \
  --key item
```

Flags:

- `--input`: ruta a un JSON de entrada.
- `--output`: ruta de salida. Debe terminar en `.json`.
- `--key`: llave que contiene el texto a buscar dentro de cada item. Por
  defecto usa `item`.

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
      "nombre_oficial": "..."
    }
  ]
}
```

Manejo de `NO_ENCONTRADO`:

- Si `status` es `NO_ENCONTRADO`, la IA no debe inventar codigo ni producto.
- Debe conservar el item para revision humana o para una segunda pasada con una
  consulta mas generica.
- El campo `mensaje` guarda el texto detectado en el HTML cuando el sitio indica
  que no hay fichas-producto.

Exit codes:

- `0`: el lote termino y el JSON fue escrito.
- `1`: error critico, por ejemplo JSON invalido, falla de conexion inicial,
  falta de token anti-forgery o salida no `.json`.

## Guia Para Humanos

Instalacion rapida:

```bash
python3 -m pip install requests beautifulsoup4 rich
```

Ejecucion:

```bash
python3 herramientas/cotizacion/scraper_perucompras.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/perucompras_resultados.json
```

Lectura de logs:

- `OK`: encontro al menos una tarjeta y tomo el primer resultado visible.
- `NO_ENCONTRADO`: PeruCompras no devolvio fichas-producto para esa busqueda.
- `Advertencia`: fallo un item individual; el script continua con el siguiente.
- `Error critico`: el proceso no puede continuar y termina con exit code `1`.

Notas operativas:

- El script espera 2 segundos entre busquedas para no golpear el servicio.
- El buscador puede devolver resultados no electricos cuando la consulta es muy
  generica. En v2 conviene agregar ranking tecnico y filtros por acuerdo marco.
