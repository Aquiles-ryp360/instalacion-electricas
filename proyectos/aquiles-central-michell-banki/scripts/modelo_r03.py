"""Modelo del proyecto académico aislado. Conserva fronteras de potencia y agua."""
from pathlib import Path
import sys, json, csv, math
from datetime import date
import numpy as np
PROY=Path(__file__).resolve().parents[1]
ROOT=PROY.parents[1]
sys.path.insert(0,str(ROOT))
from herramientas.hidroelectricas.calculos import (hidro, trifasico, linea, transitorio,
    tubo_mecanico, tirante_normal, manning_rectangular, sedimentador, vertedor, reja,
    perdidas_transformador, balance_exportacion, cargas_por_modo)
from herramientas.hidroelectricas.transitorios import moc_valvula


def read_json(name):return json.loads((PROY/'datos'/name).read_text(encoding='utf-8'))


def model():
    cfg=read_json('parametros-r03.json');hyd=read_json('hidrologia-r03.json')
    h=cfg['hidraulica'];e=cfg['electrico'];g=cfg['grupo'];a=cfg['auxiliares'];o=cfg['obras'];m=cfg['mecanica']
    baseaux=cargas_por_modo(a['filas'],a['activas_base'])
    a['base_kw']=baseaux['p_kw'];a['base_q_kvar']=baseaux['q_kvar']
    gov=next(f for f in a['filas'] if f['id']=='GOB')
    if gov['cantidad']!=g['unidades']:raise ValueError('Cantidad de gobernadores no coincide con grupos')
    a['gobernador_por_unidad_kw']=gov['p_unit_kw'];a['gobernador_fp']=gov['fp']
    maintenance=a['activas_base'].copy();maintenance.update(TOM=1,IZJ=1)
    auxmaintenance=cargas_por_modo(a['filas'],maintenance)
    def hc(q,d=None,eta_t=None,eta_g=None,salto=None,longitud=None,rugosidad=None):
        return hidro(q,h['salto_bruto_m'] if salto is None else salto,
            h['longitud_presion_m'] if longitud is None else longitud,
            h['diametro_interior_m'] if d is None else d,
            h['rugosidad_m'] if rugosidad is None else rugosidad,h['viscosidad_m2s'],h['k_local'],
            h['eta_t_nominal'] if eta_t is None else eta_t,h['eta_m'],
            h['eta_g_nominal'] if eta_g is None else eta_g)
    r40=e['linea_r20_ohm_km']*(1+e['linea_alpha_k']*(e['linea_temperatura_c']-20))
    def balance(pg,n,backup=False):
        if pg<=0:return dict(p_usuarios_kw=0,p_bornes_kw=0,n=0,residual_kw=0)
        pa=a['base_kw']+n*a['gobernador_por_unidad_kw']
        qa=a['base_q_kvar']+n*a['gobernador_por_unidad_kw']*math.tan(math.acos(a['gobernador_fp']))
        tsa=perdidas_transformador(pa,qa,e['servicios_trafo_kva'],e['tsa_p0_kw'],e['tsa_pcu_kw'])
        if n:
            iu=pg/n/e['fp_balance_conservador']/(math.sqrt(3)*g['tension_bt_kv'])
            cableloss=n*3*iu**2*(e['cable_generador_r_ohm_km']*e['cable_generador_l_m']/1000/e['cable_generador_paralelos'])/1000
        else:
            iu=pg/e['fp_balance_conservador']/(math.sqrt(3)*g['tension_bt_kv'])
            cableloss=3*iu**2*(e['cable_respaldo_r_ohm_km']*e['cable_respaldo_l_m']/1000/e['cable_respaldo_paralelos'])/1000
        # La pérdida de cables se agrupa en el consumo anterior al transformador;
        # se separa en el libro. Q de cables permanece aproximada y declarada.
        bt=balance_exportacion(pg,e['fp_balance_conservador'],pa+tsa['p_kw']+cableloss,qa,
            e['trafo_principal_kva'],e['trafo_p0_kw'],e['trafo_pcu_kw'],e['tension_mt_kv'],
            r40*e['linea_l_km'],e['linea_x_ohm_km']*e['linea_l_km'])
        sed=perdidas_transformador(bt['p_pcc_kw'],bt['q_barra_bt_kvar'],sum(e['seds_kva']),
                                  e['seds_p0_total_kw'],e['seds_pcu_total_kw'])
        pbt=max(0,bt['p_pcc_kw']-sed['p_kw']);pusers=pbt*(1-e['bt_perdidas_fraccion'])
        libro=[('Generador',pg),('Cables de generación',cableloss),('Equipos auxiliares',pa),('TSA',tsa['p_kw']),
               ('Transformador elevador',bt['trafo']['p_kw']),('Red primaria',bt['linea']['perdida_kw']),
               ('Transformadores SED',sed['p_kw']),('Red secundaria',pbt*e['bt_perdidas_fraccion']),
               ('Usuarios',pusers)]
        residual=pg-sum(x[1] for x in libro[1:])
        if pusers>0 and abs(residual)>1e-8:raise ArithmeticError('No cierra potencia')
        return dict(p_usuarios_kw=pusers,p_bornes_kw=pg,n=n,aux_kw=pa,aux_kvar=qa,tsa=tsa,cables_perdida_kw=cableloss,
            balance_mt=bt,sed=sed,libro_kw=libro,residual_kw=residual)
    populations=[];dom=0;qdemand=0
    for f in cfg['poblacion']['filas']:
        grow=(1+cfg['poblacion']['crecimiento_anual'])**(cfg['poblacion']['anio_diseno']-cfg['poblacion']['anio_base'])
        n=math.ceil(f['viviendas_ocupadas']*grow);p=math.ceil(f['poblacion']*grow)
        dot=cfg['demanda']['calificacion_tipo_i_kw'] if f['tipo_dger_estudio']=='I' else cfg['demanda']['calificacion_tipo_ii_kw']
        pk=n*dot*cfg['demanda']['simultaneidad_domestica'];dom+=pk
        populations.append({**f,'poblacion_proyectada':p,'usuarios_potenciales_proyectados':n,
                            'calificacion_kw':dot,'demanda_kw':pk})
    de=cfg['demanda'];ap=(de['luminarias_limbani']+de['luminarias_huancasayani'])*de['potencia_luminaria_kw']
    special=sum(x['kw_coincidente'] for x in de['servicios'])
    qdemand=ap*math.tan(math.acos(de['fp_alumbrado']))+sum(x['kw_coincidente']*math.tan(math.acos(x['fp'])) for x in de['servicios'])
    perfil_dom=np.array(de['perfil_domestico'])*dom;perfil_serv=np.array(de['perfil_servicios'])*special
    perfil_ap=np.array([ap if hour in de['horas_alumbrado'] else 0 for hour in range(24)])
    demand=perfil_dom+perfil_serv+perfil_ap
    critical=perfil_dom*de['fraccion_domestica_critica']+perfil_serv+perfil_ap*de['fraccion_ap_critica']
    peak=float(demand.max());daily_energy=float(demand.sum())
    demand_result=dict(filas=populations,poblacion_base=sum(f['poblacion'] for f in populations),
        viviendas_base=sum(f['viviendas_ocupadas'] for f in populations),
        poblacion_proyectada=sum(f['poblacion_proyectada'] for f in populations),
        usuarios_proyectados=sum(f['usuarios_potenciales_proyectados'] for f in populations),
        domestica_kw=dom,alumbrado_kw=ap,servicios_kw=special,q_peak_kvar=qdemand,
        s_peak_kva=math.hypot(peak,qdemand),fp_peak=peak/math.hypot(peak,qdemand),
        max_kw=peak,energia_diaria_kwh=daily_energy,energia_anual_mwh=daily_energy*365/1000,
        factor_carga=float(demand.mean()/peak),perfil_kw=demand.tolist(),perfil_critico_kw=critical.tolist(),
        pico_critico_kw=float(critical.max()),proyecciones=[])
    for years in [0,5,10,20]:
        ng=(1+cfg['poblacion']['crecimiento_anual'])**years
        cg=(1+de['crecimiento_consumo_anual'])**years
        demand_result['proyecciones'].append(dict(anio=2026+years,
            usuarios=math.ceil(demand_result['usuarios_proyectados']*ng),
            demanda_kw=dom*ng*cg+special*cg+ap*ng,
            estado='escenario de crecimiento, no previsión INEI'))
    series={}
    for name,filename in [('ARNOVIC','serie_diaria_estimada.csv'),('GR2M','serie_mensual_estimada.csv')]:
        with (PROY/'datos/hidrologia'/filename).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        dates=[date.fromisoformat(r['fecha']) for r in rows]
        q=np.array([float(r['q_captacion_estimada_m3s']) for r in rows]);months=np.array([d.month for d in dates])
        climate=np.array([q[months==month].mean() for month in range(1,13)])
        reserved=cfg['hidrologia']['reserva_ecologica_fraccion_media_mensual']*climate[months-1]
        eco=np.minimum(q,reserved)
        other=np.minimum(np.maximum(0,q-eco),cfg['hidrologia']['reserva_otros_usos_m3s'])
        usable=np.maximum(0,q-eco-other)
        if np.max(np.abs(q-eco-other-usable))>1e-10:raise ArithmeticError('No cierra reserva de agua')
        series[name]=dict(dates=dates,months=months,q=q,eco=eco,other=other,usable=usable,climate=climate)
    qnom_unit=h['q_diseno_m3s']/g['unidades']
    def curve(unit_kw,total_units):
        groups={}; qunit=qnom_unit*unit_kw/g['potencia_unitaria_kw']
        for n in range(1,total_units+1):
            def power(qi):
                ratio=qi/(n*qunit)
                et=float(np.interp(ratio,g['ratios_curva'],g['eta_t_curva']))
                eg=float(np.interp(ratio,g['ratios_curva'],g['eta_g_curva']))
                return hc(qi,eta_t=et,eta_g=eg)['p_bornes_kw']
            qs=np.linspace(n*qunit*g['caudal_min_fraccion_unitaria'],n*qunit,401)
            ps=[]; net=[]; actual=[]
            for qi in qs:
                ratio=qi/(n*qunit)
                et=float(np.interp(ratio,g['ratios_curva'],g['eta_t_curva']))
                eg=float(np.interp(ratio,g['ratios_curva'],g['eta_g_curva']))
                pg=hc(qi,eta_t=et,eta_g=eg)['p_bornes_kw']
                ps.append(pg);net.append(balance(pg,n)['p_usuarios_kw']);actual.append(qi)
            ps=np.array(ps);net=np.array(net)
            rated=unit_kw*n
            qcap=float(np.interp(rated,ps,qs))
            if ps[-1]>rated:
                lo,hi=float(qs[0]),float(qs[-1])
                for _ in range(60):
                    mid=(lo+hi)/2
                    if power(mid)<rated:lo=mid
                    else:hi=mid
                qcap=(lo+hi)/2
                qs=np.append(qs[qs<qcap],qcap)
                ps=np.array([power(qi) for qi in qs])
                net=np.array([balance(pg,n)['p_usuarios_kw'] for pg in ps])
            maxnet=balance(min(rated,float(ps[-1])),n)['p_usuarios_kw']
            groups[n]=dict(q=qs,p=ps,net=net,limite_q=qcap,limite_p= min(rated,float(ps[-1])),limite_net=maxnet)
        def evaluate(qavail):
            arr=np.atleast_1d(qavail).astype(float)
            best=np.zeros(arr.shape);pgen=np.zeros(arr.shape);nact=np.zeros(arr.shape,dtype=int);qused=np.zeros(arr.shape)
            for n,v in groups.items():
                qu=np.minimum(arr,v['limite_q'])
                feasible=qu>=v['q'][0]
                pp=np.where(feasible,np.interp(qu,v['q'],v['net']),0)
                # Recalibrar el último punto a potencia de placa, sin inventar pérdida por recorte.
                pp=np.minimum(pp,v['limite_net'])
                improve=pp>best
                best[improve]=pp[improve];pgen[improve]=np.minimum(np.interp(qu,v['q'],v['p']),v['limite_p'])[improve]
                nact[improve]=n;qused[improve]=qu[improve]
            return best,pgen,nact,qused
        return groups,evaluate
    groups,evaluate=curve(g['potencia_unitaria_kw'],g['unidades'])
    rated_flow=groups[g['unidades']]['limite_q'];rated_gen=groups[g['unidades']]['limite_p']
    nom=hc(rated_flow,eta_t=float(np.interp(rated_flow/h['q_diseno_m3s'],g['ratios_curva'],g['eta_t_curva'])),
           eta_g=float(np.interp(rated_flow/h['q_diseno_m3s'],g['ratios_curva'],g['eta_g_curva'])))
    rated_bal=balance(rated_gen,g['unidades'])
    results_series={}
    for name,s in series.items():
        net,pg,nact,used=evaluate(s['usable']);spill=s['usable']-used
        assert np.min(spill)>-1e-9
        assert np.max(np.abs(s['q']-s['eco']-s['other']-used-spill))<1e-9
        if name=='ARNOVIC':
            served=np.minimum(net[:,None],demand[None,:]).sum(axis=1)
            monthly=[dict(mes=month,q_media_m3s=float(s['q'][s['months']==month].mean()),
                q_eco_m3s=float(s['eco'][s['months']==month].mean()),
                q_usable_m3s=float(s['usable'][s['months']==month].mean()),
                q95_disponible_m3s=float(np.quantile(s['usable'][s['months']==month],.05)),
                p95_usuarios_kw=float(np.quantile(net[s['months']==month],.05)),
                p_media_usuarios_kw=float(net[s['months']==month].mean()),
                p_min_usuarios_kw=float(net[s['months']==month].min()),
                energia_disponible_mwh=float(net[s['months']==month].mean()*24*([31,28,31,30,31,30,31,31,30,31,30,31][month-1])/1000*g['disponibilidad_equipo']),
                energia_servida_mwh=float(served[s['months']==month].mean()*([31,28,31,30,31,30,31,31,30,31,30,31][month-1])/1000*g['disponibilidad_equipo'])) for month in range(1,13)]
        else:
            days=np.array([((date(d.year+1,1,1) if d.month==12 else date(d.year,d.month+1,1))-d).days for d in s['dates']])
            served=np.minimum(net[:,None],demand[None,:]).sum(axis=1)
            monthly=[]
        energy_cap=float(net.mean()*8760/1000*g['disponibilidad_equipo'])
        energy_served=float(served.mean()*365/1000*g['disponibilidad_equipo'])
        if name=='GR2M':
            energy_cap=float(np.average(net,weights=days)*8760/1000*g['disponibilidad_equipo'])
            energy_served=float(np.average(served,weights=days)*365/1000*g['disponibilidad_equipo'])
        deficit=demand_result['energia_anual_mwh']-energy_served
        results_series[name]=dict(p95_usuarios_kw=float(np.quantile(net,.05)),p90_usuarios_kw=float(np.quantile(net,.1)),
            p_min_usuarios_kw=float(net.min()),p_media_usuarios_kw=float(net.mean()),
            energia_disponible_mwh=energy_cap,energia_hidro_servida_mwh=energy_served,
            energia_no_cubierta_hidro_mwh=deficit,
            fraccion_energia_hidro=energy_served/demand_result['energia_anual_mwh'],
            fraccion_dias_pico=float(np.mean(net>=peak))*g['disponibilidad_equipo'],
            dias_sin_generacion_equiv_anual=float(np.mean(net<=0)*365),
            mensual=monthly,fraccion_vertida=float(spill.sum()/s['q'].sum()),
            agua_residuo_m3s=float(np.max(np.abs(s['q']-s['eco']-s['other']-used-spill))))
        s.update(net=net,pg=pg,nact=nact,used=used,spill=spill)
    comparison=[]
    for unit_kw,units in [(150,1),(200,1),(200,2),(200,3)]:
        _,ev=curve(unit_kw,units);net,pg,nact,used=ev(series['ARNOVIC']['usable'])
        es=float(np.minimum(net[:,None],demand).sum(axis=1).mean()*365/1000*g['disponibilidad_equipo'])
        comparison.append(dict(potencia_instalada_kw=unit_kw*units,unidades=units,
            p_max_usuarios_kw=float(net.max()),p95_usuarios_kw=float(np.quantile(net,.05)),
            energia_hidro_servida_mwh=es,energia_deficit_mwh=demand_result['energia_anual_mwh']-es,
            dias_pico_pct=float(np.mean(net>=peak)*100*g['disponibilidad_equipo'])))
    sensitivities=[]
    s=series['ARNOVIC']
    for bias in cfg['hidrologia']['sesgos_sensibilidad']:
        q=s['q']*bias;reserved=s['climate'][s['months']-1]*cfg['hidrologia']['reserva_ecologica_fraccion_media_mensual']*bias
        usable=np.maximum(0,q-reserved-cfg['hidrologia']['reserva_otros_usos_m3s'])
        net,_,_,_=evaluate(usable)
        es=float(np.minimum(net[:,None],demand).sum(axis=1).mean()*365/1000*g['disponibilidad_equipo'])
        sensitivities.append(dict(factor_sesgo=bias,p95_kw=float(np.quantile(net,.05)),
            energia_servida_mwh=es,energia_deficit_mwh=demand_result['energia_anual_mwh']-es))
    diameters=[]
    for di in h['diametros_comparacion_m']:
        hh=hc(h['q_diseno_m3s'],di)
        tt=transitorio(h['longitud_presion_m'],hh['v_ms'],di,m['espesor_nominal_m'],h['salto_bruto_m'],m['cierre_s'])
        mech=tubo_mecanico(di,m['espesor_nominal_m'],h['longitud_presion_m'],m['tolerancia'],m['corrosion_m'],
            m['vano_m'],tt['p_rapido_bar']*1e5,m['angulo_codo_deg'],m['delta_t_k'])
        diameters.append(dict(di_m=di,hidraulica=hh,transitorio=tt,mecanica=mech))
    yn=tirante_normal(h['q_diseno_m3s'],o['canal_b_m'],o['canal_s'],o['canal_n'])
    canal=dict(yn_m=yn,borde_libre_m=o['canal_altura_m']-yn,
        capacidad_m3s=manning_rectangular(o['canal_b_m'],o['canal_y_max_m'],o['canal_s'],o['canal_n'])['q_m3s'],
        **manning_rectangular(o['canal_b_m'],yn,o['canal_s'],o['canal_n']))
    sed=sedimentador(h['q_diseno_m3s'],o['desarenador_b_m'],o['desarenador_l_m'],o['desarenador_y_m'],o['sedimentacion_ws_ms'],o['sedimentacion_factor'])
    civil=dict(canal=canal,desarenador=sed,
        reja_area_m2=reja(h['q_diseno_m3s'],o['reja_v_ms'],o['reja_porosa'],o['reja_bloqueo']),
        aliviadero_ancho_m=vertedor(h['q_diseno_m3s'],o['aliviadero_c'],o['aliviadero_carga_m']),
        reserva_camara_s=o['volumen_util_camara_m3']/h['q_diseno_m3s'])
    transients=[]
    outer=h['diametro_interior_m']+2*m['espesor_nominal_m']
    for label,wall,corrosion,eps in [('nuevo_tolerancia',m['espesor_nominal_m']*(1-m['tolerancia']),0.,h['rugosidad_m']),
                                    ('fin_vida',m['espesor_nominal_m']*(1-m['tolerancia'])-m['corrosion_m'],m['corrosion_m'],.00015)]:
        di=outer-2*wall;hh=hc(h['q_diseno_m3s'],di,rugosidad=eps)
        tt=transitorio(h['longitud_presion_m'],hh['v_ms'],di,wall,h['salto_bruto_m'],m['cierre_s'])
        for close in m['cierre_alternativas_s']:
            rr=moc_valvula(h['q_diseno_m3s'],h['salto_bruto_m'],h['longitud_presion_m'],di,tt['a_ms'],hh['f'],close,15.,100,
                          limite_presion_manometrica_m=-6.8)
            rr.update(estado_pared=label,wall_m=wall,di_m=di,celeridad_ms=tt['a_ms'],q_inicial_m3s=h['q_diseno_m3s'])
            transients.append(rr)
    slow=next(x for x in transients if x['estado_pared']=='fin_vida' and x['cierre_s']==m['cierre_s'])
    abrupt=next(x for x in transients if x['estado_pared']=='fin_vida' and x['cierre_s']==0)
    def mech(pressure,span):
        return tubo_mecanico(h['diametro_interior_m'],m['espesor_nominal_m'],h['longitud_presion_m'],
            m['tolerancia'],m['corrosion_m'],span,pressure*1e5,m['angulo_codo_deg'],m['delta_t_k'])
    mechanical=mech(abrupt['max_global_bar'],m['vano_m'])
    supports=[dict(vano_m=span,**mech(slow['max_global_bar'],span)) for span in m['vanos_comparacion_m']]
    permitted=m['fy_especificado_mpa']/m['factor_estudio']*m['eficiencia_union_estudio']
    alpha=1.2e-5;dtemp=m['delta_t_k']
    nominal_gen=trifasico(g['potencia_unitaria_kw'],g['fp_nominal'],g['tension_bt_kv'])
    gen_in=nominal_gen['i_a'];sum_in=gen_in*g['unidades']
    backup_in=e['respaldo_kva']/(math.sqrt(3)*g['tension_bt_kv'])
    ik_h=sum_in/e['xd_subtransitorio_pu']
    ik_b=backup_in/e['xd_subtransitorio_respaldo_pu'];ikmax=ik_h+ik_b
    zbase=(g['tension_bt_kv']*1000)**2/(g['placa_unitaria_kva']*1000)
    zgen=complex(e['ra_generador_pu'],e['xd_subtransitorio_pu'])*zbase/g['unidades']
    ztrafo=1j*e['trafo_uk_pu']*(g['tension_bt_kv']*1000)**2/(e['trafo_principal_kva']*1000)
    ikmt=(g['tension_bt_kv']*1000/math.sqrt(3)/abs(zgen+ztrafo))*g['tension_bt_kv']/e['tension_mt_kv']
    br=linea(e['bt_rama_p_kw'],0,g['tension_bt_kv'],e['bt_r_ohm_km']*e['bt_rama_l_m']/1000,
             e['bt_x_ohm_km']*e['bt_rama_l_m']/1000)
    cb=linea(g['potencia_unitaria_kw'],nominal_gen['q_kvar'],g['tension_bt_kv'],
        e['cable_generador_r_ohm_km']*e['cable_generador_l_m']/1000/e['cable_generador_paralelos'],
        e['cable_generador_x_ohm_km']*e['cable_generador_l_m']/1000/e['cable_generador_paralelos'])
    earth_len=(math.floor(e['pat_l_m']/e['pat_paso_m'])+1)*e['pat_b_m']+(math.floor(e['pat_b_m']/e['pat_paso_m'])+1)*e['pat_l_m']
    # Rg aproximada de electrodos horizontales, no mapa de paso/contacto IEEE.
    req=math.sqrt(e['pat_l_m']*e['pat_b_m']/math.pi)
    earth=[dict(rho_ohm_m=rho,rg_screen_ohm=rho/(4*req)+rho/earth_len,
                gpr_screen_v=e['corriente_tierra_estudio_a']*(rho/(4*req)+rho/earth_len))
           for rho in e['resistividades_sensibilidad_ohm_m']]
    electrical=dict(ig_unitaria_a=gen_in,i_bus_placa_a=sum_in,
        i_trafo_placa_bt_a=e['trafo_principal_kva']/(math.sqrt(3)*g['tension_bt_kv']),
        ik_hidro_inicial_a=ik_h,ik_respaldo_inicial_a=ik_b,ik_barra_max_a=ikmax,
        ik_mt_hidro_inicial_a=ikmt,bt_rama=br,cable_generador=cb,
        resistencia_mt_40_ohm_km=r40,pat_malla_longitud_m=earth_len,pat_sensibilidad=earth,
        autonomia_cc_h=a['bateria_v']*a['bateria_ah']/1000*a['profundidad_descarga']*a['eficiencia_dc']/a['carga_dc_kw'],
        respaldo_usuarios_kw=balance(e['respaldo_kw'],0,True)['p_usuarios_kw'],
        estado='Cortocircuito inicial simétrico simplificado con reactancias supuestas; sin fuente SEIN')
    # Fallas trifásicas remotas de referencia; no se infiere la falla a tierra.
    # Se consideran 1/3 grupos hidráulicos y reactancia inicial/sostenida.
    faults=[]
    for count,xd,stage in [(3,e['xd_subtransitorio_pu'],'inicial, tres hidro'),
                           (1,e['xd_subtransitorio_pu'],'inicial, un hidro'),
                           (1,e['xd_sincrono_pu'],'sostenida, un hidro')]:
        zsrc=complex(e['ra_generador_pu'],xd)*e['tension_mt_kv']**2*1000/g['placa_unitaria_kva']/count
        zt=1j*e['trafo_uk_pu']*e['tension_mt_kv']**2*1000/e['trafo_principal_kva']
        zremote=zsrc+zt+complex(r40,e['linea_x_ohm_km'])*e['linea_l_km']
        ratio=(g['tension_bt_kv']/e['tension_mt_kv'])**2
        for skva in [160,50]:
            zsed=1j*e['sed_uk_estudio_pu']*g['tension_bt_kv']**2*1000/skva
            zbt=zremote*ratio+zsed
            zfinal=zbt+complex(e['bt_r_ohm_km'],e['bt_x_ohm_km'])*e['bt_rama_l_m']/1000
            faults.append(dict(estado=stage,sed_kva=skva,
                ik_mt_fin_a=e['tension_mt_kv']*1000/math.sqrt(3)/abs(zremote),
                ik_sed_bt_a=g['tension_bt_kv']*1000/math.sqrt(3)/abs(zbt),
                ik_bt_fin_a=g['tension_bt_kv']*1000/math.sqrt(3)/abs(zfinal)))
    electrical['fallas_remotas_trifasicas']=faults
    # Membrana y anclaje: cargas, no aprobación de cimentación de roca desconocida.
    hoop=mechanical['sigma_hoop_mpa'];eq=math.sqrt(hoop**2+(hoop/2)**2-hoop*(hoop/2))
    forces=dict(sigma_vm_membrana_mpa=eq,admisible_estudio_mpa=permitted,
        expansion_m=alpha*h['longitud_presion_m']*dtemp,
        volumen_gravedad_equiv_m3=(2*abrupt['max_global_bar']*100*.25*math.pi*h['diametro_interior_m']**2*
            math.sin(math.radians(m['angulo_codo_deg'])/2))*1.5/(.6*24),
        estado='Solo equivalencia peso-fricción (mu0.6, gamma24kN/m3, FS1.5); no dimensiona cimentación ni anclaje en roca')
    heat=nom['p_turbina_kw']-nom['p_bornes_kw']+rated_bal['aux_kw']+rated_bal['cables_perdida_kw']+rated_bal['tsa']['p_kw']
    air=heat*1000/(a['rho_aire_estudio_kg_m3']*a['cp_aire_j_kg_k']*a['salto_termico_ventilacion_k'])
    ventilation=dict(calor_estudio_kw=heat,caudal_aire_m3s=air,
        potencia_ventiladores_requerida_kw=air*a['presion_ventilador_pa']/a['eficiencia_ventilador']/1000,
        potencia_propuesta_kw=2*1.1,estado='Balance térmico conservador; presión del sistema y curvas de ventiladores pendientes')
    return dict(cfg=cfg,hidrologia=hyd,demanda=demand_result,nominal=nom,balance_nominal=rated_bal,
        caudal_nominal_m3s=rated_flow,diametros=diameters,obras=civil,transitorios=transients,
        mecanica=mechanical,apoyos=supports,acciones=forces,electrico=electrical,
        oferta=results_series,alternativas=comparison,sensibilidad_sesgo=sensitivities,
        ventilacion=ventilation,auxiliares_base=baseaux,auxiliares_mantenimiento=auxmaintenance),series,hc,balance
