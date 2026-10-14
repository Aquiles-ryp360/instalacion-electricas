# Proyecto académico de línea primaria Limbani–Huancasayani

Estudiante: Aquiles Taylor Ramos Yapo ·227368

Curso: Instalaciones Eléctricas II ·LP-R01


## 1. Enfoque, objetivos y límites

Se desarrolla un proyecto académico de diseño de una línea primaria que transporta energía desde la transformación de salida asociada a la minicentral de Limbani hasta una subestación de llegada en Huancasayani. El curso pidió línea primaria; se elimina del alcance activo la distribución entre barrios y lotes urbanos de Limbani.

Objetivo general: definir y comprobar una solución de transporte eléctrico aislado, con trazado, selección de conductor, apoyos, transformación, protección y presupuesto compatibles. Objetivos específicos: fundamentar la demanda; documentar fuentes y coordenadas; calcular comportamiento eléctrico y mecánico; producir CAD editable y QGIS con identificadores únicos; identificar verificaciones necesarias para ejecutar.

La frontera inicial se sitúa en la generación BT de la minicentral y la final en el tablero BT de la SE-HUA. Se estudian T1 y T2 y la línea MT; las redes de usuarios posteriores y las obras hidráulicas pertenecen a proyectos distintos. El esquema no conecta el sistema al SEIN. La línea puede transportar 250 kVA de estudio; esa capacidad no constituye potencia firme de la fuente.

El docente de Instalaciones Eléctricas II no está identificado en los archivos revisados. Se mantiene pendiente, sin trasladar el nombre/grado del curso de Centrales Hidroeléctricas. Autor/estudiante: Aquiles Taylor Ramos Yapo, 227368.

Se conservan originales y la versión previa como antecedentes. Las decisiones están abiertas a verificación de campo. No se atribuyen aprobaciones, servidumbres, mediciones topográficas, cotizaciones o certificados inexistentes.


## 2. Auditoría y relación con la minicentral

El expediente previo presentaba tres SED de50/100/100 kVA y redes secundarias para 764 supuestos lotes de Limbani. No representaba la conexión solicitada a Huancasayani. Además, mezclaba longitudes 2.15 km y1.967 km, citaba erróneamente RM 366-2011 para el CNE y reutilizaba RD 023 de soportes secundarios como referencia primaria.

La carpeta activa encontrada es G:/Aquiles/instalacion-electricas/proyectos/aquiles-limbani-redes. En Descargas existe una copia del repositorio y Catastro_Limbani con QGIS/CAD/expediente. No se encontró una carpeta literal denominada Instalaciones Eléctricas Proyectos. El equivalente localizado se documenta sin suponer una ruta inexistente.

La central existente se toma como antecedente aportado: aproximadamente 200 kW, generación 380 V, 60 Hz y turbina Michell-Banki; no se localizaron placas/acta de inspección que certifiquen esa configuración. La transformación previa 0.38/10 kV y250 kVA también es referencia sin placa comprobada. SE-HUA es proyectada, no instalación existente confirmada.

El estudio hidroeléctrico R03 evaluó otro replanteamiento de mayor potencia con supuestos hidráulicos condicionados. No se incorporan automáticamente su alternativa 600 kW ni su potencia de estiaje. La oferta firme de esta central existente sigue pendiente de aforos/curvas/equipos y del suministro actual a Limbani. La demanda del presente trabajo comprende Huancasayani y no suma habitantes de Limbani.

Se propone suministrar o adecuar dos transformadores de250 kVA. El presupuesto conservador considera dos equipos nuevos; una reutilización sólo podrá descontarse después de comprobar estado, relación, grupo, impedancia y capacidad a altitud.


## 3. Emplazamiento y trazado de gabinete

El ámbito es Limbani–Huancasayani, provincia de Sandia, departamento de Puno. Sistema horizontal: WGS 84/UTM 19 Sur, EPSG:32719, metros. SE-LIM propuesta: E 425715.00, N 8436650.00, tomada del CAD previo. Existe otra referencia de memoria E 425580, N 8436580, distante unos 152 m; se conserva la discrepancia, sin resolverla mediante coordenadas del centro urbano.

