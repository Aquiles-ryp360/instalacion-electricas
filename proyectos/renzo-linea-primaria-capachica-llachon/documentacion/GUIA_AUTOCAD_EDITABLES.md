# Guía de los planos editables en AutoCAD

Archivos, en `plans/`:

| Archivo | Contenido |
|---|---|
| `LP_REV8.dwg` | **Plano principal**: 23 láminas A3, ingeniería del motor LP 22,9 kV |
| `LP_REV6.dwg` | Versión anterior: 13 láminas, con la distribución de postes de gabinete |
| `armados_lp229/LD-LP-01…14.dwg` | Láminas de armados con lista de materiales (motor de D. H. Ccora) |
| `*.dxf` | Las mismas láminas en DXF, para otros programas CAD (BricsCAD, LibreCAD, QGIS) |
| `*.pdf` | Las láminas impresas por AutoCAD |

Los DWG se guardaron con AutoCAD 2018. AUDIT no encontró errores. Se abren desde AutoCAD 2018 en adelante.

## Al abrir `LP_REV8.dwg`

- Abre en la lámina **LP-01**; las demás están en las pestañas de presentación, de **LP-01** a **LP-23**:
  - **LP-01:** ubicación, clave de láminas, unifilar y datos técnicos.
  - **LP-02 a LP-13:** plantas a 1:5 000.
  - **LP-14 a LP-22:** perfil y planimetría.
  - **LP-23:** cuadro de estructuras y coordenadas.
- La pestaña **Modelo** está en coordenadas **UTM WGS84 zona 19S, en metros**.
  El comando `ID` sobre un poste da su Este y Norte reales, y el dibujo se puede superponer con otros planos georreferenciados.
- Las ventanas gráficas de las plantas están **bloqueadas**: hacer zoom dentro de ellas no cambia la escala 1:5 000.
  Para moverlas: selecciona el borde, abre Propiedades y pon *Visualización bloqueada* en **No**.
  Las ventanas están en la capa `REDCAD_VIEWPORTS`, que no se imprime.

## Editar

| Qué | Cómo |
|---|---|
| Armado o PAT de un poste | Doble clic en su cuadro (bloque `CUADRO_POSTE`) → editor de atributos (`EATTEDIT`). Los atributos son `NUMERO`, `ARMADO` y `PAT` |
| Mover un poste | En Modelo, mover el bloque `POSTE_LP` y luego su cuadro y su línea de llamada |
| Datos del cajetín (autor, revisor, fecha) | Son textos en cada lámina; con `FIND` se cambian en todas a la vez (p. ej. el nombre del autor) |
| Ocultar algo | Desactivar su capa (tabla siguiente) |
| Perfil y planimetría | Están dibujados en la propia lámina (espacio papel), en mm a escala H 1:5 000 y V según el cajetín |

Capas principales:

| Capa | Contenido |
|---|---|
| `RP_CONDUCTOR` | Eje de la línea / conductor |
| `RP_POSTE` | Postes |
| `RP_RETENIDA` | Retenidas |
| `RP_PTIERRA` | Puestas a tierra |
| `RP_CUADROPOSTE` | Cuadros de cada poste y su línea de llamada |
| `RP_VANO` | Longitud de vanos |
| `VIAS`, `AGUA`, `CRUCES` | Vías y cuerpos de agua de OpenStreetMap; cruces viales |
| `PP_TERRENO` | Perfil del terreno |
| `PP_CONDUCTOR` | Conductor a flecha máxima |
| `PP_DIST_SEGURIDAD` | Distancia mínima de seguridad |
| `PP_POSTE` | Postes en el perfil |
| `PP_GRILLA` | Grilla de cotas |
| `PP_TABLA`, `PP_TEXTO` | Tabla bajo el perfil y textos de la planimetría |
| `ROTULO`, `MARCO`, `RP_LEYENDA`, `UNIFILAR`, `NM` | Cajetín, marcos, leyendas, unifilar y norte |

Texto: estilo `ROMANS` (romans.shx, incluido en AutoCAD).

## Imprimir

Cada lámina ya tiene su configuración: **DWG To PDF.pc3**, papel **ISO full bleed A3 (420 × 297 mm)**, escala 1:1 y estilo **acad.ctb**, a color.

- Una lámina: `PLOT` y Aceptar.
- Todas: `PUBLISH`, *Agregar presentaciones* y luego Publicar.
- Para otra impresora, cambiar solo el dispositivo en `PAGESETUP` y mantener A3 y la escala 1:1.

Las láminas de armados (`armados_lp229`) están en Modelo, en mm, con su marco: se imprimen con *Ventana* sobre el marco y escala 1:1.

## Regenerar desde los datos

Si cambia el diseño, no hace falta redibujar a mano:

```powershell
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/planos_motor_epime.py --dwg
```

Esto rehace el DXF, el DWG y el PDF, y convierte los armados a DWG. Usa AutoCAD 2027 si está instalado (`ACCORE`) y,
si no, ODA File Converter (`ODA`, en `planos_formato_epime.py`). Con `--autocad` el PDF también lo traza AutoCAD.
**Ojo:** si se regenera, se pierden los cambios hechos a mano en el DWG. Conviene guardarlos con otro nombre.
