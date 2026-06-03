# Revision electrica preliminar - Piso 2 v2

## Motivo de la correccion

Correccion solicitada por revision visual del usuario sobre `electrico_piso2_v1`:

- Colocar el tablero del segundo piso en el punto marcado en azul.
- El segundo piso no debe contar con medidor.
- Reubicar interruptores hacia el interior de las habitaciones.
- Ordenar graficamente la zona de cocina para que no se vea enredada.

## Cambios aplicados

- Se agrego tablero `T2` en coordenadas aproximadas `(12.55, 4.25)`.
- Se elimino cualquier medidor del plano de segundo piso y de la leyenda.
- La leyenda ahora muestra `T2` como tablero de segundo piso.
- Los interruptores `S-P2-01` a `S-P2-07` se desplazaron hacia el interior de ambientes.
- Las rutas de `C6` en cocina se dividieron en tramos mas cortos sin etiquetas repetidas.
- La ruta `C7` de lavadora se dejo sin etiqueta sobre la linea para reducir ruido visual.

## Archivos generados

- `../data/electrico_piso2_v2.json`
- `../salidas/electrico_piso2_v2.dxf`
- `../salidas/electrico_piso2_v2.pdf`
- `../temp/electrico_piso2_v2_landscape-1.png`

## Revision visual

El PDF se genero en A4 horizontal y fue renderizado a PNG. Se verifico que:

- `T2` aparece donde el usuario marco el punto azul.
- No aparece medidor en el segundo piso.
- No existe capa `ELEC_MEDIDOR` en el DXF v2.
- Los interruptores quedan dentro o junto al ingreso interior de los ambientes.
- La zona de cocina queda menos saturada que en v1.

## Observaciones pendientes

- Confirmar si realmente habra tablero de segundo piso o solo caja de paso/subida desde `TG`.
- Confirmar lado exacto de instalacion de interruptores segun sentido final de puertas.
- Confirmar si `C6` sera cocina electrica o solo tomacorrientes de servicio.
- Confirmar ubicacion definitiva de lavadora.

## Estado

Aprobado con observaciones como correccion preliminar del Piso 2.
