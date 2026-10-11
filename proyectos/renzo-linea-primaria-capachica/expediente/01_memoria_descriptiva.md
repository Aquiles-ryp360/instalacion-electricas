# CAPÍTULO I: MEMORIA DESCRIPTIVA

**PROYECTO:**  
*INSTALACIÓN DEL SISTEMA DE ELECTRIFICACIÓN RURAL MEDIANTE LÍNEA PRIMARIA EN MEDIA TENSIÓN 22.9 kV Y SUBESTACIÓN DE DISTRIBUCIÓN 100 kVA PARA EL SECTOR CHIFRÓN, DISTRITO DE CAPACHICA — PUNO*

---

## 1. GENERALIDADES

### 1.1 Introducción
El presente proyecto corresponde al diseño definitivo a nivel de ingeniería de detalle de la **Línea Primaria en Media Tensión (22.9 kV, 3Ø)** y la **Subestación de Distribución Proyectada (SED Biposte, 100 kVA)**, destinada a suministrar energía eléctrica continua y confiable a las viviendas e infraestructura comunal del sector **Chifrón**, ubicado en la península de Capachica, Provincia y Departamento de Puno.

El desarrollo de este estudio técnico forma parte del curso de especialidad **MEC330 — Instalaciones Eléctricas II**, dictado en la Escuela Profesional de Ingeniería Mecánica Eléctrica de la Facultad de Ingeniería Mecánica Eléctrica, Electrónica y Sistemas (FIME) de la Universidad Nacional del Altiplano (UNA Puno), bajo la cátedra de los ingenieros **Leonidas Vilca Callata** y **Marcos José Villanueva Cornejo**.

### 1.2 Objetivo del Proyecto
* Dotar de suministro eléctrico al sector rural de Chifrón, beneficiando directamente a **43 familias censadas** ($C1$ a $C43$) con energía para uso doméstico, alumbrado público y pequeñas actividades socioproductivas.
* Desarrollar la ingeniería electromecánica conforme a los requerimientos del **Código Nacional de Electricidad (CNE Suministro 2011)** y la **Norma DGE "Bases para el Diseño de Líneas y Redes Primarias para Electrificación Rural" (R.D. 018-2003-EM/DGE)**.
* Optimizar la selección de materiales, cálculo de esfuerzos mecánicos de los conductores y soportes, respetando las severas condiciones climáticas del Altiplano peruano ($>3,800\text{ msnm}$).

---

## 2. UBICACIÓN GEOGRÁFICA Y POLÍTICA

El área del proyecto se ubica en el extremo oriental de la península de Capachica, adyacente a las orillas del Lago Titicaca:

* **Departamento:** Puno
* **Provincia:** Puno
* **Distrito:** Capachica
* **Sector:** Chifrón
* **Altitud de Diseño:** Variable entre $3,817.04\text{ msnm}$ y $3,924.17\text{ msnm}$ (Altitud media de cálculo: $3,850\text{ msnm}$).
* **Zona UTM:** Zona 19 Sur
* **Datum Horizontal:** WGS-84

### Coordenadas del Área de Influencia:
* **Punto de Conexión / Derivación ($E-01$):**
  * Este: $412,606.01\text{ m E}$
  * Norte: $8,270,712.24\text{ m N}$
  * Cota: $3,924.17\text{ msnm}$
* **Subestación Proyectada ($E-04$):**
  * Este: $412,759.20\text{ m E}$
  * Norte: $8,270,976.22\text{ m N}$
  * Cota: $3,839.56\text{ msnm}$
* **Fin de Traza Primaria ($E-09$):**
  * Este: $412,659.90\text{ m E}$
  * Norte: $8,271,446.51\text{ m N}$
  * Cota: $3,824.61\text{ msnm}$

### Acceso a la Zona
El acceso desde la ciudad de Puno se realiza por la carretera asfaltada Puno – Paucarcolla – Capachica ($62\text{ km}$), y luego por la trocha carrozable afirmada que conecta la capital distrital de Capachica con el sector Chifrón ($4.5\text{ km}$), permitiendo el transporte de postes de concreto armado y equipos pesados.

---

## 3. CONDICIONES CLIMÁTICAS Y AMBIENTALES

