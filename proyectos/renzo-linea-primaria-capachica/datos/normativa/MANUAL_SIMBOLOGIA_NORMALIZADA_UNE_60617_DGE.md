# COMPENDIO OFICIAL DE SIMBOLOGÍA NORMALIZADA EN PROYECTOS ELECTROMECÁNICOS
## Norma Internacional UNE-EN 60617 (CEI 617) y Norma DGE - MINEM Perú (R.M. Nº 091-2002-EM/VME)
### Autor: Br. Renzo Gabriel Mamani Galindo | MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno

---

## 1. INTRODUCCIÓN Y MARCO NORMATIVO

El diseño de planos de ingeniería eléctrica para líneas de media tensión (MT), redes de distribución secundaria en baja tensión (BT), subestaciones de distribución (SED) e instalaciones interiores, requiere el empleo estricto de **simbología gráfica normalizada**.

Este compendio consolida y sistematiza la totalidad de la información contenida en el documento oficial:
- **Norma Internacional UNE-EN 60617 / CEI 617:** *Símbolos gráficos para esquemas eléctricos*.
- **Norma DGE Símbolos Gráficos en Electricidad (R.M. Nº 091-2002-EM/VME - Ministerio de Energía y Minas del Perú):** Adopción de la serie IEC 60617 como estándar técnico de obligatorio cumplimiento en el Sistema Eléctrico Interconectado Nacional (SEIN) y en empresas distribuidoras como Electro Puno S.A.A.
- **Identificación de Componentes Eléctricos UNE 61.346-1 (IEC 61346-1 / IEC 81346):** Clasificación por letras de referencia según su clase funcional.

---

## 2. ESTRUCTURA DE LA SERIE DE NORMAS UNE-EN 60617 (CEI 617)

| Norma | Denominación y Campo de Aplicación |
| :--- | :--- |
| **UNE-EN 60617-2** | Elementos de símbolos, símbolos distintivos y otros símbolos de aplicación general |
| **UNE-EN 60617-3** | Conductores y dispositivos de conexión |
| **UNE-EN 60617-4** | Componentes pasivos básicos (resistencias, condensadores, bobinas) |
| **UNE-EN 60617-5** | Semiconductores y tubos electrónicos |
| **UNE-EN 60617-6** | Producción, transformación y conversión de la energía eléctrica (generadores, motores, transformadores) |
| **UNE-EN 60617-7** | Aparamenta y dispositivos de control y protección (interruptores, relés, fusibles, seccionadores) |
| **UNE-EN 60617-8** | Instrumentos de medida, lámparas y dispositivos de señalización |
| **UNE-EN 60617-9** | Telecomunicaciones: Conmutación y equipos periféricos |
| **UNE-EN 60617-10** | Telecomunicaciones: Transmisión |
| **UNE-EN 60617-11** | Esquemas y planos de instalación, arquitectónicos y topográficos |
| **UNE-EN 60617-12** | Operadores lógicos binarios |
| **UNE-EN 60617-13** | Operadores analógicos |

---

## 3. CATÁLOGO DETALLADO DE SÍMBOLOS POR ESPECIALIDAD

### 3.1. Contornos y Envolventes (UNE-EN 60617-2, Cap. I, Sec. 1)

| Código | Símbolo Gráfico / Representación | Descripción Técnica y Reglas de Uso |
| :--- | :--- | :--- |
| `02-01-01` a `02-01-03` | Rectángulo de trazo fino o línea discontinua envolvente | **Objeto:** Equipo, dispositivo, unidad funcional, componente o función. Si la presentación lo exige se puede utilizar un contorno de otra forma. Deben incorporarse al símbolo o situarse en su proximidad otros símbolos o descripciones apropiadas. |
| `02-01-07` | Línea de trazo discontinuo o rayado de contorno | **Pantalla / Blindaje:** Para reducir penetración de campos eléctricos o electromagnéticos. |

---

### 3.2. Conductores y Líneas (UNE-EN 60617-3, Sec. 1 / UNE-EN 60617-11)

