# Proyecto académico de línea primaria Limbani–Huancasayani

Estudiante: Aquiles Taylor Ramos Yapo ·227368

Curso: Instalaciones Eléctricas II ·LP-R01


## 1. Enfoque, objetivos y límites

### 1.1 Descripción general

El proyecto desarrolla el diseño académico de una línea primaria entre la instalación de transformación de salida de la minicentral hidroeléctrica de Limbani y una subestación de llegada en Huancasayani, provincia de Sandia, departamento de Puno. Su propósito es transportar energía en un sistema aislado, sin interconexión inicial con el Sistema Eléctrico Interconectado Nacional (SEIN).

### 1.2 Objetivos del diseño

El objetivo general es dimensionar una solución de transporte eléctrico compatible con la demanda prevista y con las características referenciales de la fuente. Los objetivos específicos son sustentar la demanda; definir el corredor y los apoyos; comprobar el comportamiento eléctrico y mecánico; seleccionar transformación y protección; y vincular los resultados con los planos, los metrados y el presupuesto.

### 1.3 Frontera del sistema y exclusiones

La frontera inicial se sitúa en la generación BT de la minicentral y la final en el tablero BT de la SE-HUA. Se estudian T1 y T2 y la línea MT; las redes de usuarios posteriores y las obras hidráulicas pertenecen a proyectos distintos. El esquema no conecta el sistema al SEIN. La línea puede transportar 250 kVA de estudio; esa capacidad no constituye potencia firme de la fuente.

### 1.4 Organización del estudio

La memoria se organiza desde los antecedentes y la demanda hasta el diseño eléctrico, la mecánica de la línea, las protecciones, la normativa y la evaluación económica. La memoria de cálculo desarrolla el modelo y las tablas completas; los planos y anexos permiten localizar cada apoyo y reconocer sus componentes.

### 1.5 Condición de los antecedentes

Se conservan originales y la versión previa como antecedentes. Las decisiones están abiertas a verificación de campo. No se atribuyen aprobaciones, servidumbres, mediciones topográficas, cotizaciones o certificados inexistentes.



## 2. Antecedentes y bases del replanteamiento

### 2.1 Antecedente de electrificación

Los documentos recibidos describían una propuesta de distribución interna en Limbani, con tres subestaciones de 50, 100 y 100 kVA. Ese antecedente aporta referencias de equipos y emplazamiento, pero no resuelve el transporte solicitado a Huancasayani. El presente diseño reemplaza ese alcance por una línea entre dos estaciones; los metrados urbanos anteriores no se incorporan al presupuesto de la línea.

### 2.2 Documentación utilizada

Se revisaron el expediente anterior, su CAD, el catastro aportado y el proyecto QGIS de Limbani. Estos archivos se conservan como antecedentes y se contrastan con el directorio de centros poblados del INEI, las vías y cauces de Open Street Map y un modelo digital de elevaciones público. El registro de fuentes identifica procedencia, fecha, sistema de referencia y limitaciones.

### 2.3 Características referenciales de la fuente

La central existente se toma como antecedente aportado: aproximadamente 200 kW, generación 380 V, 60 Hz y turbina Michell-Banki; no se localizaron placas/acta de inspección que certifiquen esa configuración. La transformación previa 0.38/10 kV y 250 kVA también es referencia sin placa comprobada. SE-HUA es proyectada, no instalación existente confirmada.

### 2.4 Relación con el estudio hidroeléctrico

El estudio hidroeléctrico R03 evaluó otro replanteamiento de mayor potencia con supuestos hidráulicos condicionados. No se incorporan automáticamente su alternativa 600 kW ni su potencia de estiaje. La oferta firme de esta central existente sigue pendiente de aforos/curvas/equipos y del suministro actual a Limbani. La demanda del presente trabajo comprende Huancasayani y no suma habitantes de Limbani.

### 2.5 Criterio de transformación

Se propone suministrar o adecuar dos transformadores de 250 kVA. El presupuesto conservador considera dos equipos nuevos; una reutilización sólo podrá descontarse después de comprobar estado, relación, grupo, impedancia y capacidad a altitud.



