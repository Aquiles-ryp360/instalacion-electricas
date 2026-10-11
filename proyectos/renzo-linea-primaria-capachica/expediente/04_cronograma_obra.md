# Cronograma de Ejecución Física de Obra
## Proyecto: Línea Primaria 22.9 kV y Redes Secundarias - Sector Chifrón, Capachica

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Curso:** MEC330 — Instalaciones Eléctricas II  
**Plazo de Ejecución:** 90 Días Calendario (03 Meses)  

---

## 1. Diagrama de Fases y Programación Temporal (90 Días)

```
Mes 1 (Días 1-30)           Mes 2 (Días 31-60)          Mes 3 (Días 61-90)
[S1][S2][S3][S4]            [S5][S6][S7][S8]            [S9][S10][S11][S12]
====================        ====================        ====================
|-- Replanteo Topo --|
       |-- Excavaciones --|
              |-- Izaje y Cimentación Postes --|
                          |-- Montaje de Armados --|
                                 |-- Montaje SED 100 kVA --|
                                        |-- Tendido de Conductores --|
                                               |-- Acometidas y AP --|
                                                        |-- Pruebas y Cierre --|
```

---

## 2. Desglose de Partidas y Ruta Crítica (WBS)

| Fase / Hito | Descripción de Actividades | Duración (Días) | Inicio (Día) | Fin (Día) | Precedencia | ¿Ruta Crítica? |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **F-01** | **Trabajos Preliminares y Replanteo:** Movilización de equipos, replanteo topográfico de los 9 vértices MT y 36 postes BT con estación total. | 15 | 1 | 15 | --- | **SÍ** |
| **F-02** | **Obras Civiles y Excavaciones:** Excavación manual y mecánica en terreno semirrocoso para pozos de cimentación y zanjas de anclaje de retenidas. | 20 | 11 | 30 | F-01 (parcial) | **SÍ** |
| **F-03** | **Transporte e Izaje de Postes:** Traslado de postes C.A.C. de 12m, 13m, 8m y 9m, izaje con grúa/cabria, aplomado y colado de concreto ciclópeo. | 20 | 25 | 44 | F-02 | **SÍ** |
| **F-04** | **Montaje de Armados y Ferretería:** Fijación de crucetas, aisladores pin ANSI 56-3, ménsulas, soportes de BT y cable de acero para retenidas R-1/RET-I. | 15 | 40 | 54 | F-03 | NO |
| **F-05** | **Montaje de Subestación SAB-1:** Instalación de plataforma portatransformador, izaje del trafo 100 kVA, tablero BT IP65 y puesta a tierra PAT-3. | 20 | 45 | 64 | F-03 | **SÍ** |
| **F-06** | **Tendido y Flechado de Conductores:** Tendido de AAAC 35 mm² en MT y CAAI en BT mediante poleas, tensado con dinamómetro según tabla CNE y atado final. | 20 | 55 | 74 | F-04, F-05 | **SÍ** |
| **F-07** | **Acometidas y Alumbrado Público:** Instalación de 15 luminarias LED 60W con pastorales y 43 acometidas domiciliarias monofásicas con medidores. | 15 | 65 | 79 | F-06 | NO |
| **F-08** | **Pruebas Eléctricas y Puesta en Servicio:** Medición de resistencia de puesta a tierra con telurómetro, aislamiento con megóhmetro, energización y recepción. | 11 | 80 | 90 | F-06, F-07 | **SÍ** |

---

## 3. Hitos Contractuales de Control

1. **Hito 1 (Día 15):** Aprobación del Acta de Replanteo Topográfico por parte de la Supervisión de Obra.
2. **Hito 2 (Día 45):** Conclusión del 100% de cimentaciones e izaje de postes C.A.C. en MT y BT.
3. **Hito 3 (Día 65):** Montaje mecánico completo de la Subestación Biposte SAB-1 100 kVA con protocolo de pruebas en fábrica del transformador.
4. **Hito 4 (Día 75):** Conclusión de tendido y templado de conductores primarios y secundarios, verificado con la tabla de flechado de Truxa.
5. **Hito 5 (Día 90):** Pruebas de aislamiento, continuidad y puesta a tierra satisfactorias, firma del Acta de Recepción de Obra y Transferencia a **Electro Puno S.A.A.**

---

## 4. Plan de Contingencia Meteorológica Altiplánica
* Debido a los vientos severos en la península de Capachica (hasta $75\text{ km/h}$), las labores de izaje de postes y tendido aéreo de conductores se programarán prioritariamente en horas matutinas (06:00 a 12:00 horas), evitando ráfagas vespertinas y tormentas convectivas.
* Se mantendrán solados protegidos contra heladas nocturnas ($-15^\circ\text{C}$) mediante aditivos acelerantes de fraguado y mantas térmicas curadoras.
