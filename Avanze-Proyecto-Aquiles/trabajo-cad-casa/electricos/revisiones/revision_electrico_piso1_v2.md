# Revision electrica preliminar - Piso 1 v2

## Motivo de la correccion

Correccion solicitada por revision visual del usuario sobre `electrico_piso1_v1`:

- Mover el medidor `M` al punto marcado en rojo, al exterior derecho de la planta.
- Mover el tablero general `TG` al punto marcado en azul, sobre el lateral derecho de la planta.
- Reubicar interruptores hacia el interior de cada ambiente segun corresponda.

## Cambios aplicados

- `TG` reubicado a coordenadas aproximadas `(14.35, 4.75)`.
- `M` reubicado a coordenadas aproximadas `(15.45, 4.75)`.
- Alimentador `M-TG` ajustado como trazo horizontal corto entre medidor y tablero.
- Rutas `C1`, `C2`, `C3` y `C8` actualizadas para salir desde la nueva ubicacion del `TG`.
- Interruptores `S-P1-01` a `S-P1-05` reubicados hacia el interior de los ambientes.

## Archivos generados

- `../data/electrico_piso1_v2.json`
- `../salidas/electrico_piso1_v2.dxf`
- `../salidas/electrico_piso1_v2.pdf`
- `../temp/electrico_piso1_v2_landscape-1.png`

## Revision visual

El PDF se genero en A4 horizontal y fue renderizado a PNG. Se verifico que:

- El medidor aparece en el lado derecho exterior.
- El tablero general aparece en el punto lateral derecho indicado.
- Los interruptores ya no quedan fuera de los ambientes principales.
- La planta arquitectonica base `piso1_v3.dxf` se mantiene.

## Observaciones pendientes

- Confirmar en campo si el medidor puede instalarse exactamente en esa fachada.
- Confirmar altura y accesibilidad del tablero general.
- Confirmar sentido real de apertura de puertas para afinar lado exacto de interruptores.

## Estado

Aprobado con observaciones como correccion preliminar del Piso 1.
