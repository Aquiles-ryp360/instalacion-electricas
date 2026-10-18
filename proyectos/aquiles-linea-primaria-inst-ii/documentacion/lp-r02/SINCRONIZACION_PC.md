# Sincronización con GitHub y PC

Solicitud del usuario: subir todo el trabajo LP-R02 y conservar las fuentes recuperadas, como los DVD. Preparado el 18 de octubre de 2026 desde `/sdcard/Documents/instalacion-electricas`, equivalente a `/mnt/sdcard/Documents/instalacion-electricas` en Debian.

Se integró `origin/main` hasta `85fcb7ec05e24612ed8d47a9ab4a62f1b8697407` por avance directo, incorporando las recuperaciones sin sobrescribirlas. El trabajo nuevo se mantiene en la rama `revision/lp-r02-auditoria-2026-10-18`. No se modifica el otro clon de `/root/instalacion-electricas`.

Se versionaron código, entradas, documentación, recursos oficiales descargados, pruebas y la copia completa de revisión en `revisiones/lp-r02/`, más su ZIP. El manifiesto y la navegación apuntan a esa copia para que los archivos abran en un clon nuevo sin reconstrucción. `build/` continúa ignorado; sus resultados se conservaron por separado como copia de revisión, sin cambiar el estado técnico.

El paquete contiene 152 archivos, incluido `manifest.json`, con 151 entradas verificables. El ZIP original y las copias de Documents se conservan sin modificación. La revisión informática previa aprobó 15 pruebas y 68 controles. La sincronización vuelve a comprobar integridad, navegación y preservación de las fuentes recuperadas.

Se instaló GitHub CLI (`gh`) para autenticar por navegador. La conexión GitHub de la aplicación rechazó inicialmente la escritura con `403 Resource not accessible by integration`. El usuario autenticó después GitHub CLI con `Aquiles-ryp360`; se comprobó permiso de escritura y se configuró el acceso de Git por HTTPS. Ningún token se incorpora al repositorio.

La [guía de PC](../../revisiones/README.md) contiene las rutas y comandos de descarga y continuación. El contenido técnico se publicó en el commit [`67a0bada7bc7831e8aef54b762512e3126eb0ac1`](https://github.com/gaelrenzo/instalacion-electricas/commit/67a0bada7bc7831e8aef54b762512e3126eb0ac1), tanto en `main` como en `revision/lp-r02-auditoria-2026-10-18`, mediante envío atómico sin forzar. Se consultaron ambas referencias remotas y el objeto de commit de GitHub; el árbol coincide exactamente con el local. El [registro de publicación](publicacion-github.json) conserva esa comprobación inicial. Los commits posteriores de documentación no modifican el paquete técnico.


## Comprobaciones de la preparación

- 15 pruebas mecánicas y eléctricas aprobadas.
- 68 controles del paquete aprobados sin reescribir sus archivos.
- SHA-256 y tamaño de las 151 entradas del manifiesto correctos; ZIP con CRC y SHA-256 correctos.
- 81 fuentes recuperadas idénticas al blob Git y tamaño del commit remoto de recuperación.
- Navegación principal: 11 proyectos y 163 enlaces locales sin errores; 15 enlaces adicionales de las guías nuevas comprobados.
- Comprobación de espacios en fuentes editables con CRLF permitido en CSV; el paquete congelado se conserva byte por byte, incluido su código de respaldo.


## Archivos y acceso desde PC

En un clon nuevo de `main` los PDF, hojas de cálculo, DXF y recursos de `revisiones/lp-r02/` están listos para abrir, junto con su ZIP de 80 902 029 bytes. GitHub aceptó el ZIP y emitió únicamente una recomendación por superar 50 MB; el archivo queda almacenado como blob Git normal. No se requiere Git LFS para descargar esta revisión.

En Documentos del teléfono también se conserva `Limbani_Huancasayani_LP_R02_cambios.bundle`, respaldo incremental verificado del commit técnico. Ese respaldo requiere la base remota `85fcb7e` y conserva el estado documental de la preparación inicial. La documentación vigente es la del repositorio.
