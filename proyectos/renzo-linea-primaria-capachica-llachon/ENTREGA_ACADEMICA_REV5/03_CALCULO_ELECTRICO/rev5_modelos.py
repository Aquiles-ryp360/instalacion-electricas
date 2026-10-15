"""Modelos condicionales Rev. 5; ninguna función fija datos de Capachica–Llachón.

Convenciones: trifásico equilibrado, longitudes eléctricas en km y unidades SI.
Las fórmulas de caída y flecha son aproximaciones con límites documentados.
"""
from __future__ import annotations

import math
from numbers import Real


def finite(name: str, value: Real, *, minimum: float | None = None,
           maximum: float | None = None, strict_min: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{name}: se requiere valor real finito")
    x = float(value)
    if minimum is not None and (x <= minimum if strict_min else x < minimum):
        raise ValueError(f"{name}: fuera de límite inferior")
    if maximum is not None and x > maximum:
        raise ValueError(f"{name}: fuera de límite superior")
    return x


def result(name: str, value: float) -> float:
    return finite(name, value)


def current_3ph_a(s_kva: Real, u_ll_kv: Real) -> float:
    """I=S/(sqrt(3) U); solo trifásico equilibrado y S aparente coincidente."""
    s = finite("s_kva", s_kva, minimum=0)
    u = finite("u_ll_kv", u_ll_kv, minimum=0, strict_min=True)
    return result("I_A", s / (math.sqrt(3) * u))


def drop_3ph_v(i_a: Real, length_km: Real, r_ohm_km: Real,
               x_ohm_km: Real, pf: Real, *, lagging: bool = True) -> float:
    """Aproximación radial ΔU≈sqrt(3) I L (R cosφ ± X sinφ)."""
    i = finite("i_a", i_a, minimum=0)
    length = finite("length_km", length_km, minimum=0)
    r = finite("r_ohm_km", r_ohm_km, minimum=0)
    x = finite("x_ohm_km", x_ohm_km, minimum=0)
    cos_phi = finite("pf", pf, minimum=0, maximum=1, strict_min=True)
    if not isinstance(lagging, bool):
        raise ValueError("lagging: se requiere bool")
    qsign = 1 if lagging else -1
    return result("delta_u_v", math.sqrt(3) * i * length *
                  (r * cos_phi + qsign * x * math.sqrt(1 - cos_phi**2)))


def copper_loss_3ph_w(i_a: Real, length_km: Real, r_ohm_km: Real) -> float:
    """P_J=3 I² R L, corriente uniforme y resistencia a temperatura del caso."""
    i = finite("i_a", i_a, minimum=0)
    length = finite("length_km", length_km, minimum=0)
    r = finite("r_ohm_km", r_ohm_km, minimum=0)
    return result("loss_w", 3 * i * i * r * length)


def corrected_ampacity_a(catalog_a: Real, correction_factors: list[Real]) -> float:
    """Producto de factores sustentados por ficha/norma; no selecciona conductor."""
    amp = finite("catalog_a", catalog_a, minimum=0, strict_min=True)
    if not correction_factors:
        raise ValueError("se requieren factores documentados")
    for j, factor in enumerate(correction_factors):
        amp *= finite(f"factor_{j}", factor, minimum=0, strict_min=True)
    return result("ampacity_a", amp)


def bolted_fault_3ph_a(u_ll_kv: Real, z_r_ohm: Real, z_x_ohm: Real) -> float:
    """Icc inicial ideal U/(sqrt(3)|Zth|); no sustituye estudio de red/protección."""
    u = finite("u_ll_kv", u_ll_kv, minimum=0, strict_min=True)
    zr = finite("z_r_ohm", z_r_ohm)
    zx = finite("z_x_ohm", z_x_ohm)
    z = math.hypot(zr, zx)
    if z == 0:
        raise ValueError("Zth no puede ser cero")
    return result("fault_a", u * 1000 / (math.sqrt(3) * z))


def ruling_span_m(spans_m: list[Real]) -> float:
    """sqrt(sum(L³)/sum(L)); vanos entre dos anclajes, hipótesis uniforme."""
    if not spans_m:
        raise ValueError("se requieren vanos medidos")
    spans = [finite(f"span_{j}", x, minimum=0, strict_min=True)
             for j, x in enumerate(spans_m)]
    return result("ruling_span_m", math.sqrt(sum(x**3 for x in spans) / sum(spans)))


def sag_level_parabolic_m(load_n_m: Real, span_m: Real,
                          horizontal_tension_n: Real) -> float:
    """f=wL²/(8H), apoyos a igual cota y flecha pequeña frente al vano."""
    w = finite("load_n_m", load_n_m, minimum=0, strict_min=True)
    span = finite("span_m", span_m, minimum=0, strict_min=True)
    h = finite("horizontal_tension_n", horizontal_tension_n, minimum=0, strict_min=True)
    return result("sag_m", w * span**2 / (8 * h))


def wind_load_n_m(pressure_pa: Real, diameter_m: Real, drag_coefficient: Real) -> float:
    """q=p d Cd sobre cilindro; p y Cd deben venir de hipótesis aprobada."""
    p = finite("pressure_pa", pressure_pa, minimum=0)
    d = finite("diameter_m", diameter_m, minimum=0, strict_min=True)
    cd = finite("drag_coefficient", drag_coefficient, minimum=0, strict_min=True)
    return result("wind_n_m", p * d * cd)


def angle_resultant_n(horizontal_tension_n: Real, deflection_deg: Real) -> float:
    """2H sin(θ/2) para dos vanos con H igual; no representa carga de rotura."""
    h = finite("horizontal_tension_n", horizontal_tension_n, minimum=0, strict_min=True)
    theta = finite("deflection_deg", deflection_deg, minimum=0, maximum=180)
    return result("resultant_n", 2 * h * math.sin(math.radians(theta) / 2))


def minimum_clearance_level_m(attachment_z_m: Real, span_m: Real, sag_m: Real,
                              obstacles: list[tuple[Real, Real]]) -> float:
    """Mínimo z_conductor(x)-z_obstáculo(x) para apoyos a igual cota.

    Cada obstáculo se mide con el mismo datum vertical; no incluye oscilación
    transversal, temperatura, desigualdad de cotas ni clasificación normativa.
    """
    z = finite("attachment_z_m", attachment_z_m)
    span = finite("span_m", span_m, minimum=0, strict_min=True)
    sag = finite("sag_m", sag_m, minimum=0)
    if not obstacles:
        raise ValueError("se requieren cotas de obstáculos")
    clearances = []
    for j, (position, obstruction_z) in enumerate(obstacles):
        x = finite(f"x_{j}", position, minimum=0, maximum=span)
        obstacle = finite(f"obstacle_z_{j}", obstruction_z)
        conductor_z = z - 4 * sag * x * (span-x) / span**2
        clearances.append(result(f"clearance_{j}", conductor_z-obstacle))
    return min(clearances)


def sensitivity_rows():
    """Cocientes hipotéticos, sin kV, kVA, conductor ni longitud reales."""
    rows = []
    for demand in (0.5, 1.0, 1.5):
        for length in (0.9, 1.0, 1.1):
            rows.append({"factor_demanda": demand, "factor_longitud": length,
                         "I_sobre_I_base": demand,
                         "caida_sobre_caida_base": demand * length,
                         "perdida_sobre_perdida_base": demand**2 * length,
                         "clase": "hipótesis adimensional; no resultado del proyecto"})
    return rows
