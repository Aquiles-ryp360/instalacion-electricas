# Cálculos disponibles y variables pendientes — Rev. 2

## Resultados calculados

Longitud del KML: 13 939,512 m UTM por suma de cuatro segmentos; 13 943,736 m geodésicos. La diferencia de 4,224 m entre métodos refleja proyección y redondeo. Brechas entre segmentos: 65,077 m en total, **fuera** de la longitud calculada. Cantidad cartográfica: 40 estructuras GIS cercanas al eje bajo filtro de 25 m; no es metrado de postes nuevos. Las 44 intersecciones OSM son alertas, no metrados de cruces certificados.

## Cálculos eléctricos condicionados

El módulo `scripts/calculos_condicionales.py` ofrece `I[A] = S[kVA] / (√3 U[kV])` para un sistema trifásico confirmado y `ΔU[V] = √3 I[A] L[km] (R[Ω/km] cosφ + X[Ω/km] sinφ)` para una aproximación radial. Rechaza `null` y valores fuera de dominio. **No se calcula corriente, caída, pérdida ni ampacidad real**: faltan demanda, tensión, fases, conductor, resistencia, reactancia, topología y factor de potencia. Cortocircuito, protección y capacidad requieren unifilar, impedancias de fuente, ajustes y datos del operador.

## Cálculos mecánicos condicionados

Para un vano nivelado y carga uniforme, la aproximación parabólica es `f[m] ≈ w[N/m] L²[m²] / (8 H[N])`. No se usa para dimensionar: faltan peso certificado del conductor y accesorios, tensión admisible, temperatura, viento, altitud de diseño, perfil topográfico, geotecnia y distancias reglamentarias aplicables. No se asignan altura, clase, cimiento, retenida ni tipo de estructura. El ensayo unitario con números sintéticos solo comprueba la fórmula, **no describe el proyecto**.

## Solicitudes a Electro Puno y campo

1. Factibilidad y punto autorizado; nomenclatura y función del tramo `TMT001868169`; alimentador, tensión nominal/máxima, fases, capacidad, as-built y estado de estructuras.
2. Demanda actual y futura; criterios de crecimiento; esquema de protección, ajustes, cortocircuito, seccionamiento y puesta a tierra.
3. Inventario y fichas de conductores, aisladores, postes, accesorios, materiales y normas internas vigentes.
4. Topografía precisa del corredor y de cada cruce; niveles y despejes; vías, cauces, edificaciones, servidumbres, accesos, suelos, resistividad y clima de diseño.
5. Decisión de necesidad de nueva obra frente a infraestructura existente, alcance aprobado y procedimiento de revisión profesional.

## Clasificación

**A**: presencia y atributos de archivos/fuentes oficiales consultadas. **B**: coordenadas, distancias y conteos derivados de esos archivos. **C**: filtro de 25 m para inspección y esquema de láminas. **D**: ingeniería eléctrica, mecánica y autorización de obra.
