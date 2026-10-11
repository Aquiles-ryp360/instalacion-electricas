# Criterios Normativos de Diseño de Ingeniería
## Proyecto: Línea Primaria 22.9 kV y Redes de Distribución Secundaria - Sector Chifrón, Capachica

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Curso:** MEC330 — Instalaciones Eléctricas II  
**Normativa Aplicable:** Sector Eléctrico Peruano (MINEM-DGE / OSINERGMIN / CNE)  

---

## 1. Código Nacional de Electricidad (CNE Suministro 2011)

### 1.1 Regla 250 — Condiciones Climáticas e Hipótesis de Sobrecarga (Zona 2/3 - Altiplano > 3,000 msnm)
Para líneas aéreas ubicadas en el departamento de Puno a altitudes superiores a 3,000 msnm (altitud de diseño: $3,817.04$ a $3,924.17\text{ msnm}$), rigen las siguientes hipótesis de diseño:

* **Hipótesis I — Viento Máximo:**
  * Temperatura: $+10.0^\circ\text{C}$
  * Velocidad de viento: $75.0\text{ km/h}$ ($20.83\text{ m/s}$)
  * Presión dinámica de viento sobre superficie cilíndrica:
    $$P_v = 0.0042 \cdot V^2 = 0.0042 \cdot (75)^2 = 23.63\text{ kgf/m}^2$$
  * Espesor radial de manguito de hielo: $0\text{ mm}$
  * Esfuerzo máximo admisible del conductor: $\le 50.0\%$ del tiro de rotura nominal ($T_R$).

* **Hipótesis II — Hielo Máximo:**
  * Temperatura: $-5.0^\circ\text{C}$
  * Espesor radial de hielo: $6.0\text{ mm}$ (densidad del hielo $\rho = 900\text{ kg/m}^3$)
  * Velocidad concomitante de viento: $37.5\text{ km/h}$ ($50\%$ del viento máximo)
  * Esfuerzo máximo admisible del conductor: $\le 50.0\%$ del tiro de rotura nominal ($T_R$).

* **Hipótesis III — Temperatura Mínima Absoluta:**
  * Temperatura: $-15.0^\circ\text{C}$
  * Viento: $0\text{ km/h}$
  * Espesor de hielo: $0\text{ mm}$
  * Esfuerzo máximo admisible del conductor: $\le 50.0\%$ del tiro de rotura nominal ($T_R$).

* **Hipótesis IV — Temperatura Máxima Absoluta:**
  * Temperatura: $+35.0^\circ\text{C}$
  * Viento: $0\text{ km/h}$
  * Espesor de hielo: $0\text{ mm}$
  * Objetivo: Determinación de la **flecha vertical máxima de diseño ($f_{\text{máx}}$)** y verificación de distancias mínimas de seguridad al suelo (gálibo vertical).

* **Hipótesis V — Templado y Estado Diario Promedio (EDS):**
  * Temperatura: $+15.0^\circ\text{C}$
  * Viento: $0\text{ km/h}$
  * Espesor de hielo: $0\text{ mm}$
  * Esfuerzo máximo admisible en EDS: $\le 18.0\%$ del tiro de rotura nominal ($T_R$) para prevenir fatiga por vibraciones eólicas y degradación mecánica por efecto Bauschinger.

---

### 1.2 Regla 232 — Distancias Verticales Mínimas de Seguridad al Terreno (Gálibos)

* **En Media Tensión ($22.9\text{ kV}$, tensión nominal entre fases):**
  * Sobre terreno natural accesible únicamente a peatones: Mínimo $5.50\text{ m}$.
  * A lo largo y dentro de la franja de servidumbre de caminos rurales: Mínimo $6.50\text{ m}$.
  * En cruces perpendiculares sobre caminos carrozables y carreteras: Mínimo $7.00\text{ m}$.
  * **Valor verificado en el proyecto:** Altura de fijación $10.60\text{ m}$ (en poste C.A.C. de 12 m, empotramiento 1.20 m), flecha máxima $f_{\text{máx}} = 1.244\text{ m}$ $\Rightarrow$ **Gálibo libre neta $= 9.356\text{ m} > 6.50\text{ m}$** (Cumple con margen de seguridad de $+2.856\text{ m}$).

* **En Baja Tensión ($380/220\text{ V}$, conductor autoportante aislado CAAI):**
  * A lo largo de calles, vías locales y caminos de acceso: Mínimo $5.00\text{ m}$.
  * En cruces perpendiculares de caminos y calles transitables: Mínimo $5.50\text{ m}$.
  * **Valor verificado en el proyecto:** Altura de fijación $6.80\text{ m}$ (poste C.A.C. 8 m) y $7.80\text{ m}$ (poste C.A.C. 9 m en cruces de vía), flecha máxima $0.65\text{ m}$ $\Rightarrow$ **Gálibo libre neta $= 6.15\text{ a }7.15\text{ m} \ge 5.50\text{ m}$** (Cumple).

