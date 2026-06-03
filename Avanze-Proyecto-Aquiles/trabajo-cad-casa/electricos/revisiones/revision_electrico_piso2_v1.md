# Revision electrica preliminar - Piso 2 v1

## Base arquitectonica

- Archivo base: `../../salidas/piso2_v3.dxf`.
- Fuente arquitectonica: croquis limpio de Piso 2 y ajuste CAD v3.

## Ambientes reconocidos

- Escalera.
- Cocina grande.
- Oficina o ambiente varios.
- Cuarto con cama superior.
- Sala.
- Pasadizo.
- Bano.
- Cuarto con cama inferior.

## Puntos colocados

- Luminarias: 11, todas asignadas a `C4`.
- Interruptores: 7, asignados a `C4`.
- Tomacorrientes: 16.
- Subida referencial desde tablero general: 1 punto `VD`.
- Tablero de segundo piso: no definido en esta version.
- Medidor: no aplica en este piso.

## Circuitos asignados

- `C4`: alumbrado del segundo piso.
- `C5`: tomacorrientes generales del segundo piso.
- `C6`: cocina o carga especial del segundo piso, por confirmar.
- `C7`: lavadora del segundo piso.

## Rutas dibujadas

- Ruta referencial de alumbrado `C4` desde `VD`.
- Ruta referencial de tomacorrientes `C5` desde `VD`.
- Ruta referencial de cocina/carga especial `C6` desde `VD`.
- Ruta referencial de lavadora `C7` desde `VD`.

## Dudas

- Confirmar si habra subtablero en segundo piso o si todos los circuitos suben desde el `TG`.
- Confirmar si la cocina sera a gas o electrica.
- Confirmar ubicacion real de lavadora.
- Confirmar cantidad final de tomacorrientes en sala, dormitorios y cocina.
- Confirmar si el bano requiere tomacorriente y su ubicacion protegida.

## Correcciones necesarias para v2

- Separar graficamente mejor la zona de cocina si se confirma artefacto de alta potencia.
- Ajustar rutas alrededor de pasadizo y puertas cuando se definan cajas de paso.
- Reubicar `VD` si la subida de tuberia real no coincide con la escalera.
- Aumentar contraste de textos electricos si el PDF se imprime tenue.

## Estado

Aprobado con observaciones como plano electrico preliminar para revision, no apto aun para ejecucion.
