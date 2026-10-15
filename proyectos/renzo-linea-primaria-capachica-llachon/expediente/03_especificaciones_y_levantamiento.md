# 3. Especificaciones técnicas preliminares y plan de levantamiento

## 3.1 Condición de estas especificaciones

Las siguientes son **condiciones para contratar estudios y evaluar alternativas**. No son especificaciones de suministro o montaje de una línea definida. La [R.D. 026-2003-EM/DGE](https://www.gob.pe/institucion/minem/normas-legales/4775087-026-2003-em-dge) identifica especificaciones de materiales y equipos para líneas/redes primarias rurales; la [R.D. 016-2003-EM/DGE](https://www.gob.pe/institucion/minem/normas-legales/4774974-016-2003-em-dge), especificaciones de montaje dentro de su ámbito. La selección de partes y el pliego de obra requieren alternativa aprobada y revisión de sus actualizaciones.

## 3.2 Información solicitada al titular de la red

Solicitar formalmente al operador que confirme si los tramos codificados `ELPU` en GISEM pertenecen a su sistema operativo y entregue, sujeto a sus procedimientos:

- Unifilar, alimentador, puntos de seccionamiento y registro conforme a obra del corredor.
- Tensión nominal, fases, conductor/sección, año/estado de instalación, estructuras, aisladores, retenidas, transformadores, descargadores, fusibles y reconectadores.
- Demanda y perfiles de carga por nodo; tensión registrada, interrupciones, pérdidas y restricciones de capacidad.
- Niveles de cortocircuito y ajustes/filosofía de protección utilizables para un estudio de coordinación.
- Condiciones del punto de conexión y proceso de factibilidad o autorización.

Si el titular no facilita una variable, se registrará ausencia y se definirá una medición o escenario **explícitamente hipotético** para estudio comparativo; no se incorporará como hecho extraído.

## 3.3 Levantamiento topográfico y patrimonial

La planificación del levantamiento deberá revisar la [R.D. 030-2003-EM/DGE](https://www.gob.pe/institucion/minem/normas-legales/4775130-030-2003-em-dge) si su ámbito corresponde. Como mínimo, el encargo debe incluir:

1. Marco de coordenadas y control geodésico documentado; puntos base y precisiones instrumentales.
2. Identificación en campo de los extremos `NMT000367723` y `NMT000027963` y cotejo con el inventario real.
3. Eje de red existente y alternativas, coordenadas/cotas de todos los apoyos relevantes, ángulos y progresivas medidas.
4. Perfil del terreno bajo conductores y en secciones laterales donde la seguridad lo requiera; edificaciones, caminos, cuerpos de agua, servicios y cruces.
5. Inventario fotográfico con código de apoyo, fecha, coordenada, orientación y observaciones; verificar conductor, herrajes, equipos, estado y accesos.
6. Identificación de predios, servidumbres, ocupaciones, restricciones ambientales/culturales y necesidad de permisos.
7. Información geotécnica y de resistividad en los emplazamientos que demanden estructuras o PAT nuevas.

La entrega topográfica deberá incluir datos brutos, procedimiento, control de calidad, CSV/GIS con unidades, planta y perfil editables. Ninguna coordenada de GISEM o cota SRTM se ajustará artificialmente para que coincida con el levantamiento.

## 3.4 Diseño detallado tras la decisión de inversión

La ingeniería aprobada deberá contener memoria eléctrica y mecánica reproducible; unifilar validado por operador; cuadros de cargas, estructuras y vanos; planos de planta/perfil con cruces, cotas y servidumbres; detalles de armados, retenidas, cimentaciones, PAT, protecciones y, si aplica, subestaciones; metrados trazados a planos; presupuesto con APU; cronograma; gestión predial y ambiental; protocolos de prueba y recepción.

**Control de suministros:** toda ficha técnica y marca o modelo propuestos deben cotejarse con las condiciones del sistema, las normas aplicables y el procedimiento de aprobación del titular. No se prescribe en este borrador ningún fabricante, sección, clase de aislador, tipo de poste ni potencia de transformación.

## 3.5 Control de cambios

Las futuras revisiones deben registrar fuente, fecha, autor profesional, dato anterior/nuevo, razón del cambio y plano/cálculo afectado. Los archivos públicos descargados en `sources/` se conservan inalterados. Los nuevos levantamientos irán a una carpeta de fuentes separada, con SHA-256 y metadatos; no se sustituirán silenciosamente los registros GIS usados en este anteproyecto.
