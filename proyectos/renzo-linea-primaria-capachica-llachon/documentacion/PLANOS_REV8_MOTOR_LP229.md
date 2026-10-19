# Planos Rev. 8: motor LP 22,9 kV + formato EPIME

Rev. 8 (19/10/2026): conductor AAAC 35 mm² (óptimo económico), revisor Leonidas Vilca Callata en el cajetín, DWG con ODA.
La Rev. 7 (AAAC 70 mm²) está en `archivo/rev7_planos/`.

## Origen

La ingeniería sale del motor [expediente-lp-22.9kv](https://github.com/dilmar231gabriel-ops/expediente-lp-22.9kv),
de D. H. Ccora, en el commit indicado en `datos/motor_lp229/COMMIT_MOTOR.txt`. Se ejecutan sus 15 pasos con `scripts/generar_expediente.py`:

- **Entrada** (`datos/motor_lp229/entrada/`):
  - `proyecto.yaml` de Capachica–Llachón;
  - el eje KML manual de este proyecto, con sus 4 tramos unidos;
  - el DEM Copernicus GLO-30 (cotas de 3 806 a 4 238 m s.n.m.);
  - las vías y el agua de OpenStreetMap.
- **Resultados** (`datos/motor_lp229/resultados/`): planilla de estructuras, perfil del terreno, parámetros de vano, cruces y trazado rectificado.
- **Láminas de armados** (`plans/armados_lp229/`): las 14 láminas LD-LP del motor, en DXF, DWG y PDF.

Resultado del motor: 122 estructuras en 13,89 km. Todos los postes cumplen la verificación de carga.

| Armados | Cantidad |
|---|---|
| PS1-3 | 78 |
| PA1-3 | 27 |
| PA2-3 | 8 |
| TS-3 | 6 |
| PSER-3, PR3-3, PTH-3 | 1 c/u |

| Otros resultados | Valor |
|---|---|
| Postes | 12/300: 74 · 12/400: 40 · 13/400: 8 |
| Retenidas RI | 44 (Rev. 7 con 70 mm²: 49) |
| Puesta a tierra | PAT-1: 41 · PAT-2: 2 |
| Vanos | 35 a 200 m, promedio 115 m |

## Qué mejora Rev. 8 frente a los planos del motor

| Planos del motor | Rev. 8 |
|---|---|
| A1, con el perfil en una franja delgada y mucho espacio vacío | A3 EPIME; la escala vertical se elige por hoja (1:250 a 1:1000) y el perfil se centra en su franja |
| Todo dibujado en milímetros en el modelo | Modelo en coordenadas UTM 19S reales, con láminas por presentaciones y ventanas gráficas a escala |
| Membrete genérico | Cajetín EPIME, como en el proyecto Conima–Tilali |
| Planta general a 1:25 000 | Plantas 1:5 000 con postes numerados, cuadro por poste (atributos), vanos, retenidas, PAT y cruces |
| Tabla de datos encima del perfil, lejos de los postes | Tabla debajo del perfil, con los valores rotados y alineados con cada poste |
| Solo DXF y PDF | DWG 2018 (AutoCAD o ODA, con AUDIT), DXF y PDF |

Láminas en `plans/LP_REV8.*` (23 en total):

- **LP-01:** ubicación, clave de láminas, unifilar y datos técnicos.
- **LP-02 a LP-13:** plantas.
- **LP-14 a LP-22:** perfil y planimetría a H 1:5 000.
- **LP-23:** cuadro de estructuras y coordenadas.

## Supuestos que siguen pendientes

- 22,9 kV, el punto de diseño (E-001, PSER-3) y la demanda (1 500 hab., INEI 2017 por confirmar) son supuestos.
  Hay que confirmarlos con Electro Puno.
- El DEM de 30 m no sirve para replantear; se necesita topografía.
- El clima es de SENAMHI Puno sin verificar.
- La línea va de 3 813 a 3 867 m s.n.m. El valor de 4 238 m citado arriba es la cota máxima del recuadro del DEM (cerros vecinos), no de la línea.
  El motor verificó el aislamiento a 3 900 m de altitud de diseño y salió CONFORME, aunque con poco margen: PIN 56-4, línea de fuga requerida de 681 mm frente a los 685 mm disponibles.
- Expediente completo de 11 volúmenes: ver [EXPEDIENTE_LP229.md](EXPEDIENTE_LP229.md).

## Regenerar

```powershell
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/planos_motor_epime.py --autocad
python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests/test_planos_motor_epime.py -q
```

Si cambia el diseño, se vuelve a correr el motor con `datos/motor_lp229/entrada/proyecto.yaml`
y se copian sus resultados en `datos/motor_lp229/resultados/`.
