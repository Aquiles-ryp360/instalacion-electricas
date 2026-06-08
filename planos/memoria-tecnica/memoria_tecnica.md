# MEMORIA TÉCNICA Y CÁLCULOS JUSTIFICATIVOS
## Proyecto: Instalación Eléctrica Residencial - Vivienda Unifamiliar de 3 Pisos

### 1. Normas de Referencia y Criterios de Diseño
El diseño de la instalación eléctrica se basa en las siguientes normativas:
* **National Electrical Code (NEC - NFPA 70):** Para el cálculo de secciones de conductores (NEC 310), dimensionamiento de circuitos ramales (NEC 210), protecciones (NEC 240) y sistemas de puesta a tierra (NEC 250).
* **Reglamento Nacional de Edificaciones (RNE EM.010):** Normativa aplicable en Perú para instalaciones interiores.
* **Código Nacional de Electricidad - Utilización (CNE-U):** Sección 050 para cargas e iluminación y Sección 060 para puesta a tierra.

### 2. Parámetros Eléctricos del Sistema
* **Tensión de suministro ($V$):** $220\text{ V}$ (Tensión monofásica de servicio).
* **Frecuencia ($f$):** $60\text{ Hz}$.
* **Factor de Potencia ($\cos \phi$):** $0.90$ (estimado para cargas residenciales combinadas).
* **Caída de Tensión Máxima Permitida:**
  * Alimentador principal: $2.5\%$
  * Circuitos derivados (ramales): $3.0\%$ (NEC 210.19(A) FPN 4)
  * Caída de tensión total combinada: $5.0\%$

---

### 3. Fórmulas de Cálculo
#### 3.1. Corriente de Diseño ($I$)
Para un sistema monofásico, la corriente nominal o de diseño se calcula mediante la fórmula:
$$I = \frac{P}{V \cdot \cos \phi}$$
Donde:
* $P$: Potencia en Watts ($W$).
* $V$: Tensión nominal ($220\text{ V}$).
* $\cos \phi$: Factor de potencia ($0.90$).

#### 3.2. Caída de Tensión ($\Delta V$)
Para circuitos monofásicos de cobre, la caída de tensión se calcula mediante la fórmula:
$$\Delta V = \frac{2 \cdot L \cdot I \cdot \rho}{S}$$
Donde:
* $L$: Longitud del conductor (metros).
* $I$: Corriente del circuito (Amperios).
* $\rho$: Resistividad del cobre a la temperatura de operación ($0.0175\ \Omega \cdot \text{mm}^2/\text{m}$).
* $S$: Sección o calibre del conductor ($\text{mm}^2$).

Porcentaje de caída de tensión:
$$\Delta V\% = \left(\frac{\Delta V}{V}\right) \cdot 100$$

---

### 4. Cuadro de Cargas y Demanda Máxima
El cuadro de cargas del proyecto se detalla a continuación. Se han agrupado los circuitos de acuerdo al levantamiento real de puntos en los planos arquitectónicos:

| Cto. | Piso | Descripción del Circuito | P. Inst. ($W$) | F.D. | P. Dem. ($W$) | $I_{\text{dem}}$ ($A$) | Protección ITM | Calibre Cond. (F+N+PE) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **C1** | Piso 1 | Alumbrado primer piso | 72 | 1.00 | 72 | 0.36 | 2P - 10 A | $3 \times 1.5\text{ mm}^2$ Cu |
| **C2** | Piso 1 | Tomacorrientes generales | 180 | 1.00 | 180 | 0.91 | 2P - 16 A | $3 \times 2.5\text{ mm}^2$ Cu |
| **C3** | Piso 1 | Tomacorrientes de cocina | 360 | 1.00 | 360 | 1.82 | 2P - 20 A | $3 \times 2.5\text{ mm}^2$ Cu |
| **C4** | Piso 2 | Alumbrado segundo piso | 72 | 1.00 | 72 | 0.36 | 2P - 10 A | $3 \times 1.5\text{ mm}^2$ Cu |
| **C5** | Piso 2 | Tomacorrientes generales | 900 | 0.70 | 630 | 3.18 | 2P - 16 A | $3 \times 2.5\text{ mm}^2$ Cu |
| **C6** | Piso 3 | Alumbrado tercer piso | 72 | 1.00 | 72 | 0.36 | 2P - 10 A | $3 \times 1.5\text{ mm}^2$ Cu |
| **C7** | Piso 3 | Tomacorrientes generales | 1080 | 0.70 | 756 | 3.82 | 2P - 16 A | $3 \times 2.5\text{ mm}^2$ Cu |
| **Total**| | **Vivienda Unifamiliar** | **2,736** | | **2,142** | **10.82** | | |

* **Potencia Instalada Total ($P_{\text{inst}}$):** $2,736\text{ W}$ ($2.74\text{ kW}$)
* **Máxima Demanda Calculada ($P_{\text{dem}}$):** $2,142\text{ W}$ ($2.14\text{ kW}$)
* **Corriente de Demanda Total ($I_{\text{dem}}$):** $10.82\text{ A}$

---

### 5. Selección y Coordinación Conductor-Protección
Para cada circuito se ha seleccionado la sección del conductor de cobre tipo TW/THW/THHN y su respectivo interruptor termomagnético (ITM) e interruptor diferencial (ID) siguiendo la regla de coordinación del NEC:
$$I_b \leq I_n \leq I_z$$
Donde:
* $I_b$: Corriente de diseño del circuito.
* $I_n$: Corriente nominal del interruptor termomagnético.
* $I_z$: Capacidad de corriente del conductor seleccionado (de acuerdo a la Tabla NEC 310.15(B)(16) a 75°C o 60°C).

