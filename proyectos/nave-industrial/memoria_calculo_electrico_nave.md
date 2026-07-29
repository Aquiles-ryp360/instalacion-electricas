# ⚡ MEMORIA DE CÁLCULO ELÉCTRICO INDUSTRIAL

**PROYECTO**: Instalaciones Eléctricas de Nave Industrial 800 m² ($20\,\text{m} \times 40\,\text{m}$)  
**NORMATIVA APLICABLE**: Código Nacional de Electricidad (CNE-Utilización y CNE-Suministro), RNE EM.010, Simbología DGE (R.D. 091-2002-EM/DGE), IEC 60909, IEEE 80.  
**ESPECIALIDAD**: Ingeniería Eléctrica / Electromecánica  

---

## 1. PARÁMETROS DEL SISTEMA Y SUMINISTRO ELÉCTRICO

* **Tensión de Red Trifásica ($U_n$)**: $380\,\text{V}$ entre fases / $220\,\text{V}$ fase-neutro.
* **Frecuencia ($f$)**: $60\,\text{Hz}$.
* **Sistema de Distribución**: Trifásico 4 hilos ($3\phi + \text{N} + \text{PE}$) con neutro corrido y puesta a tierra equipotencial.
* **Factor de Potencia Nominal ($\cos\phi_1$)**: $0.78$ (inductivo antes de compensación).
* **Factor de Potencia Objetivo ($\cos\phi_2$)**: $0.98$ (cumplimiento OSINERGMIN / CNE).
* **Resistividad del Cobre ($\rho_{\text{Cu}}$ a $75^\circ\text{C}$)**: $0.018\,\Omega\cdot\text{mm}^2/\text{m}$.
* **Potencia de Cortocircuito en Acometida ($S_{cc}$)**: $50\,\text{MVA}$ a $10\,\text{kV}$.

---

## 2. CUADRO DE CARGAS Y MÁXIMA DEMANDA (CNE-UTILIZACIÓN)

El cálculo de cargas se realiza segregando la zona de producción (industrial) de la zona administrativa:

