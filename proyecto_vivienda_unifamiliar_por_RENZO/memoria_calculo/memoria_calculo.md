# MEMORIA DE CÁLCULO
## DISEÑO Y JUSTIFICACIÓN TÉCNICA DE INSTALACIONES ELÉCTRICAS

### 1. CÁLCULO DE LA DEMANDA MÁXIMA
De acuerdo con las reglas de la **Sección 050-200** del Código Nacional de Electricidad - Utilización para viviendas unifamiliares:

#### A. Carga Básica por Área Techada (Regla 050-200(1)(a)(i)):
- **Área total:** 120 m² (Primer Piso: 40 m², Segundo Piso: 40 m², Tercer Piso: 40 m²).
- **Carga básica primeros 90 m²:** 2,500 W (F.D. 1.0)
- **Carga básica exceso sobre 90 m² (hasta 150 m²):** 1,000 W (F.D. 1.0)
- **Subtotal Carga Techada:** **3,500 W** (Máxima Demanda: 3,500 W)

#### B. Cargas Adicionales (Circuitos Derivados):
- **C3 (Cocina):** Potencia Instalada de 1,200 W (F.D. 0.80) -> Máxima Demanda = **960 W**
- **C4 (Lavandería):** Potencia Instalada de 360 W (F.D. 0.80) -> Máxima Demanda = **288 W**
- **C5 (Bomba de Agua - Carga Especial):** Motor de 1 HP = 750 W (F.D. 1.0) -> Máxima Demanda = **750 W**

#### C. Resumen de Potencia y Demanda Máxima:
- **Potencia Instalada Total (P.I.):** 132 (C1) + 2520 (C2) + 1200 (C3) + 360 (C4) + 750 (C5) = **4,962.00 W**
- **Máxima Demanda de Cálculo (M.D.):** 3,500 W (Carga Básica CNE) + 960 (C3) + 288 (C4) + 750 (C5) = **3,894.00 W** (Adoptamos el valor por circuitos que coincide con el levantamiento de cargas).

### 2. CÁLCULO DE LA CORRIENTE DE DISEÑO Y ALIMENTADOR
La corriente nominal del alimentador monofásico se calcula con la fórmula:
$$ I_n = \frac{P_{dem}}{V \times \cos \phi} $$

Donde:
- $P_{dem} = 3,894.00$ W
- $V = 220$ V (Monofásico)
- $\cos \phi = 0.90$ (Factor de potencia referencial)

$$ I_n = \frac{3,894.00}{220 \times 0.90} = 19.67 \text{ A} $$

Aplicando el **Factor de Seguridad de 1.25** (Regla CNE 050-204(2) para dimensionar alimentadores):
$$ I_d = I_n \times 1.25 = 19.67 \times 1.25 = 24.58 \text{ A} $$

#### Selección de Conductor Alimentador:
Consultando las tablas de capacidad del CNE-U para conductores tipo LSOH (o similar THW) en ducto empotrado:
- El conductor de **10 mm²** de sección tiene una capacidad admisible de corriente de **50 A** (en ducto empotrado, temperatura ambiente de 30°C).
- Dado que $I_z = 50 \text{ A} \geq I_d = 24.58 \text{ A}$, la sección de **10 mm² es adecuada por capacidad de corriente** y provee una reserva muy holgada para futuras ampliaciones de carga.

### 3. CÁLCULO DE LA CAÍDA DE TENSIÓN
La caída de tensión ($dV$) para circuitos monofásicos se calcula mediante la fórmula:
$$ dV = \frac{2 \times L \times I_n \times \rho}{S} $$

Donde:
- $L = 12.00$ m (Longitud estimada de la acometida al tablero general)
- $I_n = 19.67$ A (Corriente nominal de funcionamiento)
- $\rho = 0.0178 \text{ Ohm}\cdot\text{mm}^2/\text{m}$ (Resistividad del cobre a 20ºC)
- $S = 10 \text{ mm}^2$ (Sección del conductor seleccionado)

$$ dV = \frac{2 \times 12.00 \times 19.67 \times 0.0178}{10} = 0.84 \text{ V} $$

Expresado en porcentaje:
$$ dV \% = \left( \frac{dV}{V} \right) \times 100 = \left( \frac{0.84}{220} \right) \times 100 = 0.38 \% $$

- **Límite Normativo (Regla 050-102 CNE):** La caída de tensión en el alimentador no debe exceder el **2.5%**.
- **Evaluación:** Dado que $0.38 \% \leq 2.5 \%$, **la sección seleccionada de 10 mm² cumple satisfactoriamente por caída de tensión**.

### 4. SELECCIÓN DE LAS PROTECCIONES
La coordinación conductor-protección se realiza bajo la regla:
$$ I_b \leq I_n \leq I_z $$

Donde:
- $I_b$: Corriente de diseño del circuito (nominal).
- $I_n$: Corriente nominal del interruptor termomagnético.
- $I_z$: Capacidad de corriente del conductor seleccionado.

#### A. Interruptor General (TG-01):
- $I_b = 19.67 \text{ A}$, $I_z = 50 \text{ A}$ (para conductor de 10 mm²).
- Seleccionamos un interruptor de **2P-40A**.
- **Coordinación:** $19.67 \text{ A} \leq 40 \text{ A} \leq 50 \text{ A}$ (CUMPLE).

#### B. Circuito C1 (Alumbrado):
- Conductor: 1.5 mm² ($I_z = 15 \text{ A}$ en ducto).
- Carga: 132 W ($I_b = 0.67 \text{ A}$).
- Seleccionamos ITM de **2P-10A**.
- **Coordinación:** $0.67 \text{ A} \leq 10 \text{ A} \leq 15 \text{ A}$ (CUMPLE).

#### C. Circuito C2 (Tomacorrientes Generales):
- Conductor: 2.5 mm² ($I_z = 20 \text{ A}$ en ducto).
- Carga: 2,520 W ($I_b = 8.91  \text{ A}$ aplicando factor de demanda).
- Seleccionamos ITM de **2P-16A**.
- **Coordinación:** $8.91 \text{ A} \leq 16 \text{ A} \leq 20 \text{ A}$ (CUMPLE).
- Adicionalmente se asocia a un Interruptor Diferencial (ID) de **2P-25A-30mA** para protección contra corrientes de fuga a tierra.

#### D. Circuito C3 (Cocina):
- Conductor: 2.5 mm² ($I_z = 20  \text{ A}$).
- Carga: 1200 W ($I_b = 4.85 \text{ A}$ aplicando factor de demanda).
- Seleccionamos ITM de **2P-20A** (permite holgura por arranque de pequeños motores y electrodomésticos portátiles de cocina).
- **Coordinación:** $4.85 \text{ A} \leq 20 \text{ A} \leq 20 \text{ A}$ (coordinación límite, aceptable según CNE).

#### E. Circuito C4 y C5 (Lavandería y Bomba):
- Conductor: 2.5 mm² ($I_z = 20 \text{ A}$).
- Protecciones: ITM de **2P-16A** e Interruptor Diferencial de **2P-25A-30mA** (CUMPLE).
