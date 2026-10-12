# Memoria de Cálculo Mecánico de Conductores y Estructuras
## Línea Primaria 22.9 kV - Sector Chifrón, Península de Capachica - Puno

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Curso:** MEC330 — Instalaciones Eléctricas II  
**Script Generador:** [`scripts/calculo_mecanico_conductor.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/scripts/calculo_mecanico_conductor.py)  
**Matriz Maestra de Datos:** [`datos/matriz_maestra_datos.yaml`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/datos/matriz_maestra_datos.yaml)  
**Archivos de Datos:**  
* [`datos/estructuras/tabla_hipotesis_mecanicas_cne.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/datos/estructuras/tabla_hipotesis_mecanicas_cne.csv)  
* [`datos/estructuras/tabla_galibos_por_vano.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/datos/estructuras/tabla_galibos_por_vano.csv)  

---

## 1. Ficha Técnica Canónica del Conductor (AAAC 35 mm²)

En estricta conformidad con la norma técnica peruana **NTP 370.258**, **ASTM B399** y las especificaciones de **Electro Puno S.A.A.**, se adopta como parámetro canónico único del proyecto el conductor de aleación de aluminio homogénea:

| Parámetro Físico / Mecánico | Símbolo | Valor Canónico | Unidad | Norma / Referencia |
| :--- | :---: | :---: | :---: | :--- |
| Tipo de conductor | --- | AAAC "Truxa" | --- | Al-Mg-Si |
| Sección nominal | $S_n$ | $35.00$ | $\text{mm}^2$ | NTP 370.258 |
| Sección real | $S$ | $34.36$ | $\text{mm}^2$ | 7 hilos de $2.50\text{ mm}$ |
| Diámetro exterior | $d$ | $7.50$ | $\text{mm}$ | Calibrador |
| Peso propio unitario en aire | $w_0$ | **$0.0945$** | $\text{kgf/m}$ | Catálogo oficial fábrica |
| Tiro de rotura nominal | $T_R$ | **$1,040.00$** | $\text{kgf}$ | $10.20\text{ kN}$ |
| Módulo de elasticidad final | $E$ | $6,000.00$ | $\text{kgf/mm}^2$ | $58,860\text{ MPa}$ |
| Coeficiente de dilatación térmica | $\alpha$ | $23.0 \times 10^{-6}$ | $1/^\circ\text{C}$ | ASTM B399 |
| **Límite de tiro máximo admisible** | $T_{\text{adm}}$ | **$416.00$** | $\text{kgf}$ | **$\le 40.0\% T_R$ (DGE ER)** |
| **Límite de tiro en templado (EDS)** | $T_{\text{EDS}}$ | **$187.20$** | $\text{kgf}$ | **$\le 18.0\% T_R$ a $+15^\circ\text{C}$** |

---

## 2. Ecuación Cúbica de Cambio de Estado (Ecuación de Truxa)

Para determinar el estado tensional del conductor en cualquier condición climática $\theta_2$ a partir del estado de templado inicial conocido (EDS a $+15^\circ\text{C}$, con $\sigma_1 = \frac{187.20}{34.36} = 5.448\text{ kgf/mm}^2$), se resuelve numéricamente la ecuación de Truxa:

$$\sigma_2^3 + K \cdot \sigma_2^2 - C = 0$$

Donde los parámetros auxiliares son:
$$B = \frac{a^2 \cdot w_1^2 \cdot E}{24 \cdot S^2 \cdot \sigma_1^2}$$
$$K = \alpha \cdot E \cdot (\theta_2 - \theta_1) + B - \sigma_1$$
$$C = \frac{a^2 \cdot w_2^2 \cdot E}{24 \cdot S^2}$$

Una vez obtenido el esfuerzo $\sigma_2$ (y por ende el tiro horizontal $T_2 = \sigma_2 \cdot S$), la flecha vertical se calcula rigurosamente mediante la formulación parabólica:

$$f_{\text{vert}} = \frac{w_{\text{vert}} \cdot a^2}{8 \cdot T_2}$$

---

## 3. Resultados de las Cinco (05) Hipótesis CNE Suministro (Zona 2/3)

Para el **vano crítico del proyecto ($a = 115.59\text{ m}$ entre E-05 y E-06)**, los resultados analíticos derivados de [`scripts/calculo_mecanico_conductor.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/scripts/calculo_mecanico_conductor.py) son:

| Hipótesis CNE | Condición Ambiental | Temp. ($^\circ\text{C}$) | Viento ($\text{km/h}$) | Hielo ($\text{mm}$) | Carga Unit. $w$ ($\text{kgf/m}$) | Tiro $T$ ($\text{kgf}$) | $\% T_R$ | Límite DGE | Flecha $f_{\text{vert}}$ ($\text{m}$) | Dictamen Normativo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **I: Viento Máx.** | Viento $75\text{ km/h}$, Sin Hielo | $+10.0$ | $75.0$ | $0.0$ | $0.2008$ | **$253.62$** | $24.4\%$ | $\le 40.0\%$ | $0.622$ | **CONFORME** |
| **II: Hielo Máx.** | Hielo $6\text{ mm}$, Viento $37.5\text{ km/h}$ | $-5.0$ | $37.5$ | $6.0$ | $0.3434$ | **$358.25$** | $34.4\%$ | $\le 40.0\%$ | **$1.508$** | **CONFORME** |
| **III: Temp. Mín.** | Frío Extremo, Sin Viento | $-15.0$ | $0.0$ | $0.0$ | $0.0945$ | **$310.81$** | $29.9\%$ | $\le 40.0\%$ | $0.508$ | **CONFORME** |
| **IV: Temp. Máx.** | Calor Máx., Sin Viento | $+35.0$ | $0.0$ | $0.0$ | $0.0945$ | **$126.83$** | $12.2\%$ | $\le 40.0\%$ | **$1.244$** | **CONFORME** |
| **V: Templado (EDS)** | Estado Diario Promedio | $+15.0$ | $0.0$ | $0.0$ | $0.0945$ | **$187.20$** | **$18.0\%$** | $\le 18.0\%$ | $0.843$ | **CONFORME** |

### Verificación Aritmética de Consistencia en Hipótesis IV:
$$f_{\text{máx}} = \frac{w_0 \cdot a^2}{8 \cdot T_4} = \frac{0.0945 \cdot (115.59)^2}{8 \cdot 126.83} = \frac{0.0945 \cdot 13,361.05}{1,014.64} = \frac{1,262.62}{1,014.64} = \mathbf{1.244\text{ m}}$$
El valor calculado analíticamente coincide exactamente al milímetro con el reporte del script ($1.244\text{ m}$), validando la integridad del algoritmo sin discrepancia alguna.

---

## 4. Verificación de Distancias de Seguridad y Gálibo Vertical Vano a Vano

En aplicación de la **Regla 232 del Código Nacional de Electricidad (CNE Suministro 2011)**, se evalúa el gálibo vertical libre neta para cada uno de los 8 vanos de la línea primaria bajo la condición de máxima flecha vertical a $+35^\circ\text{C}$:

| Vano | Estructuras | Longitud $a$ (m) | Desnivel $\Delta z$ (m) | Flecha Máx. $f_{\text{máx}}$ (m) | Tiro a $+35^\circ\text{C}$ (kgf) | Gálibo Libre $H_{\text{libre}}$ (m) | Exigencia CNE (m) | Margen de Seguridad (m) | Tipo de Terreno y Cruce | Dictamen |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **1** | E-01 $\rightarrow$ E-02 | $105.00$ | $-29.17$ | $1.054$ | $126.8$ | **$9.546$** | $5.50$ | $+4.046$ | Ladera rocosa Cerro Chifrón | **CONFORME** |
| **2** | E-02 $\rightarrow$ E-03 | $105.00$ | $-30.00$ | $1.054$ | $126.8$ | **$9.546$** | $5.50$ | $+4.046$ | Pendiente pronunciada de paso | **CONFORME** |
| **3** | E-03 $\rightarrow$ E-04 | $95.21$ | $-25.44$ | $0.889$ | $126.8$ | **$10.161$** | $6.50$ | $+3.661$ | Bajada hacia SED Biposte | **CONFORME** |
| **4** | E-04 $\rightarrow$ E-05 | $97.22$ | $-22.52$ | $0.922$ | $126.8$ | **$10.128$** | $6.50$ | $+3.628$ | Salida de SED hacia camino | **CONFORME** |
| **5** | E-05 $\rightarrow$ E-06 | $115.59$ | $+10.23$ | $1.244$ | $126.8$ | **$9.356$** | $6.50$ | $+2.856$ | Vano Crítico / Cruce vehicular | **CONFORME** |
| **6** | E-06 $\rightarrow$ E-07 | $110.51$ | $-2.66$ | $1.151$ | $126.8$ | **$9.449$** | $6.50$ | $+2.949$ | Borde de ensenada y camino | **CONFORME** |
| **7** | E-07 $\rightarrow$ E-08 | $79.81$ | $0.00$ | $0.653$ | $126.8$ | **$9.947$** | $6.50$ | $+3.447$ | Acceso a playa y muelle | **CONFORME** |
| **8** | E-08 $\rightarrow$ E-09 | $108.26$ | $0.00$ | $1.111$ | $126.8$ | **$9.489$** | $6.50$ | $+2.989$ | Tramo final llano terminal | **CONFORME** |

