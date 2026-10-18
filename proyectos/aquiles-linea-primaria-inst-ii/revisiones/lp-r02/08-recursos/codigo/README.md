# Reconstrucción desde este paquete

`fragmento-repositorio` conserva el código e insumos mínimos usados en la revisión; no contiene credenciales ni historialGit. Permite reconstruir incluso si la ramaLP-R02 aún no se ha publicado.

1. Ejecutar `python3 restaurar.py /ruta/a/carpeta-nueva-vacia`.
2. Entrar en esa carpeta e instalar `proyectos/aquiles-linea-primaria-inst-ii/requirements-lp-r02.txt`.
3. Ejecutar `python3 -m unittest discover -s herramientas/lineas_primarias/tests -v`.
4. Ejecutar `python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/construir.py`.

Se reconstruye la revisión académica. Los datos pendientes de campo, placas y fabricantes siguen pendientes; el contenido no convierte la propuesta en diseño de obra.