## 3. Emplazamiento y trazado de gabinete

### 3.1 Emplazamiento de salida y sistema de referencia

El ámbito es Limbani–Huancasayani, provincia de Sandia, departamento de Puno. Sistema horizontal: WGS 84/UTM zona 19 Sur, EPSG:32719, metros. SE-LIM propuesta: E 425715.00, N 8436650.00, tomada del CAD previo. Existe otra referencia de memoria E 425580, N 8436580, distante unos 152 m; se conserva la discrepancia, sin resolverla mediante coordenadas del centro urbano.

### 3.2 Emplazamiento de llegada

SE-HUA propuesta: E423 945.21, N8 430 951.88, correspondiente al nodo OSM de Huancasayani Centro (lat-14.1917532, lon-69.7048438). Es referencia de la localidad y no ubicación verificada de predio/subestación. El plano lo indica expresamente. La restitución/captación hidroeléctrica no es objeto del trazado eléctrico.

### 3.3 Procedimiento de trazado

La consulta OSM del 14 de octubre de 2026 se archivó íntegra. Se construyó el grafo vial y se obtuvo un camino mínimo de 6 998.88 m. Se compararon desplazamientos de±20 m respecto de la vía; el corredor elegido usa-20 m, simplificación 8 m y desvíos alrededor de edificios del catastro. El eje eléctrico resultante mide 6 696.37 m; la diferencia responde a geometría de gabinete, no a una medición vial oficial.

### 3.4 Restricciones del corredor

El desplazamiento de 20 m no define servidumbre ni faja marginal. La búsqueda evita sobrevolar los polígonos de casas disponibles con una separación de estudio cercana a 4 m. Se usaron 8 m de separación a ejes cartográficos de agua para alertas y 30 m como cautela; ninguno es un ancho legal ANA. Un cauce representado por eje no permite conocer bordes, inundación ni socavación.

### 3.5 Inventario de apoyos y vanos

Hay 111 postes proyectados, P001–P111;110 vanos, V001–V110;64 cantones de retención y 128 retenidas independientes por ramal. Se eliminaron dos apoyos casi coincidentes manteniendo distancia a edificios y longitud admisible de los vanos. No se presentan postes observados en campo.

### 3.6 Cotas y precisión topográfica

Cotas de terreno obtenidas por interpolación bilineal de HGT público de~30 m: mínimo 3 235.3 y máximo 3 771.4 m. Datum vertical/composición de tesela pendientes. El DEM puede omitir taludes, techos, árboles y crecidas: no acredita distancias de seguridad reales. Se requieren levantamiento RTK/estación total, perfiles, cruces, predios y geotecnia.



## 4. Población y demanda de Huancasayani

### 4.1 Localidades comprendidas

El INEI 2017 registra Huancasayani Centro (2112030050), Bellavista (2112030051) y Lince (2112030036). El escenario agrega estas tres localidades, sin sumar la población del distrito ni Limbani. La variante Huancasarani de OSM no reemplaza la identificación censal.

### 4.2 Proyección de usuarios

La base censal reúne 549 habitantes y 321 viviendas ocupadas. Con crecimiento geométrico supuesto de 1 % anual durante nueve años, la población alcanza aproximadamente 600 habitantes en 2026. Al redondear las viviendas por localidad se estiman 353 usuarios potenciales; son una proyección, no un padrón de abonados.

### 4.3 Calificación y simultaneidad

Para estimar la demanda se adopta provisionalmente RD 108-2023: categoría I, 600 W por usuario, en Centro y Bellavista; categoría II, 400 W, en Lince; simultaneidad 0.80. La categoría requiere comprobación. El alumbrado considera 60 luminarias de 54.1 W de entrada y 14 kW de servicios supuestos.

### 4.4 Composición de la demanda

El resultado es 154.24 kW domésticos, 3.246 kW de alumbrado y 14.00 kW de servicios: 171.49 kW y 190.54 kVA con factor de potencia 0.90. Los servicios comprenden salud (3 kW), educación y comunicaciones (3 kW), bombeo (3 kW), comercio y talleres (4 kW) y usos comunales (1 kW).