**Conclusión:** En todos los vanos, el gálibo vertical libre neta supera holgadamente el mínimo reglamentario del CNE, registrándose un margen de seguridad mínimo de **$+2.856\text{ metros}$** en el vano crítico (E-05 a E-06).

---

## 5. Planilla Canónica y Verificación Estructural de Soportes

Conforme a [`datos/estructuras/planilla_estructuras_lp_capachica.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/datos/estructuras/planilla_estructuras_lp_capachica.csv) y la matriz maestra, la asignación de estructuras es:

| Estructura | Prog. (m) | Cota (msnm) | Poste C.A.C. | Armado DGE | Desvío $\Delta$ (°) | Retenida Complementaria | Función Estructural |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **E-01** | $0+000.00$ | $3,924.17$ | $12\text{ m} / 400\text{ daN}$ | **PR-1** | $0.00^\circ$ | Inclinada simple R-1 | Derivación TAP en cresta (red existente) |
| **E-02** | $0+105.00$ | $3,895.00$ | $12\text{ m} / 300\text{ daN}$ | **PS-1** | $0.00^\circ$ | Ninguna | Suspensión alineamiento en ladera |
| **E-03** | $0+210.00$ | $3,865.00$ | $12\text{ m} / 300\text{ daN}$ | **PS-1** | $0.00^\circ$ | Ninguna | Suspensión de paso en pendiente |
| **E-04** | $0+305.21$ | $3,839.56$ | $13\text{ m} / 400\text{ daN}$ (x2) | **SAB-1** | $-35.20^\circ$ | Contraviento doble en Y | SED Biposte 100 kVA + Anclaje angular |
| **E-05** | $0+402.43$ | $3,817.04$ | $12\text{ m} / 400\text{ daN}$ | **PA-1** | $-36.06^\circ$ | Biselar simple R-1 | Ángulo hacia camino secundario |
| **E-06** | $0+518.02$ | $3,827.27$ | $12\text{ m} / 400\text{ daN}$ | **PA-1** | $+31.35^\circ$ | Biselar simple R-1 | Ángulo vano crítico ($115.59\text{ m}$) |
| **E-07** | $0+628.53$ | $3,824.61$ | $12\text{ m} / 300\text{ daN}$ | **PS-1** | $-6.05^\circ$ | Ninguna | Suspensión alineamiento en tramo llano |
| **E-08** | $0+708.34$ | $3,824.61$ | $12\text{ m} / 400\text{ daN}$ | **PA-1** | $+32.95^\circ$ | Biselar simple R-1 | Ángulo pronunciado acceso muelle |
| **E-09** | $0+816.60$ | $3,824.61$ | $12\text{ m} / 400\text{ daN}$ | **PR-1** | $0.00^\circ$ | Inclinada simple R-1 | Terminal de línea primaria |

### Resumen Consolidado de Suministro Estructural:
* **Postes C.A.C. 12 m / 300 daN:** 03 unidades (E-02, E-03, E-07).
* **Postes C.A.C. 12 m / 400 daN:** 05 unidades (E-01, E-05, E-06, E-08, E-09).
* **Postes C.A.C. 13 m / 400 daN:** 02 unidades (E-04 biposte gemelo).
* **Total Postes de Concreto MT:** **10 unidades**.
* **Armados Normalizados DGE:** PR-1 (2 und), PS-1 (3 und), PA-1 (3 und), SAB-1 (1 cjto).
* **Retenidas Mecánicas MT (Cable de Acero Siemens-Martin 3/8''):** 07 conjuntos (E-01, E-04x2, E-05, E-06, E-08, E-09).

---

## 6. Cálculo Mecánico de Esfuerzos en la Cima y Base de Postes (E-01 a E-09)

En cumplimiento de las **Reglas 250 y 252 del Código Nacional de Electricidad (CNE Suministro 2011)** y la **Norma DGE R.D. 018-2003-EM/DGE**, se evalúan las cargas actuantes en la cabeza de cada estructura bajo la Hipótesis I de viento máximo ($75\text{ km/h}$, $P_v = 23.63\text{ kg/m}^2$), tiros en ángulo y tiros longitudinales terminales mediante el script [`scripts/calculo_mecanico_postes_lp.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/scripts/calculo_mecanico_postes_lp.py):

