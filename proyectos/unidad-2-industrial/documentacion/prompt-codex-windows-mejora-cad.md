# Prompt para Codex en Windows: revisión y mejora final del grifo

Copiar desde `INICIO DEL PROMPT` hasta `FIN DEL PROMPT` en la aplicación Codex
de Windows. Antes, abrir como workspace la copia sincronizada del repositorio.

## INICIO DEL PROMPT

Trabaja directamente en este repositorio de **Instalaciones Eléctricas I** y
completa una revisión final, técnica y visual, del proyecto
`proyectos/unidad-2-industrial`, un anteproyecto académico nuevo para un grifo
de combustibles líquidos en Caracoto, Puno.

Tu objetivo es mejorar lo que ya existe, no rehacer el proyecto ni copiar datos
de otro caso. El autor es **Aquiles Taylor Ramos Yapo**, el docente actual es
**Mg. Gregorio Meza Marocho** y **Miguel Mamani Chuquicallata** solo figura como
propietario consignado en la documentación de referencia facilitada por la
DREM. Están incluidos Diesel B5 S-50, Gasohol Regular y Gasohol Premium. **GLP
y GNV están excluidos**.

Primero lee completos, en este orden:

1. `AGENTS.md` de la raíz.
2. `proyectos/unidad-2-industrial/AGENTS.md`.
3. `proyectos/unidad-2-industrial/proyecto.yaml`.
4. `documentacion/registro-decisiones.md`, especialmente DEC-016 a DEC-018.
5. `documentacion/dudas-pendientes.md`.
6. `datos/ubicacion.yaml`, `datos/rotulo-planos.yaml`,
   `diseno-electrico/datos/cargas.yaml` y `presupuesto/README.md`.

Antes de diagnosticar archivos ausentes, ejecuta
`python proyectos/unidad-2-industrial/scripts/verificar_preparacion.py --solo-fuentes`.
Desde DEC-019 el clon debe contener el DXF, las dos capturas, el logo vectorial
y la evidencia comercial base; si el verificador falla, primero confirma que
la rama incluya esa decisión.

Respeta estas reglas durante todo el trabajo:

- No modifiques originales de `fuentes/local/`; genera derivados en `build/`.
- No inventes coordenadas, fotografías de campo, factibilidad, corriente de
  cortocircuito, placas, firmas, sellos, CIP ni aprobación de DREM/docente.
- La coordenada E 383250, N 8272300 UTM 19S es solo una aproximación gráfica de
  A-01. Las capturas municipal y Google Maps son contexto, no certificación
  catastral ni punto exacto. No agregues un pin falso.
- No cambies cálculos canónicos desde el dibujo. Si detectas una inconsistencia,
  corrige primero la fuente YAML/JSON y regenera.
- Conserva cambios ajenos ya presentes en el worktree; no uses reset, checkout
  destructivo ni incluyas archivos de Aquiles/primera unidad en el commit.
- Los comentarios nuevos del usuario se acumulan como pautas; registra dudas no
  bloqueantes en `documentacion/dudas-pendientes.md` y sigue avanzando.

### Revisión CAD en AutoCAD para Windows

Usa AutoCAD 2027 si está disponible para abrir las seis DXF generadas en
`build/unidad-2-industrial/cad/planos/` y, solo como referencia inmutable, el
DWG/DXF A-01 original. Inspecciona Modelo y Presentación1 a escala de impresión
A1. No crees un cajetín nuevo encima del plano.

El rótulo correcto debe reutilizar el bloque original `ROTULO` de A-01, mantener
su geometría, tamaño y ubicación, quitar textos empresariales antiguos y
sustituir sus atributos dentro de la misma huella. Debe mostrar proyecto,
propietario de referencia, ubicación, estudiante, docente, curso, código de
lámina, escala y fecha. No uses `WIPEOUT`, máscara de fondo ni rectángulo opaco;
comprueba que no tape geometría, coordenadas, leyendas o detalles.