### 4.5 Frontera del abastecimiento

La llegada en Centro no demuestra que Bellavista y Lince dispongan de redes posteriores. Esas obras corresponden a otro proyecto. Se evalúa crecimiento de usuarios de 1 % y 1.5 % anual como sensibilidad, sin garantizar consumo futuro.

### 4.6 Perfil horario de estudio

El perfil supuesto utiliza fracciones de la demanda máxima: 0.30 en carga baja, 0.55 en la mañana, 0.60 al mediodía, 0.65 por la tarde y 1.00 en el pico nocturno. No es una curva medida. Las pérdidas se calculan al pico; se agregan 5 kW de auxiliares sin duplicarlos como servicios de usuarios.



## 5. Diseño eléctrico y tensión

### 5.1 Nivel de tensión

Se selecciona para el escenario principal 10 kV, trifásico 3 hilos, 60 Hz, por compatibilidad condicionada con el antecedente 0.38/10 kV. No se ha comprobado esa relación. Antes de ejecutar deberá cotejarse íntegramente RD 018 y la tensión admitida para el régimen rural; si se trata de infraestructura nueva estandarizada, 22.9 kV merece evaluación preferente. No se declara que RD 018 autoriza 10 kV basándose sólo en su ficha.

### 5.2 Selección del conductor

Se propone conductor AAAC 6201-T81 nominal 50 mm². Datos tipo: sección real 49.5 mm², diámetro 9 mm, masa 135 kg/km, R20=0.671 Ω/km, RTS 14.7 kN, E62 GPa, alfa térmica 23 µm/(m·°C). Son especificación académica y deben sustituirse por una ficha contractual. Se compara 35/50/70 mm²;50 ofrece menores pérdidas que 35 y reserva mecánica razonable. La sección mínima aplicable requiere cotejo del texto normativo correspondiente.

### 5.3 Parámetros eléctricos de la línea

Resistencia de línea a 75°C: 5.3829 Ω/fase; reactancia 3.0632 Ω/fase, derivada de fases separadas 1.2/1.2/2.4 m, Dmg 1.5119 m y GMR 0.003505 m. Se distinguen longitud horizontal UTM y longitud tridimensional del conductor para compra.

### 5.4 Flujo de carga

El flujo de carga PQ equilibrado incluye ambos transformadores, la línea y vacío supuesto 0.45 kW+2.5 kvar por transformador. Se adopta elevación efectiva de toma+5% en T1, sujeta a fabricante y operación sin carga. Resultado: MT salida 10.182 kV, MT llegada 10.060 kV y BT371.1 V (-2.34% respecto de 380 V), antes de circuitos de usuarios. La toma es una decisión de estudio, no ajuste autorizado de un equipo existente.

### 5.5 Corriente, caída de tensión y pérdidas

Corriente de transporte al pico 11.35 A; corriente nominal a 250 kVA/10 kV14.43 A. Caída en línea 1.20% y pérdida 2.08 kW. Un límite de 5% en línea es objetivo de estudio, sin atribuirlo a un artículo de RD 018 no consultado. La calidad de tensión debe evaluarse en puntos de entrega y con la regulación de la generación.

### 5.6 Comprobación térmica

Balance térmico simplificado por convección/radiación/sol entrega 92.4 A a 75°C con h=5 W/(m²K), emisividad/absorptividad 0.5, ambiente 30°C y 1000 W/m². Es sensibilidad de gabinete, no ampacidad garantizada a altitud. El requerimiento es14.44 A; se necesita ficha de proveedor y ambiente real.

### 5.7 Transformadores y estaciones

T1 y T2:250 kVA de capacidad neta garantizada en el emplazamiento, uk6%, P0=0.45 kW y Pcu=3.1 kW propuestos, Dyn 11 para ATdelta/BTestrella-neutro. El reloj es selección de estudio y debe armonizarse con placas y diferencial. SE de piso cercada, plataforma 6×4 m, para evitar asumir capacidad de subestación aérea pesada sin pesos/cargas.