De acuerdo con la zonificación meteorológica del Código Nacional de Electricidad (Suministro 2011) y las Normas DGE para la Sierra Sur del Perú:

* **Zona Meteorológica:** Zona 2 / 3 (Altiplano > $3,000\text{ msnm}$)
* **Temperatura Máxima Absoluta:** $+35.0^\circ\text{C}$
* **Temperatura Mínima Absoluta:** $-15.0^\circ\text{C}$
* **Temperatura Media Anual (Templado / EDS):** $+15.0^\circ\text{C}$
* **Velocidad de Viento Máxima de Diseño:** $75.0\text{ km/h}$ ($20.83\text{ m/s}$)
* **Espesor de Manguito de Hielo:** $6.0\text{ mm}$ (a $-5.0^\circ\text{C}$)
* **Nivel de Contaminación Ambiental:** Ligero / Medio (zona rural lacustre)
* **Nivel Isoceráunico:** $40\text{ a } 50\text{ días de tormenta al año}$ (requiere protección pararrayos ZnO)

---

## 4. PUNTO DE DISEÑO Y ALIMENTACIÓN ELÉCTRICA

La factibilidad de suministro eléctrico se sustenta en la red primaria de media tensión operada por la concesionaria **Electro Puno S.A.A.**, verificada en el geovisor oficial **GISEM de OSINERGMIN**:
* **Código de Alimentador / Tramo:** `TMT000012389` / `TMT001847370`
* **Naturaleza de la Red:** Línea aérea de Media Tensión
* **Tensión Nominal del Sistema:** $22.9\text{ kV}$ (Trifásica, $60\text{ Hz}$, neutro sólidamente conectado a tierra o a través de transformador de zigzag).
* **Estructura de Derivación ($E-01$):** Poste C.A.C. $12\text{ m} / 400\text{ daN}$, equipado con seccionamiento mediante tres (03) cortacircuitos fusibles tipo expulsión (cut-out) de $27\text{ kV}, 100\text{ A}, 150\text{ kV BIL}$ y tres (03) pararrayos de óxido de zinc de $21\text{ kV}, 10\text{ kA}$, garantizando el aislamiento de la nueva línea ante fallas operativas.

---

## 5. ESTUDIO DE MERCADO, PROYECCIÓN Y CUADRO DE CARGAS

### 5.1 Parámetros de Partida (Metodología Oficial MEC330)
* **Usuarios Iniciales ($NU_0$):** $43\text{ viviendas}$ (Censo georreferenciado $C1$ a $C43$).
* **Tasa de Crecimiento Anual ($TC$):** $3.0\%\ (0.03)$
* **Periodo de Proyección ($n$):** $20\text{ años}$ ($2026 - 2046$)
* **Factor de Proyección:**
  $$(1 + TC)^n = (1 + 0.03)^{20} = 1.80611$$
* **Calificación Eléctrica Asignada:** $0.90\text{ kW / usuario}$
* **Tensión de Servicio BT:** $V = 220\text{ V}$
* **Factor de Potencia del Sistema:** $\cos\phi = 0.90$
* **Alumbrado Público (Lámparas de 60 W):** $P_{\text{lámpara}} = 0.06\text{ kW}$

### 5.2 Formulación Matemática Aplicada
1. **Proyección de Usuarios al Año 20:**
   $$NU_f = NU_0 \cdot (1 + TC)^n \quad \text{(redondeado al entero)}$$
2. **Potencia del Servicio Particular:**
   $$Potencia_{\text{part}} = NU_f \cdot 0.90\text{ kW}$$
3. **Número de Luminarias de Alumbrado Público:**
   $$N^\circ lum = \frac{3.3 \cdot NU_f}{18} \quad \text{(redondeado al entero)}$$
4. **Potencia de Alumbrado Público:**
   $$Potencia_{\text{alum}} = N^\circ lum \cdot 0.06\text{ kW}$$
5. **Demanda Máxima Total Activa:**
   $$Total_{\text{kW}} = Potencia_{\text{part}} + Potencia_{\text{alum}}$$