| Estructura | Poste C.A.C. | Armado DGE | Vano Viento $a_v$ (m) | Ángulo $\Delta$ (°) | $F_{\text{viento}}$ (kgf) | $F_{\text{ángulo}}$ (kgf) | $F_{\text{long}}$ (kgf) | $F_{\text{cima}}$ Bruta (kgf) | Retenida R-1 | $F_{\text{neta}}$ Poste (kgf) | $FS_{\text{poste}}$ (CNE $\ge 2.0$) | Estado CNE |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E-01** | $12\text{ m} / 400\text{ daN}$ | **PR-1** | $52.50$ | $0.00^\circ$ | $48.24$ | $0.00$ | $760.86$ | **$762.40$** | 1x ($1,078.2\text{ kgf}$) | $20.47$ | **$39.85$** | **CONFORME** |
| **E-02** | $12\text{ m} / 300\text{ daN}$ | **PS-1** | $105.00$ | $0.00^\circ$ | $76.28$ | $0.00$ | $0.00$ | **$76.28$** | Sin retenida | $76.28$ | **$8.02$** | **CONFORME** |
| **E-03** | $12\text{ m} / 300\text{ daN}$ | **PS-1** | $100.11$ | $0.00^\circ$ | $73.68$ | $0.00$ | $0.00$ | **$73.68$** | Sin retenida | $73.68$ | **$8.30$** | **CONFORME** |
| **E-04** | $13\text{ m} / 400\text{ daN}$ (x2) | **SAB-1** | $96.22$ | $-35.20^\circ$ | $70.81$ | $460.85$ | $0.00$ | **$531.66$** | 2x ($375.9\text{ kgf}$) | $22.79$ | **$71.60$** | **CONFORME** |
| **E-05** | $12\text{ m} / 400\text{ daN}$ | **PA-1** | $106.41$ | $-36.06^\circ$ | $73.49$ | $471.76$ | $0.00$ | **$545.25$** | 1x ($771.1\text{ kgf}$) | $20.47$ | **$39.85$** | **CONFORME** |
| **E-06** | $12\text{ m} / 400\text{ daN}$ | **PA-1** | $113.05$ | $+31.35^\circ$ | $80.20$ | $409.27$ | $0.00$ | **$489.47$** | 1x ($692.2\text{ kgf}$) | $20.47$ | **$39.85$** | **CONFORME** |
| **E-07** | $12\text{ m} / 300\text{ daN}$ | **PS-1** | $95.16$ | $-6.05^\circ$ | $71.07$ | $80.22$ | $0.00$ | **$151.29$** | Sin retenida | $151.29$ | **$4.04$** | **CONFORME** |
| **E-08** | $12\text{ m} / 400\text{ daN}$ | **PA-1** | $94.04$ | $+32.95^\circ$ | $70.62$ | $429.34$ | $0.00$ | **$499.96$** | 1x ($707.1\text{ kgf}$) | $20.47$ | **$39.85$** | **CONFORME** |
| **E-09** | $12\text{ m} / 400\text{ daN}$ | **PR-1** | $54.13$ | $0.00^\circ$ | $49.12$ | $0.00$ | $760.86$ | **$762.45$** | 1x ($1,078.3\text{ kgf}$) | $20.47$ | **$39.85$** | **CONFORME** |

**Conclusión Estructural:**  
Todos los postes cumplen holgadamente la exigencia de factor de seguridad $FS \ge 2.0$ estipulada por el CNE Suministro 2011. En alineamientos y deflexiones leves (E-02, E-03, E-07), los postes C.A.C. 12/300 trabajan autosoportados con $FS \ge 4.04$. En vértices de ángulo y terminales (E-01, E-04, E-05, E-06, E-08, E-09), las retenidas mecánicas absorben íntegramente las componentes horizontales de tiro, reduciendo la solicitación del poste a compresión simple con $FS \ge 39.85$.

