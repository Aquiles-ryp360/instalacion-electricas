# Ficha de norma: Código Nacional de Electricidad - Suministro 2011

## Identificación

- Código interno: CNE-Suministro.
- Nombre: Código Nacional de Electricidad - Suministro 2011.
- Entidad emisora: Ministerio de Energía y Minas (MINEM) / Dirección General de Electricidad (DGE).
- Aprobación: R.M. N.° 366-2011-MEM/DM.
- Base legal superior: Ley de Concesiones Eléctricas (D.L. N.° 25844) y su Reglamento (D.S. N.° 009-93-EM).
- Fiscalización: OSINERGMIN.
- Texto oficial: <https://www.gob.pe/institucion/minem/normas-legales/174312-366-2011-mem-dm>.
- Fecha de comprobación: 2026-10-11.

---

## Función dentro de un proyecto de Redes y Transmisión

El CNE-Suministro 2011 es la norma de **cumplimiento obligatorio** que rige las instalaciones de generación, líneas de transmisión y redes de distribución en media y baja tensión en todo el territorio peruano. Define las condiciones de seguridad pública, distancias mínimas de seguridad (DMS), cálculo mecánico de estructuras y conductores, y servidumbres de paso.

---

## Secciones y Reglas Críticas Aplicadas al Proyecto Limbani

| Parte / Sección | Título / Regla | Aplicación en el Proyecto de Limbani |
| :--- | :--- | :--- |
| **Parte 1 (Regla 010-017)** | Reglas para la puesta a tierra de sistemas eléctricos | Puesta a tierra de neutro de transformadores, puesta a tierra de protección (PAT) en estructuras de MT y BT, pararrayos en SED. Resistencia máxima $\le 25\ \Omega$ (o $\le 10\ \Omega$ en SED). |
| **Parte 2 / Sección 21** | Separaciones y Distancias Mínimas de Seguridad (DMS) | Distancias verticales del conductor al suelo:<br>- Calles y avenidas transitables: $\ge 6.5\text{ m}$ en MT (10-22.9 kV), $\ge 5.5\text{ m}$ en BT.<br>- Terrenos no transitables / laderas andinas: $\ge 5.5\text{ m}$ en MT, $\ge 4.0\text{ m}$ en BT.<br>- Cruces sobre cursos de agua y ríos (Río Limbani): $\ge 6.0\text{ m}$ libre sobre nivel de crecida máxima. |
| **Parte 2 / Sección 22** | Separaciones respecto a edificaciones y fajas marginales | Distancia horizontal mínima de conductores a fachadas, ventanas y balcones: $\ge 2.5\text{ m}$ en MT y $\ge 1.0\text{ m}$ en BT autoportante. |
| **Parte 2 / Sección 23** | Sobrecargas mecánicas y factores de seguridad | Hipótesis de cálculo mecánico según zona climática (Zona 2 - Sierra/Altiplano):<br>- Hipótesis I: Viento máximo ($V_{\text{viento}} = 80-100\text{ km/h}$, $T_{\text{min}} = 5^\circ\text{C}$).<br>- Hipótesis II: Temperatura mínima ($T = -5^\circ\text{C}$, viento moderado).<br>- Hipótesis III: Temperatura máxima ($T = 35^\circ\text{C}$, viento nulo, flecha máxima). |
| **Parte 2 / Sección 24** | Selección y esfuerzo en soportes (Postes CAC) | Factores de seguridad para postes de concreto armado centrifugado (CAC): factor $\ge 2.0$ respecto a la carga de rotura nominal en la cima. |
| **Parte 3 / Sección 30** | Subestaciones de Distribución (SED) aéreas monoposte y biposte | Montaje de transformadores en estructura biposte (SAB) con seccionadores cut-out, pararrayos de óxido de zinc (ZnO) y tablero de distribución con termomagnéticos. |

---

## Consideraciones Especiales por Altitud (> 1,000 m.s.n.m.)

- Limbani se ubica a aproximadamente **3,050 m.s.n.m.**.
- Conforme a la Regla 214 del CNE-Suministro y la norma IEC 60071, la densidad del aire disminuye con la altitud, reduciendo la rigidez dieléctrica del aire.
- **Factor de corrección por altitud ($k_a$):**
  $$k_a = e^{\frac{H - 1000}{8150}} \approx e^{\frac{3050 - 1000}{8150}} \approx 1.28$$
- Por tanto, la línea de fuga de los aisladores (aisladores poliméricos o de porcelana tipo pin y suspensión) y las distancias dieléctricas en aire deben incrementarse en un **28%** respecto al nivel del mar.