Revisa y mejora, sin alterar la ingeniería aprobada:

- **IE-01:** rutas L-01 a L-06 en carriles diferenciados; separar iluminación
  de marquesina, exterior y letrero; mantener etiquetas junto a cada recorrido.
- **IE-02:** diferenciar por nivel alumbrado, tomacorrientes, POS y
  refrigeración; evitar textos sobre muros o símbolos.
- **IE-03:** separar claramente los alimentadores de bombas STP F01-F04 del
  troncal UPS-FUEL F05-F10; usar derivaciones cortas y reconocibles.
- **IE-04:** verificar continuidad visual de PE/equipotencialidad, PAT, SPD y
  protección contra rayo sin confundirla con conductores activos.
- **IE-05:** mantener barras normal y emergencia ortogonales, ATS/UPS visibles,
  calibres de alimentadores y protecciones; eliminar diagonales/cruces que no
  representen conexión eléctrica.
- **IE-06:** conservar límites de zonas peligrosas como propuesta académica,
  con leyenda y advertencia de revisión profesional; no ampliar límites por
  intuición.

Comprueba capas, colores, tipos/grosores de línea, alturas de texto y símbolos a
escala A1. Los circuitos deben poder reconocerse tanto en color como en escala
de grises. Corrige solapes y recorridos ambiguos, pero no agregues cargas o
equipos no autorizados.

### Memoria, ubicación y cotización

Verifica que el capítulo 1 muestre: datos administrativos, captura catastral,
captura satelital y croquis vectorial A-01, cada uno con fuente y advertencia.
No presentes las capturas como fotografías actuales del lugar.

Para actualizar la evidencia comercial usa exactamente el flujo de
`presupuesto/README.md`: genera el BOM, ejecuta el cotizador v1 en modo
`heuristico`, con `--no-actualizar-precio`, revalida y resume. Una coincidencia
`OK` siempre requiere revisión humana. Rechaza accesorios, familias genéricas,
potencias ambiguas y productos que no cumplan la especificación. Nunca copies
automáticamente un precio de suministro sobre una partida instalada.

### Regeneración y controles obligatorios

1. Regenera los planos desde `scripts/generar_planos_grifo.py` si modificaste
   fuentes CAD/generador. No edites solo un DXF de `build/` dejando el generador
   desactualizado.
2. Compila con
   `.venv/bin/python proyectos/unidad-2-industrial/scripts/compilar_expediente.py --regenerar-planos`.
3. Ejecuta la batería indicada por el `Makefile` para Unidad 2 y cotización.
4. Verifica con `pdfinfo` que cada lámina mida A1 y con `pdfimages -list` que
   cada PDF de plano tenga cero imágenes raster. En el expediente sí son
   esperables las dos capturas raster de ubicación; los seis anexos deben seguir
   siendo vectoriales.
5. Inspecciona visualmente al 100 %, 200 % y vista completa: portada, páginas de
   ubicación, cotización, IE-01 a IE-06 y especialmente rótulos/unifilar.
6. Genera el paquete con
   `.venv/bin/python proyectos/unidad-2-industrial/scripts/preparar_paquete_academico.py`.
7. Actualiza registro de decisiones, auditoría y dudas si cambió algún criterio.

No declares que el diseño autoriza construcción. Continúan pendientes
factibilidad e Icc de Electro Puno, placas definitivas, verificación de campo,
fotometría/PAT, coordinación de protecciones y revisión competente de áreas
clasificadas.

Al terminar, presenta un informe corto con: archivos modificados, comparación
antes/después, resultados exactos de pruebas, tamaño/páginas de los PDF,
resultado de cotización por estados, observaciones que aún requieran campo y
ruta del ZIP final. Solo después de verificar todo, crea un commit limitado a
Unidad 2 y herramientas genéricas de cotización, y sincroniza `main` con los
remotos configurados. Si el remoto avanzó, integra sin borrar cambios del
usuario.

## FIN DEL PROMPT