SE-HUA propuesta: E423 945.21, N8 430 951.88, correspondiente al nodo OSM de Huancasayani Centro (lat-14.1917532, lon-69.7048438). Es referencia de la localidad y no ubicación verificada de predio/subestación. El plano lo indica expresamente. La restitución/captación hidroeléctrica no es objeto del trazado eléctrico.

La consulta OSM del 14/10/2026 se archivó íntegra. Se construyó el grafo vial y se obtuvo un camino mínimo de6 998.88 m. Se compararon desplazamientos de±20 m respecto de la vía; el corredor elegido usa-20 m, simplificación 8 m y desvíos alrededor de edificios del catastro. El eje eléctrico resultante mide 6 696.37 m; la diferencia responde a geometría de gabinete, no a una medición vial oficial.

El desplazamiento de20 m no define servidumbre ni faja marginal. La búsqueda evita sobrevolar los polígonos de casas disponibles con una separación de estudio cercana a4 m. Se usaron 8 m de separación a ejes cartográficos de agua para alertas y30 m como cautela; ninguno es un ancho legal ANA. Un cauce representado por eje no permite conocer bordes, inundación ni socavación.

Hay 111 postes proyectados, P001–P111;110 vanos, V001–V110;64 cantones de retención y128 retenidas independientes por ramal. Se eliminaron dos apoyos casi coincidentes manteniendo distancia a edificios y longitud admisible de los vanos. No se presentan postes observados en campo.

Cotas de terreno obtenidas por interpolación bilineal de HGT público de~30 m: mínimo 3 235.3 y máximo 3 771.4 m. Datum vertical/composición de tesela pendientes. El DEM puede omitir taludes, techos, árboles y crecidas: no acredita distancias de seguridad reales. Se requieren levantamiento RTK/estación total, perfiles, cruces, predios y geotecnia.


## 4. Población y demanda de Huancasayani

INEI 2017 distingue Huancasayani Centro 2112030050, Bellavista 2112030051 y Lince 2112030036 como registros de centros poblados del distrito. Se agregan exclusivamente estas tres denominaciones para el escenario de servicio; no se usa la población de todo el distrito ni se suma nuevamente Limbani. OSM también rotula Huancasarani cerca de Centro; esa etiqueta no sustituye el código INEI.

Base 2017:549 habitantes y321 viviendas ocupadas. Crecimiento geométrico supuesto 1% anual durante 9 años; población 2026 proyectada por registro: 600 habitantes. Los usuarios potenciales se redondean hacia arriba por localidad: 353. Vivienda ocupada no es abonado activo; el padrón comercial sigue pendiente. No se obtuvo tabla de centros poblados 2025 para este ámbito.

La RD 108-2023 es secundaria y se emplea únicamente para estimar demanda a transportar. Centro/Bellavista se asignan provisionalmente tipo I600 W y Lince tipo II400 W, con simultaneidad 0.80. La categoría requiere justificación de campo; no se afirma clasificación oficial. AP:60 luminarias 54.1 W y servicios 14 kW son supuestos de inventario.

Demanda doméstica 154.24 kW; alumbrado 3.246 kW; servicios 14.00 kW. Total usuarios 171.49 kW, fp0.90 y190.54 kVA. Los 14 kW representan salud 3, educación/comunicaciones 3, bombeo 3, comercio/talleres 4 y comunales 1; son demandas coincidentes de estudio, sin otro factor para ocultar el pico.

Una sola llegada en Centro no demuestra que Bellavista y Lince puedan recibir energía sin obras posteriores. La demanda agregada justifica infraestructura troncal; las redes aguas abajo requieren proyecto e inversión separados. Se incluyen escenarios de crecimiento 1% y1.5%, no garantía de consumo futuro.

Perfil horario para exposición: demanda baja 0.30 Pmax, mañana 0.55, mediodía 0.60, tarde 0.65 y pico nocturno 1.00. Es un escenario, no curva medida; no se calcula facturación ni energía garantizada con él. Pérdidas se calculan al pico; auxiliares centrales 5 kW son hipótesis y no se suman nuevamente a los servicios de Huancasayani.


