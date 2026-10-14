"""Motor SI sin dependencias externas. Nunca certifica un diseño ni escribe entregables."""
import math


def positivo(nombre, valor):
    if not math.isfinite(valor) or valor <= 0:
        raise ValueError(f"{nombre} debe ser finito y positivo")
    return valor


def no_negativo(nombre, valor):
    if not math.isfinite(valor) or valor < 0:
        raise ValueError(f"{nombre} debe ser finito y no negativo")
    return valor


def darcy(reynolds, rugosidad_relativa):
    positivo("Re", reynolds)
    if rugosidad_relativa < 0 or not math.isfinite(rugosidad_relativa):
        raise ValueError("Rugosidad inválida")
    if reynolds < 2300:
        return 64 / reynolds
    if reynolds < 4000:
        raise ValueError("Régimen transitorio: seleccionar un modelo justificado")
    # Solución iterativa de Colebrook-White, factor de Darcy (no Fanning).
    x = 7.0
    for _ in range(100):
        nuevo = -2 * math.log10(rugosidad_relativa / 3.7 + 2.51 * x / reynolds)
        if abs(nuevo - x) < 1e-12:
            return 1 / nuevo**2
        x = nuevo
    raise ArithmeticError("Colebrook no convergió")


def hidro(q, salto_bruto, longitud, diametro, rugosidad, viscosidad, k,
          eta_t, eta_m, eta_g, rho=1000.0, g=9.81):
    for nombre, v in [("Q", q), ("Hb", salto_bruto), ("L", longitud),
                      ("D", diametro), ("nu", viscosidad), ("rho", rho), ("g", g)]:
        positivo(nombre, v)
    if k < 0 or not math.isfinite(k):
        raise ValueError("K debe ser no negativo")
    if any(not 0 < v <= 1 for v in (eta_t, eta_m, eta_g)):
        raise ValueError("Rendimiento fuera de (0,1]")
    area = math.pi * diametro**2 / 4
    velocidad = q / area
    re = velocidad * diametro / viscosidad
    f = darcy(re, rugosidad / diametro)
    hf = f * longitud / diametro * velocidad**2 / (2 * g)
    hl = k * velocidad**2 / (2 * g)
    hn = salto_bruto - hf - hl
    if hn <= 0:
        raise ValueError("Las pérdidas consumen el salto disponible")
    ph = rho * g * q * hn / 1000
    return dict(q_m3s=q, hb_m=salto_bruto, l_m=longitud, d_m=diametro,
                area_m2=area, v_ms=velocidad, re=re, f=f, hf_m=hf,
                hl_m=hl, htotal_m=hf+hl, hn_m=hn,
                p_hidraulica_kw=ph, p_turbina_kw=ph*eta_t,
                p_acople_kw=ph*eta_t*eta_m, p_bornes_kw=ph*eta_t*eta_m*eta_g,
                eta_global=eta_t*eta_m*eta_g)


def distancia_3d(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b, strict=True)))


def comprobar_longitud(a, b, longitud):
    minimo = distancia_3d(a, b)
    return {"minimo_m": minimo, "propuesta_m": longitud,
            "geometria_posible": longitud >= minimo}


def trifasico(p_kw, fp, v_kv):
    positivo("P", p_kw)
    positivo("V", v_kv)
    if not 0 < fp <= 1:
        raise ValueError("Factor de potencia fuera de (0,1]")
    s = p_kw / fp
    return {"p_kw": p_kw, "s_kva": s,
            "q_kvar": p_kw * math.tan(math.acos(fp)),
            "i_a": s / (math.sqrt(3) * v_kv)}


def linea(p_kw, q_kvar, v_kv, r_ohm, x_ohm):
    positivo("V", v_kv)
    for nombre, valor in [("R", r_ohm), ("X", x_ohm)]:
        no_negativo(nombre, valor)
    if not math.isfinite(p_kw) or not math.isfinite(q_kvar):
        raise ValueError("Potencia no finita")
    i = math.hypot(p_kw, q_kvar) / (math.sqrt(3) * v_kv)
    return {"i_a": i, "perdida_kw": 3*i*i*r_ohm/1000,
            "variacion_pct": (r_ohm*p_kw + x_ohm*q_kvar)/(10*v_kv*v_kv)}