### 5.8 Conductores y tableros internos de baja tensión

BT interno de cada SE:20 m, dos conductores Cu 240 mm² en paralelo por fase, un neutro Cu 240 y PE35 mm², tablero 400 A con capacidad de uso a altitud. Se exige ampacidad conjunta≥400 A en disposición final; iguales material/sección/longitud y conexiones equilibradas por circuito paralelo. Sección es decisión robusta de estudio; agrupamiento, aislamiento, terminales y corrección de altitud necesitan ficha. Se excluyen ramales de usuarios.



## 6. Oferta de generación, crecimiento y operación aislada

### 6.1 Balance entre demanda y generación

La demanda 171.49 kW requiere en el modelo 183.31 kW y 212.45 kVA en generación incluyendo auxiliares. La referencia de 200 kW deja sólo 16.69 kW para otros destinos. Con 25 kW reservados a Limbani, el requerimiento supera 200 kW. La capacidad 250 kVA de línea/transformadores no resuelve ese déficit.

### 6.2 Alternativas ante déficit de potencia

Se debe comprobar demanda actual de Limbani, potencia neta estacional, estado de equipos y derechos de agua. Hasta entonces, el abastecimiento completo no se considera garantizado. Son opciones: ejecución por etapas con padrón menor; gestión de usos productivos/picos; respaldo despachable; ampliación de generación si el recurso lo sustenta; selección de una fuente alternativa. No se asigna una potencia artificial para cerrar el balance.

### 6.3 Operación en estiaje

En estiaje, el despacho debe limitar la carga a potencia hídrica disponible menos pérdidas y auxiliares; prever desconexión escalonada de usos no críticos, arranque secuencial de bombas, medición, y reserva para salud/comunicaciones. AVR y regulación de velocidad/frecuencia pertenecen a la central y su interfaz se debe verificar. No se confía en potencia nominal constante.

### 6.4 Adaptación futura al SEIN

La llegada puede funcionar sin SEIN. Una adaptación futura requiere estudio con empresa distribuidora/COES según régimen, flujo y cortocircuito, sincronismo 25, antiisla, protecciones direccionales, medición y requisitos del operador. La clase 24 kV no constituye compatibilidad automática con toda tensión ni conexión aprobada.

### 6.5 Crecimiento de la demanda

La proyección a 20 años con 1.5% alcanza más de 250 kVA sólo en usuarios; pérdidas y auxiliares hacen que la fuente requiera reforzarse antes. No se cambia ahora el proyecto por una futura interconexión hipotética.



## 7. Mecánica, estructuras y seguridad del trazado

### 7.1 Modelo de catenaria

Se calcula catenaria en el plano de la carga resultante, con desnivel real de cada par de apoyos según DEM. En cada cantón se conserva longitud sin tensión, considerando deformación elástica lineal, temperatura y fluencia de sensibilidad 345 µε. Se usa HEDS=15%RTS=2205 N a 15°C. El modelo admite apoyos inclinados; no sustituye curva tensión-deformación del conductor ni reparto real con movimiento de cadenas.

### 7.2 Estados climáticos

CNE 250-1 B, área 1(3000–4000 m): viento 29 m/s a 5°C; hielo 6 mm a 0°C; combinación 14.5 m/s y 3 mm a 0°C. Densidad hielo 913 kg/m³. Por altitud se usa K=.455 para presión eólica P=K·V²·Sf·A, Sf1 conductor redondo. Estados adicionales: frío-5°C y conductor 75°C con fluencia, ambos de sensibilidad. No son series meteorológicas.

### 7.3 Factores de carga y resistencia

Para revisión conservadora se adopta grado B de estudio y se extienden factores 253-1: vertical 1.50, viento 2.50, tensión 1.65, incluso a casos donde 250.C permite 1.0; esta extensión es decisión conservadora, no obligación general del CNE. Tabla 261-1 A: CAC no pretensado 0.65 bajo 250.B; retenida 0.90. El poste tipo 600 da N se supone con rotura 2×trabajo; esa relación exige certificado y no proviene de una medición local.

