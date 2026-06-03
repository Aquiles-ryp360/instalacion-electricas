# Revision electrico piso 2 v3

## Fuente usada

La version v3 se trabajo tomando como base directa el DXF manual:

`Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso2_v2.dxf`

No se regenero el plano desde el JSON anterior. Primero se extrajeron entidades reales del DXF actual y se dejo respaldo en:

`Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/backup_electrico_piso2_v2_manual.dxf`

## Extraccion desde DXF v2

Archivo de auditoria:

`Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/data/electrico_piso2_v2_extraido_desde_dxf.json`

Entidades levantadas:

- Capas detectadas: 19
- Textos detectados: 90
- Lineas electricas existentes detectadas: 17
- Luminarias: 11
- Interruptores: 7
- Tomacorrientes simples/con tierra: 12
- Tomacorrientes especiales en polilinea tipo rombo: 4
- Tablero T2: 1
- Ducto vertical VD: 1
- Simbolos electricos principales detectados: 36

## Modificaciones manuales preservadas

Se mantuvieron las posiciones manuales reales del DXF v2 para:

- Interruptores existentes.
- Tomacorrientes existentes.
- Luminarias principales.
- Tablero T2.
- Ducto vertical VD.
- Textos arquitectonicos y mobiliario base.

Solo se movio ligeramente el rotulo de lavadora/C7 para despejar la ruta C6/C7 en la zona de cocina-servicio.

## Lineas reordenadas

Se reordenaron 7 rutas principales existentes del DXF v2:

- Subida TG-T2.
- C4 alumbrado.
- C5 tomacorrientes.
- Tres rutas C6 cocina/servicio.
- C7 lavadora.

En v3 esas rutas se redibujaron como 19 polilineas separadas con recorridos ortogonales, offsets visuales y linetype `DASHED` para los circuitos discontinuos.

## Cambios en cocina y servicio

- Se eliminaron los recorridos diagonales que cruzaban la cocina y confundian C4, C5, C6 y C7.
- C6 cocina/servicio quedo separado con tres tramos claros: troncal, servicio bajo y servicio alto.
- C7 lavadora quedo independiente por un corredor inferior distinto.
- La subida TG-T2 se mantuvo, pero con recorrido separado de C6/C7.
- Se evitaron rutas montadas entre cocina, servicio, lavadora y tablero.

## Simbolos corregidos

Se reviso visualmente `herramientas/Simbologia-electrica/S-Seccion9.pdf`.

Referencias usadas:

- 09-93-17: tomacorriente con puesta a tierra, simbolo circular con lineas internas y marca de tierra.
- 09-93-18: salida trifasica para cocina, simbolo circular con tres lineas internas y letra/codigo.
- 09-93-30: interruptor unipolar.
- 09-93-51: salida para lampara/foco en techo.

Cambios aplicados:

- Se sustituyeron 4 rombos especiales en planta por simbolos circulares tipo Seccion 9.
- Los puntos C6 de servicio se marcaron como `TE`.
- El punto C6 de cocina se marco como `C`.
- El punto C7 de lavadora se marco como `L`.
- La leyenda ya no usa rombo para toma especial.

## Leyenda electrica

La leyenda fue reconstruida para coincidir con lo dibujado:

- Punto para foco.
- Interruptor simple.
- Tomacorriente con tierra.
- Toma especial cocina/servicio.
- Salida especial lavadora.
- Tablero segundo piso T2.
- Ducto vertical VD.
- Linea C4 alumbrado.
- Linea C5 tomacorrientes.
- Linea C6 cocina/servicio.
- Linea C7 lavadora.
- Subida/bajada TG-T2.
- Canalizacion empotrada.

## Comparacion antes/despues

Antes:

`Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/temp/electrico_piso2_v2_antes_revision.png`

Despues:

`Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/temp/electrico_piso2_v3_landscape.png`

Salida final:

`Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso2_v3.dxf`

`Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso2_v3.pdf`

## Revision visual final

Se reviso el PNG final exportado desde el PDF de QCAD. La cocina queda con C6/C7 separados, los especiales son legibles, la leyenda coincide con los simbolos y los circuitos principales siguen presentes.

## Pendientes o dudas

- Algunos textos arquitectonicos quedan muy suaves en el PDF por el estilo de impresion de capas existente, pero no se alteraron para preservar la base manual.
- La confirmacion exacta de carga/equipo para cada punto especial puede ajustarse si se entrega una lista definitiva de artefactos.
