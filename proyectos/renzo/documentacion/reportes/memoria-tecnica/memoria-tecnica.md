# MEMORIA TECNICA Y CALCULOS JUSTIFICATIVOS
## Proyecto: Instalacion Electrica Residencial - Vivienda Unifamiliar de 3 Pisos

### 1. Normas De Referencia Y Criterios De Diseno

El diseno de la instalacion electrica se basa en el Codigo Nacional de Electricidad - Utilizacion, el Reglamento Nacional de Edificaciones EM.010 y criterios NEC usados como apoyo academico para coordinacion de conductores, protecciones y puesta a tierra.

### 2. Parametros Electricos Del Sistema

- Tension de suministro: 220 V monofasico.
- Frecuencia: 60 Hz.
- Factor de potencia: 0.90.
- Alimentador principal: conductor de cobre de 10 mm2.
- Proteccion general: interruptor termomagnetico 2P-40A e interruptor diferencial 2P-40A/30mA.

### 3. Cuadro De Cargas Vigente

| Cto. | Piso | Uso | Pot. Inst. (W) | F.D. | Max. Dem. (W) | I dem (A) | Proteccion | Conductor |
| --- | :---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| C1 | 1 | Alumbrado primer piso | 500 | 1.00 | 500 | 2.53 | 2P-10A | 3 x 1.5 mm2 Cu |
| C2 | 1 | Tomacorrientes generales primer piso | 1000 | 1.00 | 1000 | 5.05 | 2P-16A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| C3 | 1 | Tomacorrientes especiales de cocina | 1500 | 1.00 | 1500 | 7.58 | 2P-20A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| C4 | 2 | Alumbrado segundo piso | 500 | 1.00 | 500 | 2.53 | 2P-10A | 3 x 1.5 mm2 Cu |
| C5 | 2 | Tomacorrientes generales segundo piso | 1500 | 0.70 | 1050 | 5.30 | 2P-16A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| C6 | 3 | Alumbrado tercer piso | 500 | 1.00 | 500 | 2.53 | 2P-10A | 3 x 1.5 mm2 Cu |
| C7 | 3 | Tomacorrientes generales tercer piso | 1500 | 0.70 | 1050 | 5.30 | 2P-16A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| **Total** |  | **Vivienda unifamiliar** | **7000** |  | **6100** | **30.81** | **2P-40A general** | **3 x 10 mm2 Cu + PE** |

### 4. Conteo De Puntos

| Nivel | Luminarias | Interruptores | Tomacorrientes | Total |
| --- | ---: | ---: | ---: | ---: |
| Primer piso | 7 | 5 | 8 | 20 |
| Segundo piso | 6 | 5 | 8 | 19 |
| Tercer piso | 6 | 6 | 8 | 20 |
| **Total** | **19** | **16** | **24** | **59** |

### 5. Corriente De Demanda

```text
I = P / (V x cos phi)
I = 6100 / (220 x 0.90) = 30.81 A
```

La proteccion general adoptada es 2P-40A. El alimentador de 10 mm2 mantiene holgura para la demanda calculada y permite coordinacion con el interruptor general.

### 6. Coordinacion Conductor-Proteccion

- Circuitos de alumbrado C1, C4 y C6: 3 x 1.5 mm2 Cu, protegidos con ITM 2P-10A.
- Circuitos de tomacorrientes C2, C5 y C7: 3 x 2.5 mm2 Cu, protegidos con ITM 2P-16A y diferencial 25A/30mA.
- Circuito de cocina C3: 3 x 2.5 mm2 Cu, protegido con ITM 2P-20A y diferencial 25A/30mA.
- Alimentador general: 3 x 10 mm2 Cu + PE, protegido con ITM 2P-40A y diferencial 40A/30mA.

### 7. Puesta A Tierra

Se adopta pozo de puesta a tierra con electrodo de cobre de 5/8 in x 2.40 m, conductor de enlace de 6 mm2 y resistencia objetivo menor a 15 ohm, sujeto a medicion en obra.
