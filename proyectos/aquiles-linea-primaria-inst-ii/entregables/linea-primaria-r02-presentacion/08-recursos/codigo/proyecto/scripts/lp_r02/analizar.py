"""Revisión LP-R02: lee entradas canónicas, nunca escribe sobre R01."""
from pathlib import Path
import json,math,csv,hashlib,sys
from collections import Counter
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from herramientas.lineas_primarias.revision import *

def guardar(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n',encoding='utf-8')
def tabla(p,rows):
    if not rows:return
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def calcular(P,O):
    C=json.loads((P/'datos/lp-r02/parametros.json').read_text());B=json.loads((P/'datos/lp-r02/geometria-base.json').read_text())
    c=C['conductor'];m=C['mecanica'];e=C['electrico'];q0=c['masa_kg_km']/1000*G;EA=c['e_pa']*c['seccion_real_mm2']*1e-6
    H0=c['rts_n']*c['tension_eds_fraccion_rts'];states=[]
    for row in C['clima']:
        s=dict(row);ice=s['hielo_mm']/1000;diam=c['diametro_mm']/1000+2*ice
        s.update(qv_N_m=q0+913*math.pi/4*(diam**2-(c['diametro_mm']/1000)**2)*G,presion_pa=.455*s['viento_ms']**2,diametro_cargado_m=diam)
        states.append(s)
    cfg=dict(H0_N=H0,q0_N_m=q0,EA_N=EA,T0_C=c['temperatura_referencia_c'],gamma_tension=m['factor_sobrecarga_longitudinal_estudio'],gamma_vertical=m['factor_sobrecarga_vertical_estudio'],gamma_viento=m['factor_sobrecarga_viento_estudio'],
             angulo_retenida_deg=m['retenida_angulo_vertical_deg'],diametro_cima_m=m['diametro_cima_estudio_m'],diametro_base_m=m['diametro_base_estudio_m'],peso_herrajes_N=m['carga_aisladores_poste_n'])
    ps=[]
    for p in B['postes']:
        t=dict(p);t['empotramiento_m']=1.9 if p['poste_m']==13 else 2.1
        ps.append(t)
    vs=[];state_rows=[]
    for i,b in enumerate(B['vanos']):
        a,p=ps[i:i+2];L=math.hypot(p['e']-a['e'],p['n']-a['n']);dz=p['z_dem_m']+p['amarre_m']-a['z_dem_m']-a['amarre_m'];az=math.atan2(p['n']-a['n'],p['e']-a['e']);v=dict(id=b['id'],desde=a['id'],hasta=p['id'],longitud_m=L,desnivel_m=dz,azimut_rad=az,estados={})
        ground=b['perfil']['terreno_dem_m'];fr=b['perfil']['fraction'];coords=[]
        for s in states:
            qw=s['presion_pa']*s['diametro_cargado_m']
            g=resolver_estado(L,dz,H0,q0,EA,c['alpha_termica'],c['temperatura_referencia_c'],s['temperatura_c'],s['qv_N_m'],qw,s['creep'])
            xyz=perfil(g);fraction=xyz[:,0]/L;z=xyz[:,2]+a['z_dem_m']+a['amarre_m']
            # Perfil central heredado de R01; envolvente lateral no disponible para estados nuevos.
            terrain=np.interp(fraction,fr,ground);gmin=float(min(z-terrain));sag=float(max(fraction*dz-xyz[:,2]))
            row=dict(vano=v['id'],estado=s['id'],L_m=L,dz_m=dz,H_N=g['H'],T_izq_N=g['T0_N'],T_der_N=g['T1_N'],T_RTS=max(g['T0_N'],g['T1_N'])/c['rts_n'],
                     flecha_vertical_m=sag,longitud_cable_m=g['longitud_m'],separacion_perfil_heredado_m=gmin,q_vertical_N_m=s['qv_N_m'],q_viento_N_m=qw,residuo_longitud_m=g['residuo_longitud_m'])
            v['estados'][s['id']]=row;state_rows.append(row)
            if s['id']=='CALOR_FINAL':
                v['perfil']=dict(fraccion=fraction.tolist(),terreno_m=terrain.tolist(),conductor_m=z.tolist())
        v['alerta_galibo']=min(r['separacion_perfil_heredado_m'] for r in v['estados'].values())<C['revision_r02']['margen_dem_estudio_m']
        vs.append(v)
    # Cada apoyo se analiza con sus dos vanos y los vectores verdaderos de cada extremo.
    post_rows=[];force_rows=[];guys=[]
    for i,p in enumerate(ps):
        adjacent=[]
        if i: v=vs[i-1];adjacent.append(dict(L=v['longitud_m'],dz=v['desnivel_m'],az=v['azimut_rad'],end=1))
        if i<len(vs):v=vs[i];adjacent.append(dict(L=v['longitud_m'],dz=v['desnivel_m'],az=v['azimut_rad'],end=0))
        rr=envolvente_poste(p,adjacent,states,cfg,c);force_rows.extend(dict(poste=p['id'],**r) for r in rr)
        cap=capacidad_momento(p['poste_m'],p['empotramiento_m'],m['poste_trabajo_dan'],m['punto_carga_bajo_cima_estudio_m'],m['poste_rotura_factor_propuesto'],m['factor_resistencia_poste_estudio'])
        current_guy=p['retencion'];raw=max(rr,key=lambda r:r['M_sin_retenidas_kNm']);guy=max(rr,key=lambda r:r['M_con_retenidas_ideales_kNm']);chosen=guy if current_guy else raw
        ratio=chosen['M_con_retenidas_ideales_kNm' if current_guy else 'M_sin_retenidas_kNm']/cap['M_resistente_estudio_kNm']
        uplift=min(r['vertical_conductores_herrajes_kN'] for r in rr)
        add_guy=(not current_guy) and (ratio>1 or uplift<0)
        planned=current_guy or add_guy
        moment=guy['M_con_retenidas_ideales_kNm'] if planned else raw['M_sin_retenidas_kNm']
        actions=[]
        if add_guy:actions.append('PROPONER RETENCION Y RETENIDAS; VERIFICAR ARMADO')
        if p['angulo_deg']>90:actions.append('REPLANTEAR GIRO MAYOR DE 90 GRADOS O ARMADO ESPECIAL')
        if uplift<0:actions.append('CARGA ASCENDENTE; COMPROBAR FIJACION Y HERREJES')
        if any(v['alerta_galibo'] for v in vs if p['id'] in [v['desde'],v['hasta']]):actions.append('REVISAR PERFIL/ALTURA O INSERTAR APOYO CON TOPOGRAFIA')
        if moment/cap['M_resistente_estudio_kNm']>1:actions.append('REFORZAR/REDUCIR VANO: FLEXION EXCEDE TIPO')
        typ='ANCLAJE_PROPUESTO' if add_guy else p['estructura']
        need=max(r['tiro_max_retenida_kN'] for r in rr) if planned else 0
        row=dict(id=p['id'],e=p['e'],n=p['n'],cota_dem_m=p['z_dem_m'],progresiva_m=p['progresiva_m'],poste_m=p['poste_m'],empotramiento_estudio_m=p['empotramiento_m'],amarre_m=p['amarre_m'],
                 angulo_deg=p['angulo_deg'],tipo_r01=p['estructura'],tipo_r02=typ,retenidas_r01=p['retenidas_num'],retenidas_r02=len(adjacent) if planned else 0,
                 M_sin_retenidas_kNm=raw['M_sin_retenidas_kNm'],M_con_ideales_kNm=guy['M_con_retenidas_ideales_kNm'],
                 M_capacidad_tipo_kNm=cap['M_resistente_estudio_kNm'],DC_r01_recalculado=ratio,DC_propuesta=moment/cap['M_resistente_estudio_kNm'],
                 vertical_min_kN=uplift,vertical_max_kN=max(r['vertical_conductores_herrajes_kN'] for r in rr),
                 compresion_retenidas_max_kN=max(r['compresion_con_retenidas_kN'] for r in rr) if planned else None,
                 retenida_tiro_kN=need,retenida_rotura_min_kN=math.ceil(max(m['retenida_rotura_min_n']/1000,need/.9)/10)*10 if need else 0,
                 caso_sin_retenidas=raw['estado'],viento_critico_deg=raw['viento_az_deg'],acciones='; '.join(actions) or 'CONSERVAR COMO CANDIDATO; CONFIRMAR CAMPO Y CERTIFICADOS',
                 capacidad_axial_kN=None,validacion='PENDIENTE: AXIAL/FLEXION, SUELO, HERRAJES Y TOPOGRAFIA')
        post_rows.append(row)
        if planned:
            for j,ad in enumerate(adjacent):
                az=ad['az'];sign=-1 if ad['end']==0 else 1;dist=p['amarre_m']/math.tan(math.radians(45))
                guys.append(dict(id=f"R02-{p['id']}-{j+1}",poste=p['id'],e=p['e']+sign*math.cos(az)*dist,n=p['n']+sign*math.sin(az)*dist,
                                 tiro_envolvente_kN=need,rotura_min_kN=row['retenida_rotura_min_kN'],estado='IDEAL: COORDENADA ESQUEMATICA SIN PREDIO NI SUELO'))
        if (i+1)%25==0:print(f'Apoyos analizados: {i+1}/{len(ps)}',flush=True)
    # Demanda: algoritmo paramétrico por años, sin convertir vivienda en abonado confirmado.
    demand=[];years=C['censo']['anio_diseno']-C['censo']['anio'];d=C['demanda']
    for loc in C['censo']['localidades']:
        users=math.ceil(loc['viviendas_ocupadas']*(1+C['censo']['r_anual'])**years)
        unit=d['tipo_i_kw'] if loc['tipo']=='I' else d['tipo_ii_kw']
        demand.append(dict(localidad=loc['nombre'],viviendas_base=loc['viviendas_ocupadas'],usuarios_potenciales=users,calificacion_kW=unit,simultaneidad=d['simultaneidad'],demanda_kW=users*unit*d['simultaneidad'],estado='HIPOTESIS DE MERCADO; SIN PADRON'))
    pk=sum(x['demanda_kW'] for x in demand)+d['ap_numero']*d['ap_kw_unit']+sum(x['kw'] for x in d['servicios'])
    cable=sum(v['estados']['EDS']['longitud_cable_m'] for v in vs)
    z,par=impedancia_linea(c,cable,e['frecuencia_hz'],[1.2,1.2,2.4],e['temperatura_conductor_c'])
    comparisons=[];lineonly=[]
    for kv in [10,20,22,22.9]:
        for tap in [1.,1.025,1.05]:comparisons.append(flujo_sistema(kv,pk,d['fp_transporte'],z,e,tap))
        load=complex(pk,pk*math.tan(math.acos(d['fp_transporte'])))*1000
        f=flujo_radial(kv*1000,[z],[load]);lineonly.append(dict(tension_origen_kV=kv,tension_llegada_kV=f['tensiones_LL_V'][-1]/1000,I_A=f['corrientes_A'][0],perdida_kW=f['perdidas_W'][0]/1000,caida_pct=(kv-f['tensiones_LL_V'][-1]/1000)/kv*100,residuo_W=f['residuo_balance_W']))
    # Curvas de carga y fuentes alternativas: escenarios, no energía medida ni precio de energía.
    energy=[];balance=[];growth=[];fault=[]
    for kv in [10,22.9]:
        for pct,hours in [(.25,2920),(.5,2920),(.75,2190),(1.,730)]:
            f=flujo_sistema(kv,pk*pct,.9,z,e,1.05)
            energy.append(dict(kV=kv,fraccion_pico=pct,horas_hipotesis=hours,P_carga_kW=pk*pct,perdida_linea_kW=f['perdida_linea_kW'],energia_perdida_linea_kWh=f['perdida_linea_kW']*hours,estado='CURVA SINTETICA, REEMPLAZAR CON MEDICIONES'))
        f=next(x for x in comparisons if x['kV']==kv and x['toma_pu']==1.05)
        for pg in [150,200]:
            for reserve in [0,25,50]:balance.append(dict(kV=kv,oferta_hipotetica_kW=pg,reserva_limbani_kW=reserve,necesidad_kW=f['P_generacion_kW']+reserve,margen_kW=pg-f['P_generacion_kW']-reserve,estado='NO CONFIRMA DISPONIBILIDAD HIDRICA'))
        for year in [0,10,20]:
            future=pk*(1+C['censo']['r_anual'])**year
            f2=flujo_sistema(kv,future,.9,z,e,1.05)
            growth.append(dict(kV=kv,anio=C['censo']['anio_diseno']+year,P_carga_kW=future,P_generador_kW=f2['P_generacion_kW'],S_generador_kVA=f2['S_generador_kVA'],BT_V=f2['BT_llegada_V']))
        zb=(kv*1000)**2/(e['generador_kva']*1000);rt=e['trafo_pcu_kw']/e['trafo_salida_kva'];xt=math.sqrt(e['trafo_uk_pu']**2-rt**2);zt=complex(rt,xt)*(kv*1000)**2/(e['trafo_salida_kva']*1000)
        for name,key in [('SUBTRANSITORIO','generador_xdpp_pu'),('TRANSITORIO','generador_xdp_pu'),('SOSTENIDO','generador_xd_pu')]:
            zg=complex(e['generador_ra_pu'],e[key])*zb
            for loc,zz in [('MT_SALIDA',zg+zt),('MT_LLEGADA',zg+zt+z),('BT_LLEGADA',zg+zt+z+zt)]:
                ik=kv*1000/math.sqrt(3)/abs(zz)
                if loc.startswith('BT'):ik*=kv*1000/e['bt_v']
                fault.append(dict(kV=kv,estado=name,punto=loc,Ik3_A=ik,impedancia_referida_MT_ohm=abs(zz),estado_datos='HIPOTESIS DE PLACA Y MODELO SIMPLIFICADO; NO AJUSTE RELE'))
    # Metrado trazable: longitudes de tendido + puentes por extremos de amarre + reserva separada.
    met=[];line_total=0;bridge_total=0
    for v in vs:
        length=3*v['estados']['EDS']['longitud_cable_m'];line_total+=length
        met.append(dict(id='C-'+v['id'],recurso='Conductor AAAC 50: terna tendida',unidad='m',cantidad=length,formula='3 x longitud catenaria EDS del vano',referencia=v['id'],estado='CALCULADO SOBRE CORREDOR DE GABINETE'))
    for p in post_rows:
        met.append(dict(id='P-'+p['id'],recurso=f"Poste CAC {p['poste_m']} m / 600 daN tipo",unidad='ud',cantidad=1,formula='1 por apoyo candidato',referencia=p['id'],estado=p['validacion']))
        met.append(dict(id='A-'+p['id'],recurso='Armado '+p['tipo_r02'],unidad='jgo',cantidad=1,formula='1 armado funcional; piezas pendientes',referencia=p['id'],estado='NO ES LISTA DE FABRICACION'))
        if p['retenidas_r02']:
            met.append(dict(id='R-'+p['id'],recurso='Retenida y anclaje por ramal',unidad='ud',cantidad=p['retenidas_r02'],formula='1 por ramal retenido',referencia=p['id'],estado='COORDENADA Y GEOTECNIA PENDIENTES'))
            bridge=3*C['revision_r02']['puente_por_ramal_m']*p['retenidas_r02'];bridge_total+=bridge
            met.append(dict(id='J-'+p['id'],recurso='Conductor para puentes/colas',unidad='m',cantidad=bridge,formula='3 fases x ramales x reserva geométrica 2 m/ramal/fase',referencia=p['id'],estado='PROVISION: LONGITUD DE PUENTES POR DETALLE'))
    reserve=math.ceil((line_total+bridge_total)*C['revision_r02']['reserva_conductor'])
    met.extend([dict(id='C-RES',recurso='Reserva adicional conductor',unidad='m',cantidad=reserve,formula='ceil(3% x (tendido + puentes))',referencia='TODOS',estado='HIPOTESIS DE SUMINISTRO'),dict(id='T-01',recurso='Transformador 250 kVA netos en sitio',unidad='ud',cantidad=2,formula='1 salida + 1 llegada',referencia='SE-LIM/SE-HUA',estado='RELACION, PERDIDAS, ALTITUD Y PLACAS PENDIENTES')])
    summary=[]
    for key in sorted({(x['recurso'],x['unidad']) for x in met}):summary.append(dict(recurso=key[0],unidad=key[1],cantidad=sum(x['cantidad'] for x in met if (x['recurso'],x['unidad'])==key),estado='METRADO DE ESTUDIO, NO ORDEN DE COMPRA'))
    # Cantidades civiles paramétricas: sin precio ni dimensión geotécnica inventada.
    civil=[dict(poste=p['id'],empotramiento_estudio_m=p['empotramiento_estudio_m'],diametro_excavacion_m=None,volumen_excavacion_m3=None,volumen_concreto_m3=None,formula='pi/4*D_exc^2*h; concreto=excavación-volumen desplazado',estado='REQUIERE GEOTECNIA Y DIMENSIONES DE FABRICANTE') for p in post_rows]
    # Vano límite de ejemplo: dos vanos iguales, terreno plano y sin retención.
    limits=[];dmax=.009;press=.455*29**2
    for grade in [400,600]:
        cap=capacidad_momento(13,1.9,grade);Mallow=cap['M_resistente_estudio_kNm'];high=0;constraint=''
        for L in range(10,301):
            worstgap=99;worstrts=0
            for s in states:
                gg=resolver_estado(L,0,H0,q0,EA,c['alpha_termica'],c['temperatura_referencia_c'],s['temperatura_c'],s['qv_N_m'],s['presion_pa']*s['diametro_cargado_m'],s['creep']);xyz=perfil(gg,61)
                worstgap=min(worstgap,10.6+float(xyz[:,2].min()));worstrts=max(worstrts,gg['T0_N']/c['rts_n'])
            Hfree=11.1;sl=(.375-.18)/13;dg=.18+sl*Hfree
            Mp=press*2.5*(dg*Hfree**2/2-sl*Hfree**3/3)/1000
            M=3*press*dmax*L*2.5*10.6/1000+Mp
            failed=[]
            if M>Mallow:failed.append('FLEXION')
            if worstgap<7.5:failed.append('FLECHA/GALIBO DE ESTUDIO')
            if worstrts>.4:failed.append('TRACCION/RTS 40% DE ESTUDIO')
            if failed:constraint=' + '.join(failed);break
            high=L
        limits.append(dict(poste='13m/'+str(grade)+'daN',vano_limite_ejemplo_m=high,primer_vano_que_falla_m=L,restriccion=constraint,M_resistente_tipo_kNm=Mallow,estado='TERRENO PLANO, DOS VANOS IGUALES, 15% RTS; NO ES VANO AUTORIZADO'))
    out=dict(revision='LP-R02',estado='REVISION ACADEMICA CON OBSERVACIONES ABIERTAS',geometria_fuente='datos/lp-r02/geometria-base.json',
             longitud_horizontal_m=sum(v['longitud_m'] for v in vs),longitud_electrica_m=cable,demanda_kW=pk,parametros_linea=par,
             configuracion_mecanica=cfg,clima=states,postes=post_rows,vanos=vs,retenidas=guys,demanda=demand,comparacion_tensiones=comparisons,
             linea_con_origen_MT_fijo=lineonly,balance_fuente=balance,energia=energy,proyeccion=growth,cortocircuito=fault,metrados=summary,
             conductor=dict(tendido_terna_m=line_total,puentes_provision_m=bridge_total,reserva_m=reserve,total_compra_estudio_m=math.ceil(line_total+bridge_total+reserve)),
             vanos_limite_ejemplo=limits,
             resumen=dict(apoyos=len(ps),vanos=len(vs),retenidas_r01=sum(p['retenidas_r01'] for p in post_rows),retenidas_propuestas=len(guys),
                          apoyos_refuerzo_propuesto=sum(p['tipo_r02']=='ANCLAJE_PROPUESTO' for p in post_rows),
                          apoyos_carga_ascendente=sum(p['vertical_min_kN']<0 for p in post_rows),
                          apoyos_exceden_flexion_base=sum(p['DC_r01_recalculado']>1 for p in post_rows),
                          apoyos_exceden_flexion_propuesta=sum(p['DC_propuesta']>1 for p in post_rows),
                          vanos_alerta_galibo=sum(v['alerta_galibo'] for v in vs),
                          T_RTS_max=max(s['T_RTS'] for v in vs for s in v['estados'].values()),
                          separacion_perfil_min_m=min(s['separacion_perfil_heredado_m'] for v in vs for s in v['estados'].values())),
             limites=['Sin placa no hay tensión de salida confirmada','DEM no valida emplazamientos ni alturas de construcción','Retenidas ideales: sin rigidez, pretensión ni cimentación verificadas','No se certifica capacidad axial ni interacción N-M','No se emite presupuesto cerrado: precios sin cotización y obras civiles sin dimensionar'])
    guardar(O/'03-calculos/resultados.json',out)
    for name,rows in [('estados_por_vano',state_rows),('fuerzas_por_apoyo',force_rows),('comparacion_tensiones',[{k:v for k,v in f.items() if not isinstance(v,list)} for f in comparisons]),('origen_MT_fijo',lineonly),('demanda',demand),('balance_fuente',balance),('energia',energy),('cortocircuito',fault),('vanos_limite_ejemplo',limits)]:tabla(O/'03-calculos'/f'{name}.csv',rows)
    for name,rows in [('postes',post_rows),('retenidas',guys),('metrado_detallado',met),('resumen_metrados',summary),('civiles_pendientes',civil)]:tabla(O/'02-metrados'/f'{name}.csv',rows)
    print(json.dumps(out['resumen'],ensure_ascii=False,indent=2,default=lambda x:x.item()),flush=True)
    return out,met,civil