#### 5.1. Circuito General de Alimentación (Acometida a TG-01)
* **Corriente de diseño:** $10.82\text{ A}$.
* **Protección adoptada:** Interruptor termomagnético de **2P - 32 A**. (Brinda margen de reserva del $200\%$ para sobrecargas transitorias o ampliaciones futuras).
* **Conductor seleccionado:** **$2 \times 10\text{ mm}^2\text{ Cu} + 1 \times 10\text{ mm}^2\text{ Cu (PE)}$** tipo THW/THHN en canalización PVC de $1"$.
* **Capacidad del conductor ($I_z$):** $50\text{ A}$ (a 60°C). Cumple con holgura: $10.82\text{ A} \leq 32\text{ A} \leq 50\text{ A}$.

#### 5.2. Circuitos de Alumbrado (C1, C4, C6)
* **Corriente máxima:** $0.36\text{ A}$ por piso.
* **Protección adoptada:** Termomagnético de **2P - 10 A**.
* **Conductor:** **$2 \times 1.5\text{ mm}^2\text{ Cu} + 1.5\text{ mm}^2\text{ Cu (PE)}$** tipo TW.
* **Capacidad del conductor ($I_z$):** $15\text{ A}$ (a 60°C). Coordinación: $0.36\text{ A} \leq 10\text{ A} \leq 15\text{ A}$.

#### 5.3. Circuitos de Tomacorrientes Generales (C2, C5, C7)
* **Corriente máxima:** $3.82\text{ A}$ (C7).
* **Protección adoptada:** Termomagnético de **2P - 16 A** + Interruptor Diferencial de **2P - 25 A / 30 mA**.
* **Conductor:** **$2 \times 2.5\text{ mm}^2\text{ Cu} + 2.5\text{ mm}^2\text{ Cu (PE)}$** tipo THW.
* **Capacidad del conductor ($I_z$):** $20\text{ A}$ (a 60°C). Coordinación: $3.82\text{ A} \leq 16\text{ A} \leq 20\text{ A}$.

#### 5.4. Circuito de Cocina (C3)
* **Corriente de diseño:** $1.82\text{ A}$.
* **Protección adoptada:** Termomagnético de **2P - 20 A** + Interruptor Diferencial de **2P - 25 A / 30 mA**.
* **Conductor:** **$2 \times 2.5\text{ mm}^2\text{ Cu} + 2.5\text{ mm}^2\text{ Cu (PE)}$** tipo THW.
* **Capacidad del conductor ($I_z$):** $20\text{ A}$ (a 60°C). Coordinación: $1.82\text{ A} \leq 20\text{ A} \leq 20\text{ A}$ (en el límite físico de corriente del conductor, ideal para proteger la canalización empotrada de PVC).

---

### 6. Cálculos de Caída de Tensión
La caída de tensión se evalúa en el punto más desfavorable (final del circuito del tercer piso C7) estimando una longitud de cable de $25\text{ m}$ desde el tablero general:
$$\Delta V = \frac{2 \cdot L \cdot I \cdot \rho}{S} = \frac{2 \cdot 25\text{ m} \cdot 3.82\text{ A} \cdot 0.0175\ \Omega \cdot \text{mm}^2/\text{m}}{2.5\text{ mm}^2} = \frac{3.3425}{2.5} = 1.34\text{ V}$$

Porcentaje de caída de tensión:
$$\Delta V\% = \left(\frac{1.34\text{ V}}{220\text{ V}}\right) \cdot 100 = 0.61\%$$

> [!TIP]
> Dado que la caída de tensión calculada ($0.61\%$) es muy inferior al límite del $3.0\%$ del NEC para circuitos ramales, el calibre de conductor seleccionado ($2.5\text{ mm}^2$) es técnicamente óptimo y no requiere sobredimensionamiento por caída de tensión.

---

### 7. Dimensionamiento del Sistema de Puesta a Tierra (SPAT)
El sistema de puesta a tierra residencial utiliza una varilla de cobre tipo Copperweld:
* **Varilla de cobre:** Diámetro $5/8"$, longitud $2.40\text{ m}$.
* **Conductor de enlace:** Cobre desnudo de $6\text{ mm}^2$ (mínimo exigido por NEC 250.66 para este calibre de acometida).
* **Resistencia objetivo:** $< 25\ \Omega$ (NEC 250.53 exige que un electrodo simple de varilla tenga una resistencia menor o igual a 25 Ohmios; de lo contrario, se debe agregar un electrodo adicional). Se prevé tratamiento con bentonita y sales para asegurar $< 15\ \Omega$.

---

### 8. Supuestos Técnicos Adoptados
1. **Factor de Demanda en Alumbrado:** Se asume un FD de $1.00$ ($100\%$) debido a que en una vivienda pequeña de 40 m² por piso es factible tener gran parte de la iluminación encendida en horas de la tarde/noche.
2. **Carga en Cocina:** Se asume que no existen cocinas eléctricas de inducción o de alta potencia (las cuales requerirían alimentación trifásica o calibres mucho mayores). Los tomacorrientes de cocina atienden pequeños artefactos de cocina y refrigeradora.
3. **Cargas Especiales:** Se asume que la vivienda no cuenta con sistemas centralizados de aire acondicionado, calefacción o termas de gran capacidad que excedan la potencia residencial contratada monofásica.
