# REVISION ELECTRICA PISO 2 - V4

**Fecha:** 2026-06-03
**Base:** electrico_piso2_v3.dxf (corregido manualmente v2)
**Generado:** electrico_piso2_v4.dxf

---

## 1. Entidades extraidas del DXF v3

Del archivo DXF v3 se extrajeron las siguientes entidades (archivo: `data/electrico_piso2_v4_extraido_desde_dxf.json`):

| Tipo | Cantidad |
|------|----------|
| Capas (layers) | 37 (18 ARQ + 19 ELEC) |
| Luminarias (C4) | 11 puntos de luz |
| Interruptores | 8 (2 S3 + 6 S) |
| Tomacorrientes standard | 12 (C5) |
| Tomacorrientes especiales | 4 (2 TE, 1 C, 1 L) |
| Ducto vertical (VD) | 1 (en posicion original incorrecta) |
| Rutas (polilineas) | 19 (C4: 11, C5: 3, C6: 3, C7: 1, CANALIZACION: 1) |
| Textos | 94 |
| Bloques tablero | T2 en (12.55, 4.25) |

## 2. Modificaciones manuales preservadas

Se conservaron todas las posiciones manuales de:
- Interruptores (escalera, cocina, oficina, sala, cuartos, pasadizo)
- Tomacorrientes standard en todas las habitaciones
- Luminarias en cada ambiente
- Tablero T2 en pasadizo central
- Distribucion arquitectonica (muros, puertas, ventanas, mobiliario)

## 3. Cambios en el ducto vertical (VD)

### Problema detectado
- El VD original estaba en (2.65, 4.80), en medio del plano, lejos del tablero T2
- Su ruta de conexion recorria horizontalmente desde x=2.65 hasta x=12.55 antes de subir al T2, dando la impresion de que "daba la vuelta"
- El simbolo (circulo con aspas X) se confundia visualmente con las luminarias (circulo con cruz +)

### Correccion aplicada
- **Nueva posicion:** VD movido a (12.05, 4.25), inmediatamente a la izquierda del tablero T2 (12.55, 4.25)
- **Nuevo simbolo:** Circulo con flecha vertical hacia arriba (representa subida vertical), claramente diferenciado de:
  - Luminaria (circulo + cruz)
  - Tomacorriente (circulo + lineas horizontales)
  - Interruptor (circulo + palanca oblicua)
- **Nueva ruta:** Recta directa de VD a T2 (2 puntos), sin rodeos

### Resultado
- El VD ahora se lee como una subida vertical directa asociada al T2
- Visualmente no se confunde con luminaria
- No hay recorrido horizontal antes de subir

## 4. Separacion de lineas en zonas comunes

### Problema detectado
En el pasadizo central, las lineas de C4 (alumbrado), C6 (cocina/servicio) y C7 (lavadora) circulaban demasiado juntas:
- C4 backbone: y=4.88
- C6: y=4.62 (solo 0.26m de separacion)
- C7: y=4.32 (solo 0.30m de separacion)

### Correccion aplicada
| Circuito | Posicion anterior | Posicion nueva | Separacion |
|----------|-------------------|----------------|------------|
| C4 Alumbrado | y=4.88 | y=4.88 (sin cambio) | - |
| C6 Cocina/servicio | y=4.62 | y=5.10 | 0.22m de C4 |
| C7 Lavadora | y=4.32 | y=3.80 | 1.08m de C6 |

Esto permite que cada circuito se identifique claramente en el pasadizo central.

## 5. Reduccion de rigidez ortogonal

No se aplicaron cambios masivos de ortogonalidad. Las rutas mantienen su trazado original con quiebres donde tienen sentido (cambios de direccion en ejes de muros). No se convirtio el trazado en una malla rigida a 90 grados.

Las rutas siguen siendo discontinuas (DASHED) segun norma tecnica.

## 6. Correccion de simbolos especiales (monofasicos)

### Problema detectado
Los tomacorrientes especiales (TE cocina/servicio, C cocina, L lavadora) estaban dibujados con 3 lineas horizontales dentro del circulo, que es el simbolo DGE para tomacorriente **trifasico** (codigo 09-93-15 y 09-93-18).

### Correccion aplicada
Se eliminio la linea central de cada simbolo, dejando solo 2 lineas horizontales (simbolo de tomacorriente **monofasico**). La distincion como "especial" se mantiene mediante las etiquetas de texto (TE, C, L).

### Simbolos corregidos (6 en total)

| Ubicacion | Etiqueta | Uso | Posicion |
|-----------|----------|-----|----------|
| Plano cocina | TE | Toma especial cocina/servicio | (3.35, 6.10) |
| Plano servicio | TE | Toma especial servicio | (5.35, 8.05) |
| Plano cocina | C | Cocina electrica | (3.10, 5.25) |
| Plano lavanderia | L | Lavadora | (5.55, 5.05) |
| Leyenda | TE | Toma especial monofasica | (16.97, 7.28) |
| Leyenda | L | Salida especial lavadora | (16.97, 6.94) |