## 5. Diseño eléctrico y tensión

Se selecciona para el escenario principal 10 kV, trifásico 3 hilos, 60 Hz, por compatibilidad condicionada con el antecedente 0.38/10 kV. No se ha comprobado esa relación. Antes de ejecutar deberá cotejarse íntegramente RD 018 y la tensión admitida para el régimen rural; si se trata de infraestructura nueva estandarizada, 22.9 kV merece evaluación preferente. No se declara que RD 018 autoriza 10 kV basándose sólo en su ficha.

Se propone conductor AAAC 6201-T81 nominal 50 mm². Datos tipo: sección real 49.5 mm², diámetro 9 mm, masa 135 kg/km, R20=0.671 ohm/km, RTS 14.7 kN, E62 GPa, alfa térmica 23 µm/(m·°C). Son especificación académica y deben sustituirse por una ficha contractual. Se compara 35/50/70 mm²;50 ofrece menores pérdidas que 35 y reserva mecánica razonable. No se inventa una sección mínima DGER.

Resistencia de línea a75°C: 5.3829 ohm/fase; reactancia 3.0632 ohm/fase, derivada de fases separadas 1.2/1.2/2.4 m, Dmg 1.5119 m y GMR 0.003505 m. Se distinguen longitud horizontal UTM y longitud tridimensional del conductor para compra.

El flujo de carga PQ equilibrado incluye ambos transformadores, la línea y vacío supuesto 0.45 kW+2.5 kvar por TX. Se adopta elevación efectiva de toma+5% en T1, sujeta a fabricante y operación sin carga. Resultado: MT salida 10.182 kV, MT llegada 10.060 kV y BT371.1 V (-2.34% respecto de380 V), antes de circuitos de usuarios. La toma es una decisión de estudio, no ajuste autorizado de un equipo existente.

Corriente de transporte al pico 11.35 A; corriente nominal a250 kVA/10 kV14.43 A. Caída en línea 1.20% y pérdida 2.08 kW. Un límite de5% en línea es objetivo de estudio, no artículo de RD 018 inventado. La calidad de tensión debe evaluarse en puntos de entrega y con la regulación de la generación.

Balance térmico simplificado por convección/radiación/sol entrega 92.4 A a75°C con h=5 W/(m²K), emisividad/absorptividad 0.5, ambiente 30°C y1000 W/m². Es sensibilidad de gabinete, no ampacidad garantizada a altitud. El requerimiento es14.44 A; se necesita ficha de proveedor y ambiente real.

T1 y T2:250 kVA de capacidad neta garantizada en el emplazamiento, uk6%, P0=0.45 kW y Pcu=3.1 kW propuestos, Dyn 11 para ATdelta/BTestrella-neutro. El reloj es selección de estudio y debe armonizarse con placas y diferencial. SE de piso cercada, plataforma 6×4 m, para evitar asumir capacidad de subestación aérea pesada sin pesos/cargas.

BT interno de cada SE:20 m, dos conductores Cu 240 mm² en paralelo por fase, un neutro Cu 240 y PE35 mm², tablero 400 A con capacidad de uso a altitud. Se exige ampacidad conjunta≥400 A en disposición final; iguales material/sección/longitud y conexiones equilibradas por circuito paralelo. Sección es decisión robusta de estudio; agrupamiento, aislamiento, terminales y corrección de altitud necesitan ficha. Se excluyen ramales de usuarios.


## 6. Oferta de generación, crecimiento y operación aislada

La demanda 171.49 kW requiere en el modelo 183.31 kW y212.45 kVA en generación incluyendo auxiliares. La referencia de200 kW deja sólo 16.69 kW para otros destinos. Con 25 kW reservados a Limbani, el requerimiento supera 200 kW. La capacidad 250 kVA de línea/transformadores no resuelve ese déficit.

