> **Alcance histórico, identificado el18/10/2026:** este análisis mezcla unproyecto urbano deLimbani con referencias deCapachica. No gobierna lalínea principal aHuancasayani. Ver `proyectos/aquiles-linea-primaria-inst-ii/proyecto.yaml` ylaauditoríaLP-R02. La precisión delcatastro y lascapacidades deequipos deben verificarse, no deducirse de serCAD.

# Análisis Profundo de Proyectos de Referencia de Líneas Eléctricas en el Repositorio

- **Autor de análisis:** Br. Aquiles Taylor Ramos Yapo (Cód. 227368)
- **Curso:** Instalaciones Eléctricas II / Redes Eléctricas y Subestaciones
- **Universidad:** Universidad Nacional del Altiplano - Puno (FIME - UNAP)
- **Fecha:** Octubre 2026

---

## 1. Objetivo del Análisis
Realizar una revisión exhaustiva de las metodologías, herramientas de cálculo, flujos de diseño CAD, estructura de expedientes y normativas aplicadas en los proyectos de líneas de transmisión y distribución existentes en el repositorio compartido (especialmente `proyectos/renzo-linea-primaria-capachica/` y `proyectos/renzo-linea-primaria-capachica-v2/`), con el fin de establecer una base técnica sólida y estandarizada para el desarrollo del **Expediente Técnico de Redes Eléctricas del Distrito de Limbani (MCH 200 kW)**.

---

## 2. Proyectos de Referencia Analizados

### 2.1 Proyecto `renzo-linea-primaria-capachica` (Línea Primaria 22.9 kV Chifrón)
- **Naturaleza:** Línea primaria rural en 22.9 kV ($0.817\text{ km}$, monofásica bifilar o trifásica), subestación aérea biposte SAB-1 (100 kVA, 22.9/0.38-0.22 kV) y red secundaria en baja tensión para 30 abonados en el sector Chifrón (Capachica, Puno).
- **Herramientas utilizadas:**
  1. `calcular_cuadro_cargas.py`: Diversificación de demanda por sectores con factor de simultaneidad y cargas de bombeo/turismo.
  2. `calculo_caida_tension_mt.py`: Cálculo analítico trifásico/bifilar de regulación de tensión ($\Delta V\%$) y pérdidas Joule ($\Delta P$).
  3. `calculo_mecanico_conductor.py`: Ecuación de cambio de estado de Truxa para conductor AAAC 35 mm², determinando tracciones de trabajo ($T$) y flechas ($f$) bajo 3 hipótesis climáticas (Viento máx, Temp mín, Flecha máx a 35°C).
  4. `generar_planos_cad_profesionales.py`: Script maestro en Python utilizando `ezdxf` y `matplotlib` para generar láminas normalizadas A3/A1 con marco institucional, membrete FIME-UNAP, simbología normalizada UNE-EN 60617 y Norma DGE-MEM (R.M. Nº 091-2002-EM/VME).
  5. `generar_laminas_planos_pdf.py`: Renderizador de planos vectoriales de alta resolución a PDF para compilación directa en el expediente técnico.
  6. `generar_perfil_topografico.py` y `generar_plano_perfil_dxf.py`: Generación del perfil longitudinal terreno vs. línea con catenarias parabólicas.

---

## 3. Matriz de Estandarización de Estructuras y Postería (Normas DGE)

Del análisis de Capachica y las normas DGE (R.D. 018-2003-EM/DGE y R.D. 026-2003-EM/DGE), se extrae la siguiente codificación canónica de estructuras aplicable a redes rurales y urbanas:

