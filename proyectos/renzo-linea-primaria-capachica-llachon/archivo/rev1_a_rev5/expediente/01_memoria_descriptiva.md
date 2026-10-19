# 1. Memoria descriptiva y justificación

## 1.1 Objeto

Definir la base documental, cartográfica y técnica para evaluar el servicio de media tensión entre Capachica y Llachón. La decisión de inversión debe responder a una necesidad comprobada de cobertura, capacidad, calidad, confiabilidad o seguridad. No se ha recibido todavía el diagnóstico del titular de la red ni la proyección de demanda; por ello la intervención física queda **por definir**.

## 1.2 Ubicación y límites elegidos

El corredor se localiza en el distrito de Capachica, provincia de Puno. Se adoptan dos **referencias GIS**, no puntos de obra autorizados:

| Extremo | Código GISEM | Longitud/latitud WGS84 | Este/Norte UTM 19S (m) | Observación |
|---|---|---|---|---|
| Capachica | `NMT000367723` | −69.830170304°, −15.643135203° | 411 020,16 / 8 270 364,54 | Separación de 5,02 m a extremo de polilínea |
| Llachón | `NMT000027963` | −69.784386472°, −15.722124515° | 415 960,00 / 8 261 645,38 | Separación de 3,48 m a extremo de polilínea |

La posición y los códigos fueron extraídos de la capa 24 de [Osinergmin GISEM](https://gisem.osinergmin.gob.pe/serverosih/rest/services/OGC/PeruOsinergmin019RedesMediaTension/MapServer). El camino de 27 tramos se infirió en la capa 22 con empalme de extremos a tolerancia ≤1 m. La continuidad cartográfica **no comprueba continuidad eléctrica ni física**. El [cuadro de tramos](../datos/cuadro_tramos_gisem.csv) conserva sus códigos y progresivas; la ruta completa figura en `derived/route.json`.

El extremo de Llachón se eligió por proximidad cartográfica al poblado y a un registro de estructura MT. Debe cambiarse si el operador determina otro punto de entrega o si las cargas reales están en otra zona. La distancia aproximada por carretera citada por [MINCETUR](https://consultasenlinea.mincetur.gob.pe/fichaInventario/index.aspx?cod_Ficha=1449) es 14 km, referencia territorial independiente que no sustituye la medición del eje eléctrico.

## 1.3 Situación de la infraestructura y problema por demostrar

La publicación GIS representa **red de media tensión existente** en el recorrido. No se dispone de planos conforme a obra, estado de conductor y estructuras, demanda, calidad de tensión, interrupciones, capacidad remanente ni autorización de conexión. En consecuencia, no es técnicamente sustentable afirmar hoy que Llachón requiera construir 13,834 km de línea nueva. La posible necesidad de obra es una hipótesis de investigación.

La suma de la geometría digital proyectada es **13 834,03 m**. El campo GISEM `LONGITUD` de los mismos 27 registros suma numéricamente **14 248,94**; su unidad no está declarada en el esquema consultado. La diferencia numérica es **414,91**. Ninguna cifra se utiliza como metrado contractual hasta cotejar inventario del titular y topografía.

## 1.4 Alternativas y criterio de selección

| Alternativa | Descripción | Condición para seleccionarla | Estado |
|---|---|---|---|
| A - operación/mantenimiento | Resolver fallas o regulación con activos actuales | Capacidad adecuada y defecto operativo identificado | Sin diagnóstico |
| B - rehabilitación/reforzamiento | Sustituir o mejorar componentes/tramos necesarios | Fallas, sobrecarga, caída de tensión o riesgo comprobados | Sin cálculos ni inspección |
| C - extensión o nuevo trazo | Incorporar infraestructura donde no exista capacidad o cobertura viable | Comparación técnica, económica, ambiental y predial favorable; conexión aprobada | Sin alternativas topográficas |

**Alternativa de trabajo del expediente:** levantar y analizar la opción B sobre la red publicada, comparándola con A y C. Esta no es una selección de obra. El criterio final debe documentar indicadores de servicio, demanda, costo de ciclo de vida, riesgos, derechos de paso y conformidad del operador.

## 1.5 Alcance territorial y ambiente

El perfil CL-02 usa 57 puntos SRTM30m entre 3823 y 3887 m. La orografía, accesos, cruces, cursos de agua, viviendas y límites prediales aún no fueron levantados a precisión de ingeniería. Deben investigarse restricciones ambientales, culturales y de servidumbre **sobre el trazo que finalmente se proponga**, sin deducir permisos a partir de cartografía pública. No se ha realizado evaluación ambiental ni predial.

## 1.6 Resultado de esta memoria

Se entrega una **base trazable para completar la ingeniería**: fuentes preservadas, ruta GIS, cotas referenciales, dos planos de planta/perfil y una matriz de datos faltantes. El expediente no cuantifica construcción, no certifica cumplimiento normativo y no constituye conformidad de Electro Puno. La memoria ampliada de antecedentes está en `documentacion/MEMORIA_ANTEPROYECTO.md`.