### 7.4 Resultados mecánicos

Resultados: máximo T/RTS=27.7%; máximo uso de flexión del poste tipo 61.6%. Compresión/vertical de estudio máxima 60.8 kN: el fabricante debe acreditar capacidad axial y combinación con flexión, no basta comprobar 600 da N transversal.

### 7.5 Funciones de las estructuras

Vano máximo 82.7 m; cantón máximo 476.5 m. Suspensión≤5°,ángulo 5–30° con retención, anclaje>30° y terminales. P003, P035, P057 superan 90° y se identifican ESP-RET: dos retenciones independientes y puentes, por diseño especial de fabricante. No se atribuyen a láminas 012/016, cuyos rangos no cubren esos ángulos. Exigen verificar herrajes y separación de fases o replantear el corredor.

### 7.6 Alturas y empotramiento de postes

Postes CAC 13 m:72;15 m:30;17 m:9. Altura de amarre 10.6/12.4/14.2 m. Empotramiento inicial 1.9/2.1 m propuesto, por verificar con suelo/fabricante. Los apoyos mayores responden al perfil modelado y aparecen en todos los cuadros.

### 7.7 Retenidas y anclajes

Cada retención dispone de anclajes longitudinales independientes por ramal, 45° vertical de estudio y resistencia de rotura mínima 60 kN. Se comprueba tiro de tres fases por ramal bajo factor 1.65 y componente vertical. La geometría del anclaje es esquemática y puede invadir predios/cauces; deberá ajustarse y recalcularse. Bloque 1.2 m cúbico es provisión de presupuesto, no cimentación verificada.

### 7.8 Distancias respecto al terreno

Margen mínimo frente al DEM en estados analizados:7.54 m. Se toma 7.5 m como margen de estudio respecto del mínimo 7 m de 232-1 en cruces viales de conductores desnudos MT≤23 kV; otros escenarios/cauces/obstáculos aplican reglas propias. La Tabla 232-1 a de 50–60 kV no se aplica a 10 kV. Techos/árboles/vehículos/inundación y balanceo transversal requieren campo.

### 7.9 Cruces de cauces

Cruces de agua se identifican por intersección OSM y se listan en vanos.csv. Ejes de agua incompletos y DEM no bastan para despejar crecidas, taludes o fajas. No se aprueba ningún cruce por tener separación cartográfica 8 m.



## 8. Cortocircuito, protección y puesta a tierra

### 8.1 Modelo de cortocircuito

Se estudia una fuente síncrona aislada 250 kVA. Hipótesis de reactancias xd″=.20, xd′=.30, xd=1.80 pu y ra=.02 pu, sumando impedancias de T1, línea y T2 según punto. Se calcula falla trifásica simétrica por Vfase/|Z|; sin aporte de motores ni tolerancias/corrección de tensión. No es un cortocircuito del SEIN ni ajuste final IEC 60909.

### 8.2 Falla mínima y criterio de detección

En llegada MT: Ik3 subtransitoria 53.4 A y sostenida 7.73 A. Esta última puede quedar por debajo de la corriente de carga. Fusibles y 50/51 sin supervisión de tensión pueden no despejarla; se incorporan 51 V, protección diferencial de transformador y protección de tierra sensible.

### 8.3 Protecciones y tiempos orientativos

Q1/Q2:interruptores MT, TC25/5 o 25/1 de clase/VA por comprobar, 50/51 y 51 V, 87 T por transformador, 59 N/64 con detección homopolar. Propuesta orientativa 51 V: corriente primaria de arranque 5 A si U<.70 pu, tiempo 0.60 s cabeza; llegada BT100 A con U<.70 pu y 0.20 s; respaldo generador 0.90 s. No son ajustes aprobados: arranque, AVR, saturación TC, corrientes decrecientes, poder de corte y coordinación necesitan curvas reales.

### 8.4 Control y alimentación de disparo