6. **Corriente Nominal de Servicio:**
   $$I = \frac{Total_{\text{kW}} \cdot 1000}{V \cdot \cos\phi} = \frac{Total_{\text{kW}} \cdot 1000}{220 \cdot 0.90} = \frac{Total_{\text{kW}} \cdot 1000}{198}$$
7. **Potencia Aparente y Selección de Transformador:**
   $$Potencia_{\text{kVA}} = \frac{Total_{\text{kW}}}{\cos\phi} = \frac{Total_{\text{kW}}}{0.90}$$

### 5.3 Cuadro Oficial de Cargas y Máxima Demanda por Circuitos

| Circuito | Sector / Zona de Red | $NU_0$ (2026) | $NU_f$ (2046) | Servicio Part. (kW) | $N^\circ$ Lum | Pot. AP (kW) | Total (kW) | Corriente $I$ (A) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C-1** | Sector Sur / Pasaje | 21 | 38 | $34.20$ | 7 | $0.42$ | $34.62$ | $174.85$ |
| **C-2** | Sector Centro / Eje | 11 | 20 | $18.00$ | 4 | $0.24$ | $18.24$ | $92.12$ |
| **C-3** | Sector Norte / Camino | 11 | 20 | $18.00$ | 4 | $0.24$ | $18.24$ | $92.12$ |
| **TOTAL** | **Red Completa Chifrón** | **43** | **78** | **$70.20$** | **15** | **$0.90$** | **$71.10$** | **$359.09$** |

### 5.4 Potencia Aparente y Selección Definitiva del Transformador
* **Demanda Máxima Total Activa:** $Total_{\text{kW}} = 71.10\text{ kW}$
* **Potencia Aparente Requerida:**
  $$Potencia_{\text{kVA}} = \frac{71.10\text{ kW}}{0.90} = \mathbf{79.00\text{ kVA}}$$
* **Selección del Transformador Comercial:**
  En el catálogo de transformadores de distribución trifásicos estandarizados en el Perú ($25, 37.5, 50, 75, 100, 160\text{ kVA}$), la potencia comercial normalizada inmediata superior es:
  $$\mathbf{S_{\text{nom}} = 100\text{ kVA}}$$
  * **Relación de Transformación:** $22.9 / 0.38 - 0.22\text{ kV}$ (Trifásico, $60\text{ Hz}$).
  * **Factor de Carga al Año 20:** $\frac{79.00}{100} = 79.0\%$, asegurando un $21\%$ de margen de reserva técnica para sobrecargas y ampliaciones futuras.

---

## 6. DESCRIPCIÓN TÉCNICA DE LA LÍNEA PRIMARIA (22.9 kV)

### 6.1 Características del Trazado
* **Longitud Total:** $816.60\text{ metros}$ ($0.817\text{ km}$)
* **Número de Estructuras:** 9 postes ($E-01$ a $E-09$)
* **Vano Promedio:** $\approx 102\text{ metros}$ (Vano mínimo: $79.8\text{ m}$, Vano máximo: $115.6\text{ m}$)
* **Topografía:** Descenso pronunciado en los primeros $305\text{ m}$ (desnivel de $84.6\text{ m}$ entre $E-01$ y $E-04$), seguido de terreno ondulado suave hacia el borde del caserío.

### 6.2 Conductor Seleccionado
* **Tipo:** Conductor desnudo de Aleación de Aluminio (**AAAC** — *All Aluminium Alloy Conductor*).
* **Sección Nominal:** **$35\text{ mm}^2$** (sección real: $34.36\text{ mm}^2$, 7 hilos de $2.50\text{ mm}$ de diámetro).
* **Diámetro Exterior:** $7.50\text{ mm}$
* **Peso Unitario:** $0.0945\text{ kg/m}$
* **Tiro de Rotura Nominal:** $1,040\text{ kg}$ ($10.20\text{ kN}$)
* **Módulo de Elasticidad Final ($E$):** $6,000\text{ kg/mm}^2$ ($58,860\text{ MPa}$)
* **Coeficiente de Dilatación Lineal ($\alpha$):** $23.0 \times 10^{-6}\ ^\circ\text{C}^{-1}$
* **Resistencia Eléctrica a $20^\circ\text{C}$:** $0.963\ \Omega\text{/km}$ (corregida a $50^\circ\text{C}$: $0.986\ \Omega\text{/km}$)
* **Reactancia Inductiva ($x$ a DMG $1.20\text{ m}$):** $0.385\ \Omega\text{/km}$

