# Planos electricos preliminares - Casa de Aquiles

Esta carpeta contiene la primera version de planos electricos interiores sobre la base arquitectonica CAD ya generada para la vivienda de Aquiles.

## Base usada

Se usaron los archivos v3 de la carpeta de salidas arquitectonicas:

- `../salidas/piso1_v3.dxf`
- `../salidas/piso2_v3.dxf`

No se redibujo la arquitectura desde cero. El script de superposicion conserva la planta arquitectonica y remapea sus capas a capas `ARQ_*`; encima agrega simbolos, circuitos y notas electricas.

## Archivos generados

Datos:

- `data/simbolos_electricos.json`
- `data/electrico_piso1_v1.json`
- `data/electrico_piso2_v1.json`

Salidas:

- `salidas/electrico_piso1_v1.dxf`
- `salidas/electrico_piso1_v1.pdf`
- `salidas/electrico_piso1_v2.dxf`
- `salidas/electrico_piso1_v2.pdf`
- `salidas/electrico_piso1_v3.dxf`
- `salidas/electrico_piso1_v3.pdf`
- `salidas/electrico_piso2_v1.dxf`
- `salidas/electrico_piso2_v1.pdf`
- `salidas/electrico_piso2_v2.dxf`
- `salidas/electrico_piso2_v2.pdf`

Capturas de revision:

- `temp/electrico_piso1_v1_landscape-1.png`
- `temp/electrico_piso1_v2_landscape-1.png`
- `temp/electrico_piso1_v3_landscape-1.png`
- `temp/electrico_piso2_v1_landscape-1.png`
- `temp/electrico_piso2_v2_landscape-1.png`

## Circuitos representados

- `C1`: Alumbrado del primer piso.
- `C2`: Tomacorrientes generales del primer piso.
- `C3`: Cocina auxiliar del primer piso, por confirmar.
- `C4`: Alumbrado del segundo piso.
- `C5`: Tomacorrientes generales del segundo piso.
- `C6`: Cocina o carga especial del segundo piso, por confirmar.
- `C7`: Lavadora del segundo piso.
- `C8`: Bomba de agua exterior.

## Criterios de ubicacion

- Se coloco una luminaria central por ambiente pequeno y luminarias adicionales donde el espacio es mayor.
- Los interruptores se ubicaron cerca de ingresos y puertas, con conmutador referencial en la zona de escalera.
- Los tomacorrientes se distribuyeron en perimetros de sala, dormitorios, cocina, banos y zonas de servicio.
- El tablero general `TG` se ubico de forma preliminar en el primer piso, cerca del ingreso/fachada derecha.
- El medidor `M` se ubico de forma preliminar en fachada, asociado al alimentador hacia el `TG`.
- La subida al segundo piso se marco como `VD`, una subida referencial desde el tablero general.
- Las rutas de canalizacion son referenciales y no representan aun recorrido constructivo definitivo.

## Datos preliminares

- Ubicacion real del medidor.
- Ubicacion final del tablero general.
- Si existira subtablero en segundo piso.
- Confirmacion de cocina electrica o cocina a gas.
- Potencia real de bomba de agua.
- Cantidad final de luminarias y tomacorrientes por ambiente.
- Recorridos definitivos de canalizacion y cajas de paso.

## Como regenerar los planos

Desde la raiz del repositorio:

```bash
herramientas/ia-cad-casas/.venv/bin/python \
  herramientas/ia-cad-casas/scripts/electrical_overlay.py \
  --base Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.dxf \
  --electrical Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/data/electrico_piso1_v1.json \
  --output Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.dxf

qcad -no-gui -platform offscreen -quit \
  -autostart "$(realpath herramientas/ia-cad-casas/cad-scripts/dxf2pdf.js)" \
  -input "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.dxf)" \
  -output "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.pdf)"
```

Cambiar `piso1` por `piso2` para regenerar el segundo piso.

## Abrir en QCAD

```bash
qcad Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.dxf
qcad Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso2_v1.dxf
```

La importacion QCAD fue verificada en modo headless al generar los PDF.

## Abrir en LibreCAD

```bash
librecad Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.dxf
librecad Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso2_v1.dxf
```

LibreCAD debe usarse como visor/editor DXF. En esta revision se hizo una prueba limitada con `librecad -platform offscreen` y ambos DXF cargaron capas antes del cierre controlado por `timeout`; la revision interactiva completa requiere una sesion grafica local.

## Estado

Version vigente del Piso 1: `electrico_piso1_v3`, corregida segun revision visual del usuario para mantener medidor/tablero de v2, afinar interruptores fuera de puertas/arcos y limpiar rutas ortogonales.

Version vigente del Piso 2: `electrico_piso2_v2`, corregida segun revision visual del usuario para agregar tablero `T2`, retirar medidor, reubicar interruptores y ordenar la zona de cocina.

Estas versiones estan aprobadas con observaciones como planos electricos preliminares. Sirven para revision visual con Aquiles, no para ejecucion de obra.
