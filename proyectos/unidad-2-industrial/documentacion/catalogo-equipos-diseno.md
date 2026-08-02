# Equipos de referencia para el calculo

Fecha de consulta: 2026-08-01. Los modelos sirven para fijar potencias y
requisitos electricos creibles mientras no existan placas del establecimiento.
No constituyen una orden de compra ni se presentaran como equipos instalados.

## Bombas sumergibles de combustible

- Familia: FE PETRO, bomba sumergible fija de 1 1/2 hp.
- Fuente primaria: [Franklin Electric Fueling Systems](https://www.franklinfueling.com/en/products/submersible-pumping/4-submersible-pumps/1-hp-fixed-speed/).
- Variante util: 60 Hz, 208-230 V monofasica; corriente maxima 11 A y potencia
  mecanica nominal 1,1 kW.
- Criterio: una bomba por tanque, cuatro en total, 2,42 kVA y factor de potencia
  0,75 por unidad, en circuitos individuales de 220 V.

## Cabeza electronica de surtidor

- Familia de referencia: Gilbarco Veeder-Root Prime PHX/ARLA.
- Fuente primaria: [Gilbarco Veeder-Root](https://www.gilbarco.com/br/solucoes/bombas-de-combustivel/prime-phx-arla).
- Datos: 220 V, 50/60 Hz, 103 VA; el fabricante pide UPS de salida senoidal para
  la cabeza electronica.
- Criterio: seis circuitos de 103 VA, uno por surtidor, desde UPS-FUEL de 3 kVA.
  La potencia de bombeo se calcula por separado en las cuatro STP.

## Compresor y bombas de servicio

- Compresor: referencia [Atlas Copco LE3](https://www.atlascopco.com/content/dam/atlas-copco/local-countries/india/documents/LE-LT-LF-LB_antwerp_leaflet_EN_2935084649.pdf), 2,2 kW para un equipo de 3 hp con prestaciones publicadas para 50/60 Hz. Se adopta equivalente trifasico 380 V, 60 Hz y 2,75 kVA.
- Bombas de agua/efluentes: contraste [Grundfos](https://api.grundfos.com/literature/Grundfosliterature-3081235.pdf), con 1,1 kW de salida, 1,5 kW de entrada y variante 3 x 380-480 V, 60 Hz. Se adoptan dos bombas de 1,875 kVA sujetas al proyecto sanitario.

## Grupo electrogeno

- Familia: [Cummins C30D6](https://www.cummins.com/en-na/generators/products/c30d6), 60 Hz, 33,8 kVA/27 kW prime y 37,5 kVA/30 kW standby.
- Altitud de calculo: 3 830 m s.n.m., referencia oficial de la capital de
  Caracoto; debe verificarse en el predio.
- Correccion inicial: 3 % por cada 500 m por encima de 1 000 m, tomada de ficha
  Stamford/Cummins; factor aproximado 0,830.
- El calculo verifica carga permanente, arranque secuencial de una STP y margen.
  El proveedor debe confirmar la desclasificacion conjunta de motor, alternador
  y refrigeracion antes de compra.

## Criterios sin marca cerrada

- Luminarias LED: el calculo fijara flujo, potencia, distribucion e IP; se exige
  ficha IES/LDT antes de construccion.
- Refrigeracion de minimarket: dos circuitos equivalentes de 1,36 kW cada uno;
  son cargas de diseno, no equipos observados.
- Tomacorrientes y oficina: cargas agrupadas con simultaneidad justificada.
- Todo equipo en area clasificada requiere certificado y marcado compatible.
  Una potencia de catalogo no valida por si sola su uso en Zona 0/1/2.
