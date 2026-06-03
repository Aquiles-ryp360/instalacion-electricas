# MEMORIA DE CALCULO

## Instalaciones electricas interiores - vivienda unifamiliar

Proyecto academico para vivienda de tres niveles en Jr. Lima S/N, Capachica, Puno. Sistema monofasico 220 V, 60 Hz.

## Circuitos adoptados

La revision reemplaza la sectorizacion anterior de cinco circuitos por nueve circuitos:

| Circuito | Uso | Potencia instalada | Factor | Demanda |
| --- | --- | ---: | ---: | ---: |
| C1 | Alumbrado primer piso | 72 W | 1.00 | 72 W |
| C2 | Tomacorrientes generales primer piso | 900 W | 0.70 | 630 W |
| C3 | Cocina | 1200 W | 0.80 | 960 W |
| C4 | Alumbrado segundo piso | 60 W | 1.00 | 60 W |
| C5 | Tomacorrientes generales segundo piso | 1620 W | 0.70 | 1134 W |
| C6 | Alumbrado tercer piso | 96 W | 1.00 | 96 W |
| C7 | Tomacorrientes generales tercer piso | 1260 W | 0.70 | 882 W |
| C8 | Lavanderia | 360 W | 0.80 | 288 W |
| C9 | Bomba de agua | 750 W | 1.00 | 750 W |

Potencia instalada total: 6318 W.

Maxima demanda estimada: 4872 W.

## Corriente de diseno

Formula:

```text
I = P / (V x fp)
```

Con P = 4872 W, V = 220 V y fp = 0.90:

```text
I = 4872 / (220 x 0.90) = 24.61 A
```

Se adopta interruptor general 2P-40A como criterio academico con reserva. La seleccion final debe verificarse con longitud real, metodo de instalacion, temperatura, agrupamiento y tablas aplicables del CNE-U.

## Conductores y protecciones preliminares

| Circuito | Proteccion | Conductor preliminar |
| --- | --- | --- |
| Alimentacion general | 2P-40A | 2 x 10 mm2 Cu + PE |
| C1, C4, C6 | 2P-10A | 3 x 1.5 mm2 Cu |
| C2, C5, C7 | 2P-16A | 3 x 2.5 mm2 Cu |
| C3 | 2P-20A | 3 x 2.5 mm2 Cu, verificar si aumenta la carga real |
| C8 | 2P-16A | 3 x 2.5 mm2 Cu |
| C9 | 2P-16A | 3 x 2.5 mm2 Cu |

Los circuitos de tomacorrientes y los puntos en zonas humedas deben contar con conductor de proteccion y proteccion diferencial segun el criterio final del tablero.

## Observaciones tecnicas

- Los datos de carga coinciden con los puntos dibujados en los planos IE-02, IE-03 e IE-04.
- La cocina, lavanderia y bomba se mantienen como cargas diferenciadas.
- Los banos incorporan tomacorriente protegido y deben ubicarse fuera de zonas de salpicadura directa.
- El sistema de puesta a tierra se representa de forma referencial y debe verificarse mediante medicion en campo.
