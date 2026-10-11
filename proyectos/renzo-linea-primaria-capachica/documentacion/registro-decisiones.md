# Registro de Decisiones de Ingeniería (ADR)
## Proyecto: Línea Primaria 22.9 kV y Redes de Distribución Secundaria - Sector Chifrón, Capachica

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Curso:** MEC330 — Instalaciones Eléctricas II  
**Fecha:** Octubre 2026  
**Estado:** Aprobado / Diseño Definitivo  

---

### DEC-001: Selección del Nivel de Tensión Nominal en Media Tensión (22.9 kV)
* **Contexto:** La localidad rural de Chifrón se ubica en la península de Capachica, donde la empresa concesionaria Electro Puno S.A.A. opera el alimentador rural en media tensión trifásica a 22.9 kV (tensión entre fases) con neutro aislado o puesto a tierra a través de impedancia.
* **Decisión:** Adoptar el sistema trifásico trifilar a tensión nominal $V_n = 22.9\text{ kV}$, $60\text{ Hz}$.
* **Justificación Técnica:** 
  1. Permite interconexión directa con la línea de distribución primaria existente en la estructura E-01 sin requerir transformadores elevadores/reductores de acoplamiento.
  2. Reduce drásticamente las corrientes de transporte ($I = 2.52\text{ A}$ a 22.9 kV para 100 kVA), minimizando la caída de tensión ($\Delta V = 0.016\%$) y las pérdidas óhmicas de transporte ($\Delta P = 0.015\text{ kW}$).
  3. Cumple la Directiva MINEM-DGE para Sistemas de Electrificación Rural (SER).

---

### DEC-002: Selección del Tipo y Calibre de Conductor de Media Tensión (AAAC 35 mm²)
* **Contexto:** Se requiere un conductor aéreo desnudo para una línea primaria de $0.817\text{ km}$ en zona altiplánica ($>3,800\text{ msnm}$) expuesta a vientos de $75\text{ km/h}$ y temperaturas de $-15^\circ\text{C}$ a $+35^\circ\text{C}$.
* **Decisión:** Seleccionar conductor de aleación de aluminio homogénea **AAAC (All Aluminium Alloy Conductor) de 35 mm²** (Designación comercial "Truxa" / ASTM B399).
* **Justificación Técnica:**
  1. El conductor AAAC presenta una excelente relación resistencia mecánica / peso propio ($T_R = 1,040.8\text{ kgf}$, $w = 0.098\text{ kg/m}$), superior al aluminio puro (AAC).
  2. Alta resistencia a la corrosión salina/lacustre en la cuenca del Lago Titicaca en comparación con conductores ACSR con núcleo de acero galvanizado.
  3. Calibre estandarizado y homologado por Electro Puno S.A.A. para redes primarias rurales de 22.9 kV.
  4. Capacidad térmica admisible en régimen continuo ($145\text{ A}$) muy superior a la corriente máxima de carga de diseño ($2.52\text{ A}$, factor de carga $< 2\%$).

---

### DEC-003: Ubicación y Configuración de la Subestación de Distribución (SED E-04)
* **Contexto:** El censo levantó 43 familias distribuidas entre la ribera de playa/muelle y la carretera principal. Se requiere ubicar la subestación en el centro de gravedad óptimo de la carga. En el spotting topográfico, el vértice E-04 presenta un desvío angular horizontal de $-35.20^\circ$.
* **Decisión:** 
  1. Ubicar la Subestación de Distribución Aérea Biposte (SAB-1) en la estructura proyectada **E-04** ($E = 412,759.20\text{ m}$, $N = 8,270,976.22\text{ m}$, cota $3,839.56\text{ msnm}$, progresiva $0+305.21\text{ m}$).
  2. Dotar a la estructura E-04 de postes gemelos de concreto C.A.C. $13\text{ m} / 400\text{ daN}$, plataforma portatransformador de perfiles de fierro galvanizado en caliente y doble retención mecánica con retenidas tipo contraviento hacia el talud estable del terreno.
