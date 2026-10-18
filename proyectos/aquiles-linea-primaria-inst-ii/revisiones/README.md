# Continuar LP-R02 desde una PC

Esta carpeta contiene la copia de revisión académica preparada para compartir por solicitud del usuario del 18 de octubre de 2026. Conserva los resultados, observaciones y bytes del paquete elaborado en el teléfono. Compartirlo no cambia su estado: **sin aprobación para construcción**.

## Obtener el proyecto

Para una carpeta nueva, con Git instalado:

```powershell
git clone https://github.com/gaelrenzo/instalacion-electricas.git
cd instalacion-electricas
```

Si ya tienes un clon, revisa tus cambios antes de actualizar:

```powershell
git status
git pull --ff-only origin main
```

Si Git informa de cambios locales o de historias divergentes, conserva tu trabajo antes de integrarlo. No uses `reset --hard` para resolverlo.

Abre [lp-r02/LEER_PRIMERO.md](lp-r02/LEER_PRIMERO.md) para navegar por las ocho carpetas. PDF, DOCX, XLSX, DXF, GeoJSON y KMZ están incluidos; no requieren ejecutar Python para consultarlos. Los planos R02 se entregan en DXF y PDF. Los DWG R01 se conservan como antecedentes.

También puedes descargar [Limbani_Huancasayani_LP_R02.zip](Limbani_Huancasayani_LP_R02.zip) mediante el botón de descarga del archivo en GitHub. El ZIP pesa 80 902 029 bytes y tiene SHA-256:

```text
242543fa470a108c4bf11170994ecd6d1bee2611f39075c63fe48a9b3c641760
```

En PowerShell se comprueba con `Get-FileHash .\Limbani_Huancasayani_LP_R02.zip -Algorithm SHA256`. Extraerlo conserva la estructura `lp-r02/` y su manifiesto de integridad.

## Editar y reproducir

Las entradas vigentes están en `../datos/lp-r02/`; los generadores están en `../scripts/lp_r02/` y el motor común en `../../../herramientas/lineas_primarias/revision.py`. El [manifiesto](../proyecto.yaml) identifica la revisión activa. La [guía de reproducción](../README-LINEA-PRIMARIA.md) contiene los comandos, dependencias y limitaciones.

La reconstrucción completa se verificó en Debian del teléfono; no se ha ejecutado en Windows. En Windows se puede usar Debian mediante WSL para conservar ese entorno. Para leer o editar los archivos exportados puedes usar aplicaciones compatibles de tu PC.

Las ediciones manuales de DOCX, XLSX o DXF no actualizan el motor automáticamente. Registra tus cambios y, si afectan el diseño, actualiza las entradas y genera una revisión nueva en `build/`. Mantén esta copia y su `manifest.json` como registro de lo compartido. La copia incluye además un fragmento de código autónomo y restaurador en `lp-r02/08-recursos/codigo/`.

## Fuentes recuperadas y continuidad

Los originales recuperados del DVD UNAP, Aricato–Phara y los formatos de clase permanecen en [referencias/guias-originales](../../../referencias/guias-originales/README.md). Su relación con el proyecto está descrita en [FUENTES_RECUPERADAS_GITHUB.md](../documentacion/lp-r02/FUENTES_RECUPERADAS_GITHUB.md). Se incorporaron después de generar los resultados R02; no se presentan como cálculos ya aplicados a esta línea.

El paquete congelado mantiene el contexto de su elaboración inicial, incluidas menciones históricas a `build/` y a la sesión sin publicación. Para continuar el trabajo usa la documentación actual del repositorio: [CONTINUIDAD_IA.md](../documentacion/lp-r02/CONTINUIDAD_IA.md), [PLANEACION.md](../documentacion/lp-r02/PLANEACION.md) y [SINCRONIZACION_PC.md](../documentacion/lp-r02/SINCRONIZACION_PC.md).