La lámina LP-E03 identifica control/medición, órdenes de disparo y conexión funcional MT→zigzag→neutro→NGR→malla. No sustituye planos de bornes/cableado. Exige alimentación DC respaldada para disparar cuando cae la tensión. Energizar inicialmente sin carga y comprobar inrush de ambos transformador; evaluar excitación progresiva con AVR y supervisión de frecuencia, sin bloquear indiscriminadamente las protecciones.

### 8.5 Puesta a tierra del sistema de media tensión

Para MTdelta se propone zigzag y resistencia de neutro en SE-LIM:5 A/10 s, R≈1155 Ω, energía térmica≈289 k J. Capacitancia supuesta 7 n F/km/fase da corriente capacitiva total~0.306 A; debe medirse/calcularse con geometría y accesorios. CBCT/59 N y control del NGR deben detectar tierra; el valor 5 A no es norma universal ni estudio definitivo de secuencia cero.

### 8.6 Puesta a tierra de masas

Puesta a tierra de SE: malla 10×10 m, cuatro líneas por dirección, paso 3.33 m, profundidad 0.6 m, Cu 35 mm² y cuatro varillas 2.4 m/16 mm. PAT de poste: dos varillas y enlace Cu 25 mm², sin neutro continuo MT. Equipotencialidad, cercos, descargadores y pantallas deben verificarse frente a paso/contacto/transferencia, CNE 036.

### 8.7 Sensibilidad a la resistividad

Una varilla 2.4 m/16 mm tiene R aproximada ρ/(2πL)[ln(4 L/d)-1]; paraρ100/300/1000 Ω·m resultan~35.8/107.3/357.9 Ω. Dos varillas no equivalen automáticamente a R/2 por resistencia mutua. Se adjunta sensibilidad de malla; no se promete 25 Ω ni seguridad por resistencia baja aislada.

### 8.8 Conductores de tierra y seguridad

Cu 35 mm² de malla y PE se proponen por robustez mecánica/corrosión y margen térmico. Verificar ensayo de resistividad, corriente realmente inyectada a terreno, tiempo de despeje, factor de reparto y tensiones admisibles. Bajo NGR 5 A y resistencia provisional, contacto transferido puede dominar aun con falla limitada.

### 8.9 Aislamiento y sobretensiones

Descargadores Zn O y aisladores requieren coordinación con tensión máxima a tierra durante falla, resistencia NGR, contaminación y altitud. Se propone clase 24 kV de equipos para 10 kV, pero 125 kV de impulso no se considera garantía en sitio sin proveedor. No se reproduce el factor de altitud 1.28 del expediente anterior sin sustento.



## 9. Normativa verificada y ruta de ejecución real

### 9.1 Código Nacional de Electricidad

El CNE Suministro 2011 se aprobó por RM 214-2011-MEM/DM. Rige la seguridad de la línea y estaciones según su ámbito. CNE Utilización RM 037-2006 con modificatoria 175-2008 se aplica a instalaciones de utilización/auxiliares BT. Una lista de títulos no es certificación de cumplimiento; la matriz identifica reglas efectivamente consultadas y controles pendientes.

### 9.2 Disposiciones DGE

RD 024 corresponde a soportes primarios; RD 023 es secundaria y se retira de la base activa. RD 108-2023 es secundaria, sólo usada para demanda. RD 018 es referencia primaria con descarga oficial no recuperada; se conserva la limitación y no se atribuyen su sección mínima, caída máxima, tensión o puesta a tierra sin cotejo del texto. Proyectos de norma prepublicados no se tratan como normas aprobadas.

### 9.3 Electrificación rural

Ley 28749 y Reglamento DS 018-2020 deben consultarse con modificaciones. Se verificó DS 003-2026-EM, publicado 25/04/2026: su artículo 3 modifica, entre otros, artículos 51.1 c/51.2 f sobre requisito ambiental cuando corresponde. No se infiere de ello exoneración automática para esta línea. Su régimen requiere confirmar calificación SER, titularidad y concesión eléctrica rural aplicable.

### 9.4 Ruta de autorizaciones