| Código | Representación Gráfica | Descripción y Reglas de Rotulación |
| :--- | :--- | :--- |
| `03-01-01` | Línea continua `————` | Conductor, cable o línea de transmisión/distribución. |
| `03-01-02` | Trazos oblicuos cruzando la línea `—///—` | Número de conductores. Tantos trazos oblicuos como conductores integren el circuito (ej. 3 trazos = trifásico). |
| `03-01-03` | Trazo oblicuo único con número `—/ 3N—` | Trazo oblicuo único acompañado de una cifra que indica el número total de fases y conductores activos (ej. `3N` = trifásico 3 fases + neutro). |
| `03-01-05` | Rotulado complementario sobre la traza | **Designación completa de línea:** <br>• Naturaleza: CA trifásica, frecuencia y tensión: `3N ~ 380/220 V, 50 Hz` o `60 Hz`<br>• Número y sección de conductores: `3(1x35)+1x25+1x16 mm²`<br>• Separadores: `x` entre cantidad y sección; `+` entre secciones distintas. |
| `03-01-06` | Línea sinuosa continua | Conexión flexible. |
| `03-01-07` | Línea con envoltura circular punteada | Conductor apantallado. |
| `03-01-08` | Dos o tres líneas entrelazadas helicoidales | Conexión trenzada / cable preensamblado (autoportante CAAI). |

---

### 3.3. Uniones y Ramificaciones (UNE-EN 60617-3, Sec. 2)

| Código | Representación Gráfica | Descripción y Reglas de Uso |
| :--- | :--- | :--- |
| `03-02-01` | Punto negro relleno en intersección `●` | Unión o punto de conexión galvánica entre conductores. |
| `03-02-02` | Círculo pequeño vacío `○` | Terminal de conexión o borne. |
| `03-02-03` | Serie de círculos contiguos | Regleta de terminales (bornera). Permite añadir marcas numéricas de terminales. |
| `03-02-04` / `03-02-05` | Conexión en T con o sin punto de unión | Derivación o ramificación en T de un circuito. |
| `03-02-06` / `03-02-07` | Intersección en cruz con puntos | Unión doble de conductores. |

---

### 3.4. Puesta a Tierra, Masa y Equipotencialidad (UNE-EN 60617-2, Sec. 15)

| Código | Representación Gráfica | Descripción Técnica y Aplicación en Redes |
| :--- | :--- | :--- |
| `02-15-01` | Línea vertical que remata en 3 barras horizontales paralelas y decrecientes hacia abajo | **Tierra, símbolo general:** Utilizado para puestas a tierra de protección (PAT-1, PAT-2, PAT-3) en postes, crucetas, pararrayos y masa del transformador. Puede rotularse con el valor objetivo (ej. $\le 25\ \Omega$ o $\le 10\ \Omega$). |
| `02-15-04` | Línea inclinada con trazos diagonales tipo rastrillo o línea engrosada | **Masa / Chasis:** Conexión equipotencial a estructura metálica de máquinas o tableros. |

---

### 3.5. Naturaleza de la Corriente y Tensión (UNE-EN 60617-2, Sec. 2)

| Código | Símbolo | Significado y Formato de Rotulado |
| :--- | :--- | :--- |
| `02-02-03` | `—` (línea recta) | Corriente continua (DC). Tensión a la derecha, tipo de red a la izquierda (ej. `2/M 220/110 V`). |
| `02-02-04` | `~` (senoide) | Corriente alterna (AC). Frecuencia a la derecha (ej. `60 Hz`). Número de fases y neutro a la izquierda (ej. `3/N ~ 380/220 V 60 Hz`). |
| `02-02-13` | `+` | Polaridad positiva. |
| `02-02-14` | `-` | Polaridad negativa. |
| `02-02-15` | `N` | Conductor Neutro. |
| `02-02-16` | `M` | Conductor Medio (en corriente continua trifilar). |

---

### 3.6. Tomas de Corriente y Conectores (UNE-EN 60617-3, Sec. 3 / UNE-EN 60617-11, Sec. 13)

| Código | Representación Gráfica | Descripción |
| :--- | :--- | :--- |
| `03-03-01` | Semicírculo hueco `⌒` | Contacto hembra / Base de enchufe. |
| `03-03-03` | Barra con terminal saliente `┬` | Contacto macho / Clavija de enchufe. |
| `03-03-05` | Semicírculo acoplado con barra | Base y clavija conectadas. |
| `03-03-08` | Semicírculo con trazo oblicuo y cifra 3 | Base y clavija multipolares trifásicas en esquema unifilar. |
| `11-13-04` | Semicírculo con espiga y contacto a tierra | Base de toma de corriente monofásica con borne de protección (PE). |

---

### 3.7. Iluminación y Alumbrado Público (UNE-EN 60617-11, Cap. IV, Sec. 15)