### 6.3 Soportes (Postes)
* **Material:** Concreto Armado Centrifugado (**C.A.C.**), acabado liso, conicidad $1.5\%$.
* **Tipos Empleados:**
  * Postes de Suspensión / Alineamiento: **C.A.C. $12\text{ m} / 300\text{ daN}$** ($E-02, E-03, E-07$)
  * Postes de Ángulo y Terminales: **C.A.C. $12\text{ m} / 400\text{ daN}$** ($E-01, E-05, E-06, E-08, E-09$)
  * Estructura Biposte de Subestación: **02 Postes C.A.C. $13\text{ m} / 400\text{ daN}$** ($E-04$)
* **Empotramiento de Postes:**
  * Postes de $12\text{ m}$: $t = 0.10 \times H + 0.20 = 1.40\text{ m}$
  * Postes de $13\text{ m}$: $t = 0.10 \times H + 0.20 = 1.50\text{ m}$

### 6.4 Aislamiento y Ferretería
* **Aisladores de Suspensión:** Tipo polimérico de goma de silicona, tensión nominal $25\text{ kV}$, longitud de línea de fuga mínima $720\text{ mm}$ (adaptada a altitud $>3,800\text{ msnm}$ según IEC 60071-1).
* **Aisladores de Espiga (Pin):** Tipo pin de porcelana ANSI 56-3 con espiga de acero galvanizado en caliente de $1\ 3/8'' \times 10''$.
* **Crucetas:** Crucetas de madera tratada o perfil de fierro galvanizado en caliente (F°G°) de $2.00\text{ m} \times 75\text{ mm} \times 75\text{ mm} \times 6.4\text{ mm}$.
* **Ferretería General:** Todo el material ferroso es galvanizado en caliente bajo norma ASTM A-153.

### 6.5 Armados Normalizados DGE
De conformidad con las láminas oficiales del archivo de ferretería [`laminas_de_detalle.dwg`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/fuentes/referencia_aricato/laminas_de_detalle.dwg):
* **Armado PS-1:** Estructura de suspensión trifásica vertical con aisladores poliméricos/pin.
* **Armado PA-1:** Estructura de alineamiento con ángulo hasta $30^\circ$ con aisladores pin reforzados.
* **Armado PR-1:** Estructura de anclaje/retención terminal con aisladores poliméricos de suspensión y grapas pistolas.
* **Armado SAB-1:** Estructura biposte para montaje de transformador de distribución, pararrayos, cut-out y tablero de distribución BT.

### 6.6 Sistema de Puesta a Tierra (PAT)
* **Tipo:** Armado normalizado **PAT-3**.
* **Configuración:** Electrodo vertical de cobre electrolítico de $5/8'' \times 2.40\text{ m}$, conductor de bajada de cobre desnudo de $35\text{ mm}^2$, conectado mediante soldadura exotérmica (cadweld).
* **Tratamiento del Terreno:** Relleno de zanja con tierra cernida mezclada con bentonita sódica / sales electrolíticas para garantizar una resistencia de puesta a tierra:
  * En neutro de transformador: $R_{\text{pat}} \le 10\ \Omega$
  * En estructuras de derivación y pararrayos: $R_{\text{pat}} \le 15\ \Omega$

---

## 7. RESUMEN DE LA PLANILLA DE ESTRUCTURAS

