# Memoria Tecnica Del Proyecto Electrico

**Proyecto:** Instalaciones electricas de vivienda unifamiliar de 3 pisos
**Responsable:** Renzo Gabriel Mamani Galindo
**Ubicacion referencial:** Jr. Lima S/N, Capachica, Puno
**Base de diseno:** `diseno-electrico/datos/modelo-electrico.json`

## 1. Alcance

El proyecto comprende las instalaciones electricas interiores de una vivienda unifamiliar de tres niveles con suministro monofasico de 220 V, 60 Hz. Incluye tablero general, tableros secundarios, circuitos de alumbrado, tomacorrientes, protecciones termomagneticas y diferenciales, canalizaciones empotradas y sistema de puesta a tierra.

No se incluye circuito dedicado de electrobomba ni cargas industriales dentro del modelo electrico interior vigente.

## 2. Normativa Y Criterios

- Codigo Nacional de Electricidad - Utilizacion.
- Reglamento Nacional de Edificaciones, especialidad EM.010.
- Criterios NEC como apoyo academico para coordinacion de protecciones, puesta a tierra y seguridad de tomacorrientes.
- Factor de potencia de calculo: 0.90.
- Resistencia objetivo del pozo de tierra: menor a 15 ohm, verificable en obra.

## 3. Tableros

| Tablero | Ubicacion | Circuitos asociados | Funcion |
| --- | --- | --- | --- |
| TG-01 | Primer piso | C1, C2, C3 | Tablero general y proteccion principal |
| TD-02 | Segundo piso | C4, C5 | Subtablero del segundo nivel |
| TD-03 | Tercer piso | C6, C7 | Subtablero del tercer nivel |

## 4. Cuadro De Cargas Vigente

| Cto. | Piso | Uso | Pot. inst. (W) | F.D. | Max. dem. (W) | I dem. (A) | Proteccion | Conductor |
| --- | :---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| C1 | 1 | Alumbrado primer piso | 500 | 1.00 | 500 | 2.53 | 2P-10A | 3 x 1.5 mm2 Cu |
| C2 | 1 | Tomacorrientes generales primer piso | 1000 | 1.00 | 1000 | 5.05 | 2P-16A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| C3 | 1 | Tomacorrientes especiales de cocina | 1500 | 1.00 | 1500 | 7.58 | 2P-20A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| C4 | 2 | Alumbrado segundo piso | 500 | 1.00 | 500 | 2.53 | 2P-10A | 3 x 1.5 mm2 Cu |
| C5 | 2 | Tomacorrientes generales segundo piso | 1500 | 0.70 | 1050 | 5.30 | 2P-16A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| C6 | 3 | Alumbrado tercer piso | 500 | 1.00 | 500 | 2.53 | 2P-10A | 3 x 1.5 mm2 Cu |
| C7 | 3 | Tomacorrientes generales tercer piso | 1500 | 0.70 | 1050 | 5.30 | 2P-16A + ID 25A/30mA | 3 x 2.5 mm2 Cu |
| **Total** |  | **Vivienda unifamiliar** | **7000** |  | **6100** | **30.81** | **2P-40A general** | **2 x 10 mm2 Cu + PE** |

La corriente de demanda se obtiene con:

```text
I = P / (V x cos phi)
I = 6100 / (220 x 0.90) = 30.81 A
```

Se adopta interruptor termomagnetico general de 2P-40A e interruptor diferencial general de 2P-40A/30mA.

## 5. Conteo De Puntos

| Nivel | Luminarias | Interruptores | Tomacorrientes | Total |
| --- | ---: | ---: | ---: | ---: |
| Primer piso | 7 | 5 | 8 | 20 |
| Segundo piso | 6 | 5 | 8 | 19 |
| Tercer piso | 6 | 6 | 8 | 20 |
| **Total** | **19** | **16** | **24** | **59** |

## 6. Conductores Y Canalizaciones

- Alumbrado C1, C4 y C6: 3 x 1.5 mm2 Cu, canalizacion PVC 3/4 in, proteccion 2P-10A.
- Tomacorrientes C2, C5 y C7: 3 x 2.5 mm2 Cu, canalizacion PVC 3/4 in, proteccion 2P-16A con diferencial 25A/30mA.
- Cocina C3: 3 x 2.5 mm2 Cu, canalizacion PVC 3/4 in, proteccion 2P-20A con diferencial 25A/30mA.
- Alimentador general: 2 x 10 mm2 Cu + PE en PVC 1 in, protegido por 2P-40A.
- Subalimentadores a TD-02 y TD-03: 3 x 4 mm2 Cu, protegidos por 2P-25A.

## 7. Puesta A Tierra

El sistema de puesta a tierra contempla varilla Copperweld de 5/8 in x 2.40 m, caja de registro, conector split-bolt, conductor de enlace de cobre de 6 mm2 hasta la barra de tierra del TG-01 y tratamiento del pozo con gel o bentonita. La resistencia debe medirse en obra y quedar por debajo de 15 ohm.

## 8. Cierre Tecnico

El modelo vigente queda definido por siete circuitos C1-C7, tres tableros TG-01, TD-02 y TD-03, potencia instalada de 7000 W y demanda maxima de 6100 W. Los documentos de metrado, presupuesto, planos y requerimientos deben conservar estos valores como referencia unica.
