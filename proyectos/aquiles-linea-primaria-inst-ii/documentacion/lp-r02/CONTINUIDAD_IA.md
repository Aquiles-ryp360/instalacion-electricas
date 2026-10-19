# Continuidad de la revisión LP-R02

Leer primero `proyecto.yaml`, `AGENTS.md`, `datos/lp-r02/parametros.json` y `07-evaluacion-y-pendientes` del paquete. El origen adoptado es la minicentral aislada según LP-R01; la consulta al usuario sobre la fuente no recibió respuesta explícita. No cambiar a red Electro Puno sin nueva evidencia.

## Estado y alcance

Revisión académica y diagnóstico del corredor de una terna sin ramales. No es ingeniería aprobada de obra. Mantener separados los proyectos de Centrales Hidroeléctricas y de Instalaciones Eléctricas II. `docs/curso/segunda-unidad.md` trata otro proyecto, un grifo; no aporta rúbrica de esta línea. El docente de este expediente sigue sin confirmar.

Los 111 apoyos de gabinete conservan las coordenadas/cotas y alturas heredadas para comparar; 46 tienen carga ascendente en algún estado. Se proponen 16 cambios de suspensión a retención y 32 retenidas adicionales ideales. No certificar capacidad axial, cimentaciones, grapas, pretensión o predios por superar comprobaciones de flexión.

## Reproducción

Desde la raíz del repositorio:

```bash
python3 -m pip install -r proyectos/aquiles-linea-primaria-inst-ii/requirements-lp-r02.txt
python3 -m unittest herramientas.lineas_primarias.tests.test_revision -v
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/construir.py --salida build/aquiles-linea-primaria-inst-ii/lp-r02-reproduccion
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/verificar.py --salida build/aquiles-linea-primaria-inst-ii/lp-r02-reproduccion
```

El constructor rechaza sobrescritura de una salida existente. Crear otra carpeta para ensayos. Las salidas van a `build/`; no publicar automáticamente como `entregables/`. PDF de planos se renderiza del DXF guardado; el modelo CAD sí contiene el eje y111 bloques con atributos. No crear un DWG ficticio: esta revisión proporciona DXF yPDF; la conversión nativaDWG requiere herramienta y reapertura verificable.

## Entradas y procedencia

- `datos/lp-r02/parametros.json`: hipótesis de equipo, clima y decisiones pendientes.
- `datos/lp-r02/geometria-base.json`: extracción explícita de geometría/perfil de los resultados canónicosR01, conSHA256; no usa `archivo/`.
- `datos/lp-r02/registro-parametros.csv`: unidad, fuente, estado y confianza de parámetros críticos.
- `datos/lp-r02/fuentes.json` y `recursos/linea-primaria-limbani/2026-10-18/`: documentos oficiales descargados.
- `documentacion/lp-r02/inventarios/`: inventario del repositorio, contenidoCRC de3ZIP y revisión de6DXF de Capachica.

La revisión usa únicamente el perfil muestreado heredado para comparar separaciones nuevas; no remuestrea la envolvente lateral del DEM ni inventa cota de campo. Los anclajes de retenidas son posiciones geométricas ideales y deben confrontarse con casas/cauces/predios antes de diseñar. `build/` contiene información regenerable, nunca evidencia de campo.

## Decisiones pendientes y secuencia

1. Obtener placa generador/T1/T2 y confirmar si200 kW/250 kVA es aplicable. Un documento local de otra asignatura usa150 kW: no conciliar por suposiciones.
2. Confirmar potencia disponible en estiaje, reserva para Limbani y padrón/curva horaria de Huancasayani.
3. Decidir10/22.9 kV mediante compatibilidad y costo total.20/22 kV son sensibilidades; no pedir transformador22 kV cuando se haya elegido22.9 kV.
4. Levantar eje y fases, cruces, obstáculos, predios y geotecnia/Wenner. Recalcular al cambiar coordenadas.
5. Elegir aisladores rígidos o cadenas; cambiar el modelo mecánico si hay movimiento de cadenas. No aplicar un H único de cantón a vanos rígidos desiguales.
6. Exigir certificados de postes y armadosCAC, capacidades con signo y curvaN-M.13 m/400 daN no significa400 kg verticales. La carga transversal no da capacidad axial.
7. Resolver protección de fuente débil, puesta a tierra, aislamiento y cimentación. No copiar ajustesSEIN.
8. Actualizar CAD, métricas y presupuesto desde la misma versión de datos, verificar y documentar la revisión humana.

