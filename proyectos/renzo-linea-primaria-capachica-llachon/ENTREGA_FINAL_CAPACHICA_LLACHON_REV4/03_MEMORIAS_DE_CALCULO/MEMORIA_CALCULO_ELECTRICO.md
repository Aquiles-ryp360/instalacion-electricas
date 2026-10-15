# Memoria de cálculo eléctrico — modelo condicionado

**Resultado de dimensionamiento: pendiente.** No hay tensión, fases, demanda, conductor, parámetros R/X, Icc ni punto aprobado. La longitud KML cartográfica (13939.511910 m, cuatro segmentos) **no es aún longitud eléctrica aprobada**.

| Cálculo | Entradas y unidades | Ecuación/modelo | Salida y criterio de aceptación |
|---|---|---|---|
| Demanda | Estudio de carga presente/futura [kVA], simultaneidad, horizonte | Escenarios por tramo y punta coincidente | S diseño [kVA], aceptada por promotor/titular |
| Corriente trifásica | S [kVA], U línea [kV], 3 fases confirmadas | I [A] = S/(√3 U) | I por escenario; comparar ampacidad corregida |
| Conductor | I, ficha fabricante, material/sección, temperatura/altitud | Ampacidad corregida y resistencia de falla | Sección candidata justificada; sin ficha no seleccionar |
| Caída radial | I [A], L [km], R/X [Ω/km], cosφ | ΔU [V] ≈ √3 Σ I L (R cosφ + X senφ) | ΔU [%] frente a criterio oficial; flujo de red si hay derivaciones |
| Pérdidas | I por tramo [A], R [Ω/km], L [km] | P [W] = 3 Σ I² R L | P y energía por perfil horario/escenario |
| Cortocircuito/protección | Z fuente/red, U prefalla, curvas y ajustes | Equivalente de red; falla mínima/máxima, coordinación | Corte, sensibilidad, selectividad aprobados |
| Aislamiento/PAT | U máxima, esquema neutro, resistividad [Ω·m] | Selección BIL y estudio PAT según caso | Seguridad y especificaciones verificadas |
| Distancias | Categoría de cruce, perfil, flecha final | Distancia mínima calculada contra tabla pertinente CNE | Margen ≥ criterio aplicable |

El archivo editable `modelo_calculos_rev4.py` valida valores finitos y usa las fórmulas de corriente, caída y flecha **solo para ensayos con entradas proporcionadas**; no ejecuta una selección del proyecto. Requiere documentar estado de cada parámetro, versión de ficha, temperatura, factor de potencia, escenario y modelo de red. No se usaron valores típicos ni se emitió amperaje, caída o Icc para esta línea.
