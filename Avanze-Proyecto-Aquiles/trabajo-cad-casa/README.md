# Trabajo CAD Casa Aquiles

Zona específica para interpretar los croquis reales de la casa de Aquiles y generar planos arquitectónicos 2D editables. El motor genérico se conserva separado en `herramientas/ia-cad-casas/`.

## Fuentes usadas

- Croquis principal Piso 1: `Avanze-Proyecto-Aquiles/Full-Imagenes/Croquis-de-plano de la casa/Piso 1 croquis limpio.png`
- Croquis principal Piso 2: `Avanze-Proyecto-Aquiles/Full-Imagenes/Croquis-de-plano de la casa/Piso 2 croquis limpio.png`
- Fotos de respaldo: `20260602_195759.jpg.jpeg` y `WhatsApp Image 2026-05-19 at 09.46.21.jpeg`
- Referencia de estilo, no de distribución: `Avanze-Proyecto-Aquiles/Full-Imagenes/Plantillas-como-deve-verse-el-cad/prefabricadascasasdemadera_com.jpg`

## Layouts vigentes

- Piso 1 recomendado: `layouts/layout_aquiles_piso1_v3.json`
- Piso 2 recomendado: `layouts/layout_aquiles_piso2_v3.json`

También se conservan `v1` y `v2` por piso para mostrar la evolución:

- `layout_aquiles_piso1_v1.json`: primera interpretación con ambientes principales.
- `layout_aquiles_piso1_v2.json`: muros manuales, puertas, trama y escalera ajustada.
- `layout_aquiles_piso1_v3.json`: versión limpia recomendada.
- `layout_aquiles_piso2_v1.json`: primera interpretación basada en retícula.
- `layout_aquiles_piso2_v2.json`: contorno en L y muros manuales.
- `layout_aquiles_piso2_v3.json`: versión limpia recomendada con mobiliario básico de referencia.

Los archivos antiguos `layout_aquiles_v1.json`, `layout_aquiles_v2.json` y `layout_aquiles_v3.json` se mantienen como historial previo del Piso 2. No se borraron ni renombraron.

## Salidas generadas

En `salidas/`:

- `piso1_v1.dxf` / `piso1_v1.pdf`
- `piso1_v2.dxf` / `piso1_v2.pdf`
- `piso1_v3.dxf` / `piso1_v3.pdf`
- `piso2_v1.dxf` / `piso2_v1.pdf`
- `piso2_v2.dxf` / `piso2_v2.pdf`
- `piso2_v3.dxf` / `piso2_v3.pdf`

Las mejores salidas actuales son `piso1_v3.*` y `piso2_v3.*`.

## Regenerar planos

Desde la raíz del repositorio:

```bash
./herramientas/ia-cad-casas/generar_plano.sh \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_piso1_v3.json \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.dxf \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.pdf

./herramientas/ia-cad-casas/generar_plano.sh \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_piso2_v3.json \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso2_v3.dxf \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso2_v3.pdf
```

El script crea el DXF con Python/ezdxf y exporta el PDF con QCAD headless.

## Abrir en CAD

QCAD:

```bash
qcad Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.dxf
qcad Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso2_v3.dxf
```

LibreCAD:

```bash
librecad Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.dxf
librecad Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso2_v3.dxf
```

LibreCAD abrió la estructura de capas en prueba interactiva con `timeout`; se usa como visor/editor secundario. QCAD queda como motor principal para exportar PDF.

## Pendiente con Aquiles

- Confirmar nombres reales de los dos ambientes superiores del Piso 1.
- Confirmar qué representa el bloque sombreado inferior izquierdo del Piso 1.
- Confirmar si el ancho inferior rotulado como `8 m` en Piso 2 incluye baño + dormitorio o solo dormitorio.
- Medir en obra el espesor real de muros, vanos de puertas y ventanas.
- Recién después de confirmar arquitectura, pasar a plano eléctrico.
