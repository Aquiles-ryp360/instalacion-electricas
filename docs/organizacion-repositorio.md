# Organización del repositorio · 14 de octubre de 2026

La reorganización separa los expedientes de Aquiles por curso, corrige la navegación general e incorpora los cambios que ya existían en `origin/main`. No modifica el dimensionamiento, la geometría ni los resultados de los diseños publicados.

## Rutas de los proyectos

| Ubicación anterior | Ubicación actual | Curso |
| --- | --- | --- |
| `proyectos/aquiles-minicentral-limbani/` | [proyectos/aquiles-central-michell-banki/](../proyectos/aquiles-central-michell-banki/README.md) | Centrales Hidroeléctricas |
| `proyectos/aquiles-limbani-redes/` | [proyectos/aquiles-linea-primaria-inst-ii/](../proyectos/aquiles-linea-primaria-inst-ii/README.md) | Instalaciones Eléctricas II |

Las carpetas conservan la misma profundidad para mantener las rutas relativas de las herramientas. El nombre Michell-Banki identifica el tema y la tecnología estudiada; los valores de potencia y las condiciones del antecedente se consultan en la memoria, no se deducen del nombre de carpeta.

Los enlaces a una ruta antigua sobre la rama `main` deben actualizarse. Los enlaces fijados al commit anterior [e094bc2](https://github.com/gaelrenzo/instalacion-electricas/tree/e094bc2b114ec542455f6a419dc2647a399dada4) continúan disponibles como referencia histórica.

## Entradas, entregas e historia

- **Minicentral R03:** entradas `datos/*-r03.json`, series `datos/hidrologia/`, fuentes editables `expediente/r03/` y PDFs compartidos `entregables/r03/`. Los documentos y programas anteriores R02 pasan a `archivo/r02/`, conservando sus bytes. El catálogo semilla normativo permanece activo como `datos/base-normativa.json`.
- **Línea primaria LP-R01:** parámetros `datos/lp-r01/`, memoria `expediente/lp-r01/`, programas `scripts/lp_r01/` y paquete `entregables/linea-primaria-r01/`. Los antiguos documentos, planos y generadores de distribución urbana se conservan en `archivo/red-urbana/`; no alimentan el diseño activo de la línea.
- **Vivienda de Diego:** documentos editables en `expediente/`, datos en `datos/`, CAD/QElectroTech en `diseno-electrico/planos/`, documentos compartidos en `entregables/` y originales en `fuentes/`. Se corrigen rutas de su generador sin ejecutar ni modificar sus cálculos.
- **Demás proyectos:** conservan sus carpetas, alcance y datos. El catálogo diferencia autores y variantes; no declara terminada una ingeniería por el nombre `v2` o `final`.

Los PDF de la minicentral se copian desde las salidas revisadas a su carpeta de entrega, con igualdad SHA-256. Los PDF, DWG, DXF, QGIS, KMZ y ZIP existentes de la línea se trasladan intactos. Los paquetes ZIP y sus manifiestos internos representan la revisión publicada; no se reescriben solo para cambiar una ruta externa del repositorio.

Los metadatos de comprobaciones antiguas pueden registrar rutas absolutas del equipo en la fecha de generación. Son evidencia histórica; no se confunden con entradas de ejecución actuales.

## Recursos compartidos y herramientas

Los escudos de UNA Puno y las imágenes regionales de ubicación se copian, con procedencia, a [recursos/](../recursos/README.md). Sus originales se conservan. Los constructores de ambos cursos utilizan estos recursos sin depender de la carpeta de otro proyecto.

La tesela DEM compartida se consulta en `referencias/local/topografia-limbani/`, ignorada por Git. Los entregables geográficos publicados incluyen los datos necesarios para visualizarse; reconstruir la investigación requiere las fuentes locales descritas en cada proyecto.

Se actualizan los índices de herramientas y documentos. El flujo de integración continua elimina la referencia inexistente a `proyectos/nave-industrial/tests` y coincide con las cuatro suites ya declaradas en `make test`. Los diagnósticos locales de CAD se guardan bajo `build/diagnosticos/`.

## Comprobación y mantenimiento

Ejecutar desde la raíz:

```powershell
python herramientas/verificar_organizacion.py
```

El control verifica el catálogo de proyectos, sus identificadores, los enlaces de navegación, las rutas activas declaradas para los dos cursos y la sintaxis de los programas reubicados. No sustituye una verificación eléctrica ni valida los enlaces web externos.

Se registra además una comparación SHA-256 de los archivos anteriores a la migración. Las excepciones admitidas son los textos de navegación, metadatos y rutas de programas; las magnitudes numéricas del diseño se conservan. La evidencia detallada de trabajo queda en `build/organizacion-repositorio/`, local e ignorada por Git.

Al añadir un proyecto: crear su `proyecto.yaml` y README, incorporarlo al [catálogo](../proyectos/README.md), conservar las fuentes originales y declarar expresamente el estado de sus entregas. Los antecedentes en `archivo/` no son entradas activas.