Se debe comprobar demanda actual de Limbani, potencia neta estacional, estado de equipos y derechos de agua. Hasta entonces, el abastecimiento completo no se considera garantizado. Son opciones: ejecución por etapas con padrón menor; gestión de usos productivos/picos; respaldo despachable; ampliación de generación si el recurso lo sustenta; selección de una fuente alternativa. No se asigna una potencia artificial para cerrar el balance.

En estiaje, el despacho debe limitar la carga a potencia hídrica disponible menos pérdidas y auxiliares; prever desconexión escalonada de usos no críticos, arranque secuencial de bombas, medición, y reserva para salud/comunicaciones. AVR y regulación de velocidad/frecuencia pertenecen a la central y su interfaz se debe verificar. No se confía en potencia nominal constante.

La llegada puede funcionar sin SEIN. Una adaptación futura requiere estudio con empresa distribuidora/COES según régimen, flujo y cortocircuito, sincronismo 25, antiisla, protecciones direccionales, medición y requisitos del operador. La clase 24 kV no constituye compatibilidad automática con toda tensión ni conexión aprobada.

La proyección a20 años con 1.5% alcanza más de250 kVA sólo en usuarios; pérdidas y auxiliares hacen que la fuente requiera reforzarse antes. No se cambia ahora el proyecto por una futura interconexión hipotética.


## 7. Mecánica, estructuras y seguridad del trazado

Se calcula catenaria en el plano de la carga resultante, con desnivel real de cada par de apoyos según DEM. En cada cantón se conserva longitud sin tensión, considerando deformación elástica lineal, temperatura y fluencia de sensibilidad 345 µε. Se usa HEDS=15%RTS=2205 N a15°C. El modelo admite apoyos inclinados; no sustituye curva tensión-deformación del conductor ni reparto real con movimiento de cadenas.

CNE 250-1 B, área 1(3000–4000 m): viento 29 m/s a5°C; hielo 6 mm a0°C; combinación 14.5 m/s y3 mm a0°C. Densidad hielo 913 kg/m³. Por altitud se usa K=.455 para presión eólica P=K·V²·Sf·A, Sf1 conductor redondo. Estados adicionales: frío-5°C y conductor 75°C con fluencia, ambos de sensibilidad. No son series meteorológicas.

Para revisión conservadora se adopta grado B de estudio y se extienden factores 253-1: vertical 1.50, viento 2.50, tensión 1.65, incluso a casos donde 250.C permite 1.0; esta extensión es decisión conservadora, no obligación general del CNE. Tabla 261-1 A: CAC no pretensado 0.65 bajo 250.B; retenida 0.90. El poste tipo 600 da N se supone con rotura 2×trabajo; esa relación exige certificado y no proviene de una medición local.

Resultados: máximo T/RTS=27.7%; máximo uso de flexión del poste tipo 61.6%. Compresión/vertical de estudio máxima 60.8 kN: el fabricante debe acreditar capacidad axial y combinación con flexión, no basta comprobar 600 da N transversal.

Vanomáximo 82.7 m; cantónmáximo 476.5 m. Suspensión≤5°,ángulo 5–30° con retención, anclaje>30° y terminales. P003, P035, P057 superan 90° y se identifican ESP-RET: dos retenciones independientes y puentes, por diseño especial de fabricante. No se atribuyen a láminas 012/016, cuyos rangos no cubren esos ángulos. Exigen verificar herrajes y separación de fases o replantear el corredor.

Postes CAC 13 m:72;15 m:30;17 m:9. Altura de amarre 10.6/12.4/14.2 m. Empotramiento inicial 1.9/2.1 m propuesto, por verificar con suelo/fabricante. Los apoyos mayores responden al perfil modelado y aparecen en todos los cuadros.

Cada retención dispone de anclajes longitudinales independientes por ramal, 45° vertical de estudio y resistencia de rotura mínima 60 kN. Se comprueba tiro de tres fases por ramal bajo factor 1.65 y componente vertical. La geometría del anclaje es esquemática y puede invadir predios/cauces; deberá ajustarse y recalcularse. Bloque 1.2 m cúbico es provisión de presupuesto, no cimentación verificada.