| Código de Armado | Tipo de Estructura | Función Mecánica / Eléctrica | Tipo de Poste CAC Típico | Tipo de Retenida Requerida |
| :---: | :---: | :---: | :---: | :---: |
| **PS-1 / PS-3** | Suspensión alineamiento | Soporte de paso en tramos rectos o ángulos menores ($< 5^\circ$). | CAC 12m/300 daN (MT) / CAC 8m/200 daN (BT) | Ninguna |
| **PA-1 / PA-3** | Ángulo | Desvío angular de traza ($5^\circ$ a $30^\circ$). Esfuerzo resultante lateral. | CAC 12m/400 daN o 13m/400 daN | Retenida biselar simple |
| **PR-1 / PR-3** | Retención / Anclaje | Absorción de esfuerzos longitudinales en tramos largos o ángulos ($> 30^\circ$). | CAC 13m/400 daN o 13m/600 daN | Retenida inclinada simple o contraviento |
| **SAB** | Subestación Aérea Biposte | Soporte de plataforma, transformador trifásico, cut-outs y pararrayos. | 2 x CAC 13m/400 daN espaciados $2.00\text{ m}$ | Contraviento doble / Inclinada |
| **FIN / TERM** | Terminal de línea | Remate de circuito al final de calle o tramo. | CAC 12m/400 daN o CAC 8m/300 daN | Retenida inclinada terminal |

---

## 4. Adaptación y Particularidades para el Proyecto Limbani

A diferencia del proyecto Capachica (que es una línea corta en península lacustre a 3,825 m.s.n.m.), el proyecto Limbani presenta características distintivas fundamentales:

1. **Topografía de Valle Encajonado:**
   - Limbani se ubica a 3,050 m.s.n.m. en una garganta estrecha entre laderas de alta pendiente y flanqueada por los ríos Limbani y Chinchalamani.
   - Longitud troncal de transmisión: $\approx 2.15\text{ km}$ desde la casa de máquinas de la MCH Limbani (Sector Norte) hasta la salida sur (Sector Piscina).
   - El cruce del río exige estructuras reforzadas (CAC 13m/600 daN con armados de anclaje PR y vanos mayores a 100 m).
2. **Mayor Escala de Demanda y Usuarios:**
   - Capachica: 30 abonados dispersos, 1 subestación de 100 kVA.
   - **Limbani:** **764 viviendas consolidadas, 623 lotes catastrados, 19 calles y pasajes urbanos**.
   - Demanda coincidente total: **181.80 kW** abastecida por la MCH Limbani de **200 kW**.
   - Requiere **tres (03) subestaciones aéreas biposte**: SED-01 (50 kVA), SED-02 (100 kVA) y SED-03 (100 kVA), totalizando 250 kVA para mantener las caídas de tensión en BT por debajo de 3.82% ($\le 5.0\%$).
3. **Flujo de Trazado CAD sobre Catastro Oficial:**
   - En Limbani no se trabaja con líneas aproximadas de Google Earth, sino con el **Catastro Urbano Oficial y Poligonal WGS 84 Zona 19 Sur** (`catastro_limbani.dxf`), donde cada manzana, calle, paramento y lote ya está levantado con precisión milimétrica.
   - Por tanto, la postería debe ubicarse sobre las veredas y bordes de calzada del catastro, respetando anchos de vía y accesos domiciliarios.

---

## 5. Metodología de Integración de Planos y Metrados en el Expediente

Siguiendo el modelo probado en las referencias del curso:
1. **Definición de Matriz Canónica de Postes y Redes:** Coordenadas Este, Norte, Cota, Altura/Carga de rotura, Tipo de Armado, Retenida y Puesta a Tierra.
2. **Generación del Plano Digital DXF:** Inyección de entidades (postes, conductores, transformadores, luminarias, acometidas) con capas, colores y tipos de línea estandarizados.
3. **Cálculo Automatizado de Metrados:** Conteo programático de elementos y suma de longitudes de conductores directamente desde las geometrías del plano DXF, garantizando 100% de coherencia entre plano y presupuesto.
4. **Exportación de Láminas PDF y DXF para el Anexo de Planos:** Láminas ejecutivas con escala normalizada, grilla UTM y carátula para inserción en el expediente técnico.