Ejecución real: acreditar titular, origen autorizado de energía y derechos sobre equipos; elegir régimen LCE/SER; gestionar concesión/autorización que corresponda a actividades e instalaciones; resolver derechos de predios y servidumbres; determinar instrumento ambiental eléctrico/SEIA; coordinar ANA en cauces/fajas si hay interferencia; tramitar cruces viales y afectaciones municipales; evaluación de patrimonio cultural cuando corresponda; proyecto y firma profesional, revisión de seguridad, pruebas y operación. Estos trámites no se consideran obtenidos.

### 9.5 Obras civiles y seguridad laboral

Para obras de SE y cimentaciones se seleccionarán versiones aplicables RNE E.020, E.030, E.050, E.060 y seguridad RESESATE 2013/legislación SST. No se dimensionan edificios sismorresistentes ni fundaciones con datos ficticios. La LP no modifica derechos de uso de agua de la central; éstos deben verificarse separadamente.

### 9.6 Complementos internacionales

IEC 60076-1:2011 y 60076-3:2013+AMD 1:2018 se proponen como complemento de especificación y ensayos de transformadores/aislamiento cuando el criterio no está desarrollado en el documento nacional. Se consultaron fichas IEC, no textos de pago íntegros: no se atribuyen cláusulas ni resultados certificados. La edición contractual y sus disposiciones se deben cotejar al adquirir los equipos.



## 10. Metrados, presupuesto y viabilidad

### 10.1 Origen de las cantidades

Cantidades provienen del eje y tablas: 111 postes, 110 vanos, 128 retenidas, dos SE de 250 kVA. Conductor: suma de longitudes de catenarias EDS por fase×3, más 3%reserva: 20 883 m a comprar. No se multiplica la longitud horizontal por tres ignorando desnivel/flecha.

### 10.2 Partidas consideradas

Se incluyen armados por función, PAT por poste, dos transformadores, celdas, NGR/zigzag, mallas, tableros/cables BT internos, descargadores/control, plataformas/cercos, pruebas, gestión y campo. Provisión civil no garantiza bloque/fundación: cantidades se identifican como geométricas provisionales y deben cambiar con geotecnia.

### 10.3 Precios y fecha de referencia

Todos los precios son estimaciones PEN al14 de octubre de 2026. El catálogo público Nexans no ofrece precios verificables del producto/tamaño para este sitio; no se hallaron ofertas específicas de equipos garantizados a 3772 m. No se presentan los valores como cotizaciones. Transporte extraordinario 12%, ingeniería 8%, contingencia 20% e IGV 18% se explicitan; precios de poste incluyen montaje y no se añade otra partida general de montaje.

### 10.4 Inversión y sensibilidad

Orden de magnitud: directo S/2 020 021; inversión con logística/ingeniería/contingencia e IGV S/3 432 420. Rango de sensibilidad-25/+40%: S/2 574 315 a S/4 805 389. No incluye generación/reforzamiento hídrico ni distribución posterior en Huancasayani ni tasación definitiva de compensaciones.

### 10.5 Alcance de la viabilidad

Viabilidad de transporte eléctrico: favorable bajo hipótesis de equipos, tensión y terreno, por corriente y caída reducidas. Viabilidad de abastecimiento continuo: no acreditada, por oferta real, estiaje y reserva Limbani. Viabilidad económica integral: indeterminada sin energía firme/padrón/tarifa/cotizaciones. No se calcula un VAN/TIR de apariencia precisa sobre datos faltantes.



## 11. Planos, QGIS y control de coherencia

### 11.1 Planos y armados vectoriales

La entrega incorpora 19 planos A3, incluidos siete perfiles longitudinales ampliados con identificadores, longitudes, alturas de amarre, flechas y separación respecto al DEM. El anexo añade 23 hojas de armados y componentes exportadas del CAD como PDF vectorial, con sus vistas, cotas, tablas y rótulos completos. La conversión utiliza Potrace sobre las copias normativas y conserva los PDF originales para contraste; no es un redibujo por IA ni un CAD emitido por MINEM. La adaptación de las variantes de madera y de sujeción PIN a las estructuras CAC estudiadas requiere diseño específico.

### 11.2 Visualización en Google Earth