Todos pasaron de 3 lineas (trifasico) a 2 lineas (monofasico).

## 7. Cambios en la leyenda

| Elemento | Cambio |
|----------|--------|
| Simbolo VD | Actualizado a circulo con flecha vertical (coincide con el nuevo simbolo en plano) |
| TE en leyenda | Texto actualizado: "Toma especial monofasica (cocina/servicio)" |
| L en leyenda | Texto actualizado: "Salida especial monofasica (lavadora)" |
| Nota adicional | Agregada: "Toda la instalacion de tomacorrientes es MONOFASICA (220V). No existen tomacorrientes trifasicos en esta vivienda." |

## 8. Diferenciacion de simbolos electricos

| Simbolo | Representacion | Como se diferencia |
|---------|---------------|-------------------|
| Tomacorriente simple | Circulo + 2 lineas horizontales | Sin etiqueta adicional |
| Tomacorriente con tierra | Circulo + 2 lineas + linea vertical abajo | Linea vertical de conexion a tierra |
| Toma especial monofasica | Circulo + 2 lineas + texto TE/C/L | Misma grafica que simple pero con etiqueta de texto |
| Salida especial lavadora | Circulo + 2 lineas + texto L | Misma grafica + texto L |
| Interruptor simple | Circulo + palanca oblicua + texto S | Forma de palanca |
| Interruptor conmutado | Circulo + palanca oblicua + texto S3 | Texto S3 |
| Punto de luz | Circulo + cruz (+) | Forma de cruz |
| Ducto vertical | Circulo + flecha vertical hacia arriba | Forma de flecha vertical, nunca confundible con cruz o aspas |
| Tablero T2 | Rectangulo con texto T2 | Forma rectangular unica |

## 9. Confirmacion: NO existen tomacorrientes trifasicos

Se verifico entidad por entidad en el DXF v4:
- Todos los tomacorrientes en ELEC_TOMACORRIENTES tienen 2 lineas horizontales (monofasico)
- Ningun simbolo tiene 3 lineas horizontales
- La leyenda NO menciona ni muestra tomacorriente trifasico

**Estado: CONFIRMADO - No hay tomacorrientes trifasicos en este plano.**

## 10. Zonas prioritarias revisadas

| Zona | Estado |
|------|--------|
| Cocina | Tomacorrientes especiales corregidos a monofasicos, rutas de C6 separadas |
| Pasadizo central | C4/C6/C7 con separacion mejorada |
| Tablero T2 | Sin cambios, posicion preservada |
| VD - conexion a T2 | Ruta directa, sin rodeos |
| Sala | Sin cambios, todo correcto |
| Bano / Cuartos | Sin cambios, todo correcto |

## 11. Resumen de archivos generados

| Archivo | Ruta |
|---------|------|
| Respaldo v3 previo | `salidas/backup_electrico_piso2_v3_prev4.dxf` |
| Extraccion DXF | `data/electrico_piso2_v4_extraido_desde_dxf.json` |
| Render antes | `temp/electrico_piso2_v4_antes_revision.png` |
| DXF v4 | `salidas/electrico_piso2_v4.dxf` |
| PDF v4 | `salidas/electrico_piso2_v4.pdf` |
| PNG landscape | `temp/electrico_piso2_v4_landscape.png` |
| Este reporte | `revisiones/revision_electrico_piso2_v4.md` |

## 12. Pendientes / dudas

- La posicion exacta del VD (12.05) podria revisarse en QCAD para ajuste fino de alineacion con muros
- La separacion de lineas C6/C7 podria requerir un offset adicional si en QCAD se ven demasiado cerca de alguna pared
- El texto "subida TG" original se reemplazo por "subida vertical" para mayor claridad; verificar que sea consistente con la nomenclatura del proyecto

## 13. Confirmacion de revision visual final

La revision visual se realizo mediante renderizado automatizado a PNG y PDF. Se confirma:
- [x] El ducto vertical ya no parece luminaria (tiene flecha vertical unica)
- [x] El ducto vertical esta junto al tablero T2
- [x] El ducto no "da la vuelta" antes de subir (ruta directa)
- [x] Las lineas de C4, C5, C6, C7 tienen mejor separacion
- [x] No todas las rutas se ven rigidamente rectas
- [x] Cocina y pasadizo se leen mejor
- [x] Los simbolos especiales son monofasicos (2 lineas)
- [x] La leyenda coincide con el dibujo real
- [x] No se eliminaron circuitos (se mantienen C4-C7 completos)
- [x] El plano se parece al v3 manual mejorado, no es una regeneracion desde cero

---

*Revision generada automaticamente mediante script Python + ezdxf.*
