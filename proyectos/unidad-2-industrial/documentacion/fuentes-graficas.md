# Fuentes graficas del expediente

## Escudo UNAP

- Fuente: [pagina de logos de la Facultad de Ciencias Juridicas y Politicas de
  la UNAP](https://derecho.unap.edu.pe/logo/).
- Recurso SVG: `https://derecho.unap.edu.pe/storage/2019/05/unap_logo.svg`.
- SHA-256 verificado: `9f15da7b391761fe2fc9eb64ff0f4039e2d96e95b360056b8cb7b1675152bebe`.
- Uso: portada y encabezado del expediente con el mismo esquema grafico del
  proyecto Aquiles de la primera unidad.
- Motivo del cambio: el PNG heredado mide solo 113 x 124 px y se pixelaba al
  ampliar; el SVG conserva trazos vectoriales.

El script `scripts/preparar_recursos_expediente.py` descarga, verifica y
convierte el recurso a PDF vectorial dentro de `build/`. Si la huella cambia,
la generacion se detiene para que el recurso sea revisado antes de usarlo.