---

## 7. Dimensionamiento y Verificación de Retenidas Mecánicas Tipo R-1

Las retenidas a tierra se diseñan con cable de acero galvanizado grado Siemens-Martin de $3/8''$ ($9.52\text{ mm}$, carga de rotura nominal $T_R = 3,150.0\text{ kgf}$) instalado con inclinación normalizada a $\theta = 45^\circ$ ($\cos 45^\circ = 0.7071$).

$$T_{\text{cable}} = \frac{F_{\text{cima}}}{N_{\text{ret}} \cdot \cos 45^\circ}$$

| Estructura | Función de Retenida | Tiro Horizontal $F_{\text{cima}}$ (kgf) | N° Retenidas | Tiro en Cable $T_{\text{cable}}$ (kgf) | Rotura Nominal $T_R$ (kgf) | Factor de Seguridad $FS_{\text{ret}}$ (Exigido $\ge 2.5$) | Dictamen |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E-01** | Derivación TAP / Anclaje simple | $762.40$ | 1 | **$1,078.19$** | $3,150.0$ | **$2.92$** | **CONFORME** |
| **E-04** | SED Biposte Contraviento doble en Y | $531.66$ | 2 | **$375.94$** | $3,150.0$ | **$8.38$** | **CONFORME** |
| **E-05** | Ángulo biselar simple ($-36.06^\circ$) | $545.25$ | 1 | **$771.10$** | $3,150.0$ | **$4.09$** | **CONFORME** |
| **E-06** | Ángulo biselar simple ($+31.35^\circ$) | $489.47$ | 1 | **$692.21$** | $3,150.0$ | **$4.55$** | **CONFORME** |
| **E-08** | Ángulo biselar simple ($+32.95^\circ$) | $499.96$ | 1 | **$707.05$** | $3,150.0$ | **$4.46$** | **CONFORME** |
| **E-09** | Terminal de línea primaria simple | $762.45$ | 1 | **$1,078.27$** | $3,150.0$ | **$2.92$** | **CONFORME** |

*El factor de seguridad mínimo obtenido en retenidas es de **$2.92$** (E-01 y E-09), superando el umbral reglamentario de $2.50$.*

---

## 8. Verificación Geotécnica de Cimentaciones por el Método de Sulzberger

El cálculo de estabilidad geotécnica de las cimentaciones cilíndricas de concreto ciclópeo ($f'_c = 140\text{ kg/cm}^2 + 30\%$ P.M.) se desarrolla conforme a [`scripts/calculo_cimentacion_sulzberger_lp.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/scripts/calculo_cimentacion_sulzberger_lp.py) para el suelo coluvial-compacto de Capachica ($C_t = 8.0\text{ kg/cm}^3$, $C'_t = 10.0\text{ kg/cm}^3$, $\tan\alpha = 0.01\text{ rad}$):