| N° | Estructura | Progresiva (m) | Cota (msnm) | Poste C.A.C. | Armado DGE | Función en el Sistema |
| :-: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **E-01** | $0+000.00$ | $3,924.17$ | $12\text{ m} / 400\text{ daN}$ | **PR-1** | Derivación con cut-out y pararrayos en red Electro Puno |
| **2** | **E-02** | $0+105.00$ | $3,895.00$ | $12\text{ m} / 300\text{ daN}$ | **PS-1** | Suspensión en bajada de ladera |
| **3** | **E-03** | $0+210.00$ | $3,865.00$ | $12\text{ m} / 300\text{ daN}$ | **PS-1** | Suspensión |
| **4** | **E-04** | $0+305.21$ | $3,839.56$ | $13\text{ m} / 400\text{ daN}$ (x2) | **SAB-1** | **Subestación Biposte (Trafo 100 kVA 22.9/0.38-0.22 kV)** |
| **5** | **E-05** | $0+402.43$ | $3,817.04$ | $12\text{ m} / 400\text{ daN}$ | **PA-1** | Vértice de ángulo ($-36.06^\circ$) con retenida biselar |
| **6** | **E-06** | $0+518.02$ | $3,827.27$ | $12\text{ m} / 400\text{ daN}$ | **PA-1** | Vértice de ángulo ($+31.35^\circ$) con retenida biselar |
| **7** | **E-07** | $0+628.53$ | $3,824.61$ | $12\text{ m} / 300\text{ daN}$ | **PS-1** | Suspensión / Alineamiento |
| **8** | **E-08** | $0+708.34$ | $3,824.61$ | $12\text{ m} / 300\text{ daN}$ | **PA-1** | Ángulo leve ($+32.95^\circ$) con retenida |
| **9** | **E-09** | $0+816.60$ | $3,824.61$ | $12\text{ m} / 400\text{ daN}$ | **PR-1** | Retención terminal con retenida terminal simple |

---

## 8. RESULTADOS DE LOS CÁLCULOS JUSTIFICATIVOS

### 8.1 Cálculo Eléctrico
* **Caída de Tensión Máxima en MT:** $\Delta V = 26.88\text{ V} \rightarrow \mathbf{0.12\%}$ (Límite normativo CNE: $\le 5.0\%$). **CUMPLE AMPLIAMENTE**.
* **Pérdidas de Potencia Activa en MT:** $\Delta P = 0.183\text{ kW} \rightarrow \mathbf{0.12\%}$ de la potencia transmitida.
* **Corriente de Carga en MT:** $I_{\text{nominal}} = 4.20\text{ A}$ a plena carga del transformador.

### 8.2 Cálculo Mecánico de Conductores (Ecuación de Cambio de Estado)
* **Hipótesis Base EDS ($+15^\circ\text{C}$):** Tiro de templado $T_{\text{EDS}} = 187.20\text{ kg}$ ($18.0\%$ del tiro de rotura).
* **Hipótesis IV (Temp. Máxima $+35^\circ\text{C}$):** Flecha máxima en el vano crítico de $115.6\text{ m}$ es $f_{\text{máx}} = 1.33\text{ m}$.
* **Distancia Vertical al Suelo:** 
  * Altura de soporte útil: $12.0 - 1.4 = 10.60\text{ m}$
  * Altura mínima del conductor: $10.60 - 1.33 = \mathbf{9.27\text{ m}} > 6.50\text{ m}$ (exigido por CNE Suministro Regla 232 para cruce de vías). **CUMPLE HOLGADAMENTE**.

---

## 9. PLANOS Y ENTREGABLES ASOCIADOS

El proyecto cuenta con la documentación gráfica y documental requerida para su tramitación:
1. **Plano de Perfil Longitudinal y Distribución de Estructuras (DXF/DWG):** [`PLANO_PERFIL_LONGITUDINAL_LP_CAPACHICA.dxf`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/entregables/planos/PLANO_PERFIL_LONGITUDINAL_LP_CAPACHICA.dxf)
2. **Láminas de Detalle de Ferretería y Armados (DWG):** [`laminas_de_detalle.dwg`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/fuentes/referencia_aricato/laminas_de_detalle.dwg)
3. **Diagrama Unifilar de Subestación (DWG):** [`DIAGRAMAUNIFILAR.dwg`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/fuentes/referencia_aricato/DIAGRAMAUNIFILAR.dwg)
4. **Planilla de Estructuras (CSV):** [`planilla_estructuras_lp_capachica.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/datos/estructuras/planilla_estructuras_lp_capachica.csv)
5. **Censo de Cargas Georreferenciado (CSV):** [`censo_43_abonados.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/datos/cargas/censo_43_abonados.csv)

---
*Puno, Octubre de 2026*  
**Renzo Gabriel Mamani Galindo**  
Estudiante de Ingeniería Mecánica Eléctrica — UNA Puno  
Código: 228447