El archivo KMZ permite consultar 111 postes y 110 vanos, sus fichas y los perfiles de cada tramo. Incluye 208 curvas derivadas del DEM, con equidistancia de 20 m y curvas principales cada 100 m, relieve sombreado y recorrido en tres dimensiones. La resolución aproximada de 30 m del DEM limita esta representación: la equidistancia no equivale a exactitud vertical. Las alturas relativas al terreno de Google Earth y las cotas absolutas del DEM se muestran como modos distintos y no acreditan un levantamiento de campo.

### 11.3 Unidades y simbología del CAD

El DXF R2018 utiliza unidades en metros en espacio modelo y UTM zona 19 Sur. Sus bloques de poste representan siempre el círculo CAC de DGE 09-91-20; función S/A/AN/T/ESP mediante atributos y rótulo. Se emplean 09-91-18 para retenida inclinada, 03-31-44 para tierra y 09-90-09 para SE en proyección. Geometría de bloque corresponde al poste; el desplazamiento del rótulo es sólo anotación.

### 11.4 Contenido de los planos

El CAD incluye láminas A3: ubicación general, plantas/perfiles por~1 km con cuadrícula UTM y tabla de apoyos, unifilar, estructuras y puesta a tierra/SE. En planta se dibuja UN solo eje con leyenda 3×AAAC 50 mm², según 09-91-03 y 04-40-01/03; las tres fases físicas se muestran en detalles de estructuras. Escalas de planta y perfil son explícitas; esquemas eléctricos/constructivos sin escala. PDF renderizado de las propias láminas CAD.

### 11.5 QGIS y control de coherencia

QGIS reúne copias del catastro original, el eje, los vanos, los postes, las retenidas, las subestaciones, las referencias OSM, el DEM y las curvas derivadas. Sus 13 capas se guardan con rutas relativas y se verifican al reabrir una copia del paquete. Los identificadores, las coordenadas y las longitudes proceden de una fuente de resultados común al CAD, las tablas y los metrados. Se conservan los archivos originales con sus hashes. Los 53 controles de coherencia de la entrega comprueban esa concordancia documental y la ausencia de imágenes raster en el anexo de armados; no certifican topografía ni calidad de montaje.



## 12. Conclusiones y comprobaciones posteriores

### 12.1 Resultado del diseño de la línea

La corrección efectiva transforma el proyecto urbano previo en una línea troncal independiente a Huancasayani: 6.696 km, AAAC 50 mm², 10 kV condicionado a compatibilidad, 111 postes, 110 vanos y dos transformaciones 250 kVA propuestas. El documento, los cálculos y los gráficos comparten fuente única.

### 12.2 Balance de abastecimiento

Demanda 2026:171.49 kW para 353 usuarios potenciales. El flujo PQ con toma de estudio+5% entrega~371.1 V en llegada y exige 183.31 kW. Por ello, 200 kW de referencia no bastan para Huancasayani y 25 kW adicionales de Limbani; estiaje puede reducir más la oferta.

### 12.3 Protección y seguridad

La fuente aislada obliga a considerar corriente de falla decreciente y protección 51 V/diferencial/tierra. Las tablas de flexión/tensión y margen DEM son comprobaciones de estudio; no sustituyen certificados de postes/retenciones, perfiles de campo y condiciones de paso/contacto.

### 12.4 Comprobaciones prioritarias

Prioridad de campo: identificar con certeza CM/SE salida y predio SE llegada; placas/tensión/impedancias/AVR; padrón y curva de Huancasayani; demanda Limbani y potencia estacional; topografía con cruces/techos/cauces; geotecnia y resistividad; cotejo completo RD 018 y régimen; fichas/ofertas y ajustes deprotección. Estas comprobaciones delimitan el trabajo posterior a la presentación académica.

### 12.5 Actualización con datos de campo

La implementación posterior deberá recalcular eje, postes, pérdidas/flujo, cortocircuito y presupuesto cuando cambien datos de campo. Si no se acredita fuente suficiente, se debe reducir etapa de usuarios o reforzar generación/respaldo; no declarar la línea como garantía de 200 kW permanentes.