Margen mínimo frente al DEM en estados analizados:7.54 m. Se toma 7.5 m como margen de estudio respecto del mínimo 7 m de232-1 en cruces viales de conductores desnudos MT≤23 kV; otros escenarios/cauces/obstáculos aplican reglas propias. La Tabla 232-1 a de50–60 kV no se aplica a10 kV. Techos/árboles/vehículos/inundación y balanceo transversal requieren campo.

Cruces de agua se identifican por intersección OSM y se listan en vanos.csv. Ejes de agua incompletos y DEM no bastan para despejar crecidas, taludes o fajas. No se aprueba ningún cruce por tener separación cartográfica 8 m.


## 8. Cortocircuito, protección y puesta a tierra

Se estudia una fuente síncrona aislada 250 kVA. Hipótesis de reactancias xd″=.20, xd′=.30, xd=1.80 pu y ra=.02 pu, sumando impedancias de T1, línea y T2 según punto. Se calcula falla trifásica simétrica por Vfase/|Z|; sin aporte de motores ni tolerancias/corrección de tensión. No es un cortocircuito del SEIN ni ajuste final IEC 60909.

En llegada MT: Ik3 subtransitoria 53.4 A y sostenida 7.73 A. Esta última puede quedar por debajo de la corriente de carga. Fusibles y50/51 sin supervisión de tensión pueden no despejarla; se incorporan 51 V, protección diferencial de TX y protección de tierra sensible.

Q1/Q2:interruptores MT, TC25/5 o25/1 de clase/VA por comprobar, 50/51 y51 V, 87 T por TX, 59 N/64 con detección homopolar. Propuesta orientativa 51 V: pickupprimario 5 A si U<.70 pu, tiempo 0.60 s cabeza; llegada BT100 A con U<.70 pu y0.20 s; respaldo generador 0.90 s. No son ajustes aprobados: arranque, AVR, saturación TC, corrientes decrecientes, poder de corte y coordinación necesitan curvas reales.

La lámina LP-E03 identifica control/medición, órdenes de disparo y conexión funcional MT→zigzag→neutro→NGR→malla. No sustituye planos de bornes/cableado. Exige alimentación DC respaldada para disparar cuando cae la tensión. Energizar inicialmente sin carga y comprobar inrush de ambos TX; evaluar excitación progresiva con AVR y supervisión de frecuencia, sin bloquear indiscriminadamente las protecciones.

Para MTdelta se propone zigzag y resistencia de neutro en SE-LIM:5 A/10 s, R≈1155 ohm, energía térmica≈289 k J. Capacitancia supuesta 7 n F/km/fase da corriente capacitiva total~0.306 A; debe medirse/calcularse con geometría y accesorios. CBCT/59 N y control del NGR deben detectar tierra; el valor 5 A no es norma universal ni estudio definitivo de secuencia cero.

Puesta a tierra de SE: malla 10×10 m, cuatro líneas por dirección, paso 3.33 m, profundidad 0.6 m, Cu 35 mm² y cuatro varillas 2.4 m/16 mm. PAT de poste: dos varillas y enlace Cu 25 mm², sin neutro continuo MT. Equipotencialidad, cercos, descargadores y pantallas deben verificarse frente a paso/contacto/transferencia, CNE 036.

Una varilla 2.4 m/16 mm tiene R aproximada ρ/(2πL)[ln(4 L/d)-1]; paraρ100/300/1000 ohm·m resultan~35.8/107.3/357.9 ohm. Dos varillas no equivalen automáticamente a R/2 por resistencia mutua. Se adjunta sensibilidad de malla; no se promete 25 ohm ni seguridad por resistencia baja aislada.

Cu 35 mm² de malla y PE se proponen por robustez mecánica/corrosión y margen térmico. Verificar ensayo de resistividad, corriente realmente inyectada a terreno, tiempo de despeje, factor de reparto y tensiones admisibles. Bajo NGR 5 A y resistencia provisional, contacto transferido puede dominar aun con falla limitada.

