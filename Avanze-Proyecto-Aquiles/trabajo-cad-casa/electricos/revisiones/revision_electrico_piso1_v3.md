# Revision electrica preliminar - Piso 1 v3

## Problemas corregidos respecto a v2

- Interruptores que visualmente quedaban demasiado cerca del vano, arco o trayectoria de puerta.
- Etiquetas largas de `TG` y `M` que se encimaban en la zona derecha.
- Rutas con diagonales largas y cruces visualmente confusos.
- Tramos de canalizacion que no se veian como recorridos tecnicos preliminares.

## Interruptores revisados

- `S-P1-01`: asociado a escalera. Se ajusto dentro de la zona util, fuera del vano.
- `S-P1-02`: asociado al ambiente superior 1. Se movio hacia el interior, por encima del vano y fuera del arco.
- `S-P1-03`: asociado al ambiente superior 2. Se movio hacia el interior del ambiente, fuera del arco de puerta.
- `S-P1-04`: asociado al garage o ambiente inferior derecho. Se dejo junto al ingreso interior, sin invadir el arco.
- `S-P1-05`: asociado al ambiente inferior izquierdo. Se acerco al muro lateral interior para que no quede flotando.

## Criterio usado respecto a puertas

Se uso el arco dibujado en el plano como referencia visual. Cuando el sentido exacto de apertura no estaba confirmado, el interruptor se coloco del lado mas accesible al ingresar y fuera de:

- vano de puerta;
- arco de apertura;
- trayectoria de la hoja;
- textos arquitectonicos principales.

## Rutas limpiadas

- `C1`: separado en dos tramos ortogonales para alumbrado superior e inferior.
- `C2`: separado en dos tramos ortogonales para tomacorrientes superiores e inferiores.
- `C3`: corregido con remate ortogonal hacia el tomacorriente especial de cocina/servicio.
- `C8`: corregido con salida clara desde `TG` hacia bomba exterior, sin diagonal larga.
- `M-TG`: se mantuvo como tramo horizontal corto.

## Elementos mantenidos sin mover

- `TG` permanece en la ubicacion validada de v2: aproximadamente `(14.35, 4.75)`.
- `M` permanece en la ubicacion validada de v2: aproximadamente `(15.45, 4.75)`.
- El alimentador `M-TG` permanece horizontal y corto.
- La base arquitectonica sigue siendo `piso1_v3.dxf`.

## Revision visual

Se genero `electrico_piso1_v3.pdf` en A4 horizontal y se renderizo a PNG. La revision visual confirma:

- Ningun interruptor queda en medio de una puerta.
- Ningun interruptor queda sobre un arco de apertura.
- Los interruptores se leen junto a ingresos o muros interiores.
- `TG` y `M` mantienen la ubicacion validada por el usuario.
- `C8` llega a la bomba exterior.
- Las rutas son mas ortogonales y limpias que en v2.
- La leyenda no tapa la planta.
- QCAD importo el DXF y exporto el PDF correctamente.

## Archivos generados

- `../data/electrico_piso1_v3.json`
- `../salidas/electrico_piso1_v3.dxf`
- `../salidas/electrico_piso1_v3.pdf`
- `../temp/electrico_piso1_v3_landscape-1.png`

## Pendiente

- Confirmar sentido definitivo de puertas.
- Confirmar uso real de los ambientes del primer piso.
- Confirmar si `C3` corresponde a cocina, servicio o se elimina.
- Confirmar potencia y ubicacion exacta de bomba exterior `C8`.

## Veredicto

APROBADO CON OBSERVACIONES como plano electrico preliminar del primer piso.
