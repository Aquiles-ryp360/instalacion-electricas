# Metrados M01, memoria descriptiva y ubicación

Fecha: 19/10/2026. Base del repositorio: `d98269a992758689f302c4dcd35b9b4e4878cca2`; última entrega de Aquiles recibida: `d777714bda51b92840efb03fb39e7414efed6912`. Se continúa el trabajo de PC, preservando la geometría y los archivos nativos. La revisión técnica sigue siendo **LP-R02** y el detalle de metrados es **LP-R02-M01**.

## Problema y cambio

La entrega anterior tenía conteos por función/altura y una partida por conjunto, sin inventario comprobable de los componentes de cada apoyo. La captura del usuario corresponde a la página 54/72 del expediente, referencia DGE PR3: contiene una lista de piezas por armado. El original se conserva en `fuentes/metrados-m01/`, con procedencia y SHA256.

M01 incorpora catálogo, recetas, inventario por poste y resumen de suministro. Desarrolla 111 apoyos, cuatro armados CAC, la retenida RI-A y el sistema de tierra de apoyo. Se conserva también la planilla de los 110 vanos, con catenaria por fase, terna y totales. Las fichas identifican código, descripción, unidad, coeficiente, número de conjuntos y cantidad. Se informa por separado lo ya incluido con pernos y abrazaderas: no se compra ni valoriza dos veces. Los precios por conjunto del presupuesto comprenden sus componentes; este cambio no los convierte en precios unitarios cotizados.

El Excel tiene 12 hojas. `Ficha_poste!B4` permite elegir un poste; `Inventario` conserva también combinaciones de cantidad cero para que cambiar de función active los componentes nuevos. `Matriz_armados` contiene coeficientes editables, `Resumen_materiales` concilia las compras y `Accesorios_incluidos` controla tuercas, contratuercas, arandelas y pernos que ya vienen con el conjunto. Los conteos de unidades se presentan como enteros; las longitudes tienen decimales. Cada XLSX es autónomo y no tiene vínculos externos: cambiar un libro no modifica los demás. Para sincronizarlos se regeneran los tres desde las entradas canónicas; cualquier cambio de geometría exige una nueva revisión técnica antes de actualizar sus metrados.

## Fuentes y decisiones de adaptación

- RD 024-2003-EM/DGE: columna **trifásica sin neutro** de las láminas 004/PS1-3 (PDF 9), 008/PA1-3 (13), 020/PR3-3 (25), 026/PTH-3 (31) y 074/RI-A (91). Se inspeccionaron visualmente las listas; no se suman accesorios del neutro.
- PAC Electro Puno 2024, PDF 59: acredita adquisición de la familia de crucetas metálicas para CAC. No proporciona una certificación para el poste de 600 daN ni el despiece de sus adaptadores. Su PDF y SHA256 se conservan en `recursos/linea-primaria-limbani/2026-10-19/`.
- Se sustituye el poste de madera por el CAC del modelo, se elimina el tirafondo para madera y se declara una abrazadera CAC por par de riostras, con dos pernos y sus accesorios. Es un **coeficiente académico de metrado**, sujeto al plano del fabricante. La cruceta metálica de 2.50 m es también una adopción explícita.
- RI-A: la referencia dibuja cable de 10 mm y 16 m. No se deduce de ese diámetro una resistencia certificada. M01 mantiene **60 kN de rotura mínima** y desarrolla la longitud como `h_amarre/sen(45°) + 3 m` por ramal; las colas son una provisión declarada.
- PAT-P desglosa las 111 partidas de tierra de apoyo ya presupuestadas. Un electrodo, conector y terminal; Cu nominal de 16 mm², longitud `h_amarre + 3 m` y fijaciones cada metro más extremos son hipótesis de metrado. Las láminas 077/078-A se usan como referencia de materiales; no se copian grapas para madera. No equivale a resistencia de dispersión comprobada ni incluye las dos mallas de subestación.
- El modelo resistente previo usa **300 N por apoyo** para aisladores/accesorios. Las masas unitarias reales del catálogo se conservan `null`: M01 no acredita que el nuevo despiece pese 300 N. Debe recalcularse la mecánica con el suministro real antes de validar la configuración y separaciones.
- P003, P035 y P057 tienen giro mayor de 90°. Se usa el conteo base PR3-3, identificando que su geometría específica sigue sin resolver. No se presenta como adaptación constructiva aprobada.

`datos/metrados-m01/catalogo.json` registra materiales, unidades, fuentes, confianza, masa no conocida y accesorios incluidos. `criterios.json` identifica hipótesis y procedencia de los coeficientes. No se alteró `revisiones/lp-r02/03-calculos/resultados.json`.

## Corrección del conductor

La presentación anterior calculaba `160 ramales × 3 fases × 2 m = 960 m` de puentes. Ese conteo relacionaba ramales mecánicos con interrupciones eléctricas, incluyendo apoyos de paso. M01 calcula un puente por fase en cada una de las 38 retenciones y una cola por fase en cada uno de los 2 terminales: `3 × (38 + 2) × 2 = 240 m`. Suspensión y ángulo de paso mantienen continuidad. Los 2 m son una provisión de montaje, no una longitud medida en fabricante.

El tendido de las tres fases sigue siendo 20 274.360891 m. La reserva es `ceil(0.03 × (20 274.360891 + 240)) = 616 m`; el suministro es `ceil(20 274.360891 + 240 + 616) = 21 131 m`, antes 21 873 m. La reserva y el redondeo se compran una sola vez; no se reparten como cortes de montaje por apoyo. La mitad de los vanos adyacentes se asigna contablemente a cada poste para conciliar el tendido.

