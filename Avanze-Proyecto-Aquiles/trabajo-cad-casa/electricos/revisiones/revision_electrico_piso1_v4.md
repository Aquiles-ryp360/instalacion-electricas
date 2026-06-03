# Revision electrica preliminar - Piso 1 v4

## 1. Observacion del usuario

El usuario aclaro que:
- El area rayada del plano en la parte inferior izquierda **no representa pavimento ni garaje techado**. Esta zona rayada es **tierra / area sin techo / patio exterior**.
- El garaje solo tiene techo aproximadamente **hasta 8 metros desde la puerta o ingreso**. Mas alla de ese limite, no debe considerarse ambiente techado.
- La zona de tierra sin techo no debe tener luminarias interiores, ni interruptores de alumbrado interior, ni tomacorrientes generales interiores.

## 2. Interpretacion corregida del garaje y zona de tierra

- **Zona Frontal (Garaje Techado):** Comprende desde el ingreso (`x` = 15.00 m) hasta los 8 metros hacia la izquierda (`x` = 7.00 m). En este tramo se mantiene la iluminacion interior y los tomacorrientes de servicio.
- **Zona Posterior / Lateral (Tierra y Sin Techo):** Comprende el tramo de `x` = 0.00 m a `x` = 7.00 m de la franja inferior (incluyendo el area rayada/sombreada). Se considera un area exterior descubierta.
- **Separacion Visual:** Se agrego una linea discontinua vertical en `x` = 7.00 m etiquetada como **"Limite techo garaje"** para marcar fisicamente en el plano la frontera del techado. Adicionalmente, se incluyo una anotacion discreta: **"Area sin techo / tierra (sin luminaria interior)"** en el area descubierta.

## 3. Modificaciones de Luminarias (Circuito C1)

- **Eliminadas:** 
  - `L-P1-06` (ubicada en `x` = 1.50, `y` = 2.20, dentro del area rayada).
  - `L-P1-04` (ubicada en `x` = 6.00, `y` = 2.25, en la parte posterior no techada del garaje).
- **Corregidas / Centradas:**
  - `L-P1-05` se movio y centro a `x` = 11.00, `y` = 2.25, quedando en el punto medio exacto de la zona techada del garaje (que mide 8 metros, de `x` = 7.00 a `x` = 15.00).
- **Mantenidas:**
  - `L-P1-01` en Escalera (`x` = 0.90, `y` = 5.90).
  - `L-P1-02` en Ambiente Superior 1 (`x` = 6.00, `y` = 6.80).
  - `L-P1-03` en Ambiente Superior 2 (`x` = 12.00, `y` = 6.80).

## 4. Modificaciones de Interruptores (Circuito C1)

- **Eliminados:**
  - `S-P1-05` (ubicado en `x` = 2.70, `y` = 3.20). Este interruptor controlaba a `L-P1-06`, por lo que al eliminarse la luminaria, el interruptor pierde funcion y se retira para evitar elementos huérfanos.
- **Mantenidos:**
  - `S-P1-01` en Escalera (`x` = 1.25, `y` = 5.20).
  - `S-P1-02` en Ambiente Superior 1 (`x` = 3.75, `y` = 5.20).
  - `S-P1-03` en Ambiente Superior 2 (`x` = 13.25, `y` = 5.05).
  - `S-P1-04` en el ingreso del Garaje (`x` = 13.80, `y` = 4.25) para controlar la luminaria del garaje techado `L-P1-05`.

## 5. Modificaciones de Tomacorrientes (Circuito C2)

- **Eliminados:**
  - `T-P1-08` (ubicado en `x` = 0.35, `y` = 1.40, dentro de la zona rayada de tierra).
- **Movidos:**
  - `T-P1-01` se reubico desde la zona sin techo (`x` = 4.00, `y` = 0.35) hacia la zona techada en el muro inferior (`x` = 12.00, `y` = 0.35).