---

### 1.3 Regla 362 — Puestas a Tierra y Resistencias Máximas Reglamentarias

* **Subestación de Distribución MT/BT (Transformador 100 kVA):**
  * Resistencia de puesta a tierra exigida: $R \le 10.0\ \Omega$.
  * Configuración adoptada: Puesta a tierra tipo **PAT-3** compuesta por 2 electrodos verticales de cobre de $5/8'' \times 2.40\text{ m}$ en paralelo, separados $S = 4.80\text{ m}$, con conductor de enlace Cu $35\text{ mm}^2$ y tratamiento con bentonita sódica en suelo de $\rho = 200\ \Omega\cdot\text{m}$.
  * Valor calculado: **$R_{\text{SED}} = 6.80\ \Omega \le 10.0\ \Omega$** (Conforme).

* **Red Secundaria de Baja Tensión (Neutro y Masas):**
  * Resistencia de puesta a tierra exigida para neutro en BT: $R \le 25.0\ \Omega$.
  * Configuración adoptada: Puesta a tierra tipo **PAT-1** (1 varilla de cobre $5/8'' \times 2.40\text{ m}$ tratada con bentonita).
  * Valor calculado: **$R_{\text{BT}} \le 18.20\ \Omega \le 25.0\ \Omega$** (Conforme).

---

## 2. Bases para el Diseño de Líneas y Redes Primarias (R.D. N° 018-2003-EM/DGE)

* **Tensión de Diseño:** $22.9\text{ kV}$, trifásica, 3 conductores en disposición triangular/horizontal.
* **Factor de Seguridad de Postes:**
  * Factor de seguridad mínimo al volcamiento y rotura de postes de concreto: $\text{F.S.} \ge 2.0$ para esfuerzos normales, y $\text{F.S.} \ge 1.5$ para esfuerzos con hipótesis de rotura de conductor.
* **Empotramiento de Postes:**
  $$t = \frac{H}{10} + 0.20\text{ m}$$
  * Para poste C.A.C. de $12.0\text{ m}$: $t = 1.20 + 0.20 = 1.40\text{ m}$ (en terreno blando/mixto) o $1.20\text{ m}$ en roca/suelo firme compactado con solado de concreto ciclópeo.
  * Para poste C.A.C. de $13.0\text{ m}$ (SED): $t = 1.50\text{ m}$.
  * Para poste C.A.C. de $8.0\text{ m}$ (BT): $t = 1.00\text{ m}$.
  * Para poste C.A.C. de $9.0\text{ m}$ (BT cruce vía): $t = 1.10\text{ m}$.

---

## 3. Norma de Calidad de los Servicios Eléctricos (NTCSE - D.S. N° 020-97-EM)

* **Tolerancia de Tensión en el Punto de Entrega:**
  * Zonas rurales: $\pm 7.5\%$ de la tensión nominal.
  * Zonas urbanas y de servicio regular: $\pm 5.0\%$.
  * **Criterio conservador adoptado en el proyecto:** Límite máximo admisible $\Delta V_{\text{máx}} \le 5.0\%$.
  * **Resultados de cálculo:**
    * Media Tensión ($22.9\text{ kV}$): $\Delta V = 0.016\%$ ($3.76\text{ V}$).
    * Baja Tensión ($380/220\text{ V}$): $\Delta V = 2.14\%$ ($8.13\text{ V}$) en el abonado más crítico ($C31$).

---

## 4. Corrección de Aislamiento por Altitud (IEC 60071-1 / CNE Suministro)

Para instalaciones situadas por encima de los 1,000 msnm, la densidad del aire disminuye, reduciendo la rigidez dieléctrica superficial del aire y los aisladores. A la altitud de diseño ($H = 3,924\text{ msnm}$):

* **Factor de Corrección por Altitud ($k_a$):**
  $$k_a = e^{m \cdot \frac{H - 1000}{8150}} \approx e^{1.0 \cdot \frac{3924 - 1000}{8150}} = e^{0.3588} = 1.432$$
* **Tensión de Sostenimiento al Impulso Atmosférico (BIL):**
  * Tensión nominal del sistema: $22.9\text{ kV}$ (Tensión más elevada para el material: $U_m = 27\text{ kV}$).
  * BIL normalizado a nivel del mar: $125\text{ kV}$.
  * BIL requerido a $3,924\text{ msnm}$:
    $$\text{BIL}_{\text{alt}} = 125\text{ kV} \cdot 1.432 = 179\text{ kV}$$
* **Selección Técnica:** Se adoptan aisladores y equipos con nivel de aislamiento homologado clase $27\text{ kV}$ con línea de fuga extendida para alta contaminación lacustre ($\ge 31\text{ mm/kV}$), aisladores tipo pin ANSI 56-3 y pararrayos poliméricos de óxido de zinc de $21\text{ kV} / 10\text{ kA}$ (MCOV $17.5\text{ kV}$).