* **Justificación Técnica:**
  1. Centro de gravedad de cargas: Minimiza la caída de tensión acumulada en las redes de baja tensión hacia los extremos más distantes ($820\text{ m}$ hacia C-1 y $456\text{ m}$ hacia C-2).
  2. Justificación del ángulo de $-35.20^\circ$: El armado SAB-1 se configura mecánicamente como estructura de anclaje/retención angular reforzada; los tiros mecánicos resultantes ($T_{\text{res}} \approx 2 \cdot T \cdot \sin(35.20^\circ/2)$) son íntegramente absorbidos por dos retenidas de acero siemens-martin de $3/8''$ ancladas en macizos de concreto de $1.20 \times 0.60 \times 0.30\text{ m}$, garantizando estabilidad absoluta al volcamiento con factor de seguridad $> 2.0$.
  3. Accesibilidad técnica: Ubicación adyacente a camino vehicular carrozable, facilitando el transporte, izaje del transformador de 100 kVA ($520\text{ kg}$) y futuras maniobras de mantenimiento.

---

### DEC-004: Dimensionamiento Estructural y Asignación de Armados en Vértice E-08
* **Contexto:** La estructura E-08 se ubica en progresiva $0+670.36\text{ m}$ con una deflexión angular horizontal de $\Delta = 32.95^\circ$. En borradores preliminares existía discrepancia entre usar poste C.A.C. 12/300 o 12/400.
* **Decisión:** Asignar a la estructura **E-08 un poste de concreto armado centrifugado C.A.C. 12 m / 400 daN**, con armado de anclaje/ángulo **PA-1** y equiparlo obligatoriamente con **retenida mecánica a tierra tipo R-1** en la bisectriz del ángulo exterior.
* **Justificación Técnica:**
  1. La deflexión angular de $32.95^\circ$ excede el límite seguro de $30^\circ$ para postes ligeros de 300 daN sin retención complementaria.
  2. La estructura E-06 (ángulo similar de $31.35^\circ$) tiene asignado poste 12/400. Aplicar C.A.C. 12/400 en E-08 unifica el criterio de seguridad estructural para ángulos $> 30^\circ$.
  3. La retención biselar R-1 neutraliza el $100\%$ del tiro resultante transversal del conductor en la hipótesis de viento máximo ($253.6\text{ kgf} \times 3\text{ fases}$), garantizando flechas y deflexiones nulas en la cabeza del poste.

---

### DEC-005: Estructuración Canónica de la Red de Baja Tensión en Dos (02) Circuitos
* **Contexto:** El censo oficial contiene 43 abonados georreferenciados. En revisiones iniciales se planteó un esquema de 3 circuitos con una rama central que generaba sobrecosto en posterío y cruces redundantes.
* **Decisión:** Diseñar la red de baja tensión en **dos (02) circuitos trifásicos independientes 380/220 V**, originados en el tablero de distribución de la SED 100 kVA:
  * **Circuito C-1 (Troncal Norte + C31):** $820.0\text{ m}$ con conductor autoportante CAAI $3\times35+1\times25+1\times16\text{ mm}^2$, abasteciendo a 31 lotes censados ($C01$ a $C31$, 56 abonados proyectados) hacia la ensenada, playa y muelle lacustre.
  * **Circuito C-2 (Troncal Carretera al Fondo):** $456.0\text{ m}$ con conductor autoportante CAAI $3\times25+1\times25+1\times16\text{ mm}^2$, abasteciendo a 12 lotes censados ($C32$ a $C43$, 22 abonados proyectados) hacia el extremo sur de la vía carrozable.
* **Justificación Técnica:**
  1. Elimina postes redundantes y optimiza el metrado total a 36 postes C.A.C. de 8m/200daN y 9m/300daN.
  2. Distribuye la demanda de manera equilibrada: $51.00\text{ kW}$ ($86.13\text{ A}$) en C-1 y $20.10\text{ kW}$ ($33.95\text{ A}$) en C-2.
  3. Garantiza caídas de tensión dentro del estándar NTCSE ($\Delta V_{\text{máx}} = 2.14\% \le 5.0\%$).
