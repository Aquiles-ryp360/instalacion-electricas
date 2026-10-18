# Verificación de la recuperación

Base: main en 3619a7f06e64488628182d915e9d85e87d1515a5.

## Comprobaciones realizadas

- Los 69 originales recuperados coinciden, byte por byte, con su SHA Git y SHA-256 de origen.
- Ningún destino de recuperación sobrescribe un archivo del estado de partida.
- No se duplican los blobs de originales ya presentes en la rama principal.
- Se abrió el contenido de seis comprimidos históricos y tres actuales; se verificaron sus SHA y la lectura de miembros.
- Se comprobaron encabezados de DWG y documentos Office heredados. La hoja XLS de cimentación se abrió con xlrd.
- Se inspeccionaron en lectura los seis Excel modernos históricos: fórmulas, hojas, enlaces y valores de error almacenados.
- Se abrieron 57 PDF candidatos sin errores de lectura. La muestra visual incluyó memoria, lámina de armado y cálculo termomagnético.
- Se revisaron visualmente las fotografías de clase y se descartaron dos tomas parcialmente redundantes.
- Los enlaces locales de los índices se contrastaron con los archivos nuevos y el árbol base completo.
- El único cambio en un archivo anterior es una sección añadida al final de referencias/README.md.

## Alcance

La comprobación de integridad confirma la recuperación de las fuentes.
No se alteró ni se certificó su contenido de ingeniería. Los tres Excel del
proyecto guía conservan enlaces externos y errores previos, descritos en el índice.
No se ejecutaron AutoCAD, DIALux, Excel ni Microsoft Project. Las referencias externas
de DWG y los vínculos de Office pueden requerir archivos de su entorno original.

La recuperación no cambia fuentes activas, parámetros, programas ni entregables
de los proyectos actuales. Por ese alcance documental no se ejecutaron sus
pipelines ni se regeneraron resultados.

La publicación se realiza en la rama aquiles/recuperacion-bases-plantillas del
fork Aquiles-ryp360/instalacion-electricas. Se conserva main sin cambios.
