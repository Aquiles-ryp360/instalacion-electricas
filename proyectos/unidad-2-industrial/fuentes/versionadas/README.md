# Recursos versionados para reproducción

Esta carpeta contiene recursos externos pequeños que el pipeline necesita para
compilar sin depender de la red. Sus huellas se verifican antes de copiarlos a
`build/`.

`identidad/unap_logo.svg` fue publicado en el dominio oficial de la UNAP y
`identidad/unap_logo.pdf` es su conversión vectorial verificada. El SVG conserva
como procedencia `https://derecho.unap.edu.pe/storage/2019/05/unap_logo.svg` y
SHA-256 `9f15da7b391761fe2fc9eb64ff0f4039e2d96e95b360056b8cb7b1675152bebe`.

No editar estos archivos directamente. Para comprobar si la fuente oficial
sigue entregando el mismo SVG, ejecutar:

```bash
.venv/bin/python proyectos/unidad-2-industrial/scripts/preparar_recursos_expediente.py \
  --actualizar-desde-web
```
