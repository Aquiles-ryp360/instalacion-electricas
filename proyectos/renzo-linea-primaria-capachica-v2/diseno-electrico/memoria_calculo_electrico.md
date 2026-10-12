# Memoria de Cálculo Eléctrico y Diseño de Subestación
## Proyecto: Línea Primaria 22.9 kV y Redes Secundarias - Sector Chifrón, Capachica

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Curso:** MEC330 — Instalaciones Eléctricas II  
**Scripts Generadores:**  
* [`scripts/calculo_caida_tension_mt.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/scripts/calculo_caida_tension_mt.py)  
* [`scripts/calcular_cuadro_cargas.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/scripts/calcular_cuadro_cargas.py)  
**Archivo de Datos:** [`datos/cargas/cuadro_cargas_oficial.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/datos/cargas/cuadro_cargas_oficial.csv)  

---

## 1. Cuadro de Cargas y Determinación de la Máxima Demanda

El censo oficial empadronó a **43 viviendas rurales** ($C01$ a $C43$) en el sector Chifrón. Conforme a la metodología DGE para proyectos de electrificación rural, se aplica una tasa intercensal del $3.0\%$ anual a un horizonte de diseño de 20 años ($N_{20} = N_0 \cdot (1 + r)^{20} \approx 43 \cdot 1.806 = 78\text{ abonados}$), con una dotación básica de $600\text{ W/abonado}$ para uso doméstico, factores de simultaneidad normalizados y adición de cargas especiales (bombeo comunal, alumbrado público y turismo).

### 1.1 Resumen Consolidado por Circuitos de Baja Tensión:

| Circuito | Descripción y Cobertura | Abonados Censados | Abonados Proy. (Año 20) | Alumbrado Público LED 60W | Potencia Activa $P$ ($\text{kW}$) | Potencia Aparente $S$ ($\text{kVA}$) | Corriente Trifásica a 380V ($I_{3\phi}$) | Conductor Principal |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **C-1** | Troncal Norte + Lote C31 (Playa y Muelle) | $31$ | $56$ | $10$ unid. | $51.00\text{ kW}$ | $56.67\text{ kVA}$ | **$86.13\text{ A}$** | CAAI $3\times35+1\times25+1\times16$ |
| **C-2** | Troncal Carretera al Fondo ($C32$ a $C43$) | $12$ | $22$ | $5$ unid. | $20.10\text{ kW}$ | $22.33\text{ kVA}$ | **$33.95\text{ A}$** | CAAI $3\times25+1\times25+1\times16$ |
| **TOTAL** | **Sistema Integral Sector Chifrón** | **$43$** | **$78$** | **$15$ unid.** | **$71.10\text{ kW}$** | **$79.00\text{ kVA}$** | **$120.03\text{ A}$** | **SED 100 kVA Biposte** |

### 1.2 Selección del Transformador de Distribución:
* Potencia aparente demandada: $S_{\text{dem}} = 79.00\text{ kVA}$.
* Potencia comercial normalizada superior (Norma DGE / Electro Puno): **$S_n = 100\text{ kVA}$**.
* Margen de reserva para crecimiento de demanda:
  $$\text{Reserva} = \frac{100\text{ kVA} - 79.00\text{ kVA}}{100\text{ kVA}} \times 100 = \mathbf{21.0\%}$$
* **Características Técnicas de la SED:**
  * Tipo: Subestación Aérea Biposte en estructura E-04 (Armado DGE SAB-1).
  * Relación de transformación: $22.9 / 0.38 - 0.22\text{ kV}$.
  * Conexión: Dyn5 (primario en delta, secundario en estrella con neutro accesible).
  * Frecuencia: $60\text{ Hz}$, Refrigeración: ONAN, Aislamiento: Aceite dieléctrico mineral.

---

## 2. Cálculo de la Línea Primaria en Media Tensión (22.9 kV)

### 2.1 Parámetros Eléctricos de Línea:
* Tensión nominal entre fases: $V_n = 22.9\text{ kV} = 22,900\text{ V}$.
* Longitud total de línea proyectada (E-01 a E-09): $L = 0.8166\text{ km}$.
* Longitud hasta la SED (E-01 a E-04): $L_{\text{SED}} = 0.3052\text{ km}$.
* Potencia activa proyectada de cálculo: $P = 90.00\text{ kW}$ (considerando capacidad de ampliación futura).
* Factor de potencia: $\cos\phi = 0.90$ inductivo ($\sin\phi = 0.4359$, $Q = P \cdot \tan\phi = 43.59\text{ kVAR}$).
* Conductor: AAAC $35\text{ mm}^2$ (Truxa):
  * Resistencia eléctrica a $20^\circ\text{C}$: $r = 0.986\ \Omega/\text{km}$.
  * Reactancia inductiva media a $60\text{ Hz}$ (DMD $= 1.25\text{ m}$): $x = 0.385\ \Omega/\text{km}$.

### 2.2 Corriente de Transporte en Media Tensión:
$$I = \frac{P}{\sqrt{3} \cdot V_n \cdot \cos\phi} = \frac{90\text{ kW}}{\sqrt{3} \cdot 22.9\text{ kV} \cdot 0.90} = \mathbf{2.52\text{ A}}$$

### 2.3 Caída de Tensión en Media Tensión:
Aplicando la fórmula de aproximación exacta para líneas cortas trifásicas:
$$\Delta V = \frac{P \cdot r + Q \cdot x}{V_n} \cdot L$$
$$\Delta V = \frac{(90 \cdot 0.986) + (43.59 \cdot 0.385)}{22.9} \cdot 0.8166$$
$$\Delta V = \frac{88.74 + 16.78}{22.9} \cdot 0.8166 = \frac{105.52}{22.9} \cdot 0.8166 = 4.608 \cdot 0.8166 = \mathbf{3.76\text{ V}}$$

En porcentaje sobre la tensión nominal:
$$\Delta V\% = \frac{3.76\text{ V}}{22,900\text{ V}} \times 100 = \mathbf{0.016\%} \ll \mathbf{5.0\%} \quad \textbf{(AMPLIAMENTE CONFORME)}$$

### 2.4 Pérdidas de Potencia y Energía Anual:
* Pérdidas de potencia activa en el transporte trifásico:
  $$\Delta P = 3 \cdot I^2 \cdot r \cdot L = 3 \cdot (2.52\text{ A})^2 \cdot 0.986\ \Omega/\text{km} \cdot 0.8166\text{ km} = 3 \cdot 6.3504 \cdot 0.986 \cdot 0.8166 = \mathbf{0.015\text{ kW}}$$
* Pérdidas porcentuales:
  $$\Delta P\% = \frac{0.015\text{ kW}}{90.00\text{ kW}} \times 100 = \mathbf{0.017\%}$$
* Pérdidas de energía anual ($T = 8,760\text{ horas/año}$, factor de utilización $0.35$):
  $$\Delta E = \Delta P \cdot 8760 \cdot 0.35 \approx \mathbf{46.0\text{ kWh/año}}$$

---

## 3. Validación por Flujo de Carga en OpenDSS (dss-python)

El modelo de la línea primaria se simuló con el motor OpenDSS vía `dss-python` 0.15.7 (API C-API nativa, compatible con Linux/Windows, sin `win32com`). El script generado (`build/modelo_MT.dss`) representa los 9 nodos (E-01 a E-09), los 8 tramos con LineCode AAAC $35\text{ mm}^2$ ($r_1 = 0.986\ \Omega/\text{km}$, $x_1 = 0.385\ \Omega/\text{km}$), la SED como transformador Dyn5 $22.9/0.38\text{ kV}$ de $100\text{ kVA}$ y la carga agregada de $71.10\text{ kW} + 34.09\text{ kvar}$ en el secundario.

### 3.1 Resultados del flujo de carga (motor OpenDSS):
* Convergencia: **TRUE** (solución equilibrada, sin divergencias).
* Voltajes en nodos MT (por unidad): E-01 a E-03: $1.00007$–$1.00004\text{ pu}$; E-04 a E-09: $1.00002\text{ pu}$. Desviación máxima respecto a $1.0\text{ pu}$: $\mathbf{0.007\%}$ (límite normativo $5.0\%$).
* Voltaje en secundario de SED (E-04_BT): $\mathbf{0.97103\text{ pu}}$ ($-2.90\%$).
* Corrientes de tramo MT: $2.044$–$2.046\text{ A}$ en los tramos E-01 a E-04 (tramo de alimentación de la SED); $0.009\text{ A}$ a $0.002\text{ A}$ en los tramos E-04 a E-09 (aguas abajo de la SED, sin cargas directas en el modelo agregado).
* Pérdidas totales: $\mathbf{0.268\text{ kW}} + \mathbf{4.08\text{ kvar}}$ (≈$0.01\text{ kW}$ en la línea MT + ≈$0.26\text{ kW}$ en el transformador).
  * *Hipótesis identificada:* el modelo DSS usa los valores de pérdida por defecto del transformador (`%loadloss`/`%noloadloss`); deben confirmarse con la placa del fabricante para la memoria definitiva.

### 3.2 Concordancia con el cálculo analítico:
La caída de tensión simulada en MT ($0.007\%$) concuerda en orden de magnitud con el cálculo analítico de la sección 2.3 ($0.016\%$); la diferencia se debe a que el flujo de carga modela la demanda real de $79\text{ kVA}$ en la SED frente a los $90\text{ kW}$ de cálculo analítico con ampliación futura. La corriente de transporte simulada ($2.04\text{ A}$) concuerda con $I = 79\text{ kVA} / (\sqrt{3} \cdot 22.9\text{ kV}) = 1.99\text{ A}$.

### 3.3 Diagnóstico de nodos críticos:
Con límite de caída de tensión del $5.0\%$: **CUMPLIMIENTO VERIFICADO**, $0$ nodos críticos de $11$ evaluados. Herramienta: `analizar_nodos_criticos()` de `herramientas/red_mt/`. Resultados canónicos: [`datos/flujo_opendss/resultados.json`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/datos/flujo_opendss/resultados.json).

---

## 4. Caída de Tensión en Redes Secundarias de Baja Tensión (380/220 V)

La caída de tensión en el tramo más desfavorable de baja tensión se calcula por sumatoria de momentos eléctricos:
$$\Delta V = \sum \frac{P_i \cdot L_i}{K \cdot S}$$

* **Circuito C-1 (Longitud $820.0\text{ m}$, conductor CAAI $3\times35+1\times25+1\times16\text{ mm}^2$):**
  * Caída de tensión máxima acumulada al extremo más alejado (lote $C31$):
    $$\Delta V_{\text{C-1}} = \mathbf{8.13\text{ V}} \implies \Delta V\% = \frac{8.13}{380} \times 100 = \mathbf{2.14\%} \le \mathbf{5.0\%} \quad \textbf{(CONFORME)}$$
* **Circuito C-2 (Longitud $456.0\text{ m}$, conductor CAAI $3\times25+1\times25+1\times16\text{ mm}^2$):**
  * Caída de tensión máxima acumulada al fondo de la carretera (lote $C43$):
    $$\Delta V_{\text{C-2}} = \mathbf{4.37\text{ V}} \implies \Delta V\% = \frac{4.37}{380} \times 100 = \mathbf{1.15\%} \le \mathbf{5.0\%} \quad \textbf{(CONFORME)}$$

---

## 5. Sustento Geotécnico y Cálculo del Sistema de Puesta a Tierra (Fórmula de Dwight)

### 5.1 Caracterización Geotécnica y Sondeos de Resistividad Wenner
El sector Chifrón (Península de Capachica) presenta una formación geológica de origen coluvial-lacustre, constituida por estratos de arcilla limosa arenosa compacta con gravilla fina y roca sedimentaria a profundidades superiores a $2.50\text{ m}$.
Los sondeos geoeléctricos verticales mediante el método tetraelectródico de Wenner ejecutados en la zona del proyecto arrojaron los siguientes valores de resistividad aparente:
* Profundidad $a = 1.00\text{ m}$: $\rho_1 = 220.0\ \Omega\cdot\text{m}$
* Profundidad $a = 2.00\text{ m}$: $\rho_2 = 205.0\ \Omega\cdot\text{m}$
* Profundidad $a = 3.00\text{ m}$: $\rho_3 = 195.0\ \Omega\cdot\text{m}$
* Profundidad $a = 4.00\text{ m}$: $\rho_4 = 180.0\ \Omega\cdot\text{m}$
* **Resistividad aparente ponderada de diseño adoptada:** $\rho = \mathbf{200.0\ \Omega\cdot\text{m}}$.

### 5.2 Electrodo Vertical Simple (Jabalina de Cobre $5/8'' \times 2.40\text{ m}$):
La resistencia teórica de una jabalina según la fórmula de Dwight es:
$$R = \frac{\rho}{2 \cdot \pi \cdot L} \cdot \left[ \ln\left(\frac{4 \cdot L}{d}\right) - 1 \right]$$
Donde:
* $L = 2.40\text{ m}$ (longitud de la varilla).
* $d = 0.016\text{ m}$ (diámetro $5/8''$).
* $\frac{4 \cdot L}{d} = \frac{9.60}{0.016} = 600 \implies \ln(600) \approx 6.397$.
* En suelo natural sin tratar:
  $$R_1 = \frac{200}{2 \cdot \pi \cdot 2.40} \cdot (6.397 - 1) = \frac{200}{15.08} \cdot 5.397 = 13.26 \cdot 5.397 = \mathbf{71.58\ \Omega}$$

### 5.3 Tratamiento Químico con Bentonita Sódica (PAT-1 en Redes de BT):
El pozo se excava a diámetro $D = 0.40\text{ m}$ rellenado con bentonita sódica de resistividad $\rho_b = 3.0\ \Omega\cdot\text{m}$. La resistencia equivalente desciende a:
$$R_{\text{PAT-1}} \approx \mathbf{18.20\ \Omega} \le \mathbf{25.0\ \Omega} \quad \textbf{(CONFORME PARA BT - CNE Regla 362)}$$

### 5.4 Sistema de Puesta a Tierra de la SED Biposte (PAT-3):
Se disponen **dos (02) electrodos verticales de cobre de $5/8'' \times 2.40\text{ m}$ en paralelo**, separados a $S = 4.80\text{ m}$ ($S = 2 \cdot L$), enlazados con cable de cobre desnudo de $35\text{ mm}^2$ embebido en zanja con bentonita. La resistencia equivalente combinada es:
$$R_{\text{SED}} = \frac{R_1}{2} \cdot \left( 1 + \frac{L}{S} \cdot \frac{1}{\ln(4L/d) - 1} \right) \cdot \eta_{\text{bentonita}} \approx \mathbf{6.80\ \Omega} \le \mathbf{10.0\ \Omega} \quad \textbf{(CONFORME PARA SED - CNE Regla 362)}$$

---

## 6. Cálculo de Cortocircuito y Coordinación de Protecciones MT / BT

### 6.1 Niveles de Cortocircuito en el Sistema
* **Potencia de Cortocircuito Trifásico en Barra 22.9 kV (SET Juliaca / Tap Coata):** $S_{cc} = 50.0\text{ MVA}$.
* **Corriente de Cortocircuito Trifásico en Lado MT ($22.9\text{ kV}$):**
  $$I_{cc,3\phi,\text{MT}} = \frac{S_{cc}}{\sqrt{3} \cdot V_n} = \frac{50,000\text{ kVA}}{\sqrt{3} \cdot 22.9\text{ kV}} = \mathbf{1,260.6\text{ A}} \approx \mathbf{1.26\text{ kA}}$$
  *Capacidad interruptiva nominal del Cut-Out 27 kV:* $10.0\text{ kA} \gg 1.26\text{ kA}$ (**Holgadamente conforme**).

* **Corriente de Cortocircuito en Bornes Secundarios del Transformador (380 V):**
  * Impedancia de cortocircuito del transformador 100 kVA: $u_{cc} = 4.5\% = 0.045$.
  * Corriente de cortocircuito secundaria franca:
    $$I_{cc,3\phi,\text{BT}} = \frac{S_n}{\sqrt{3} \cdot V_{2n} \cdot u_{cc}} = \frac{100\text{ kVA}}{\sqrt{3} \cdot 0.38\text{ kV} \cdot 0.045} = \frac{100}{0.02962} = \mathbf{3,376.1\text{ A}} \approx \mathbf{3.38\text{ kA}}$$

### 6.2 Coordinación y Selección de Equipos de Protección

1. **Protección en Media Tensión (E-01 y E-04):**
   * Corriente nominal primaria a $100\text{ kVA}$:
     $$I_{1n} = \frac{100}{\sqrt{3} \cdot 22.9} = \mathbf{2.52\text{ A}}$$
   * Selección de fusible: **Fusible tipo Chicote de expulsión rápida, Curva K, Calibre 4 A**.
   * Relación de coordinación: $I_{\text{fusible}} / I_{1n} = 4 / 2.52 = 1.58 \times I_{1n}$.
   * *Verificación inrush:* Soporta $10 \times I_{1n} = 25.2\text{ A}$ durante $0.1\text{ s}$ sin fusión prematura.
   * *Verificación de falla secundaria reflejada:* Despeja corrientes de falla franca en BT en un tiempo $< 0.08\text{ s}$.

2. **Protección en Baja Tensión (Tablero General SED E-04, 380/220 V):**
   * **Circuito C-1 ($I_{\text{carga}} = 86.13\text{ A}$):**
     * Interruptor termomagnético en caja moldeada (MCCB) regulable $3 \times 100\text{ A}$, poder de corte $I_{cu} = 16.0\text{ kA} > 3.38\text{ kA}$ (**Conforme**).
   * **Circuito C-2 ($I_{\text{carga}} = 33.95\text{ A}$):**
     * Interruptor termomagnético en caja moldeada (MCCB) $3 \times 63\text{ A}$, poder de corte $I_{cu} = 16.0\text{ kA} > 3.38\text{ kA}$ (**Conforme**).
   * **Circuito Alumbrado Público ($I_{\text{AP}} = 2.27\text{ A}$):**
     * Interruptor termomagnético modular en riel DIN $2 \times 16\text{ A}$, poder de corte $I_{cn} = 10.0\text{ kA} > 3.38\text{ kA}$, coordinado con contactor modular $25\text{ A}$ y fotocélula electrónica de control automático.
   * **Selectividad Total:** La curva de disparo térmico y magnético de los MCCB en BT opera antes de que el fusible K de 4 A en MT alcance su tiempo de fusión pre-arco para fallas en la red secundaria, garantizando selectividad total y continuidad de servicio.
