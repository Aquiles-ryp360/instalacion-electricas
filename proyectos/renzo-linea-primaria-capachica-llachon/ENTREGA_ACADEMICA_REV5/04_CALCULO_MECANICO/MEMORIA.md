# Cálculo mecánico condicionado

**Sin vanos ni apoyos de proyecto aprobados.** `SITIOS_PARA_INGRESO_CAMPO.csv` conserva las 27 PN como sitios geométricos y deja vacías cota, aceptación de apoyo, vanos y fuerzas. No se presentan flechas o despejes reales.

| Modelo | Ecuación y unidades | Límite de validez / criterio |
|---|---|---|
| Vano regulador | L_r [m]=√(ΣL_i³/ΣL_i), L_i>0 [m] | Tramo entre anclajes con conductor/carga/tensión uniforme; definir primero apoyos reales. |
| Flecha nivelada | f [m]≈w [N/m] L² [m²]/(8H [N]) | Parábola, apoyos a igual cota y flecha pequeña; usar catenaria/cambio de estado con topografía y temperatura para diseño. |
| Viento lineal | q [N/m]=p [Pa] d [m] C_d | Requiere presión de caso, diámetro y coeficiente justificables. |
| Ángulo de deflexión | F [N]=2H sin(θ/2) | Solo tensiones horizontales iguales; sumar viento, peso, desequilibrios y factores para estructura. |
| Despeje nivelado muestreado | z_c(x)=z_fijación-4f x(L-x)/L²; g_mín=min(z_c-z_obstáculo) [m] | Apoyos a igual cota y obstáculos con mismo datum; no considera oscilación ni perfil continuo. Comparar contra tabla vigente por tipo de cruce. |

Casos a resolver: temperatura extrema, viento aplicable, estados de tendido/rotura según norma y titular, esfuerzos longitudinales/transversales, aisladores/herrajes, poste y retenidas. Para despeje se necesita perfil con datum vertical, cota de conductor bajo flecha crítica y obstáculo/clase de cruce; para cimentación, reacciones y geotecnia. Sin esas entradas no se asigna altura, clase, cimentación ni retenida.
