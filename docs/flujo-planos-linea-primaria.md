# Flujo reproducible de planos de línea primaria

## Objetivo y alcance

Este flujo sirve para los proyectos de línea primaria de `proyectos/`. Cada
proyecto conserva sus fuentes, cálculos y entregables. Las funciones comunes
de CAD y verificación pueden residir en `herramientas/cad/`, pero los datos,
la configuración y los nombres de las láminas pertenecen al proyecto.

El estado de una lámina debe ser explícito: `anteproyecto`, `revision_tecnica`
o `aprobado_para_entrega`. La generación automática nunca equivale a
aprobación de ingeniería ni a autorización de construcción.

## Qué se toma de los proyectos actuales

| Proyecto | Componente aprovechable | Condición para incorporarlo |
| --- | --- | --- |
| Chifrón | Seis láminas MT LP-01, PL-01, U-01, D-01 a D-03; capas, bloques y rótulo A3 de `generar_planos_autocad_lp.py` | Leer estructuras y vanos de datos validados, en lugar de las listas internas del generador. Mantener el aviso de conexión no confirmada. |
| Chifrón v2 | Lectura de KML y conversión WGS84 a UTM | Usar una transformación CRS comprobable y excluir redes BT, acometidas y alumbrado de la entrega MT. |
| Capachica–Llachón | Separación de PC, PN y CV; rechazo de sobrescritura; auditoría DXF/PDF; manifiesto SHA-256 y procedencia | No promover candidatos a estructuras aprobadas. Hacer que la revisión vigente de `proyecto.yaml` coincida con la entrega. |

## Contrato de entrada por proyecto

### Entrada inicial con el nombre de un lugar

La interfaz puede comenzar con un texto como `Capachica, Puno, Perú`. Un
geocodificador propone coordenadas y un área de estudio; guarda el nombre
consultado, proveedor, respuesta, fecha y coordenadas. La coincidencia debe
mostrarse al usuario porque un topónimo puede referirse a más de un sitio.

Con esa área se puede descargar un modelo digital de elevación (DEM),
registrar su proveedor, resolución, sistema vertical e identificador de tesela,
además de la huella SHA-256 del raster derivado, y
producir un mapa de relieve y curvas de nivel **preliminares**. QGIS y un
proceso Python pueden hacer este trabajo sin Topomagic. Si un proveedor no
está disponible, el proceso registra el fallo y usa otro DEM documentado;
no mezcla cotas de fuentes distintas sin conciliarlas.

La primera implementación es
[`herramientas/topografia/generar_topografia.py`](../herramientas/topografia/README.md):
recibe el nombre de un lugar y usa Copernicus DEM público para crear GeoTIFF,
curvas DXF y un mapa PDF/PNG, con manifiesto de procedencia.

El nombre del lugar por sí solo no determina el punto de alimentación ni el
eje de una línea. Para dibujar un perfil longitudinal se requiere un eje KML,
GIS o un trazado candidato generado y revisado. Cualquier perfil extraído de
un DEM global queda rotulado `topografia_preliminar_dem`: no se utiliza para
aprobar postes, cimentaciones, flechas ni gálibos. Al llegar el levantamiento
de campo, se comparan sus cotas con el DEM y se emite una nueva revisión.

`proyecto.yaml` identifica proyecto, revisión activa, alcance, estado y rutas
de los datos canónicos. El generador no elige entradas por el nombre de una
carpeta `rev`, `final` o por fecha de modificación.

La entrada mínima para una **planta de anteproyecto** contiene:

1. Eje o ejes originales, archivo fuente y SHA-256; CRS de origen y CRS métrico.
2. Geometría derivada con método, fecha y enlace a la fuente original.
3. Tabla de puntos con identificador, coordenadas, tipo (`existente_gis`,
   `candidato` o `aprobado`), fuente y estado de verificación.
4. Cruces, brechas y discrepancias cartográficas visibles y clasificados.

Para **planos de ingeniería de detalle** se requieren además, según la lámina:

| Lámina | Datos que deben estar validados antes de emitirla como diseño |
| --- | --- |
| Planta de línea | Traza, estructuras aprobadas, conexión aprobada, cruces y servidumbres contrastados. |
| Perfil longitudinal | Topografía de campo apta, progresivas, cotas, apoyos, flechas y gálibos calculados para cada vano. |
| Unifilar MT | Punto de alimentación, tensión, demanda, equipos y coordinación de protecciones confirmados. |
| Armados y detalles | Tipo de poste y armado asignados, esfuerzos, retenidas, cimentación y puesta a tierra sustentados. |

Si falta un dato, registrar `dato requerido`, fuente pendiente y láminas
afectadas. El generador podrá producir una vista de anteproyecto con marca
visible, pero debe bloquear cualquier rótulo o paquete que la presente como
ingeniería aprobada.

## Secuencia de ejecución

```text
fuentes inmutables
  -> inventario, SHA-256, CRS y clasificación de evidencia
  -> datos canónicos y conciliación de rutas, puntos y revisiones
  -> cálculos eléctricos, mecánicos y topográficos con tablas exportadas
  -> paquete CAD en build/<id>/<revision>/
  -> auditoría estructural y visual
  -> revisión técnica documentada
  -> publicación controlada en entregables/
```