def transitorio(longitud, velocidad, diametro, espesor, salto, cierre,
                modulo_agua=2.2e9, modulo_acero=2e11, rho=1000.0, g=9.81):
    for nombre, v in [("L", longitud), ("v", velocidad), ("D", diametro),
                      ("e", espesor), ("Hb", salto), ("Tcierre", cierre),
                      ("Kw", modulo_agua), ("E", modulo_acero), ("rho", rho), ("g", g)]:
        positivo(nombre, v)
    # Modelo elástico ideal, restricción axial simplificada. No sustituye MOC.
    a = math.sqrt(modulo_agua/rho/(1+modulo_agua*diametro/(modulo_acero*espesor)))
    critico = 2*longitud/a
    lento = 2*longitud*velocidad/(g*cierre)
    rapido = a*velocidad/g
    return {"a_ms": a, "tc_s": critico, "cierre_s": cierre,
            "regimen": "lento" if cierre > critico else "rapido",
            "dh_lento_m": lento if cierre > critico else None,
            "dh_joukowsky_m": rapido,
            "p_lento_bar": rho*g*(salto+lento)/1e5 if cierre > critico else None,
            "p_rapido_bar": rho*g*(salto+rapido)/1e5,
            "estado": "cribado; requiere simulacion transitoria"}


def manning_rectangular(b, y, pendiente, n, g=9.81):
    for nombre, v in [("b", b), ("y", y), ("S", pendiente), ("n", n)]:
        positivo(nombre, v)
    area = b*y
    radio = area/(b+2*y)
    q = area * radio**(2/3) * math.sqrt(pendiente)/n
    return {"q_m3s": q, "v_ms": q/area, "fr": q/area/math.sqrt(g*y)}


def tirante_normal(q, b, pendiente, n):
    positivo("Q", q)
    bajo, alto = 1e-8, 10.0
    if manning_rectangular(b, alto, pendiente, n)["q_m3s"] < q:
        raise ValueError("Tirante excede intervalo de búsqueda")
    for _ in range(100):
        medio = (bajo+alto)/2
        if manning_rectangular(b, medio, pendiente, n)["q_m3s"] < q:
            bajo = medio
        else:
            alto = medio
    return (bajo+alto)/2


def cargas_por_modo(filas, activas):
    """Suma P y Q por equipos activos; no convierte simultaneidad en factor residencial."""
    if len({f['id'] for f in filas}) != len(filas):
        raise ValueError("Identificadores duplicados")
    if set(activas) != {f['id'] for f in filas}:
        raise ValueError("El modo debe declarar cada equipo")
    detalle = []
    for f in filas:
        n = activas[f['id']]
        no_negativo("Cantidad activa", n)
        if not isinstance(n, int) or not isinstance(f['cantidad'], int) or not 0 <= n <= f['cantidad']:
            raise ValueError("Cantidad activa inválida")
        positivo("Potencia unitaria", f['p_unit_kw'])
        if not math.isfinite(f['fp']) or not 0 < f['fp'] <= 1:
            raise ValueError("Factor de potencia inválido")
        p = n * f['p_unit_kw']
        detalle.append(dict(id=f['id'], activas=n, p_kw=p,
                            q_kvar=p*math.tan(math.acos(f['fp']))))
    p = sum(f['p_kw'] for f in detalle)
    q = sum(f['q_kvar'] for f in detalle)
    return dict(p_kw=p, q_kvar=q, s_kva=math.hypot(p,q), filas=detalle)


def perdidas_transformador(p_kw, q_kvar, s_nom_kva, p0_kw, pcu_kw):
    """P0 + Pcu nominal (S/Sn)^2; no incluye magnetización reactiva."""
    positivo("Sn", s_nom_kva)
    no_negativo("P0", p0_kw)
    no_negativo("Pcu", pcu_kw)
    if not math.isfinite(p_kw) or not math.isfinite(q_kvar):
        raise ValueError("Potencia no finita")
    carga = math.hypot(p_kw,q_kvar)/s_nom_kva
    return dict(carga_pu=carga, p_kw=p0_kw+pcu_kw*carga**2)


def balance_exportacion(p_gen_kw, fp_gen, p_aux_kw, q_aux_kvar,
                        s_tx_kva, p0_tx_kw, pcu_tx_kw, v_mt_kv, r_ohm, x_ohm):
    """Balance aproximado desde barra BT hacia PCC. Q de excitación es hipótesis."""
    gen = trifasico(p_gen_kw,fp_gen,1.0)
    no_negativo("P auxiliar",p_aux_kw)
    if not math.isfinite(q_aux_kvar):
        raise ValueError("Q auxiliar no finito")
    p_bt = p_gen_kw-p_aux_kw
    q_bt = gen['q_kvar']-q_aux_kvar
    tx = perdidas_transformador(p_bt,q_bt,s_tx_kva,p0_tx_kw,pcu_tx_kw)
    p_mt = p_bt-tx['p_kw']
    lin = linea(p_mt,q_bt,v_mt_kv,r_ohm,x_ohm)
    return dict(p_gen_kw=p_gen_kw, p_aux_kw=p_aux_kw, q_aux_kvar=q_aux_kvar,
                p_barra_bt_kw=p_bt, q_barra_bt_kvar=q_bt, trafo=tx, linea=lin,
                p_pcc_kw=p_mt-lin['perdida_kw'],
                residual_kw=p_gen_kw-(p_aux_kw+tx['p_kw']+lin['perdida_kw']+p_mt-lin['perdida_kw']),
                alcance='balance activo aproximado; reactiva de transformadores y flujo AC pendientes')


