# Línea primaria 22,9 kV Capachica–Llachón

Línea troncal trifásica en 22,9 kV de 13,89 km, con 122 estructuras, desde la red existente de Capachica hasta Llachón (Puno).
Proyecto académico, EPIME – UNA Puno. **Revisión vigente: Rev. 7.**

## Qué abrir

| Necesito… | Archivo |
|---|---|
| El expediente técnico completo (11 volúmenes) | [`expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip`](expediente/EXPEDIENTE_LP229_CAPACHICA_LLACHON.zip) · [resumen y supuestos](documentacion/EXPEDIENTE_LP229.md) |
| Los planos en AutoCAD | [`plans/LP_REV7.dwg`](plans/LP_REV7.dwg) (23 láminas A3) · [guía de AutoCAD](documentacion/GUIA_AUTOCAD_EDITABLES.md) |
| Los planos en PDF | [`plans/LP_REV7.pdf`](plans/LP_REV7.pdf) |
| Las láminas de armados | [`plans/armados_lp229/`](plans/armados_lp229/) (14 láminas, DWG/DXF/PDF) |
| Cómo se hicieron los planos | [PLANOS_REV7_MOTOR_LP229.md](documentacion/PLANOS_REV7_MOTOR_LP229.md) · [formato EPIME](documentacion/FORMATO_PLANOS_EPIME_REV6.md) |
| Versiones anteriores (Rev. 1 a Rev. 6) | [`archivo/`](archivo/README.md) |

Resultados: valor referencial **S/ 1 359 760,11**, máxima demanda de 143 kW al año 2047, caída de tensión de 0,29 %. **17 de 17 verificaciones CONFORME.**
Antes de presentarlo como estudio definitivo hay que reemplazar los supuestos: factibilidad de Electro Puno, población, topografía, resistividad y suelos.
La lista está en [EXPEDIENTE_LP229.md](documentacion/EXPEDIENTE_LP229.md).

## Carpetas

```text
datos/            entradas: eje KML (vertices_corredor_manual.csv), cruces viales y motor_lp229/ (entrada y resultados del motor)
sources/          fuentes originales sin modificar (KML, GISEM, OSM, SRTM)
scripts/          planos_motor_epime.py (Rev. 7) y planos_formato_epime.py (formato EPIME y funciones comunes)
tests/            pruebas de los dos scripts
plans/            planos vigentes Rev. 7 y armados
expediente/       expediente técnico completo (ZIP)
documentacion/    guía de AutoCAD, explicación de los planos y del expediente
archivo/          Rev. 1 a Rev. 6 (no usar como entrada vigente)
```

## Regenerar los planos

```powershell
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/planos_motor_epime.py --autocad
python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests -q
```

`--autocad` usa AutoCAD 2027 para generar el DWG y el PDF. Sin esa opción solo sale el DXF y un PDF de vista previa.
La ingeniería (estructuras, perfil y flechas) viene del motor [expediente-lp-22.9kv](https://github.com/dilmar231gabriel-ops/expediente-lp-22.9kv), de D. H. Ccora.
Su entrada está en `datos/motor_lp229/entrada/proyecto.yaml`.
