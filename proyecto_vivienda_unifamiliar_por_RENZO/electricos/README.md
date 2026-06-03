# Electricos - vivienda unifamiliar

## Criterio de organizacion

La carpeta contiene los datos, salidas y revisiones de los planos electricos regenerados para el proyecto de vivienda unifamiliar de Renzo Gabriel Mamani Galindo.

- `data/`: JSON fuente con puntos electricos, circuitos y referencias a los DXF arquitectonicos vigentes.
- `salidas/`: DXF y PDF revisables generados por la herramienta.
- `revisiones/`: auditoria tecnica y revision visual por plano.
- `temp/`: archivos temporales de revision.

## Base arquitectonica vigente

Se usan como base:

- `planos_cad/primer_piso_v3.dxf`
- `planos_cad/segundo_piso_v3.dxf`
- `planos_cad/tercer_piso_v3.dxf`

Los JSON de layout se usan para posicionar puntos electricos y rotular ambientes, pero las entidades arquitectonicas de muros, puertas, ventanas y escaleras se importan desde los DXF vigentes.

## Circuitos adoptados

| Circuito | Uso | Proteccion preliminar | Conductor |
| --- | --- | --- | --- |
| C1 | Alumbrado primer piso | 2P-10A | 3 x 1.5 mm2 Cu |
| C2 | Tomacorrientes generales primer piso | 2P-16A | 3 x 2.5 mm2 Cu |
| C3 | Cocina | 2P-20A | 3 x 2.5 mm2 Cu |
| C4 | Alumbrado segundo piso | 2P-10A | 3 x 1.5 mm2 Cu |
| C5 | Tomacorrientes generales segundo piso | 2P-16A | 3 x 2.5 mm2 Cu |
| C6 | Alumbrado tercer piso | 2P-10A | 3 x 1.5 mm2 Cu |
| C7 | Tomacorrientes generales tercer piso | 2P-16A | 3 x 2.5 mm2 Cu |
| C8 | Lavanderia | 2P-16A | 3 x 2.5 mm2 Cu |
| C9 | Bomba de agua | 2P-16A | 3 x 2.5 mm2 Cu |

## Simbologia usada

- Luminaria de techo: circulo con cruz.
- Interruptor simple: circulo pequeno con etiqueta S.
- Interruptor conmutado: circulo pequeno con etiqueta S3.
- Tomacorriente doble con tierra: circulo con trazo horizontal y vertical.
- Tomacorriente protegido: simbolo de tomacorriente con etiqueta P.
- Tomacorriente especial/bomba: simbolo de tomacorriente con etiqueta E.
- Tablero general/subtablero: rectangulo rotulado TG-01, TD-01 o TD-02.
- Medidor: circulo rotulado M.
- Puesta a tierra: simbolo de lineas decrecientes.
- Canalizacion: linea discontinua por circuito.

## Capas CAD

Los DXF electricos incluyen capas arquitectonicas y electricas: `ARQ_MUROS`, `ARQ_PUERTAS`, `ARQ_VENTANAS`, `ELEC_LUMINARIAS`, `ELEC_INTERRUPTORES`, `ELEC_TOMACORRIENTES`, `ELEC_TABLEROS`, `ELEC_MEDIDOR`, `ELEC_PUESTA_TIERRA`, `ELEC_TEXTOS`, `ELEC_LEYENDA`, `ELEC_ROTULO`, `MARCO` y `ELEC_CIRCUITO_C1` a `ELEC_CIRCUITO_C9`.

## Archivos finales

- `planos/IE-02-alumbrado.pdf`
- `planos/IE-03-tomacorrientes.pdf`
- `planos/IE-04-circuitos-canalizaciones.pdf`
- `planos_electricos/IE-02-alumbrado-v1.dxf`
- `planos_electricos/IE-03-tomacorrientes-v1.dxf`
- `planos_electricos/IE-04-circuitos-canalizaciones-v1.dxf`

Las copias previas de los PDF fueron conservadas como `salidas/*-original.pdf`.
