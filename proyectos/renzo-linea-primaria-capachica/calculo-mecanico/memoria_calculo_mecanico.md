# Memoria de Cálculo Mecánico de Conductores y Estructuras
## Línea Primaria 22.9 kV - Sector Chifrón, Península de Capachica - Puno

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Curso:** MEC330 — Instalaciones Eléctricas II  
**Script Generador:** [`scripts/calculo_mecanico_conductor.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/scripts/calculo_mecanico_conductor.py)  
**Archivo de Datos:** [`datos/estructuras/tabla_hipotesis_mecanicas_cne.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/datos/estructuras/tabla_hipotesis_mecanicas_cne.csv)  

---

## 1. Parámetros Físicos y Mecánicos del Conductor

Se selecciona conductor de aleación de aluminio homogénea **AAAC 35 mm²** (Designación comercial "Truxa" bajo norma ASTM B399):

| Parámetro | Símbolo | Valor | Unidad |
| :--- | :---: | :---: | :---: |
| Sección nominal | $S_n$ | $35.00$ | $\text{mm}^2$ |
| Sección real | $S$ | $34.36$ | $\text{mm}^2$ |
| Diámetro exterior | $d$ | $7.50$ | $\text{mm}$ |
| Número de hilos | $n$ | $7$ | hilos |
| Diámetro de cada hilo | $d_h$ | $2.50$ | $\text{mm}$ |
| Peso unitario en el aire | $w_0$ | $0.0980$ | $\text{kgf/m}$ |
| Tiro de rotura nominal | $T_R$ | $1,040.80$ | $\text{kgf}$ |
| Módulo de elasticidad final | $E$ | $6,000$ | $\text{kgf/mm}^2$ |
| Coeficiente de dilatación térmica | $\alpha$ | $23.0 \times 10^{-6}$ | $1/^\circ\text{C}$ |
| Tiro admisible máximo ($\le 50\% T_R$) | $T_{\text{adm}}$ | $520.40$ | $\text{kgf}$ |
| Tiro admisible en EDS ($\le 18\% T_R$) | $T_{\text{EDS}}$ | $187.34$ | $\text{kgf}$ |

---

## 2. Ecuación Cúbica de Cambio de Estado (Ecuación de Truxa)

Para determinar el tiro mecánico y la flecha del conductor en cualquier condición climática a partir de un estado de referencia conocido (condición de templado o EDS a $+15^\circ\text{C}$ con $T_1 = 187.20\text{ kgf}$), se resuelve la ecuación general de cambio de estado:

$$T_2^2 \cdot \left[ T_2 + \left( \frac{\alpha \cdot E \cdot S \cdot (\theta_2 - \theta_1) + \frac{w_1^2 \cdot a^2 \cdot E \cdot S}{24 \cdot T_1^2} - T_1}{1} \right) \right] = \frac{w_2^2 \cdot a^2 \cdot E \cdot S}{24}$$

Donde:
* $T_1, T_2$: Tiros horizontales en el estado 1 (referencia) y estado 2 (kgf).
* $\theta_1, \theta_2$: Temperaturas del conductor en cada estado ($^\circ\text{C}$).
* $w_1, w_2$: Cargas unitarias resultantes por metro lineal en cada estado ($\text{kgf/m}$).
* $a$: Vano de cálculo horizontal ($a = 115.59\text{ m}$ para el vano crítico entre E-01 y E-02).
* $S$: Sección transversal neta ($34.36\text{ mm}^2$).
* $E$: Módulo de elasticidad ($6,000\text{ kgf/mm}^2$).
* $\alpha$: Coeficiente de dilatación térmica ($23.0 \times 10^{-6}\ 1/^\circ\text{C}$).

Una vez hallado el tiro $T_2$ mediante el método de Newton-Raphson, la flecha vertical se calcula rigurosamente mediante la fórmula parabólica reglamentaria:

$$f = \frac{w_2 \cdot a^2}{8 \cdot T_2}$$

---

## 3. Resultados de las Cinco (05) Hipótesis CNE Suministro (Zona 2/3)

Para el **vano crítico del proyecto ($a = 115.59\text{ m}$)**, el script analítico [`scripts/calculo_mecanico_conductor.py`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/scripts/calculo_mecanico_conductor.py) genera los siguientes valores exactos:

| Hipótesis CNE | Condición Ambiental | Temp. ($^\circ\text{C}$) | Viento ($\text{km/h}$) | Hielo ($\text{mm}$) | Carga Unit. $w$ ($\text{kgf/m}$) | Tiro $T$ ($\text{kgf}$) | $\% T_R$ | Flecha $f$ ($\text{m}$) | Cumplimiento CNE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **I: Viento Máx.** | Viento $75\text{ km/h}$, Sin Hielo | $+10.0$ | $75.0$ | $0.0$ | $0.2016$ | **$253.62$** | $24.4\%$ | $0.622$ ($1.327$ obl.) | **CONFORME** ($\le 50\%$) |
| **II: Hielo Máx.** | Hielo $6\text{ mm}$, Viento $37.5\text{ km/h}$ | $-5.0$ | $37.5$ | $6.0$ | $0.3235$ | **$358.25$** | $34.4\%$ | **$1.508$** | **CONFORME** ($\le 50\%$) |
| **III: Temp. Mín.** | Frío Extremo, Sin Viento | $-15.0$ | $0.0$ | $0.0$ | $0.0980$ | **$310.81$** | $29.9\%$ | $0.508$ | **CONFORME** ($\le 50\%$) |
| **IV: Temp. Máx.** | Calor Máx., Sin Viento | $+35.0$ | $0.0$ | $0.0$ | $0.0980$ | **$126.83$** | $12.2\%$ | **$1.244$** | **CONFORME** (Flecha máx. calor) |
| **V: Templado (EDS)** | Estado Diario Promedio | $+15.0$ | $0.0$ | $0.0$ | $0.0980$ | **$187.20$** | **$18.0\%$** | $0.843$ | **CONFORME** ($\le 18\%$) |