### 1. Preparar y conciliar datos

- Leer `proyecto.yaml` y verificar que todas las rutas declaradas existen.
- Conservar KML, GIS, levantamientos y documentos originales en `fuentes/` o
  `sources/`, sin corregirlos para acomodar el dibujo.
- Convertir a un CRS métrico declarado; comprobar longitud, orden de vértices,
  separaciones y puntos de conexión contra la fuente.
- Resolver discrepancias entre YAML, CSV, memorias y scripts antes de dibujar.
  Los valores no resueltos quedan marcados como pendientes.

### 2. Calcular una sola vez

- Los scripts de cálculo leen las entradas canónicas y escriben tablas de
  resultados con unidades, fórmula o método, procedencia y estado.
- Planta y perfil consumen las mismas coordenadas, progresivas y vanos.
- El generador de planos no recalcula una versión alternativa de flecha,
  gálibo, esfuerzos o metrados a partir de constantes propias.
- Verificar invariantes: IDs únicos, progresivas crecientes dentro de cada
  segmento, suma de vanos frente a longitud del eje y correspondencia entre
  estructura, vano y tabla de resultados. Las brechas de un KML segmentado se
  representan como brechas, sin sumarlas como línea construida.

### 3. Generar planos

- Producir primero en una carpeta nueva de `build/`; rechazar la
  sobrescritura de una revisión ya generada.
- Dibujar la geometría georreferenciada en el espacio modelo, en metros, y
  las presentaciones A3 en milímetros. Registrar CRS, escala, código, revisión,
  fecha, fuentes y estado de la lámina en su rótulo.
- Usar capas y bloques comunes para eje MT, estructuras, SED, retenidas,
  puesta a tierra, cotas, texto y elementos pendientes. Mantener categorías
  de evidencia distinguibles en leyenda y en capas.
- Generar DXF y PDF desde el mismo modelo de datos. Crear PNG de control del
  DXF renderizado; si PDF y DXF se dibujan por rutas separadas, comparar ambos
  antes de aceptar la lámina.
- Producir un índice de láminas y un manifiesto con SHA-256 de cada entrada y
  salida, versión del generador, CRS, estado y lista de pendientes.

### 4. Verificar antes de publicar

Controles automáticos obligatorios:

1. Auditoría `ezdxf`: cero errores, unidades, capas requeridas, bloques,
   presentación y geometría esperada por lámina.
2. PDF: una página por lámina, formato A3 declarado, rótulo, código y revisión
   concordantes con DXF e índice.
3. Datos: conteos, coordenadas, progresivas y resultados principales iguales
   entre tablas, plano y memoria; hashes de fuentes intactos.
4. Visual: render de todas las láminas, revisión de recortes, solapes,
   tipografía, símbolos, leyenda, escala gráfica y ploteo legible. La
   detección automática de solapes sirve como alerta, no como aprobación.
5. Estado: ninguna lámina de anteproyecto puede aparecer en el índice o ZIP
   como plano constructivo. Los datos requeridos permanecen visibles.

La revisión humana registra nombre, fecha, observaciones, correcciones y
decisión por lámina. Solo después de esa revisión se copia el paquete aprobado
de `build/` a `entregables/`; el ZIP se forma con esos mismos archivos y se
verifica reabriéndolo.

## Aplicación inicial

1. **Chifrón:** tomar la matriz maestra y la planilla de vértices como entradas
   a conciliar; retirar la dependencia de listas internas del generador de seis
   DXF. Mantener LP-00 como evidencia de la discrepancia de conexión y dejar
   los seis planos MT en revisión hasta cerrar los datos requeridos.
2. **Chifrón v2:** conservarlo como antecedente de técnicas KML y PDF; no usar
   su P-01 de redes BT para la entrega de línea primaria.
3. **Capachica–Llachón:** conservar la separación PC/PN/CV y el manifiesto de
   Rev. 5; alinear `proyecto.yaml` con la revisión que se adopte. Generar
   planos de apoyos de diseño únicamente cuando exista un CSV aprobado; la
   plantilla de ese CSV no equivale a una aprobación.

## Criterio de terminación

El proceso termina cuando una ejecución nueva reproduce el paquete desde sus
entradas declaradas, las verificaciones automáticas pasan, cada lámina tiene
revisión humana registrada, el expediente cita los mismos resultados y el
índice distingue claramente planos vigentes, referenciales y antecedentes.

## Referencias para la topografía preliminar

- [OpenTopography Global DEM API](https://opentopography.org/developers):
  acceso programático a SRTM GL1 y otros DEM globales mediante clave API.
- [USGS SRTM](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm):
  descripción oficial del producto de aproximadamente 30 m y su datum vertical.
- [QGIS Elevation Profile](https://docs.qgis.org/3.44/en/docs/user_manual/map_views/elevation_profile.html):
  inspección y exportación del perfil sobre un eje seleccionado.
