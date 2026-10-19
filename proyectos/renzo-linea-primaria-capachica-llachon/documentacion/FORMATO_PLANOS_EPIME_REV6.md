# Formato de planos EPIME — Rev. 6

## Referencia analizada

Se usó como modelo el proyecto de curso «Mejoramiento de línea primaria 22.9 kV Conima–Tilali»
(DWG AutoCAD 2018, cuatro láminas A3 01-LP, revisado en el curso de la EPIME). Lo que define su forma de dibujo:

| Elemento | Cómo está planteado en Conima–Tilali | Adoptado en Capachica Rev. 6 |
|---|---|---|
| Lámina | A3 horizontal, doble marco, una presentación por plano | Igual: presentaciones `LP-01`…`LP-13` |
| Cajetín | Abajo a la derecha: EPIME, PROYECTO, ESCALA, FECHA, TEMA, ubicación, REVISADO, AUTOR, PLANO N° y hoja x/n | Igual; datos en `CAJETIN` del script |
| Modelo | Coordenadas UTM reales en metros; el papel ve el modelo por ventanas | Igual: modelo UTM 19S, ventanas 1:5000 |
| Postes | Círculo rojo en capa `RP_POSTE` | Bloque `POSTE_LP`, capa `RP_POSTE` |
| Cuadro por poste | Bloque con atributos N°, armado y PAT, unido al poste | Bloque `CUADRO_POSTE` (atributos `NUMERO`, `ARMADO`, `PAT`), alternado a cada lado |
| Retenidas / PAT | Bloques `RETENIDA` y `PAT-1` junto al poste | Bloques `RETENIDA` (orientada fuera del ángulo o en el eje) y `PAT` |
| Conductor | Polilínea azul `RP_CONDUCTOR` con etiqueta de vano | Igual, más el vano en metros a mitad del tramo |
| Leyenda | Símbolo, cantidad total y descripción | Igual, con cantidades calculadas |
| Cuadro de estructuras | Tipo, armado, poste, retenida, PAT, cantidad y descripción | Igual (resumen por tipo) |
| Coordenadas | Tabla N°, armado, E, N, cota | Tabla N°, armado, poste, retenida, PAT, progresiva, vano, E, N |
| Unifilar | Barra, seccionamiento, línea y SED | Red existente, cut-out, pararrayos, L.P. y punto de llegada |
| Norte | Bloque N.M. | Bloque `NM` |

Capas principales: `RP_CONDUCTOR`, `RP_POSTE`, `RP_RETENIDA`, `RP_PTIERRA`, `RP_CUADROPOSTE`, `RP_VANO`,
`RP_EMPALME`, `VIAS`, `CRUCES`, `ROTULO`, `RP_LEYENDA`, `UNIFILAR` y `REDCAD_VIEWPORTS` (no se imprime).

## Mejoras respecto de las láminas CL Rev. 4/5

- Las CL eran cartográficas: no tenían postes numerados, armados, vanos, retenidas, PAT, leyenda con cantidades ni cajetín de curso.
- Rev. 6 dibuja a escala fija 1:5000 en todas las plantas, con láminas encadenadas («viene de» y «continúa en») y una clave de láminas en LP-01.
- Los editables son DXF y DWG 2018 con bloques y atributos. Para corregir un armado se edita el atributo; para cambiar el cajetín, `CAJETIN` en el script.

## Hipótesis (marcadas con (*) en los planos)

La distribución de 168 estructuras es una **propuesta académica de gabinete**, no un replanteo:

- Eje: KML manual de 4 tramos; los 3 empalmes se trazan rectos y quedan por levantar.
- Vértices de diseño: eje simplificado a 6 m; los vértices a menos de 30 m se fusionan en su punto medio.
- Vano máximo de 100 m, repartido en partes iguales entre vértices.
- Armados: PS-1 hasta 5°, PA-1 de 5° a 30°, PR-1 por encima de 30°, en los terminales y como anclaje de paso cada 1000 m como máximo.
- PAT-3 en todo PA-1 y PR-1, y cada 4 postes PS-1.
- Tensión de 22.9 kV y conductor AAAC 3x35 mm² sin confirmar con Electro Puno.

Antes de construir hacen falta topografía, el punto de diseño y los parámetros del operador, y el cálculo mecánico de cada vano.
La lista aprobada que pide `colocar_postes_automatico.py` sigue pendiente; este CSV no la reemplaza.

## Regenerar

```powershell
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/planos_formato_epime.py --autocad
python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests/test_planos_formato_epime.py -q
```

Sin `--autocad` se generan el DXF y un PDF de vista previa con matplotlib.
Ese PDF muestra en LP-01 capas que AutoCAD congela en la ventana gráfica.