## Limitaciones del motor

Cable elástico lineal enT/EA, fluencia de sensibilidad sin curva del fabricante, viento muestreado cada15 grados y dimensiones de poste cónico tipo. Sin modelar deslizamiento de grapas, torsión/eccentricidades de herrajes reales, vibración/fatiga, pretensión ni rigidez de retenidas. La resistencia equivalente de flexión requiere confirmar punto de ensayo, sección crítica y factores del gradoCNE real. El flujo es trifásico equilibradoPQ de línea corta, TX con impedancias nominales yP0/Q0 supuestos; no simulaAVR, transitorios ni carga desequilibrada. El caso1.05 pu es elevación efectiva ideal, no posición física de toma validada.

## Cambios hechos en este entorno

Clonado completo de `gaelrenzo/instalacion-electricas`, base3619a7f06e64488628182d915e9d85e87d1515a5. La elaboración inicial quedó en la rama `revision/lp-r02-auditoria-2026-10-18`. Para la sincronización solicitada posteriormente se prepararon una copia versionada y su ZIP en `revisiones/`; consultar `revisiones/README.md` y el registro de sincronización. Esta copia mantiene los resultados técnicos originales y su manifiesto. Copia de`/root/instalacion-electricas` pertenece a otro remoto y no se modificó. La rutaAndroid`/sdcard/Documents` se resuelve aquí como`/mnt/sdcard/Documents`.

Se instalaron dependenciasPython para cálculo/documentos/CAD en el entorno existente; versiones en`entorno.json`. No se instalóAutoCAD ni se presumeQGIS presente. Los dos fallos iniciales de serialización de tiposNumPy se corrigieron en el constructor; los resultados se regeneran y verifican. Conservar el registro de fallos y correcciones sin presentar una ejecución fallida como aprobada.

Fuentes de sistema requeridas: DejaVu Sans. En Debian, si faltan, instalar el paquete `fonts-dejavu-core`. El paquete incluye un fragmento de código e insumos y un restaurador para reconstruir en carpeta nueva sin Git ni archivos de Windows.


## Continuación desde otro equipo

Los enlaces activos del manifiesto apuntan a `revisiones/lp-r02`, que se versiona con los PDF, XLSX, DXF y recursos listos para abrir. `build/` sigue reservado a reconstrucciones. El paquete congelado conserva el contexto de su generación; la documentación viva es la de este proyecto. Las fuentes recuperadas posteriormente del DVD UNAP y Aricato–Phara se integran sin modificar sus bytes: ver `FUENTES_RECUPERADAS_GITHUB.md` y `fuentes-recuperadas-preservar.json`. No afirmar que estos nuevos documentos ya se aplicaron al cálculo R02.


## Publicación en GitHub

El contenido técnico se publicó y verificó en `main` y `revision/lp-r02-auditoria-2026-10-18`, commit `67a0bada7bc7831e8aef54b762512e3126eb0ac1`. La sesión GitHub CLI quedó autenticada con escritura. Consultar `SINCRONIZACION_PC.md` y `publicacion-github.json` para la evidencia de sincronización. La publicación conserva el estado académico con observaciones; no añade aprobación de ingeniería.

## Continuación en PC: presentación P01

La presentación P01 se registra en `PRESENTACION_P01.md` y `proyecto.yaml`, sin modificar los resultados técnicos LP-R02. La entrega está en `entregables/linea-primaria-r02-presentacion/`. Incluye expediente integrado con el formato de vivienda Aquiles, capítulos editables, DWG nativo guardado y reabierto con AutoCAD 2027 y QGIS 3.44.15 portable verificado. Las afirmaciones anteriores de «sólo DXF» y «sin QGIS» describen la generación móvil, conservada en `revisiones/lp-r02`, no esta continuación.

El ZIP P01 completo se adjunta a la versión GitHub `lp-r02-p01-20261018` por superar 100 MiB. Mantener la copia móvil con su manifiesto y las fuentes recuperadas. El diseño sigue con sus observaciones abiertas; no cambiar la tensión ni trasladar el dimensionamiento del curso de Centrales Hidroeléctricas por haber mejorado la presentación.