Descargadores Zn O y aisladores requieren coordinación con tensión máxima a tierra durante falla, resistencia NGR, contaminación y altitud. Se propone clase 24 kV de equipos para 10 kV, pero 125 kV de impulso no se considera garantía en sitio sin proveedor. No se reproduce el factor de altitud 1.28 del expediente anterior sin sustento.


## 9. Normativa verificada y ruta de ejecución real

El CNE Suministro 2011 se aprobó por RM 214-2011-MEM/DM. Rige la seguridad de la línea y estaciones según su ámbito. CNE Utilización RM 037-2006 con modificatoria 175-2008 se aplica a instalaciones de utilización/auxiliares BT. Una lista de títulos no es certificación de cumplimiento; la matriz identifica reglas efectivamente consultadas y controles pendientes.

RD 024 corresponde a soportes primarios; RD 023 es secundaria y se retira de la base activa. RD 108-2023 es secundaria, sólo usada para demanda. RD 018 es referencia primaria con descarga oficial no recuperada; se conserva la limitación y no se atribuyen su sección mínima, caída máxima, tensión o puesta a tierra sin cotejo del texto. Proyectos de norma prepublicados no se tratan como normas aprobadas.

Ley 28749 y Reglamento DS 018-2020 deben consultarse con modificaciones. Se verificó DS 003-2026-EM, publicado 25/04/2026: su artículo 3 modifica, entre otros, artículos 51.1 c/51.2 f sobre requisito ambiental cuando corresponde. No se infiere de ello exoneración automática para esta línea. Su régimen requiere confirmar calificación SER, titularidad y concesión eléctrica rural aplicable.

Ejecución real: acreditar titular, origen autorizado de energía y derechos sobre equipos; elegir régimen LCE/SER; gestionar concesión/autorización que corresponda a actividades e instalaciones; resolver derechos de predios y servidumbres; determinar instrumento ambiental eléctrico/SEIA; coordinar ANA en cauces/fajas si hay interferencia; tramitar cruces viales y afectaciones municipales; evaluación de patrimonio cultural cuando corresponda; proyecto y firma profesional, revisión de seguridad, pruebas y operación.

Para obras de SE y cimentaciones se seleccionarán versiones aplicables RNE E.020, E.030, E.050, E.060 y seguridad RESESATE 2013/legislación SST. No se dimensionan edificios sismorresistentes ni fundaciones con datos ficticios. La LP no modifica derechos de uso de agua de la central; éstos deben verificarse separadamente.

IEC 60076-1:2011 y60076-3:2013+AMD 1:2018 se proponen como complemento de especificación y ensayos de transformadores/aislamiento cuando el criterio no está desarrollado en el documento nacional. Se consultaron fichas IEC, no textos de pago íntegros: no se atribuyen cláusulas ni resultados certificados. La edición contractual y sus disposiciones se deben cotejar al adquirir los equipos.

No se presenta ningún trámite como obtenido ni se presupone concesión de una empresa local. Un eventual SEIN requiere ruta de conexión independiente.


## 10. Metrados, presupuesto y viabilidad

Cantidades provienen del eje y tablas: 111 postes, 110 vanos, 128 retenidas, dos SE de250 kVA. Conductor: suma de longitudes de catenarias EDS por fase×3, más 3%reserva: 20 883 m a comprar. No se multiplica la longitud horizontal por tres ignorando desnivel/flecha.

Se incluyen armados por función, PAT por poste, dos transformadores, celdas, NGR/zigzag, mallas, tableros/cables BT internos, descargadores/control, plataformas/cercos, pruebas, gestión y campo. Provisión civil no garantiza bloque/fundación: cantidades se identifican como geométricas provisionales y deben cambiar con geotecnia.

Todos los precios son estimaciones PEN al14/10/2026. El catálogo público Nexans no ofrece precios verificables del producto/tamaño para este sitio; no se hallaron ofertas específicas de equipos garantizados a3772 m. No se presentan los valores como cotizaciones. Transporte extraordinario 12%, ingeniería 8%, contingencia 20% e IGV 18% se explicitan; precios de poste incluyen montaje y no se añade otra partida general de montaje.