Con precios referenciales por conjunto y el conductor a S/ 5.80/m, el recálculo nativo da **S/ 2 553 726.92**, antes S/ 2 559 924.11. Se conservan las ecuaciones y resultados eléctricos/mecánicos de LP-R02; la menor compra de reserva/puentes no cambia la longitud de catenaria del modelo eléctrico.

## Memoria y plano de ubicación

La memoria descriptiva tiene PDF propio y forma parte del expediente integrado. Incorpora antecedentes, finalidad, objetivos, ubicación política/geográfica, coordenadas, acceso y relieve con su estado de comprobación, estados ambientales de cálculo, instalaciones, alcance de obras y secuencia prevista. No se inventaron tiempos de viaje, carreteras reconocidas, ensayos de suelo, resistividad ni un cronograma contractual.

UB-01 desarrolla Perú → Puno → Sandia → Limbani y el corredor. La fuente es el servicio oficial **IGN / DATOS_GEOESPACIALES/LÍMITES**, capas 3, 4 y 5. Las respuestas GeoJSON, metadatos, consulta y SHA256 se conservan en `recursos/linea-primaria-limbani/2026-10-19/ubicacion-ign/`. Se usan las 25 entidades departamentales con código; la respuesta conserva además una entidad vacía sin código/nombre que no se dibuja. No se reparan ni alteran los originales para producir una demarcación distinta.

Los límites son referenciales. El plano es una elaboración del proyecto a partir de la fuente oficial, no un plano aprobado por IGN. El eje proviene de LP-R02 y no de un levantamiento oficial. Se comprobó espacialmente que sus dos extremos y la longitud del eje están dentro del polígono referencial de Limbani (ubigeo 211203). El plano identifica WGS 84 y UTM 19 S, norte, escala gráfica, coordenadas y fuente. Se entrega en PDF A3 y SVG editable.

## Entrega y continuidad

Ocho carpetas: `00_Expediente`, `01_Memoria_Descriptiva`, `02_Calculos`, `03_Metrados`, `04_Planos`, `05_Cartografia`, `06_Presupuesto` y `07_Recursos`. Los nombres y rutas activos se declaran en `proyecto.yaml`. El trabajo intermedio conserva las rutas de la entrega base dentro de `build/`; `rutas_entrega.py` hace la equivalencia para reconstrucciones desde cualquiera de las dos estructuras.

El CAD DWG/DXF y la cartografía QGIS de PC se trasladan conservando bytes. La nueva ubicación UB-01 es una lámina adicional. No se atribuye a esta revisión una nueva sesión de AutoCAD ni una reapertura de QGIS. La prueba de Office anterior es histórica; esta revisión recalcula con **LibreOffice**.

Las fuentes LaTeX activas están en `expediente/final/` y `expediente/memoria-descriptiva/`. El ZIP anterior se conserva en `archivo/presentacion-pre-m01/` y el estado original sigue disponible en el commit de base. No usar el archivo histórico como entrada canónica.

## Reproducción y verificación

En Debian usar `python3`, que corresponde al intérprete con las dependencias del proyecto; el alias `python` de Termux no tiene necesariamente los mismos paquetes. En Windows puede usarse `python` con esas dependencias instaladas. Requiere LibreOffice y pdflatex en PATH para regenerar; la verificación de integridad no los necesita.

```bash
python3 -m pip install -r proyectos/aquiles-linea-primaria-inst-ii/requirements-m01.txt
python3 -m unittest discover -s proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02 -p test_metrados_componentes.py -v
python3 -m unittest herramientas.lineas_primarias.tests.test_revision -v
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/actualizar_metrados.py preparar --trabajo build/aquiles-linea-primaria-inst-ii/m01-reproduccion
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/actualizar_metrados.py recalcular --trabajo build/aquiles-linea-primaria-inst-ii/m01-reproduccion
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/actualizar_metrados.py documentos --trabajo build/aquiles-linea-primaria-inst-ii/m01-reproduccion
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/actualizar_metrados.py ensayos --trabajo build/aquiles-linea-primaria-inst-ii/m01-reproduccion
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/actualizar_metrados.py empaquetar --trabajo build/aquiles-linea-primaria-inst-ii/m01-reproduccion
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/actualizar_metrados.py verificar-publicado
```

`preparar` exige una carpeta nueva. Los resultados regenerados no se publican automáticamente. `Entrega_M01/` y el ZIP se revisan antes de reemplazar la entrega activa. Verificar los gráficos y volver a compilar el PDF cuando cambien las entradas; el selector del Excel no modifica por sí solo un PDF ya exportado.

Sistema Debian: `fonts-dejavu-core`, `libreoffice-calc`, `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-pictures` y `texlive-lang-spanish`. En esta sesión se añadió este último paquete para resolver el fallo de Babel; los demás ya estaban instalados. Hubo un intento de prueba con el Python de Termux sin NumPy; se corrigió usando el Python de Debian. La primera composición detectó un encabezado de tabla demasiado ancho y notas de ficha continuadas; se corrigió el formato conservando cantidades y el rechazo de desbordamientos del compilador.

Consultar `validacion-m01.json`, `ensayos-entradas.json`, `pruebas.json`, `validacion-ubicacion.json` y el registro visual para la evidencia final. Las condiciones resistentes, topográficas y de suministro abiertas no constituyen una aprobación de ingeniería.