- **Mantenidos:**
  - `T-P1-02` (`x` = 8.00, `y` = 0.35, en muro inferior del garaje techado).
  - `T-P1-03` (`x` = 14.35, `y` = 2.00, en muro derecho del garaje techado).
  - Los de ambientes superiores (`T-P1-04`, `T-P1-05`, `T-P1-06`, `T-P1-07`, `T-P1-09` especial de cocina) se mantuvieron intactos.

## 6. Cambios en Rutas de Canalizacion (C1, C2 y C8)

- **Ruta C1 (Alumbrado):** La ruta inferior `R-P1-C1-B` se simplifico. Ahora conecta el Tablero General `TG` directamente con la luminaria `L-P1-05` a traves de `[14.35, 4.75] -> [14.35, 2.25] -> [11.00, 2.25]`. No se extiende hacia el area exterior sin techo.
- **Ruta C2 (Tomacorrientes):** La ruta inferior `R-P1-C2-B` se acorto para alimentar solo los tomacorrientes de la zona techada. Va de `TG` a `T-P1-03`, baja al muro inferior y conecta `T-P1-01` (`x` = 12.00) y `T-P1-02` (`x` = 8.00), terminando en este ultimo punto. No avanza hacia la zona sin techo.
- **Ruta C8 (Bomba Exterior):** Se mantuvo el tendido ortogonal subterraneo referencial desde `TG` por la parte baja del garaje hasta la bomba `B-P1` (`x` = -0.55, `y` = 1.00). Se actualizo su etiqueta en la leyenda y en la ruta para indicar de forma explicita: **"C8 bomba exterior (subterranea ref.)"**, evitando cualquier confusion con instalaciones de interior.

## 7. Elementos mantenidos sin mover

- **Medidor (M):** Permanece intacto en `x` = 15.45, `y` = 4.75.
- **Tablero General (TG):** Permanece intacto en `x` = 14.35, `y` = 4.75.
- **Alimentador M-TG:** Se mantiene corto y horizontal.

## 8. Sincronizacion de Calculos y Conteo de Cargas (v4)

- **Actualizacion del JSON de Calculo (`proyecto_aquiles_base.json`):**
  - El circuito **C1** (Alumbrado 1er Piso) se actualizo a **80 W** en la base de calculo (correspondiente a 4 luminarias * 20W/punto).
  - El circuito **C2** (Tomacorrientes 1er Piso) se actualizo a **1260 W** (correspondiente a 7 tomacorrientes * 180W/punto).
- **Ejecucion del Motor de Calculo:** Se ejecuto el script `calcular_instalacion.py` para regenerar las tablas LaTeX `tabla_cargas.tex` y `tabla_conductores.tex` en la carpeta `herramientas/calculos-electricos-vivienda/output/`.
- **Alineacion de Valores en el Capitulo II de LaTeX:** Se actualizaron los valores redactados en el texto de `capitulos/02-calculos-justificativos.tex` para que coincidan de manera exacta con el nuevo resultado del motor de calculo:
  - Potencia de maxima demanda adoptada: **10,358 W**.
  - Corriente de empleo del alimentador: **52.31 A**.
  - Corriente de diseno preliminar: **65.39 A**.
  - Caida de tension del alimentador: **0.635%**.
- **Compilacion del Expediente:** Se compilo con exito el documento general de LaTeX mediante `pdflatex`, generando el archivo final actualizado [main.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/proyecto-latex-instalaciones/build/main.pdf).

## 9. Pendiente

- Confirmar ubicacion definitiva y potencia de la bomba de agua.
- Validar si se requerira una luminaria exterior de alumbrado general de patio (tipo reflector o aplique de pared exterior) en la zona de tierra/sin techo para etapas posteriores del proyecto.

## 10. Veredicto Visual

**APROBADO** como plano electrico preliminar del primer piso corregido (Versión v4).
Las luminarias e interruptores interiores han sido retirados con exito de las zonas exteriores sin techo y de tierra rayada, y la separacion de ambientes es clara e inequivoca.
El DXF abre correctamente en QCAD/LibreCAD y el PDF es legible.
Tanto el plano como los calculos de la memoria tecnica estan completamente sincronizados.

