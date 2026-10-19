# Línea primaria 22,9 kV Capachica–Llachón

Línea troncal trifásica en 22,9 kV de 13,89 km, con 122 estructuras, desde la red existente de Capachica hasta Llachón (Puno).
Proyecto académico, EPIME – UNA Puno. **Revisión vigente: Rev. 8.**
Autor: Renzo Gabriel Mamani Galindo · Revisor: Leonidas Vilca Callata.

## Qué abrir

| Necesito… | Archivo |
|---|---|
| El expediente técnico completo (11 volúmenes) | [`expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip`](expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip) · [resumen y supuestos](documentacion/EXPEDIENTE_LP229.md) |
| Todo el proyecto en un solo PDF (233 páginas, con marcadores) | [`expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON_COMPLETO.pdf`](expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON_COMPLETO.pdf) |
| Los planos en AutoCAD | [`plans/LP_REV8.dwg`](plans/LP_REV8.dwg) (23 láminas A3) · [guía de AutoCAD](documentacion/GUIA_AUTOCAD_EDITABLES.md) |
| Los planos en PDF | [`plans/LP_REV8.pdf`](plans/LP_REV8.pdf) |
| Las láminas de armados | [`plans/armados_lp229/`](plans/armados_lp229/) (14 láminas, DWG/DXF/PDF) |
| Cómo se hicieron los planos | [PLANOS_REV8_MOTOR_LP229.md](documentacion/PLANOS_REV8_MOTOR_LP229.md) · [formato EPIME](documentacion/FORMATO_PLANOS_EPIME_REV6.md) |
| Versiones anteriores (Rev. 1 a Rev. 7) | [`archivo/`](archivo/README.md) |

Resultados: conductor **AAAC 35 mm²** (óptimo económico), valor referencial **S/ 1 246 413,96**, máxima demanda de 143 kW al año 2047,
caída de tensión de 0,48 %. **17 de 17 verificaciones CONFORME.**
Antes de presentarlo como estudio definitivo hay que reemplazar los supuestos: factibilidad de Electro Puno, población, topografía, resistividad y suelos.
La lista está en [EXPEDIENTE_LP229.md](documentacion/EXPEDIENTE_LP229.md).

## Carpetas

```text
datos/            entradas: eje KML (vertices_corredor_manual.csv), cruces viales y motor_lp229/ (entrada y resultados del motor)
sources/          fuentes originales sin modificar (KML, GISEM, OSM, SRTM)
scripts/          generar_expediente.py (todo), planos_motor_epime.py (Rev. 8) y planos_formato_epime.py (formato EPIME)
tests/            pruebas de los dos scripts
plans/            planos vigentes Rev. 8 y armados
expediente/       expediente técnico completo (ZIP)
documentacion/    guía de AutoCAD, explicación de los planos y del expediente
archivo/          Rev. 1 a Rev. 7 (no usar como entrada vigente)
```

## Regenerar el expediente

Un solo comando corre el motor, rehace los planos y arma el ZIP. Necesita un clon del motor y Microsoft Office:

```powershell
git clone https://github.com/dilmar231gabriel-ops/expediente-lp-22.9kv C:\Users\renzo\EXP_LP\motor
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/generar_expediente.py --motor C:\Users\renzo\EXP_LP\motor
python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests -q
```

Le aplica al motor los parches de `datos/motor_lp229/` (Office en vez de LibreOffice; sección del conductor y revisor en el cajetín).
Los DWG salen con AutoCAD si está instalado y, si no, con ODA File Converter (`C:\Users\renzo\ODAFileConverter`).
Solo los planos: `scripts/planos_motor_epime.py --dwg`.
La ingeniería (estructuras, perfil y flechas) viene del motor [expediente-lp-22.9kv](https://github.com/dilmar231gabriel-ops/expediente-lp-22.9kv), de D. H. Ccora.
Su entrada está en `datos/motor_lp229/entrada/proyecto.yaml`.