| Código | Símbolo Gráfico Normalizado | Descripción Técnica y Reglas de Dibujo |
| :--- | :--- | :--- |
| `11-15-01` | Círculo con 4 trazos radiales ortogonales | Punto de salida para aparato de iluminación (centro de luz de techo). |
| `11-15-03` | Círculo con aspa cruzada interior (`⨂` / círculo con 'X') | **Lámpara / Luminaria, símbolo general:** Símbolo obligatorio para luminarias de Alumbrado Público (AP) montadas en pastoral de poste C.A.C. |
| `11-15-04` | Círculo con 'X' y líneas laterales de tubo | Luminaria, símbolo general / lámpara fluorescente o luminaria lineal. |
| `11-15-05` | Rectángulo con 3 tubos inscritos | Luminaria con 3 lámparas. |

---

### 3.8. Aparamenta de Maniobra, Contactos y Protección (UNE-EN 60617-7)

| Código | Símbolo Gráfico Normalizado | Descripción Técnica y Función en Redes Eléctricas |
| :--- | :--- | :--- |
| `07-02-01` | Barra con contacto abierto $30^\circ$ sobre borne | Contacto normalmente abierto (NA) / Símbolo general de interruptor de maniobra. |
| `07-02-03` | Barra apoyada en borne con corte | Contacto normalmente cerrado (NC). |
| `07-13-01` | Interruptor simple de potencia | Aparato mecánico de conexión capaz de abrir y cerrar circuitos en vacío o carga nominal. |
| `07-13-02` | Contacto con semicírculo adosado | **Contactor:** Contacto principal de cierre maniobrado por bobina electromagnética. |
| `07-13-05` | Interruptor con cruz o cuadrado en el vástago | **Interruptor Automático Termomagnético (ITM):** Dispositivo de corte en carga con disparo automático ante sobrecarga térmica (bimetal) y cortocircuito magnético (bobina). |
| `07-13-06` | Interruptor con barra transversal de corte visible en el extremo | **Seccionador:** Dispositivo de maniobra sin carga que garantiza distancia de aislamiento y corte visible físico de seguridad para mantenimiento. |
| `07-13-08` | Combinación de interruptor y seccionador | **Interruptor - Seccionador:** Maniobra bajo carga nominal y garantiza corte visible. |
| `07-21-01` | Rectángulo cruzado longitudinalmente por la línea conductora | **Fusible, símbolo general:** Dispositivo de protección por fusión térmica ante corrientes de cortocircuito o sobrecorriente severa. En MT: fusible tipo expulsión Chicote en seccionador Cut-Out. |
| `07-21-07` | Rectángulo atravesado unido al contacto móvil | **Fusible Interruptor / Seccionador Cut-Out (Seccionador fusible):** Portafusible basculante de expulsión que actúa simultáneamente como fusible y seccionador aéreo de media tensión. |

---

### 3.9. Relés y Mandos de Protección (UNE-EN 60617-7, Cap. IV y V)

| Código | Símbolo | Significado |
| :--- | :--- | :--- |
| `07-15-01` | Rectángulo perpendicular al circuito | Bobina de mando de relé o contactor, símbolo general. |
| `07-15-21` | Bobina con elemento térmico bimetálico | Dispositivo de mando térmico (relé bimetálico de sobrecarga). |
| `07-16-01` | Caja de relé con parámetro funcional | **Relé de Medida y Protección:**<br>• `I >` : Relé de máxima intensidad (sobrecorriente instantánea 50).<br>• `I >>` : Relé temporizado de sobrecorriente (51).<br>• `I_d >` : Relé diferencial de fuga a tierra (51N / 87).<br>• `U >` / `U <` : Relé de máxima / mínima tensión (59 / 27). |

---

### 3.10. Transformadores y Máquinas Eléctricas (UNE-EN 60617-6)