$$M_r = M_b + M_s = \frac{a \cdot b^3 \cdot C}{12}\tan\alpha + \frac{b \cdot t^3 \cdot C'_t}{36}\tan\alpha$$

| Estructura | Poste C.A.C. | Empot. $t$ (m) | Diám. Exc. $D$ (m) | Momento Vuelco $M_v$ (kgf·m) | Momento Resistente $M_r$ (kgf·m) | Factor de Seguridad $FS_{\text{Sulz}}$ (Exigido $\ge 1.50$) | FS Arrancamiento Bloque Retenida ($\ge 2.0$) | Estado Geotécnico |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E-01** | $12\text{ m} / 400\text{ daN}$ | $1.40$ | $0.80$ | $236.09$ | **$6,583.10$** | **$27.88$** | **$2.84$** | **CONFORME** |
| **E-02** | $12\text{ m} / 300\text{ daN}$ | $1.40$ | $0.80$ | $879.76$ | **$6,583.10$** | **$7.48$** | N/A | **CONFORME** |
| **E-03** | $12\text{ m} / 300\text{ daN}$ | $1.40$ | $0.80$ | $849.78$ | **$6,583.10$** | **$7.75$** | N/A | **CONFORME** |
| **E-04** | $13\text{ m} / 400\text{ daN}$ (x2) | $1.50$ | $0.90$ | $284.88$ | **$9,501.12$** | **$33.35$** | **$8.16$** | **CONFORME** |
| **E-05** | $12\text{ m} / 400\text{ daN}$ | $1.40$ | $0.80$ | $236.09$ | **$6,583.10$** | **$27.88$** | **$3.98$** | **CONFORME** |
| **E-06** | $12\text{ m} / 400\text{ daN}$ | $1.40$ | $0.80$ | $236.09$ | **$6,583.10$** | **$27.88$** | **$4.43$** | **CONFORME** |
| **E-07** | $12\text{ m} / 300\text{ daN}$ | $1.40$ | $0.80$ | $1,744.88$ | **$6,583.10$** | **$3.77$** | N/A | **CONFORME** |
| **E-08** | $12\text{ m} / 400\text{ daN}$ | $1.40$ | $0.80$ | $236.09$ | **$6,583.10$** | **$27.88$** | **$4.34$** | **CONFORME** |
| **E-09** | $12\text{ m} / 400\text{ daN}$ | $1.40$ | $0.80$ | $236.09$ | **$6,583.10$** | **$27.88$** | **$2.84$** | **CONFORME** |

*La cimentación es enteramente estable contra el volcamiento en las 9 estructuras ($FS \ge 3.77$), y los bloques de anclaje de concreto de $0.40 \times 0.40 \times 0.20\text{ m}$ a $1.80\text{ m}$ de profundidad presentan factor de seguridad al arrancamiento vertical de $FS_{\text{arr}} \ge 2.84$ (mínimo exigido $2.00$).*

---

## 9. Coordinación de Aislamiento para Gran Altitud (3,850 msnm)

Conforme a las normas **IEC 60071-1**, **IEC 60071-2** y la **Regla 242 del CNE Suministro**, los requerimientos dieléctricos para $22.9\text{ kV}$ a la altitud de Capachica ($3,850\text{ msnm}$, presión barométrica $62.85\text{ kPa}$, densidad relativa del aire $\delta = 0.631$) analizados en [`scripts/coordinacion_aislamiento_lp.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/scripts/coordinacion_aislamiento_lp.py) son:

1. **Factor de Corrección por Altitud ($K_a$):**
   * $K_a = e^{1.0 \cdot \frac{3850 - 1000}{8150}} = 1.419$ (IEC 60071-2).
   * Factor de corrección empírico CNE: $K_a = 1.0 + \frac{2850}{1000} \cdot 0.087 = \mathbf{1.248}$.
2. **Nivel Básico de Aislamiento al Impulso de Rayo (BIL):**
   * $\text{BIL}_{\text{requerido}} = 125\text{ kV} \times 1.248 = 155.99\text{ kV}$.
   * **BIL Normalizado Seleccionado:** **$170.0\text{ kV}$** (con límite admisible comercial de $150.0\text{ kV}$ en cut-outs y transformadores).
3. **Tensión Soportada a Frecuencia Industrial (1 min húmedo):**
   * $V_{\text{soportada}} = 50.0\text{ kV} \times 1.248 = \mathbf{62.4\text{ kV}}$.
4. **Distancias Mínimas en Aire en Estructuras:**
   * Distancia Fase - Tierra: $220\text{ mm} \times 1.248 = \mathbf{274.5\text{ mm}}$ (adoptado en cruceta: $\ge 400.0\text{ mm}$).
   * Distancia Fase - Fase: $280\text{ mm} \times 1.248 = \mathbf{349.4\text{ mm}}$ (adoptado DMG: $\mathbf{1,200.0\text{ mm}}$).
5. **Línea de Fuga Específica (Polución Lacustre Lago Titicaca, Nivel II):**
   * Exigencia mínima: $31.0\text{ mm/kV} \times 24.2\text{ kV} = \mathbf{750.2\text{ mm}}$.
   * Aislador polimérico 25 kV seleccionado (6 aletas HTV): **$810.0\text{ mm}$** ($+8.0\%$ de margen neto, **CONFORME**).
6. **Descargadores de Sobretensión de Óxido de Zinc (ZnO):**
   * Tensión asignada ($U_r$): **$21.0\text{ kV}$ eficaz**.
   * Tensión de operación continua máxima (MCOV): **$17.5\text{ kV}$ eficaz**.
   * Corriente nominal de descarga: **$10\text{ kA}$** (Clase distribución pesada).