| Circuito | Descripción de Carga | Cant. | P. Inst. Unit. | P. Inst. Total ($kW$) | Fact. Demanda ($FD$) | Máx. Demanda ($kW$) | Máx. Demanda ($kVA$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **C1** | Alumbrado Nave High-Bay LED 200W | 32 | $200\,\text{W}$ | $6.40$ | $1.00$ | $6.40$ | $6.74$ |
| **C2** | Tomacorrientes Industriales 380V Stecker 32A | 7 | $1500\,\text{W}$ | $10.50$ | $0.75$ | $7.88$ | $9.26$ |
| **C3** | Fuerza — Motor Puente Grúa 10 HP | 1 | $7.46\,\text{kW}$ | $7.46$ | $1.00$ | $7.46$ | $9.33$ |
| **C4** | Fuerza — Compresor de Aire 15 HP | 1 | $11.19\,\text{kW}$ | $11.19$ | $1.00$ | $11.19$ | $13.99$ |
| **C5** | Fuerza — Maquinaria CNC (Tornos/Corte) | 1 | $25.00\,\text{kW}$ | $25.00$ | $0.80$ | $20.00$ | $23.53$ |
| **C6** | Alumbrado y Tomas Oficinas 220V | 1 | $4.50\,\text{kW}$ | $4.50$ | $0.80$ | $3.60$ | $4.00$ |
| **C7** | Banco de Condensadores Automático | 1 | $15.00\,\text{kVAR}$ | $15.00$ | $1.00$ | $0.00$ | $15.00\,\text{kVAR}$ |
| **C8** | Reserva Futura (3Ø) | 1 | $10.00\,\text{kW}$ | $10.00$ | $0.20$ | $2.00$ | $2.35$ |
| **TOTAL**| **CÁLCULO CONSOLIDADO NAVE INDUSTRIAL** | | | **$79.05\,\text{kW}$** | **$0.74$ (med)** | **$58.53\,\text{kW}$** | **$68.86\,\text{kVA}$** |

---

## 3. CÁLCULO DE ALIMENTADORES Y CAÍDA DE TENSIÓN TRIFÁSICA

### A. Corriente de Empleo Nominal ($I_b$)
$$I_b = \frac{MD}{\sqrt{3} \cdot U_n \cdot \cos\phi} = \frac{58,530\,\text{W}}{\sqrt{3} \cdot 380\,\text{V} \cdot 0.85} = 104.54\,\text{A}$$

### B. Corriente de Diseño del Conductor ($I_d$)
Según CNE-U 050-104 (factor de seguridad del $125\%$ para continuas de motores y tableros):
$$I_d = 1.25 \cdot I_b = 1.25 \cdot 104.54\,\text{A} = 130.68\,\text{A}$$

### C. Selección del Cable Principal de Potencia
* **Tipo de Cable**: Libre de Halógenos termoestable **N2XH-90 / 0.6/1 kV**.
* **Sección Seleccionada**: **$3-1\times50\,\text{mm}^2 + 1\times25\,\text{mm}^2 (\text{N}) + 1\times16\,\text{mm}^2 (\text{PE})$**.
* **Capacidad de Corriente ($I_z$)**: $135\,\text{A}$ en bandeja a $30^\circ\text{C}$ $\rightarrow$ **CUMPLE** ($I_z = 135\,\text{A} > I_d = 130.68\,\text{A}$).

### D. Verificación de Caída de Tensión ($\Delta V$)
Para una longitud de alimentador $L = 25\,\text{m}$ desde el medidor hasta el TGD-Nave:
$$\Delta V = \frac{\sqrt{3} \cdot I_b \cdot L \cdot \rho_{\text{Cu}}}{S} = \frac{\sqrt{3} \cdot 104.54\,\text{A} \cdot 25\,\text{m} \cdot 0.018\,\Omega\cdot\text{mm}^2/\text{m}}{50\,\text{mm}^2} = 1.63\,\text{V}$$
$$\Delta V \% = \frac{1.63\,\text{V}}{380\,\text{V}} \times 100 = 0.43\%$$
* **Límite CNE-U 050-102**: $\le 2.5\%$ para alimentadores y $\le 4.0\%$ total. **CUMPLE AMPLIAMENTE ($0.43\% \ll 2.5\%$)**.

---

## 4. CÁLCULO DE CORRIENTE DE CORTOCIRCUITO TRIFÁSICO ($I_{cc}$) SEGÚN IEC 60909

### A. Impedancia del Transformador $100\,\text{kVA}$ ($10\text{kV}/0.38\text{kV}$, $u_k = 4.5\%$)
$$Z_t = \frac{u_k \%}{100} \cdot \frac{U_n^2}{S_n} = \frac{0.045 \cdot 380^2}{100,000\,\text{VA}} = 0.06498\,\Omega$$

### B. Corriente de Cortocircuito Simétrica en Barras TGD ($I_{cc3\phi}$)
$$I_{cc3\phi} = \frac{c \cdot U_n}{\sqrt{3} \cdot Z_t} = \frac{1.05 \cdot 380\,\text{V}}{\sqrt{3} \cdot 0.06498\,\Omega} = 3,546.8\,\text{A} \approx 3.55\,\text{kA}$$

* **Poder de Corte Recomendado del Interruptor General (MCCB)**:  
  Se especifica un **Interruptor Automático en Caja Moldeada (MCCB) de $3\text{P} \times 125\text{A}$ con $I_{cu} = 25\,\text{kA}$**, garantizando un margen de seguridad de casi 7 veces la corriente de cortocircuito calculada.

---

## 5. CÁLCULO DEL BANCO DE CONDENSADORES (COMPENSACIÓN REACTIVA)

* **Potencia Activa ($P$)**: $58.53\,\text{kW}$.
* **$\tan\phi_1$ (sin corregir, $\cos\phi_1 = 0.78$)**: $\tan(\arccos 0.78) = 0.802$.
* **$\tan\phi_2$ (corregido, $\cos\phi_2 = 0.98$)**: $\tan(\arccos 0.98) = 0.203$.
* **Potencia Reactiva Requerida ($Q_c$)**:
$$Q_c = P \cdot (\tan\phi_1 - \tan\phi_2) = 58.53\,\text{kW} \cdot (0.802 - 0.203) = 35.06\,\text{kVAR}$$
* **Banco Seleccionado**: **Banco de Condensadores Automático de $15\,\text{kVAR}$ a $35\,\text{kVAR}$ en 4 pasos ($5+10+10+10\,\text{kVAR}$)** impulsado por regulador microprocesado de factor de potencia.

---

## 6. ESTUDIO LUMINOTÉCNICO Y NÚMERO DE LUMINARIAS (MÉTODO DE LOS LÚMENES - NTP 370.301)

* **Dimensiones del Área de Producción**: $a = 20\,\text{m}$, $b = 37\,\text{m}$, $h_{útil} = 6.50\,\text{m}$.
* **Niveles de Iluminancia Requeridos ($E$)**: $300\,\text{lux}$ (Trabajo de precisión media en talleres).
* **Índice del Local ($K$)**:
$$K = \frac{a \cdot b}{h_{útil} \cdot (a + b)} = \frac{20 \cdot 37}{6.5 \cdot (20 + 37)} = \frac{740}{370.5} = 1.99 \approx 2.0$$
* **Factor de Utilización ($CU$)**: $0.72$ (Reflectancia Techo $70\%$, Paredes $50\%$, Suelo $20\%$).
* **Factor de Mantenimiento ($fm$)**: $0.75$ (Ambiente industrial sucio/polvoriento).
* **Flujo Luminoso Necesario ($\Phi_{total}$)**:
$$\Phi_{total} = \frac{E \cdot A}{CU \cdot fm} = \frac{300\,\text{lux} \cdot 740\,\text{m}^2}{0.72 \cdot 0.75} = \frac{222,000}{0.54} = 411,111\,\text{lúmenes}$$
* **Selección de Luminaria**: Campana **LED High-Bay $200\,\text{W}$ ($130\,\text{lm/W} = 26,000\,\text{lm}$ por luminaria)**.
* **Número de Luminarias Necesarias ($N$)**:
$$N = \frac{\Phi_{total}}{\Phi_{lum}} = \frac{411,111}{26,000} = 15.8 \approx 32\,\text{luminarias (para uniformidad 4 filas x 8 columnas)}$$

---

## 7. SISTEMA DE PUESTA A TIERRA (CÁLCULO DE RESISTENCIA DE LA MALLA IEEE 80)

* **Resistividad Media del Terreno ($\rho$)**: $80\,\Omega\cdot\text{m}$ (terreno arcilloso/terroso en altiplano/costa).
* **Configuración de Malla**: Anillo perimetral de $20\,\text{m} \times 40\,\text{m}$ ($L = 120\,\text{m}$) con 6 pozos verticales de $2.40\,\text{m}$ con jabalina de cobre $5/8''$.
* **Conductor**: Cobre desnudo $50\,\text{mm}^2$ enterrado a $h = 0.80\,\text{m}$.
* **Resistencia Calculada de la Malla ($R_m$)**:
$$R_m \approx \frac{\rho}{4 \cdot r} + \frac{\rho}{L} \approx \frac{80}{4 \cdot 11.28} + \frac{80}{120} = 1.77 + 0.66 = 2.43\,\Omega$$
* **Criterio CNE-U 060-712**: $R \le 5.0\,\Omega$ para instalaciones industriales y tableros principales. **CUMPLE ($2.43\,\Omega < 5.0\,\Omega$)**.
