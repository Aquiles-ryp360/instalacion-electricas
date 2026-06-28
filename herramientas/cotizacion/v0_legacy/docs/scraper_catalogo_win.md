# Scraper catalogo.win

## Metadata

**Proposito:** enriquecer un JSON de materiales con el primer codigo y nombre encontrado en el catalogo web de `https://catalogo.win/`.

**Script principal:** `herramientas/cotizacion/scrapers/catalogo_win.py`

**Wrapper compatible:** `herramientas/cotizacion/scraper_catalogo.py`

**Dependencias directas:**

- `requests`: sesion HTTP, cookies y consultas a la API.
- `rich`: logs visuales, progreso y resumen en consola.
- `openpyxl`: exportacion opcional a Excel `.xlsx`.

El sitio requiere una peticion inicial `GET https://catalogo.win/` para obtener cookie de sesion y token CSRF. El scraper extrae el token desde `<meta name="csrf-token">` y consulta el endpoint JSON de busqueda usando `X-CSRF-Token`.

## Guia para IAs

### Contrato machine-to-machine

Comando base:

```bash
python3 herramientas/cotizacion/scrapers/catalogo_win.py \
  --input RUTA_ENTRADA.json \
  --output RUTA_SALIDA.csv
```

Con llave explicita:

```bash
python3 herramientas/cotizacion/scrapers/catalogo_win.py \
  --input proyectos/renzo/datos/bom-materiales.json \
  --output build/renzo/catalogo_win.csv \
  --key item
```

### Flags

- `--input`: ruta obligatoria al JSON de entrada.
- `--output`: ruta obligatoria de salida. `.csv` escribe CSV, `.xlsx`/`.xlsm` escribe Excel y cualquier otra extension escribe JSON.
- `--key`: llave opcional que contiene el texto de busqueda del material.

Si `--key` no se envia, el scraper intenta estas llaves en orden:

1. `item`
2. `nombre`
3. `descripcion`

### Formato de entrada esperado

Lista directa:

```json
[
  {
    "item": "Cable THW 2.5 mm2 cobre",
    "unidad": "m",
    "cantidad": 120
  },
  {
    "item": "Interruptor termomagnetico 2P 20A",
    "unidad": "und",
    "cantidad": 1
  }
]
```

Objeto con arreglo interno:

```json
{
  "proyecto": "Instalaciones electricas interiores",
  "materiales": [
    {
      "codigo": "BOM-001",
      "item": "Tubo PVC SAP 20 mm",
      "unidad": "m",
      "cantidad": 80
    }
  ]
}
```

Tambien acepta contenedores llamados `items`, `data` o `rows`.

### Salida CSV

Columnas:

- `index`: posicion del item en el archivo de entrada.
- `input_key`: llave usada para construir la consulta.
- `query`: texto original tomado del BOM.
- `query_usada`: consulta que finalmente produjo el primer resultado.
- `query_intentos`: consultas intentadas, separadas por ` | `.
- `codigo`: codigo encontrado en catalogo.win, normalmente `codigo_display`.
- `nombre`: nombre encontrado, normalmente `nombre_item`.
- `catalogo_id`, `codigo_osce`, `codigo_onu`, `codigo_searchable`: identificadores disponibles del primer resultado.
- `unidad_medida`, `tipo_bien`, `precio_ref`: metadatos comerciales/catalogo del primer resultado.
- `nombre_grupo`, `nombre_clase`, `nombre_familia`, `fecha_alta`: clasificacion SIGA/MEF cuando la API la devuelve.
- `total_hits`, `processing_time_ms`: diagnostico de la busqueda.
- `status`: estado de la fila.
- `error`: detalle si hubo error recuperable.

Estados posibles:

- `ok`: se encontro codigo o nombre.
- `sin_resultados`: la API respondio, pero sin resultados.
- `sin_codigo_nombre`: hubo resultado, pero no contenia campos utiles.
- `sin_nombre`: el item no tenia llave de busqueda usable.
- `error_item`: fallo solo esa consulta; el proceso continuo.

### Exit Codes

- `0`: ejecucion completada y archivo de salida escrito.
- `1`: error critico. Ejemplos: no hay conexion, JSON invalido, no se pudo capturar cookie/token, no se pudo escribir la salida o interrupcion manual.

Los errores por item no deben detener un agente autonomo. Deben revisarse en la columna `status` y `error`.

## Guia para Humanos

### Instalacion

Desde la raiz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r herramientas/cotizacion/requirements.txt
```

Si solo quieres instalar las dependencias minimas:

```bash
python3 -m pip install requests rich openpyxl
```

### Uso rapido

```bash
python3 herramientas/cotizacion/scrapers/catalogo_win.py \
  --input proyectos/aquiles/presupuesto/bom_final_aquiles.json \
  --output build/aquiles/catalogo_win.csv \
  --key item
```

### Como leer los logs

El scraper muestra:

- inicio de sesion correcto cuando captura cookie y token CSRF;
- una barra de progreso mientras consulta los materiales;
- advertencias amarillas cuando un item falla y se continua;
- una tabla final con conteo por estado.

Un resultado `ok` no significa validacion tecnica completa. Significa que se tomo el primer resultado devuelto por catalogo.win. Para compras o entregables formales, revisa manualmente si el codigo corresponde al material real.
