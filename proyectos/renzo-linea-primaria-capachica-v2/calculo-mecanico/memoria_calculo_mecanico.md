# Memoria de Cálculo Mecánico de Conductores y Estructuras
## Línea Primaria 22.9 kV - Sector Chifrón, Península de Capachica - Puno

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Curso:** MEC330 — Instalaciones Eléctricas II  
**Script Generador:** [`scripts/calculo_mecanico_conductor.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/scripts/calculo_mecanico_conductor.py)  
**Matriz Maestra de Datos:** [`datos/matriz_maestra_datos.yaml`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/datos/matriz_maestra_datos.yaml)  
**Archivos de Datos:**  
* [`datos/estructuras/tabla_hipotesis_mecanicas_cne.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/datos/estructuras/tabla_hipotesis_mecanicas_cne.csv)  
* [`datos/estructuras/tabla_galibos_por_vano.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/datos/estructuras/tabla_galibos_por_vano.csv)  

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

Para el **vano crítico del proyecto ($a = 115.59\text{ m}$ entre E-05 y E-06)**, los resultados analíticos derivados de [`scripts/calculo_mecanico_conductor.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/scripts/calculo_mecanico_conductor.py) son:

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

Conforme a [`datos/estructuras/planilla_estructuras_lp_capachica.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica-v2/datos/estructuras/planilla_estructuras_lp_capachica.csv) y la matriz maestra, la asignación de estructuras es:

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
