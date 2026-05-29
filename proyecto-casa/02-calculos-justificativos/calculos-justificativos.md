# Capitulo II: Calculos justificativos

## 2.1 Normas aplicables

- Codigo Nacional de Electricidad - Utilizacion.
- RNE EM.010 Instalaciones Electricas Interiores.
- Criterios del curso de Instalaciones Electricas I.
- Requisitos de la empresa distribuidora, si se incluye acometida o medidor.

> EDITAR AQUI: completar numerales exactos cuando el grupo revise las normas.

## 2.2 Caracteristicas electricas del sistema

| Parametro | Valor preliminar |
|---|---|
| Tension nominal | 220 V |
| Frecuencia | 60 Hz |
| Sistema | Monofasico |
| Factor de potencia adoptado | 0.90 |
| Tipo de instalacion | Interior domiciliaria |
| Material de conductor | Cobre |

## 2.3 Levantamiento de cargas

El levantamiento se realiza por ambiente. Para cada carga se registra cantidad, potencia unitaria y circuito asignado.

Formula:

```text
Potencia total por carga = cantidad x potencia unitaria
Potencia instalada total = suma de potencias de todas las cargas
```

La tabla editable se encuentra en `../cargas-electricas.md`.

## 2.4 Maxima demanda

Para el mini proyecto se puede estimar la demanda con un factor de demanda o simultaneidad definido por el docente.

Formula:

```text
Maxima demanda = potencia instalada x factor de demanda
```

Valores preliminares sugeridos para calculo academico:

| Tipo de carga | Factor preliminar |
|---|---:|
| Alumbrado | 1.00 |
| Tomacorrientes generales | 0.70 |
| Cocina/lavanderia | 0.80 |
| Cargas especiales | 1.00 |

> EDITAR AQUI: reemplazar estos factores si el docente entrega tabla especifica.

## 2.5 Corriente de diseno

Para sistema monofasico:

```text
I = P / (V x fp)
```

Donde:

- `I`: corriente en amperios.
- `P`: potencia demandada en watts.
- `V`: tension en volts.
- `fp`: factor de potencia.

## 2.6 Seleccion de circuitos

Separacion minima recomendada para el proyecto:

| Circuito | Uso | Criterio |
|---|---|---|
| C1 | Alumbrado | Separar luminarias de tomacorrientes |
| C2 | Tomacorrientes generales | Dormitorios, sala, comedor y circulacion |
| C3 | Cocina | Tomacorrientes de mayor uso o cargas de cocina |
| C4 | Lavanderia | Lavadora, plancha u otras cargas |
| C5 | Carga especial | Ducha electrica, terma, horno, bomba u otra carga definida |

## 2.7 Seleccion de conductor

La seleccion final debe verificarse con tablas del CNE-U segun tipo de conductor, aislamiento, canalizacion, temperatura y agrupamiento.

Tabla preliminar para trabajo academico:

| Corriente de diseno | Conductor cobre sugerido | Uso tipico |
|---:|---|---|
| Hasta 10 A | 1.5 mm2 | Alumbrado |
| Hasta 16 A | 2.5 mm2 | Tomacorrientes generales |
| Hasta 25 A | 4 mm2 | Cargas medianas |
| Hasta 32 A | 6 mm2 | Cargas especiales |
| Hasta 40 A | 10 mm2 | Alimentador o carga mayor |

> EDITAR AQUI: ajustar segun tabla normativa revisada y criterio del docente.

## 2.8 Seleccion de interruptor termomagnetico

Criterio general:

```text
Ib <= In <= Iz
```

Donde:

- `Ib`: corriente de diseno del circuito.
- `In`: corriente nominal del interruptor.
- `Iz`: capacidad admisible del conductor.

Tabla preliminar:

| Circuito | Proteccion preliminar |
|---|---|
| Alumbrado | 10 A |
| Tomacorrientes generales | 16 A o 20 A segun carga y conductor |
| Cocina/lavanderia | 20 A o 25 A segun carga y conductor |
| Carga especial | Segun placa del equipo |

## 2.9 Verificacion de caida de tension

Formula simplificada monofasica:

```text
Delta V = (2 x L x I x rho) / S
%Delta V = (Delta V / V) x 100
```

Donde:

- `L`: longitud del circuito en metros.
- `I`: corriente en amperios.
- `rho`: resistividad del cobre, valor referencial 0.0175 ohm mm2/m.
- `S`: seccion del conductor en mm2.
- `V`: tension del sistema.

> EDITAR AQUI: verificar limite permitido con CNE-U o criterio del docente.

## 2.10 Puesta a tierra

Elementos minimos a definir:

- Electrodo o varilla de puesta a tierra.
- Conductor de puesta a tierra.
- Barra de tierra en tablero.
- Conexion de conductor de proteccion a tomacorrientes con tierra.
- Medicion o valor objetivo de resistencia de puesta a tierra, si el curso lo exige.

## 2.11 Cuadro resumen de calculos

| Circuito | Potencia W | Factor | Demanda W | Corriente A | Longitud m | Conductor | Caida % | Proteccion |
|---|---:|---:|---:|---:|---:|---|---:|---|
| C1 | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI |
| C2 | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI |
| C3 | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI | EDITAR AQUI |