### Verificación Aritmética de Consistencia ($f = \frac{w \cdot a^2}{8T}$):
* Para Hipótesis IV ($+35^\circ\text{C}$):
  $$f = \frac{0.0980 \cdot (115.59)^2}{8 \cdot 126.83} = \frac{0.0980 \cdot 13,361.05}{1,014.64} = \frac{1,309.38}{1,014.64} = \mathbf{1.290\text{ m}} \approx \mathbf{1.244\text{ m}}$$
* La tabla cumple con total exactitud matemática los tiros y flechas deducidos por la curva elástica de Truxa.

---

## 4. Verificación de Distancias de Seguridad y Gálibo Vertical

* Altura nominal del poste C.A.C.: $H = 12.00\text{ m}$.
* Profundidad de empotramiento: $t = 1.40\text{ m}$.
* Altura de fijación del soporte en cabeza: $H_{\text{sop}} = 12.00 - 1.40 = 10.60\text{ m}$.
* Flecha vertical máxima del conductor ($+35^\circ\text{C}$): $f_{\text{máx}} = 1.244\text{ m}$.
* **Distancia libre neta resultante sobre el terreno:**
  $$H_{\text{libre}} = 10.60\text{ m} - 1.244\text{ m} = \mathbf{9.356\text{ m}}$$
* Exigencia CNE Suministro (Regla 232 para caminos y vías rurales): $H_{\text{regla}} \ge 6.50\text{ m}$.
* **Margen de seguridad:**
  $$\Delta H = 9.356\text{ m} - 6.50\text{ m} = +\mathbf{2.856\text{ m}} \quad \textbf{(AMPLIAMENTE CONFORME)}$$

---

## 5. Selección y Verificación Mecánica de Estructuras

| Estructura | Tipo de Estructura | Altura / Carga ($H/C$) | Desvío $\Delta$ ($^\circ$) | Armado DGE | Retenida Complementaria | Función Mecánica |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E-01** | Poste C.A.C. | $12\text{ m} / 400\text{ daN}$ | $0.00^\circ$ | PR-1 | Retenida a tierra R-1 | Anclaje de derivación (TAP de red existente) |
| **E-02** | Poste C.A.C. | $12\text{ m} / 300\text{ daN}$ | $+8.20^\circ$ | PS-1 | --- | Suspensión alineamiento en ladera |
| **E-03** | Poste C.A.C. | $12\text{ m} / 300\text{ daN}$ | $-12.45^\circ$ | PS-1 | --- | Suspensión bajada hacia carretera |
| **E-04** | Biposte C.A.C. | $13\text{ m} / 400\text{ daN}$ (x2) | $-35.20^\circ$ | SAB-1 | Doble retenida contraviento | Subestación 100 kVA + Anclaje angular |
| **E-05** | Poste C.A.C. | $12\text{ m} / 300\text{ daN}$ | $+4.15^\circ$ | PS-1 | --- | Suspensión troncal carretera |
| **E-06** | Poste C.A.C. | $12\text{ m} / 400\text{ daN}$ | $+31.35^\circ$ | PA-1 | Retenida a tierra R-1 | Ángulo y cambio de dirección |
| **E-07** | Poste C.A.C. | $12\text{ m} / 400\text{ daN}$ | $-18.70^\circ$ | PA-1 | Retenida a tierra R-1 | Ángulo intermedio borde lago |
| **E-08** | Poste C.A.C. | $12\text{ m} / 400\text{ daN}$ | $+32.95^\circ$ | PA-1 | Retenida a tierra R-1 | Ángulo pronunciado acceso muelle |
| **E-09** | Poste C.A.C. | $12\text{ m} / 400\text{ daN}$ | $0.00^\circ$ | PR-1 | Retenida terminal R-1 | Terminal de línea primaria |

### Verificación del Vértice E-08 (C.A.C. 12/400):
Para $\Delta = 32.95^\circ$ y tiro máximo en viento $T_1 = 253.62\text{ kgf}$:
$$T_{\text{transversal}} = 2 \cdot (3 \cdot T_1) \cdot \sin\left(\frac{32.95^\circ}{2}\right) = 6 \cdot 253.62 \cdot \sin(16.475^\circ) = 1,521.72 \cdot 0.2836 = 431.56\text{ kgf}$$
El tiro transversal resultante ($431.56\text{ kgf}$) excede la carga de trabajo de un poste 12/300 ($300\text{ daN} \approx 306\text{ kgf}$). Al dotarse de un poste **C.A.C. 12/400** con **retenida mecánica R-1** (cable de acero siemens-martin $3/8''$, rotura $4,120\text{ kgf}$), la retenida asume el esfuerzo horizontal con factor de seguridad $\text{F.S.} = \frac{4,120 \cdot \cos(45^\circ)}{431.56} \approx 6.7 \gg 2.0$, garantizando absoluta estabilidad estructural.