| Código | Representación Gráfica | Descripción y Aplicación en SED |
| :--- | :--- | :--- |
| `06-09-01` | Dos círculos entrelazados `⚇` | **Transformador de 2 devanados (Esquema Unifilar):** Representación estándar de transformador de distribución. Se acompaña del grupo de conexión (ej. `Dyn5`), potencia (`100 kVA`) y tensiones (`22.9 / 0.38-0.22 kV`). |
| `06-09-02` | Dos bobinados con núcleos paralelos | Transformador de 2 devanados en representación multifilar / esquemática detallada. |
| `06-10-07` | Dos círculos entrelazados con símbolos `Y` y `Δ` inscritos | Transformador trifásico con conexión estrella-triángulo o triángulo-estrella (`Dyn5`). |
| `06-02-05` | Símbolo de triángulo `Δ` | Devanado trifásico conectado en delta/triángulo. |
| `06-02-07` | Símbolo de estrella `Y` | Devanado trifásico conectado en estrella. |
| `06-02-08` | Símbolo de estrella con punto neutro `Y_N` | Devanado trifásico en estrella con neutro accesible al exterior. |
| `06-04-01` | Círculo con letra identificadora | **Máquina Eléctrica Rotativa:** `M` = Motor; `G` = Generador; `MS` = Motor síncrono; `GS` = Generador síncrono. |

---

### 3.11. Simbología Topográfica de Redes de Distribución Aérea (UNE-EN 60617-11 y Norma DGE Perú)

| Código DGE / UNE | Símbolo Gráfico en Planta CAD | Descripción Constructiva Normalizada |
| :--- | :--- | :--- |
| `DGE 09-91-20` / `11-11-01` | Círculo limpio con centro coordenado ($\phi = 1.5\text{ m}$ a escala) | **Soporte / Poste para Línea Aérea:** Poste de concreto armado centrifugado (C.A.C.) de 8 m/200 daN (BT) o 13 m/400 daN (MT). |
| `DGE 09-91-18` | Línea tensora con aislador de tracción y anclaje perpendicular | **Retenida Inclinada (Viento):** Cable de acero galvanizado Grado Siemens-Martin de 3/8" $\phi$ con varilla de anclaje de $5/8" \times 2.40\text{ m}$ y bloque de concreto prefabricado. |
| `DGE 09-91-19` | Línea recta con bloque vertical adosado | **Retenida Vertical (Contraviento):** Empleada en zonas urbanas o de servidumbre restringida. |
| `DGE 09-91-24` / `11-15-03` | Pastoral en línea quebrada con luminaria circular y aspa inscrita | **Conjunto de Alumbrado Público:** Pastoral de F°G° de $1.50\text{ m}$ con luminaria LED cerrada de 60 W y fotocélula de control electrónico. |
| `DGE 09-91-27` | Rectángulo perimetral con 2 postes y transformador | **Subestación Aérea Biposte (SAB):** Estructura compuesta por 2 postes C.A.C., plataforma portatransformador, seccionadores Cut-Out y pararrayos de óxido metálico. |
| `DGE 09-91-30` | Cuadrado/Rectángulo con círculo interior y letra `M` o código | **Caja de Conexión y Medición (Acometida Domiciliaria):** Caja metálica o poliéster tipo L-M con medidor estático de energía activa kWh. |

---

## 4. DESIGNACIÓN Y CODIFICACIÓN DE COMPONENTES SEGÚN UNE 61.346-1 (IEC 61346)

La norma establece letras distintivas obligatorias para clasificar los componentes eléctricos en diagramas unifilares y listados de materiales:

| Letra | Clase de Aparato / Función | Ejemplos de Aplicación en Proyectos Eléctricos |
| :---: | :--- | :--- |
| **A** | Grupos constructivos, subconjuntos funcionales | Amplificadores, fuentes estabilizadas, módulos de telemetría. |
| **B** | Transductores y sensores (magnitud física a eléctrica) | Fotocélulas crepusculares, sondas de temperatura PT100. |
| **C** | Condensadores | Bancos de condensadores para corrección de factor de potencia. |
| **D** | Dispositivos de memoria y elementos binarios | Módulos lógicos, controladores programables. |
| **E** | Diversos / Equipos terminales de consumo | Alumbrado público, calefactores de tableros contra condensación. |
| **F** | **Dispositivos de protección** | Fusibles chicote MT, fusibles NH en BT, descargadores de sobretensión (pararrayos ZnO), relés térmicos. |
| **G** | Generadores y fuentes de energía | Alternadores síncronos, grupos electrógenos, bancos de baterías. |
| **H** | Equipos de señalización | Lámparas piloto indicadoras de presencia de fase (R, S, T), sirenas. |
| **K** | **Relés y contactores** | Contactores de maniobra para alumbrado público, relés auxiliares. |
| **L** | Inductancias y reactancias | Reactancias de filtrado, bobinas de choque. |
| **M** | Motores | Motores eléctricos de bombas o ventiladores. |
| **N** | Reguladores y amplificadores | Reguladores automáticos de tensión (AVR). |
| **P** | **Instrumentos de medida y prueba** | Medidores multifunción, vatímetros, voltímetros, amperímetros. |
| **Q** | **Aparatos de maniobra de potencia para altas corrientes** | Interruptores automáticos de caja moldeada (MCCB), interruptores termomagnéticos (ITM), seccionadores bajo carga. |
| **R** | Resistencias | Resistencias de calentamiento, resistencias de puesta a tierra neutro. |
| **S** | Interruptores y selectores de control | Selectores manual/automático, pulsadores de marcha/parada. |
| **T** | **Transformadores** | Transformadores de distribución (22.9/0.38-0.22 kV), transformadores de corriente (TC), transformadores de tensión (TT). |
| **U** | Moduladores y convertidores | Inversores, variadores electrónicos de frecuencia (VFD). |
| **V** | Semiconductores y diodos | Tiristores, diodos rectificadores, varistores. |
| **W** | **Vías de conducción, conductores y cables** | Ternas aéreas de media tensión (AAAC), redes autoportantes BT (CAAI), acometidas concéntricas (SET). |
| **X** | **Bornes, regletas y clavijas** | Barras colectoras de cobre, borneras de conexión de medidores. |
| **Y** | Equipos mecánicos accionados eléctricamente | Frenos electromagnéticos, electroválvulas. |
| **Z** | Filtros y equipos de compensación | Filtros activos de armónicos, limitadores de sobretensión transitoria. |

