# Cálculo eléctrico condicionado

**Resultado del proyecto: pendiente**, por falta de tensión, fases, demanda, conductor R/X/ampacidad, longitud eléctrica aprobada y equivalente de red. `rev5_modelos.py` no contiene parámetros por defecto del proyecto. `ENTRADAS_PENDIENTES.csv` conserva vacíos.

| Cálculo | Entrada y ecuación | Validez y aceptación |
|---|---|---|
| Corriente trifásica | I [A] = S [kVA]/(√3 U_LL [kV]) | Solo S coincidente y red trifásica equilibrada confirmadas; I ≤ ampacidad corregida. |
| Caída aproximada | ΔU [V] ≈ √3 I [A] L [km] (R [Ω/km] cosφ ± X [Ω/km] senφ) | Alimentador radial equilibrado, corriente uniforme, R a temperatura del caso; `+` inductivo. Se requiere flujo por tramo para cargas repartidas. Comparar ΔU/U con criterio oficial. |
| Pérdida Joule | P [W] = 3 I² R [Ω/km] L [km] | Corriente constante por tramo; sumar con perfil de carga para energía. |
| Ampacidad | I_perm [A] = I_cat [A] ∏f_i | Solo factores f>0 con ficha/criterio trazado; algunos pueden superar 1. Comparar I de punta y contingencia aplicable. |
| Icc trifásica ideal | Icc [A] = U_LL [V]/(√3 |Z_th| [Ω]) | Falla franca y equivalente de secuencia positiva. No resuelve mínimos, asimetría, monofásica ni coordinación. |

`ESCENARIOS_ADIMENSIONALES.csv` considera multiplicadores hipotéticos de demanda λ y longitud μ, con U, R, X, cosφ y topología constantes: I/I₀=λ; ΔU/ΔU₀=λμ; P/P₀=λ²μ. Por ejemplo λ=1,5 y μ=1,1 da 1,5; 1,65; 2,475 respectivamente. **No son amperios, voltios ni watts de esta línea.** No se emitió conductor ni protección elegidos.
