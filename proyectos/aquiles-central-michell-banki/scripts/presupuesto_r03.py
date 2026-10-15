"""Metrados derivados y precios explícitos. Ningún dato se presenta como cotización."""
from pathlib import Path
import csv, math
PROY=Path(__file__).resolve().parents[1]


def calcular(r):
    c=r['cfg'];o=c['obras'];h=c['hidraulica'];e=c['electrico'];eco=c['economia']
    t=o['espesor_concreto_canal_m']
    vcan=o['canal_l_m']*((o['canal_b_m']+2*t)*t+2*t*o['canal_altura_m'])
    td=o['espesor_muro_desarenador_m'];ld=o['desarenador_l_m'];bd=o['desarenador_b_m']
    vd=o['desarenador_camaras']*((ld+2*td)*(bd+2*td)*o['espesor_losa_desarenador_m']+
        ((ld+2*td)*(bd+2*td)-ld*bd)*(o['desarenador_y_m']+.5))
    tc=o['espesor_muro_camara_m'];lc=o['camara_l_m'];bc=o['camara_b_m']
    vc=(lc+2*tc)*(bc+2*tc)*o['espesor_losa_camara_m']+((lc+2*tc)*(bc+2*tc)-lc*bc)*(o['camara_y_m']+.5)
    vconc=vcan+vd+vc
    excavation=(o['canal_b_m']+2*t+.4)*(o['canal_altura_m']+.3)*o['canal_l_m']
    # Los sobreanchos siguientes solo estiman excavación, no estabilidad de taludes.
    excavation+=o['desarenador_camaras']*(ld+2*td+.8)*(bd+2*td+.8)*(o['desarenador_y_m']+.5)
    excavation+=(lc+2*tc+.8)*(bc+2*tc+.8)*(o['camara_y_m']+.5)
    mass=r['mecanica']['masa_nom_kg']
    q={'UNO':1,'DOS':2,'TRES':3,'EXCAVACION':excavation,
       'CONCRETO_HIDRAULICO':vconc,'ARMADURA_HIDRAULICA':100*vconc,
       'APOYOS':math.ceil(h['longitud_presion_m']/c['mecanica']['vano_m'])+1,
       'CASA_AREA':o['casa_l_m']*o['casa_b_m'],'MASA_TUBERIA':mass,'MASA_ACCESORIOS':.05*mass,
       'VALVULAS':c['grupo']['unidades']+1,'GRUPOS':c['grupo']['unidades'],
       'CABLE_CU240':3*e['cable_generador_paralelos']*e['cable_generador_l_m']*c['grupo']['unidades'],
       'CABLE_CU400':3*e['cable_respaldo_paralelos']*e['cable_respaldo_l_m'],
       'MALLA_CU':r['electrico']['pat_malla_longitud_m']+30,
       'RED_MT':e['linea_l_km'],'SED160':e['seds_kva'].count(160),'SED100':e['seds_kva'].count(100),
       'SED50':e['seds_kva'].count(50),'RED_BT':e['bt_l_total_m'],
       'USUARIOS':r['demanda']['usuarios_proyectados'],
       'LUMINARIAS':c['demanda']['luminarias_limbani']+c['demanda']['luminarias_huancasayani']}
    with (PROY/'datos/precios-r03.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    for row in rows:
        row['cantidad']=q[row['regla_cantidad']];row['precio_unitario_pen']=float(row['precio_unitario_pen'])
        row['parcial_pen']=row['cantidad']*row['precio_unitario_pen']
    subtotal=sum(x['parcial_pen'] for x in rows)
    transport_base=sum(x['parcial_pen'] for x in rows if x['codigo'].startswith(('TF','MQ','EC')))
    logistics=eco['transporte_montaje_fraccion']*transport_base
    studies=eco['gastos_estudios_supervision_fraccion']*(subtotal+logistics)
    contingency=eco['contingencia_fraccion']*(subtotal+logistics+studies)
    total=subtotal+logistics+studies+contingency
    factor=(1-(1+eco['tasa_real'])**(-eco['horizonte_anios']))/eco['tasa_real']
    annual=r['oferta']['ARNOVIC']['energia_hidro_servida_mwh']*1000
    demand=r['demanda']['energia_anual_mwh']*1000
    backup=(demand-annual)/eco['eficiencia_respaldo_hasta_usuarios']
    litres=backup*eco['consumo_respaldo_l_kwh']
    fuel=litres*eco['combustible_estimado_pen_l']
    opex=total*eco['opex_anual_fraccion_capex']
    tariffs=[dict(ingreso_escenario_pen_kwh=t,
        van_hibrido_pen=(demand*t-opex-fuel)*factor-total,
        ingreso_anual_pen=demand*t) for t in eco['precios_energia_sensibilidad_pen_kwh']]
    lcoe=(total/factor+opex+fuel)/demand
    return dict(partidas=rows,cantidades=q,concreto_canal_m3=vcan,concreto_desarenador_m3=vd,
        concreto_camara_m3=vc,subtotal_pen=subtotal,base_logistica_pen=transport_base,
        transporte_montaje_pen=logistics,estudios_supervision_pen=studies,
        contingencia_pen=contingency,total_pen=total,
        rango_costo_pen=[total*(1-eco['margen_costos_fraccion']),total*(1+eco['margen_costos_fraccion'])],
        anualidad=factor,opex_sin_combustible_pen_anio=opex,
        energia_respaldo_bornes_kwh_anio=backup,combustible_l_anio=litres,combustible_pen_anio=fuel,
        costo_equilibrio_pen_kwh=lcoe,escenarios=tariffs,
        estado='Estimaciones2026;sin cotización firme ni impuestos desagregados;VAN de escenario,no evaluación socialInvierte.pe')