---

## 5. REGLAS DE ORO PARA EL DISEÑO DE PLANOS CAD DE DISTRIBUCIÓN

Para alcanzar una calidad de grado profesional y auditoría formal (calificación 95-100/100):

1. **Despeje Geográfico Absoluto:**
   - En la traza del plano en planta, **nunca rotular textos largos de especificaciones constructivas sobre los postes** (ej. `"PAT-1: Cu 5/8"`, `"RET-I: Inclinada 3/8""`, `"CAC 8m/200daN"`). Esto satura el plano y genera superposiciones inaceptables con vías y acometidas.
   - En el mapa geográfico **únicamente se rotula el código del poste** (ej. `P1-01`), acompañado de su respectivo **símbolo gráfico normalizado UNE/DGE** (símbolo de tierra `02-15-01`, símbolo de retenida `09-91-18`, o luminaria `11-15-03`).

2. **Uso Obligatorio de la Planilla de Estructuras y Armados:**
   - Todas las especificaciones constructivas individuales de cada poste se tabulan en la **Planilla de Estructuras y Armados de Redes Secundarias**, ubicada en el panel técnico lateral del plano.
   - Columnas requeridas:
     * N° y Código de Poste (`P1-01`, etc.)
     * Función Estructural (Alineamiento, Ángulo, Fin de Línea, Derivación)
     * Tipo de Poste y Resistencia (C.A.C. 8 m / 200 daN)
     * Tipo de Armado Secundario Normalizado DGE (E1, PA1, PS1)
     * Retenida Mecánica (Ninguna, RET-I, RET-CV)
     * Puesta a Tierra (Ninguna, PAT-1 $\le 25\ \Omega$, PAT-3 $\le 10\ \Omega$)
     * Alumbrado Público (Sin luminaria / LED 60 W)
     * Vano Mecánico al poste siguiente (m)

3. **Jerarquía Visual y Capas Gráficas:**
   - **Vías y Topografía:** Color gris neutro suave (`#64748B`, línea discontinua de eje).
   - **Línea Primaria MT:** Trazo continuo azul cian (`#0284C7`), espesor mayor ($2.8\text{ pt}$).
   - **Red Secundaria BT Troncal C-1:** Trazo continuo azul eléctrico (`#1D4ED8`), espesor $2.6\text{ pt}$.
   - **Red Secundaria BT Troncal C-2:** Trazo continuo ámbar oscuro (`#B45309`), espesor $2.4\text{ pt}$.
   - **Acometidas Domiciliarias:** Trazo discontinuo gris pizarra (`#64748B`, espesor $0.75\text{ pt}$) desde el poste más cercano hasta la caja medidor.
   - **Cajas Portamedidor:** Bloque normalizado con código de cliente (`C01` a `C43`) rotulado con máscara anticolisión para evitar superposiciones entre viviendas colindantes.

---
*Este compendio es de consulta y aplicación permanente para todos los proyectos del área de Potencia e Instalaciones Eléctricas.*