Orden de magnitud: directo S/2 020 021; inversión con logística/ingeniería/contingencia e IGV S/3 432 420. Rango de sensibilidad-25/+40%: S/2 574 315 a S/4 805 389. No incluye generación/reforzamiento hídrico ni distribución posterior en Huancasayani ni tasación definitiva de compensaciones.

Viabilidad de transporte eléctrico: favorable bajo hipótesis de equipos, tensión y terreno, por corriente y caída reducidas. Viabilidad de abastecimiento continuo: no acreditada, por oferta real, estiaje y reserva Limbani. Viabilidad económica integral: indeterminada sin energía firme/padrón/tarifa/cotizaciones. No se calcula un VAN/TIR de apariencia precisa sobre datos faltantes.


## 11. Planos, QGIS y control de coherencia

El DXF R2018 utiliza unidadesmetros en modelspace y UTM 19 S. Sus bloques de poste representan siempre el círculo CAC de DGE 09-91-20; función S/A/AN/T/ESP mediante atributos y rótulo. Se emplean 09-91-18 para retenida inclinada, 03-31-44 para tierra y09-90-09 para SE en proyección. Geometría de bloque corresponde al poste; el desplazamiento del rótulo es sólo anotación.

El CAD incluye láminas A3: ubicación general, plantas/perfiles por~1 km con cuadrícula UTM y tabla deapoyos, unifilar, estructuras y puesta a tierra/SE. En planta se dibuja UN solo eje con leyenda 3×AAAC 50 mm², según 09-91-03 y04-40-01/03; las tres fases físicas se muestran en detalles de estructuras. Escalas de planta y perfil son explícitas; esquemas eléctricos/constructivos sin escala. PDF renderizado de las propias láminas CAD.

QGIS contiene copias del catastro original, eje, vanos, postes, retenidas, SE y referencias OSM; CRS 32719 y rutas relativas. Ortofoto antecedente disponible como capa opcional sin exigir servicios Google/XYZ. Se verifica guardar/reabrir y se ensaya portabilidad del paquete. No se utiliza el catastro ampliado con viviendas sintéticas como dato censal.

Cada poste y vano procede de resultados.json. Se verifica conteo, coordenadas de bloques CAD, continuidad/longitudes, identificadores en GIS/CSV y metrados; los originales se conservan con manifiestoshash. Verificaciones numéricas no certifican topografía, calidad de montaje ni homologación de símbolos de fabricantes.


## 12. Conclusiones y comprobaciones posteriores

La corrección efectiva transforma el proyecto urbano previo en una línea troncal independiente a Huancasayani: 6.696 km, AAAC 50 mm², 10 kV condicionado a compatibilidad, 111 postes, 110 vanos y dos transformaciones 250 kVA propuestas. El documento, los cálculos y los gráficos comparten fuente única.

Demanda 2026:171.49 kW para 353 usuarios potenciales. El flujo PQ con toma de estudio+5% entrega~371.1 V en llegada y exige 183.31 kW. Por ello, 200 kW de referencia no bastan para Huancasayani y25 kW adicionales de Limbani; estiaje puede reducir más la oferta.

La fuente aislada obliga a considerar corriente de falla decreciente y protección 51 V/diferencial/tierra. Las tablas de flexión/tensión y margen DEM son comprobaciones de estudio; no sustituyen certificados de postes/retenciones, perfiles de campo y condiciones de paso/contacto.

Prioridad de campo: identificar con certeza CM/SE salida y predio SE llegada; placas/tensión/impedancias/AVR; padrón y curva de Huancasayani; demanda Limbani y potencia estacional; topografía con cruces/techos/cauces; geotecnia y resistividad; cotejo completo RD 018 y régimen; fichas/ofertas y ajustes deprotección. No requiere inventar información para presentar académicamente el trabajo.

La implementación posterior deberá recalcular eje, postes, pérdidas/flujo, cortocircuito y presupuesto cuando cambien datos de campo. Si no se acredita fuente suficiente, se debe reducir etapa de usuarios o reforzar generación/respaldo; no declarar la línea como garantía de200 kW permanentes.
