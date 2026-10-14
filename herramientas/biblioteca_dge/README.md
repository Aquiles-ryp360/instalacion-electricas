# Biblioteca CAD de armados y simbología DGE - Perú

Biblioteca de consulta derivada de normas publicadas, con fuentes y procedencia por lámina. **Los CAD derivados no son archivos emitidos por el MINEM.** Los dibujos originales se conservan en PDF para contrastar todas sus vistas, cotas, llamadas y tablas de piezas.

## Descarga

- [Biblioteca completa: CAD, fuentes, índices y condiciones](entregables/Biblioteca_CAD_DGE_Peru.zip).
- [DWG maestro MT con 102 láminas: descarga separada por su tamaño](entregables/BIBLIOTECA_DGE_MT_COMPLETA.dwg). El ZIP contiene los 102 DXF individuales MT y los otros CAD de la biblioteca.
- [Índice MT: 102 láminas de RD 024-2003](entregables/catalogo-armados-MT.csv).
- [Índice BT: 21 láminas de RD 023-2003](entregables/catalogo-armados-BT.csv).
- [Complemento BT: lámina 022 aprobada en 2019](entregables/catalogo-complementos.json).
- [182 símbolos de la sección 9: códigos, definición y página](entregables/catalogo-simbolos.json).
- [Fuentes y hashes](entregables/fuentes.json).

## Qué contiene

La RD 024 contiene 102 **hojas**, no 102 tipos de poste: algunas corresponden a variantes de estructura y otras a aisladores, ferretería, subestaciones, retenidas y puesta a tierra. Las 102 hojas se incluyen completas en DXF individuales y en un DWG con pestañas. Se conservan ambas partes de la lámina 064 y las hojas con sufijos A/B; no se renumeran.

La RD 023 base contiene 21 láminas de baja tensión, en otro CAD. Se incorpora por separado la lámina 022 aprobada mediante RD 002-2019-MEM/DGE, recuperada del PDF oficial de El Peruano del 9 de enero de 2019. Las bibliotecas de MT y BT no son intercambiables.

La sección 9 de la RM 091-2002-EM/VME aporta 182 bloques CAD, incluidos poste CAC **DGE_09_91_20**, poste de madera, retenida **DGE_09_91_18**, línea **DGE_09_91_03**, subestación en proyección **DGE_09_90_09** y en servicio **DGE_09_90_10**. Los bloques se extraen de los vectores del PDF oficial. Se omite la retícula de puntos auxiliar del documento. El catálogo incluye el significado y la página de cada símbolo: no hay que deducir la función por su aspecto.

La plantilla original REDLIN de Esolutions, edición 2025-12, se conserva sin alterar junto a su `Leeme.txt`. **Es un recurso de terceros**, no un CAD de autoría MINEM; sus propias condiciones piden contrastar los datos. La copia MT que incorpora tiene imágenes de mayor resolución que la descarga histórica de MINEM, y la copia BT contiene geometría vectorial. Se utiliza para convertir las hojas; la norma directa MINEM queda disponible como contraste. Se conservan los créditos y las condiciones de distribución del fabricante. No se usan proyectos de estudiantes.

## Cómo editar y usar

1. Abra el DWG de la familia apropiada y seleccione una pestaña por código; para una sola hoja, abra su DXF. El DWG se guarda con AutoCAD instalado y se reabre para verificarlo; no se renombra una extensión.
2. Las hojas de detalle utilizan **milímetros de hoja**, sin georreferenciación. Son reproducciones documentales; **no representan todas las piezas a tamaño real**. No escale herrajes midiendo sus contornos: use la cota y la especificación originales.
3. MT parte de escaneos: sus letras y cotas son **contornos editables**, no objetos TEXT ni DIMENSION. No se afirma que exista un despiece paramétrico completo. BT se transfiere desde vectores PDF; parte del texto del PDF también está delineado. El complemento 022 conserva texto nativo donde existe en el PDF.
   En las hojas MT la capa `DGE_CONTORNOS` permanece apagada para evitar doble trazo al imprimir. Puede activarla para editar los contornos; los rellenos se conservan en otra capa.
4. Para modificar una leyenda, cambie el texto añadido o sustituya el contorno correspondiente por TEXT. Para modificar una dimensión de ingeniería, elabore un detalle propio sustentado y conserve la hoja normativa sin alterar como referencia.
5. En un CAD topográfico UTM, inserte las hojas en **espacio papel**, en mm. El modelo de Limbani usa metros EPSG:32719. No mezcle las hojas con las coordenadas de los postes.
6. Para plano geográfico, inserte el bloque simbólico del código correspondiente, con tamaño gráfico según la escala de impresión. El símbolo de subestación no es el detalle constructivo de una subestación. El círculo CAC indica material de soporte; la función se identifica por el rótulo del armado.

## Aplicabilidad

Esta entrega cubre los **corpus indicados**, no todas las normas y diseños de todas las concesionarias del Perú. La investigación encontró la RM 370-2022 como **prepublicación** de actualización de soportes primarios; no se trata como sustitución aprobada de la RD 024. Verificar modificaciones posteriores y las exigencias de la concesionaria antes de usar la biblioteca para una ejecución real.

Las láminas 004/008/020 incluyen elementos de madera. La adaptación a CAC, las cargas, altitud, longitud de aisladores, separaciones, crucetas y abrazaderas deben calcularse. No se puede adoptar una lista de piezas sólo por coincidir el nombre PS/PA/PR. Las variantes con neutro y sin neutro tienen columnas distintas; no sumar ambas.

En Limbani, las 23 hojas seleccionadas se incorporan al CAD de LP-R01 como referencias en espacio papel y al anexo del expediente. La memoria explica la adaptación CAC pendiente, la diferencia entre una sujeción PIN y una retención y los tres armados especiales mayores de 90°. La transformación de 250 kVA sobre piso no se sustituye por una subestación aérea biposte de otra potencia.

El anexo de Limbani contiene esas 23 hojas exportadas directamente del DXF a **PDF vectorial A3**, con rótulo, tablas y cotas conservados. Se comprueba que no contiene imágenes raster. `exportar_pdf.py` realiza la exportación y permite repetirla sin redibujar las láminas.

## Reproducción

Las fuentes descargadas se encuentran en `referencias/local/biblioteca-dge` (no se modifican). Los resultados de trabajo se generan primero en `build/biblioteca-dge/biblioteca`. Se necesitan Python, ezdxf, Pillow, PyMuPDF y Potrace 1.16; ReportLab para el anexo. En esta computadora las dependencias se instalaron en G:\Aquiles, sin modificar QGIS ni AutoCAD.

Desde la raíz del repositorio:

```powershell
python herramientas/biblioteca_dge/generar.py
python -m herramientas.biblioteca_dge.complementar
python herramientas/biblioteca_dge/nativo.py
python herramientas/biblioteca_dge/revisar.py
python herramientas/biblioteca_dge/compactar.py
python herramientas/biblioteca_dge/publicar.py
```

La integración del proyecto se reproduce después de generar su CAD base:

```powershell
python proyectos/aquiles-limbani-redes/scripts/lp_r01/integrar_armados_cad.py
python proyectos/aquiles-limbani-redes/scripts/lp_r01/perfiles.py
python proyectos/aquiles-limbani-redes/scripts/lp_r01/dwg.py
python proyectos/aquiles-limbani-redes/scripts/lp_r01/finalizar.py
```

Consultar los registros de verificación para saber qué se comprobó. La apertura y la coherencia geométrica no sustituyen la validación de ingeniería de los componentes.
