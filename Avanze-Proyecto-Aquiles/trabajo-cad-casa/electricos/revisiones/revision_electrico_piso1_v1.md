# Revision electrica preliminar - Piso 1 v1

## Base arquitectonica

- Archivo base: `../../salidas/piso1_v3.dxf`.
- Fuente arquitectonica: croquis limpio de Piso 1 y ajuste CAD v3.

## Ambientes reconocidos

- Escalera.
- Ambiente superior 1.
- Ambiente superior 2.
- Garage o ambiente amplio inferior.
- Zona de fachada/ingreso.
- Punto exterior asociado a bomba o pozo.

## Puntos colocados

- Luminarias: 6, todas asignadas a `C1`.
- Interruptores: 5, asignados a `C1`.
- Tomacorrientes: 9.
- Tablero general: 1, identificado como `TG`.
- Medidor: 1, identificado como `M`.
- Equipo exterior: 1 punto de bomba, asignado a `C8`.

## Circuitos asignados

- `C1`: alumbrado del primer piso.
- `C2`: tomacorrientes generales del primer piso.
- `C3`: toma auxiliar de cocina o servicio, por confirmar.
- `C8`: bomba exterior.

## Rutas dibujadas

- Alimentador `M` a `TG`.
- Ruta referencial de alumbrado `C1`.
- Ruta referencial de tomacorrientes `C2`.
- Ruta referencial de toma auxiliar `C3`.
- Ruta referencial exterior hacia bomba `C8`.

## Dudas

- Confirmar si el ambiente inferior es garage, tienda, deposito o sala.
- Confirmar uso real de los dos ambientes superiores.
- Confirmar ubicacion real del medidor y tablero general.
- Confirmar si existe bomba de agua exterior y su potencia.
- Confirmar si el punto `C3` corresponde a cocina, servicio o queda eliminado.

## Correcciones necesarias para v2

- Ajustar etiquetas si Aquiles confirma nombres de ambientes.
- Reubicar `TG` y `M` si la acometida real esta en otra fachada.
- Refinar rutas para reducir cruces y acercarlas a muros/cajas de paso.
- Aumentar contraste de textos electricos si el PDF se imprime tenue.

## Estado

Aprobado con observaciones como plano electrico preliminar para revision, no apto aun para ejecucion.