def tubo_mecanico(diametro, espesor_nom, longitud, tolerancia_fraccion,
                   corrosion_m, vano_m, presion_pa, angulo_codo_deg,
                   delta_t_c, rho_acero=7850.0, rho_agua=1000.0,
                   e_acero=2e11, alpha=1.2e-5, g=9.81):
    """Cribado de membrana, viga y empuje; sin aprobación por código ni suelo."""
    for nombre,v in [("Di",diametro),("e",espesor_nom),("L",longitud),
                     ("vano",vano_m),("rho acero",rho_acero),("rho agua",rho_agua),
                     ("E",e_acero),("alpha",alpha),("g",g)]:
        positivo(nombre,v)
    for nombre,v in [("corrosión",corrosion_m),("presión",presion_pa),
                     ("delta T",delta_t_c)]:
        no_negativo(nombre,v)
    if not math.isfinite(tolerancia_fraccion) or not 0 <= tolerancia_fraccion < 1:
        raise ValueError("Tolerancia inválida")
    if not math.isfinite(angulo_codo_deg) or not 0 <= angulo_codo_deg <= 180:
        raise ValueError("Ángulo inválido")
    ef = espesor_nom*(1-tolerancia_fraccion)-corrosion_m
    positivo("Espesor efectivo",ef)
    do = diametro+2*espesor_nom
    di_ef = do-2*ef
    dm = do-ef
    area_acero_nom = math.pi*(do**2-diametro**2)/4
    area_agua = math.pi*di_ef**2/4
    area_acero_ef = math.pi*(do**2-di_ef**2)/4
    masa_m = rho_acero*area_acero_nom
    peso = g*(rho_acero*area_acero_ef+rho_agua*area_agua)
    inercia = math.pi*(do**4-di_ef**4)/64
    mmax = peso*vano_m**2/8
    flexion = mmax*(do/2)/inercia
    sigma_h = presion_pa*dm/(2*ef)
    sigma_l = sigma_h/2
    vm = max(math.sqrt(sigma_h**2+s**2-sigma_h*s)
             for s in [sigma_l-flexion,sigma_l+flexion])
    return dict(do_m=do, di_ef_m=di_ef, espesor_ef_m=ef,
                masa_nom_kg_m=masa_m, masa_nom_kg=masa_m*longitud,
                carga_lineal_n_m=peso, inercia_m4=inercia,
                mmax_kn_m=mmax/1000, reaccion_kn=peso*vano_m/2000,
                sigma_hoop_mpa=sigma_h/1e6, sigma_long_presion_mpa=sigma_l/1e6,
                sigma_flexion_mpa=flexion/1e6, von_mises_global_mpa=vm/1e6,
                flecha_mm=5*peso*vano_m**4/(384*e_acero*inercia)*1000,
                empuje_codo_kn=2*presion_pa*area_agua*math.sin(math.radians(angulo_codo_deg)/2)/1000,
                expansion_libre_mm=alpha*longitud*delta_t_c*1000,
                tension_termica_bloqueada_mpa=e_acero*alpha*delta_t_c/1e6,
                alcance='viga horizontal simple + membrana ideal; faltan efectos locales, soldadura, sismo y código')


def sedimentador(q, ancho, largo, tirante, ws, factor):
    for nombre,v in [("Q",q),("b",ancho),("L",largo),("y",tirante),("ws",ws),("F",factor)]:
        positivo(nombre,v)
    area = ancho*largo
    volumen = area*tirante
    tiempo_res = volumen/q
    tiempo_caida = tirante/ws
    return dict(area_m2=area, area_min_m2=factor*q/ws, volumen_m3=volumen,
                v_long_ms=q/(ancho*tirante), residencia_s=tiempo_res,
                caida_s=tiempo_caida, relacion_tiempos=tiempo_res/tiempo_caida,
                criterio_ideal=area>=factor*q/ws)


def vertedor(q, coeficiente, carga_m):
    for nombre,v in [("Q",q),("Cw",coeficiente),("h",carga_m)]:
        positivo(nombre,v)
    return q/(coeficiente*carga_m**1.5)


def reja(q, velocidad_libre, porosidad, bloqueo):
    for nombre,v in [("Q",q),("velocidad",velocidad_libre)]:
        positivo(nombre,v)
    if not 0 < porosidad <= 1 or not 0 <= bloqueo < 1:
        raise ValueError("Porosidad o bloqueo inválido")
    return q/(velocidad_libre*porosidad*(1-bloqueo))
