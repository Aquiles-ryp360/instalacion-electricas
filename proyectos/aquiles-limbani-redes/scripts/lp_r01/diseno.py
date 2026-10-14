"""Fuente única LP-R01: trazado, catenarias inclinadas, cálculo eléctrico y metrados."""
from pathlib import Path
import sys,json,math,csv,heapq
import numpy as np
from shapely.geometry import Point,LineString,Polygon,shape,mapping
from shapely.ops import unary_union,nearest_points
from shapely import make_valid,contains_xy
from pyproj import Transformer
from trazado import osm,elevation,shortest,P,ROOT,B,D
sys.path.insert(0,str(ROOT))
from herramientas.lineas_primarias.mecanica import estado,puntos
C=json.loads((D/'parametros.json').read_text(encoding='utf-8'))
O=ROOT/'output/linea-primaria-limbani-huancasayani'
def write_json(f,data):
    f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def gj(features):return dict(type='FeatureCollection',crs={'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::32719'}},features=features)
def feature(g,props):return dict(type='Feature',geometry=mapping(g),properties=props)
def angle(a,b,c):
    u=np.array(b)-np.array(a);v=np.array(c)-np.array(b)
    return float(math.degrees(math.acos(np.clip(u@v/(np.linalg.norm(u)*np.linalg.norm(v)),-1,1))))

def avoid_houses(coords,houses):
    """Visibilidad local alrededor de polígonos del catastro, sin sobrevolar casas."""
    buffered=houses.buffer(4,join_style=2)
    polygons=list(buffered.geoms) if hasattr(buffered,'geoms') else [buffered]
    obstacle=unary_union([Polygon(g.exterior) for g in polygons if g.geom_type=='Polygon'])
    coords=list(coords)
    for i,pair in enumerate(coords):
        p=Point(pair)
        if obstacle.contains(p):
            q=nearest_points(p,obstacle.boundary)[1]
            direction=np.array(q.coords[0])-np.array(pair);direction/=np.linalg.norm(direction)
            coords[i]=tuple(np.array(q.coords[0])+direction*.03)
    out=[coords[0]]
    for a,b in zip(coords,coords[1:]):
        line=LineString([a,b])
        if line.intersection(obstacle.buffer(-.02)).length<.01:out.append(b);continue
        # A* en malla de 2m; obstáculos vectoriales conservados y validación de segmentos.
        inside=obstacle.buffer(-.02);grid_obstacle=obstacle.buffer(.3,join_style=2)
        xmin,ymin,xmax,ymax=line.bounds;xs=np.arange(xmin-90,xmax+92,2);ys=np.arange(ymin-90,ymax+92,2)
        xx,yy=np.meshgrid(xs,ys);blocked=contains_xy(grid_obstacle,xx,yy)
        def cell(pair):
            p=Point(pair);j=int(round((p.x-xs[0])/2));i=int(round((p.y-ys[0])/2));choices=[]
            for di in range(-8,9):
                for dj in range(-8,9):
                    ni,nj=i+di,j+dj
                    if not(0<=ni<len(ys) and 0<=nj<len(xs)) or blocked[ni,nj]:continue
                    q=(xs[nj],ys[ni])
                    if LineString([pair,q]).intersection(inside).length<.01:choices.append((math.dist(pair,q),(ni,nj)))
            if not choices:raise ValueError('Extremo sin conexión cartográfica libre')
            return min(choices)[1]
        ca,cb=cell(a),cell(b);todo=[(0,0,ca)];dist={ca:0};prev={}
        while todo:
            _,cost,k=heapq.heappop(todo)
            if cost!=dist[k]:continue
            if k==cb:break
            for di,dj in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nxt=(k[0]+di,k[1]+dj)
                if not (0<=nxt[0]<len(ys) and 0<=nxt[1]<len(xs)) or blocked[nxt]:continue
                l=math.hypot(di,dj)*2
                new=cost+l
                if new<dist.get(nxt,float('inf')):
                    dist[nxt]=new;prev[nxt]=k;heapq.heappush(todo,(new+2*math.dist(nxt,cb),new,nxt))
        if cb not in dist:raise ValueError('Corredor local sin solución fuera de casas')
        ids=[cb]
        while ids[-1]!=ca:ids.append(prev[ids[-1]])
        ids.reverse();path=[a]+[(xs[j],ys[i]) for i,j in ids]+[b]
        compact=[path[0]];k=0
        while k<len(path)-1:
            nxt=next(j for j in range(len(path)-1,k,-1) if LineString([path[k],path[j]]).intersection(inside).length<.01)
            compact.append(path[nxt]);k=nxt
        out.extend(compact[1:])
    return out

def route_and_poles():
    nodes,ways=osm();t=Transformer.from_crs(4326,32719,always_xy=True)
    start=Point(C['inicio']['e'],C['inicio']['n']);end=Point(*t.transform(C['fin']['lon'],C['fin']['lat']))
    road,ids=shortest(nodes,ways,start,end)
    waters=unary_union([LineString(w['xy']) for w in ways if 'waterway' in w['tags']])
    raw=json.loads((B/'investigacion/casas-originales.geojson').read_text(encoding='utf-8'))
    house_geometries=[shape(f['geometry']) for f in raw['features'] if f['geometry']]
    repaired=sum(not g.is_valid for g in house_geometries)
    houses=unary_union([make_valid(g) for g in house_geometries]);candidates=[]
    for side in [20,-20]:
        off=road.offset_curve(side,join_style=2).simplify(8,preserve_topology=True)
        if off.geom_type!='LineString':continue
        coords=list(off.coords)
        if Point(coords[-1]).distance(start)<Point(coords[0]).distance(start):coords.reverse()
        route=LineString([start.coords[0]]+coords+[end.coords[0]])
        score=route.intersection(houses.buffer(4)).length*20+route.intersection(waters.buffer(8)).length*50
        candidates.append((score,side,route))
    score,side,route=min(candidates,key=lambda v:v[0]);coords=avoid_houses(list(route.coords),houses);xy=[coords[0]];moved=0
    for a,b in zip(coords,coords[1:]):
        n=max(1,math.ceil(math.dist(a,b)/85))
        xy.extend(tuple(np.array(a)+(np.array(b)-np.array(a))*j/n) for j in range(1,n+1))
    def penalty(p):return max(0,8-p.distance(waters))*100+max(0,4-p.distance(houses))*100
    for i in range(1,len(xy)-1):
        p=Point(xy[i])
        # Mantener el eje ya desviado de inmuebles; los conflictos de cauce se registran.
        if p.distance(houses)>=3.98:continue
        choices=[]
        for dx in range(-20,21,5):
            for dy in range(-20,21,5):
                q=Point(p.x+dx,p.y+dy)
                if max(q.distance(Point(xy[i-1])),q.distance(Point(xy[i+1])))<=85:
                    choices.append((penalty(q)*100+math.hypot(dx,dy),q))
        if choices:
            q=min(choices,key=lambda v:v[0])[1];moved+=p.distance(q)>0;xy[i]=q.coords[0]
    refined=[xy[0]]
    for a,b in zip(xy,xy[1:]):
        n=max(1,math.ceil(math.dist(a,b)/85))
        refined.extend(tuple(np.array(a)+(np.array(b)-np.array(a))*j/n) for j in range(1,n+1))
    xy=refined
    # Elimina apoyos casi coincidentes si la cuerda conserva separación a casas y vano <=85m.
    changed=True
    while changed:
        changed=False
        for i in range(1,len(xy)-1):
            chord=LineString([xy[i-1],xy[i+1]])
            if min(math.dist(xy[i-1],xy[i]),math.dist(xy[i],xy[i+1]))<10 and chord.length<=85 and chord.distance(houses)>=3.98:
                xy.pop(i);changed=True;break
    route=LineString(xy);posts=[];ch=0;last_anchor=0
    for i,(x,y) in enumerate(xy):
        if i:ch+=math.dist(xy[i-1],xy[i])
        a=angle(xy[i-1],xy[i],xy[i+1]) if 0<i<len(xy)-1 else 0
        kind='TERMINAL' if i in (0,len(xy)-1) else ('ANCLAJE' if a>30 or ch-last_anchor>=500 else ('ANGULO' if a>5 else 'SUSPENSION'))
        if kind!='SUSPENSION':last_anchor=ch
        p=Point(x,y);dw=p.distance(waters);dh=p.distance(houses)
        posts.append(dict(id=f'P{i+1:03}',e=x,n=y,z_dem_m=elevation(x,y),progresiva_m=ch,angulo_deg=a,
                    estructura=kind,retencion=kind!='SUSPENSION',poste_m=13,amarre_m=10.6,distancia_cauce_m=dw,distancia_casa_m=dh,
                    cautela='; '.join(s for cond,s in [(dw<30,'Verificar cauce/faja'),(dw<8,'Conflicto cartográfico cauce'),(dh<4,'Conflicto inmueble')] if cond),
                    estado='PROYECTADO EN GABINETE; NO REPLANTEADO'))
    write_json(D/'referencias-osm.geojson',gj([feature(LineString(w['xy']),{'osm_id':w['id'],'clase':w['tags'].get('highway',w['tags'].get('waterway','otro'))}) for w in ways if 'highway' in w['tags'] or 'waterway' in w['tags']]))
    return route,posts,dict(longitud_vial_m=road.length,offset_m=side,criterio_score=score,postes_desplazados=moved,
           cruces_inmuebles_m=route.intersection(houses.buffer(4)).length,zona_cauce_estudio_m=route.intersection(waters.buffer(8)).length,
           casas_originales=len(raw['features']),casas_reparadas_solo_analisis=repaired,nodos_osm=ids),waters

def mechanical(posts,waters):
    c=C['conductor'];m=C['mecanica'];ea=c['e_pa']*c['seccion_real_mm2']*1e-6
    qr=c['masa_kg_km']/1000*9.80665;hr=c['rts_n']*c['tension_eds_fraccion_rts'];d=c['diametro_mm']/1000;spans=[]
    for i,(a,b) in enumerate(zip(posts,posts[1:])):
        l=math.hypot(b['e']-a['e'],b['n']-a['n']);dz=b['z_dem_m']+b['amarre_m']-a['z_dem_m']-a['amarre_m']
        spans.append(dict(id=f'V{i+1:03}',desde=a['id'],hasta=b['id'],longitud_m=l,desnivel_m=dz,
                    cruza_cauce=LineString([(a['e'],a['n']),(b['e'],b['n'])]).intersects(waters),estados={}))
    anchors=[i for i,p in enumerate(posts) if p['retencion']];sections=[]
    for k,(a,b) in enumerate(zip(anchors,anchors[1:])):
        subset=spans[a:b];vanos=[(v['longitud_m'],v['desnivel_m']) for v in subset]
        sec=dict(id=f'C{k+1:03}',desde=posts[a]['id'],hasta=posts[b]['id'],longitud_m=sum(v[0] for v in vanos),
                 vano_regulador_m=math.sqrt(sum(v[0]**3 for v in vanos)/sum(v[0] for v in vanos)),estados={})
        for cl in C['clima']:
            ice=cl['hielo_mm']/1000;qi=913*math.pi/4*((d+2*ice)**2-d*d)*9.80665;qv=qr+qi;qw=.455*cl['viento_ms']**2*(d+2*ice)
            h,gs,residual=estado(vanos,hr,qr,ea,c['alpha_termica'],15,cl['temperatura_c'],qv,qw,cl['creep'])
            sec['estados'][cl['id']]=dict(h_n=h,q_vertical_n_m=qv,q_viento_n_m=qw,residuo_longitud_m=residual)
            for j,(v,g) in enumerate(zip(subset,gs)):
                pts=puntos(g,v['longitud_m'],v['desnivel_m'],qv,qw,61);frac=pts[:,0]/v['longitud_m'];z=pts[:,2]
                pa=posts[a+j];pb=posts[a+j+1]
                ground=[elevation(pa['e']+(pb['e']-pa['e'])*s,pa['n']+(pb['n']-pa['n'])*s) for s in frac]
                clearance=z+pa['z_dem_m']+pa['amarre_m']-ground
                v['estados'][cl['id']]=dict(h_n=h,flecha_vertical_m=float(max(frac*v['desnivel_m']-z)),
                     tension_max_n=max(g['t_inicial_n'],g['t_final_n']),longitud_conductor_m=g['longitud_m'],
                     distancia_dem_min_m=float(min(clearance)),desviacion_viento_m=float(max(abs(pts[:,1]))))
                if cl['id']=='CALOR_FINAL':v['perfil']=dict(fraction=frac.tolist(),terreno_dem_m=ground,conductor_m=(z+pa['z_dem_m']+pa['amarre_m']).tolist())
                v['canton']=sec['id']
        sections.append(sec)
    guys=[]
    for i,p in enumerate(posts):
        adjacent=[v for v in spans if p['id'] in [v['desde'],v['hasta']]];mm=mg=mv=0
        for cl in C['clima']:
            ice=cl['hielo_mm']/1000;qw=.455*cl['viento_ms']**2*(d+2*ice);trib=sum(v['longitud_m']/2 for v in adjacent)
            above=p['poste_m']-(1.9 if p['poste_m']==13 else 2.1)
            fw=3*qw*trib*2.5;wp=.455*cl['viento_ms']**2*m['diametro_poste_medio_m']*above*2.5
            moment=fw*p['amarre_m']+wp*above/2
            if not p['retencion']:
                h=max(v['estados'][cl['id']]['h_n'] for v in adjacent)
                moment+=3*2*h*math.sin(math.radians(p['angulo_deg'])/2)*1.65*p['amarre_m']
            mm=max(mm,moment);tmax=max(v['estados'][cl['id']]['tension_max_n'] for v in adjacent)
            mg=max(mg,3*tmax*1.65/math.cos(math.radians(45)))
            qv=qr+913*math.pi/4*((d+2*ice)**2-d*d)*9.80665
            vert=3*qv*trib*1.5+300+3*tmax*sum(abs(v['desnivel_m'])/math.hypot(v['longitud_m'],v['desnivel_m']) for v in adjacent)*1.5
            if p['retencion']:vert+=mg*math.sin(math.radians(45))*len(adjacent)
            mv=max(mv,vert)
        cap=6000*2*.65*(above-.2)
        p.update(momento_estudio_knm=mm/1000,capacidad_momento_tipo_knm=cap/1000,utilizacion_poste=mm/cap,
                 vertical_estudio_kn=mv/1000,retencion_ramal_kn=mg/1000 if p['retencion'] else 0,
                 retenida_rotura_min_kn=math.ceil(max(60,mg/.9/1000)/10)*10 if p['retencion'] else 0,retenidas_num=len(adjacent) if p['retencion'] else 0)
        if p['retencion']:
            for j,v in enumerate(adjacent):
                other=posts[i+1] if v['desde']==p['id'] else posts[i-1]
                unit=(np.array([p['e'],p['n']])-np.array([other['e'],other['n']]))/v['longitud_m']
                anchor=np.array([p['e'],p['n']])+unit*p['amarre_m']
                guys.append(dict(id=f"R-{p['id']}-{j+1}",poste=p['id'],e=float(anchor[0]),n=float(anchor[1]),
                    resistencia_rotura_kn=p['retenida_rotura_min_kn'],tiro_estudio_kn=mg/1000,estado='VERIFICAR PREDIO/GEOTECNIA'))
    return spans,sections,guys

def electrical(length):
    d=C['demanda'];e=C['electrico'];c=C['conductor'];localities=[]
    for v in C['censo']['localidades']:
        f=(1+C['censo']['r_anual'])**9;users=math.ceil(v['viviendas_ocupadas']*f);unit=d['tipo_i_kw'] if v['tipo']=='I' else d['tipo_ii_kw']
        localities.append(dict(**v,usuarios_2026=users,poblacion_proyectada_2026=round(v['poblacion']*f),demanda_domestica_kw=users*unit*d['simultaneidad']))
    pd=sum(v['demanda_domestica_kw'] for v in localities);pap=d['ap_numero']*d['ap_kw_unit'];ps=sum(v['kw'] for v in d['servicios']);p=pd+pap+ps
    fp=d['fp_transporte'];q=p*math.tan(math.acos(fp));s=p/fp;r=c['r20_ohm_km']*(1+c['alpha_r']*55)*length/1000
    spacing=(1.2*1.2*2.4)**(1/3);gmr=.7788*c['diametro_mm']/2000;x=.0753982237*math.log(spacing/gmr)*length/1000;v=e['tension_kv']*1000
    arrival_p=e['trafo_p0_kw']+e['trafo_pcu_kw']*(s/250)**2;tr=e['trafo_pcu_kw']/250;tx=math.sqrt(e['trafo_uk_pu']**2-tr**2)
    arrival_q=250*tx*(s/250)**2;pin=p+arrival_p;qin=q+arrival_q;i=math.hypot(pin,qin)*1000/(math.sqrt(3)*v)
    pl=3*i*i*r/1000;ql=3*i*i*x/1000;pout=pin+pl;qout=qin+ql;sexit=math.hypot(pout,qout)
    exit_p=e['trafo_p0_kw']+e['trafo_pcu_kw']*(sexit/250)**2;exit_q=250*tx*(sexit/250)**2
    pg=pout+exit_p+e['aux_generacion_estudio_kw'];qg=qout+exit_q
    drop=math.sqrt(3)*i*(r*pin/math.hypot(pin,qin)+x*qin/math.hypot(pin,qin))/v*100;inom=250000/(math.sqrt(3)*v)
    # Flujo equilibrado PQ con impedancias de ambos TX y línea; toma de estudio +5% en salida.
    # 1% de corriente reactiva de vacío por TX es hipótesis explícita, no ensayo de placa.
    zb=v*v/250000;zt=complex(tr,tx)*zb;zl=complex(r,x);sload=complex(p,q)*1000;shunt=complex(e['trafo_p0_kw'],2.5)*1000
    source=v*1.05/math.sqrt(3);vl=complex(v/math.sqrt(3),0)
    for iteration in range(100):
        it2=(sload/3/vl).conjugate();vr=vl+zt*it2;il=it2+(shunt/3/vr).conjugate()
        vs=vr+zl*il;it1=il+(shunt/3/vs).conjugate();vg=vs+zt*it1
        residual=source-vg;vl+=residual*.7
        if abs(residual)<1e-7:break
    else:raise ValueError('Flujo PQ no converge')
    # Reconstruye en solución para conservar el balance P y Q.
    it2=(sload/3/vl).conjugate();vr=vl+zt*it2;il=it2+(shunt/3/vr).conjugate();vs=vr+zl*il;it1=il+(shunt/3/vs).conjugate()
    arrival_p=e['trafo_p0_kw']+3*abs(it2)**2*zt.real/1000;exit_p=e['trafo_p0_kw']+3*abs(it1)**2*zt.real/1000
    pl=3*abs(il)**2*r/1000;power=3*source*it1.conjugate()/1000;pg=power.real+e['aux_generacion_estudio_kw'];qg=power.imag;i=abs(il)
    drop=(abs(vs)-abs(vr))/abs(vs)*100
    flux=dict(toma_elevacion_pu=1.05,q_vacio_tx_kvar=2.5,tension_llegada_bt_v=abs(vl)*math.sqrt(3)*380/v,
              tension_inicio_mt_kv=abs(vs)*math.sqrt(3)/1000,tension_fin_mt_kv=abs(vr)*math.sqrt(3)/1000,
              desviacion_bt_pct=(abs(vl)*math.sqrt(3)/v-1)*100,iteraciones=iteration+1,residuo_v=abs(residual),
              metodo='Barrido inverso equilibrado PQ, impedancias nominales fijas; toma +5% y Q0 por validar con proveedor')
    conv=c['h_conveccion_estudio_w_m2k']*math.pi*c['diametro_mm']/1000*45
    rad=c['emisividad']*5.670374419e-8*math.pi*c['diametro_mm']/1000*((75+273.15)**4-(30+273.15)**4)
    solar=c['absorptividad_solar']*c['radiacion_w_m2']*c['diametro_mm']/1000;ith=math.sqrt(max(0,conv+rad-solar)/(c['r20_ohm_km']*(1+c['alpha_r']*55)/1000))
    fault=[];zb=v*v/250000;zt=complex(tr,tx)*zb;zl=complex(r,x)
    for name,xg in [('SUBTRANSITORIO',e['generador_xdpp_pu']),('TRANSITORIO',e['generador_xdp_pu']),('SOSTENIDO',e['generador_xd_pu'])]:
        zg=complex(e['generador_ra_pu'],xg)*zb
        for loc,z in [('SE-LIM_MT',zg+zt),('SE-HUA_MT',zg+zt+zl),('SE-HUA_BT',zg+zt+zl+zt)]:
            un=v if '_MT' in loc else 380;imp=z if '_MT' in loc else z*(380/v)**2
            fault.append(dict(estado=name,punto=loc,ik3_a=un/math.sqrt(3)/abs(imp),z_ohm=abs(imp)))
    alternatives=[]
    for sec,r20,diam in [(35,.958,7.5),(50,.671,9),(70,.485,10.7)]:
        rr=r20*(1+.0036*55)*length/1000;xx=.0753982237*math.log(spacing/(.7788*diam/2000))*length/1000
        alternatives.append(dict(seccion_mm2=sec,r20_ohm_km=r20,caida_pct=math.sqrt(3)*inom*(rr*.9+xx*math.sqrt(1-.9**2))/v*100,perdida_kw=3*inom**2*rr/1000))
    future=[dict(anio=2026+y,r_anual=rate,p_usuarios_kw=p*(1+rate)**y,s_usuarios_kva=s*(1+rate)**y) for y in [0,10,20] for rate in ([.01] if y==0 else [.01,.015])]
    ic=3*2*math.pi*60*(length/1000*e['capacitancia_estimada_nf_km']*1e-9)*v/math.sqrt(3)
    return dict(localidades=localities,usuarios=sum(v['usuarios_2026'] for v in localities),poblacion=sum(v['poblacion_proyectada_2026'] for v in localities),
        domestica_kw=pd,ap_kw=pap,servicios_kw=ps,p_usuarios_kw=p,q_usuarios_kvar=q,s_usuarios_kva=s,linea_r75_ohm=r,linea_x_ohm=x,
        gmr_m=gmr,dm_fases_m=spacing,corriente_demanda_a=i,corriente_250kva_a=inom,perdida_linea_kw=pl,perdida_tx_llegada_kw=arrival_p,
        perdida_tx_salida_kw=exit_p,p_generador_necesaria_kw=pg,q_generador_kvar=qg,s_generador_kva=math.hypot(pg,qg),caida_linea_pct=drop,flujo_pq=flux,
        ampacidad_modelo_a=ith,fallas=fault,reservas=[dict(reserva_limbani_kw=a,potencia_necesaria_kw=pg+a,margen_kw=200-pg-a) for a in [0,25,50,100]],
        alternativas=alternatives,proyeccion=future,ngr_ohm=v/math.sqrt(3)/5,ngr_energia_kj=v/math.sqrt(3)*5*10/1000,
        carga_capacitiva_tierra_a=ic,ig_bt_250kva_a=250000/math.sqrt(3)/380,caida_tx_llegada_pct=(tr*fp+tx*math.sqrt(1-fp*fp))*s/250*100)

def budget(posts,spans,guys):
    c=C['costos'];length=sum(v['estados']['EDS']['longitud_conductor_m'] for v in spans)*3
    amounts=[('AAAC 50 mm2, tres fases + 3% reserva','m',math.ceil(length*1.03),c['conductor_pen_m']),
       ('Poste CAC 13 m 600 daN tipo, suministro y montaje','ud',sum(p['poste_m']==13 for p in posts),c['poste_cac_instalado_pen']),
       ('Poste CAC 15 m 600 daN tipo, suministro y montaje','ud',sum(p['poste_m']==15 for p in posts),5300),
       ('Poste CAC 17 m 600 daN tipo, suministro y montaje','ud',sum(p['poste_m']==17 for p in posts),7100),
       ('Armado suspensión','ud',sum(p['estructura']=='SUSPENSION' for p in posts),c['armado_suspension_pen']),
       ('Armado angular de retención','ud',sum(p['estructura']=='ANGULO' for p in posts),c['armado_angulo_pen']),
       ('Armado anclaje/terminal','ud',sum(p['estructura'] in ['ANCLAJE','TERMINAL'] for p in posts),c['armado_anclaje_pen']),
       ('Retenida completa; bloque 1.2m tipo, por verificar','ud',len(guys),2600),('PAT poste, 2 varillas y enlace','ud',len(posts),c['tierra_poste_pen']),
       ('Transformador 250 kVA garantizado a altitud','ud',2,c['trafo250_altitud_pen']),('Celda de protección por SE','ud',2,c['celda_proteccion_pen']),
       ('Zigzag y NGR MT 5A/10s','lote',1,c['ngr_zigzag_pen']),('Malla SE 10x10m + 4 varillas','ud',2,c['malla_se_pen']),
       ('Tablero BT 400A','ud',2,22000),('Cable BT 2x240mm2/fase + N240, 20m/SE','m',280,105),('PE de SE Cu35, 20m/SE','m',40,20),('Descargadores y terminales SE','lote',2,8000),('Protecciones y comunicaciones','lote',1,35000),
       ('Plataforma SE 6x4m, cerco 20m y drenaje','ud',2,55000),('Pruebas y capacitación','lote',1,30000),('Campo, gestión ambiental y servidumbre','provisión',1,45000)]
    rows=[dict(partida=a,unidad=u,cantidad=q,precio_pen=p,parcial_pen=q*p,clase_precio='ESTIMADO; NO COTIZACION') for a,u,q,p in amounts]
    direct=sum(r['parcial_pen'] for r in rows);lo=direct*.12;eng=direct*.08;cont=(direct+lo+eng)*.2;base=direct+lo+eng+cont
    return dict(partidas=rows,longitud_conductor_sin_reserva_m=length,directo_pen=direct,logistica_extra_pen=lo,ingenieria_pen=eng,
                contingencia_pen=cont,total_sin_igv_pen=base,igv_pen=base*.18,total_con_igv_pen=base*1.18,intervalo_con_igv_pen=[base*1.18*.75,base*1.18*1.4])

def csvout(name,rows):
    if not rows:return
    f=O/'tablas'/name;f.parent.mkdir(parents=True,exist_ok=True)
    with f.open('w',encoding='utf-8-sig',newline='') as out:
        w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    O.mkdir(parents=True,exist_ok=True);route,posts,meta,waters=route_and_poles();spans,sections,guys=mechanical(posts,waters)
    # Alturas aumentadas para superar 7,5 m frente al DEM. No acredita distancia real en campo.
    for _ in range(3):
        changed=False
        for i,v in enumerate(spans):
            gap=min(s['distancia_dem_min_m'] for s in v['estados'].values())
            if gap<7.5:
                for p in posts[i:i+2]:
                    if p['poste_m']<17:
                        p['poste_m']+=2;p['amarre_m']+=1.8;changed=True
        if not changed:break
        spans,sections,guys=mechanical(posts,waters)
    el=electrical(route.length);bu=budget(posts,spans,guys)
    data=dict(revision='LP-R01',crs='EPSG:32719',linea_longitud_m=route.length,geometria=mapping(route),trazado=meta,
              postes=posts,vanos=spans,cantones=sections,retenidas=guys,electrico=el,presupuesto=bu)
    write_json(D/'resultados.json',data)
    write_json(D/'postes.geojson',gj([feature(Point(p['e'],p['n']),p) for p in posts]))
    write_json(D/'linea.geojson',gj([feature(route,dict(id='LP-LIM-HUA',longitud_m=route.length,tension_kv=10,estado='ACADEMICO'))]))
    write_json(D/'vanos.geojson',gj([feature(LineString([(a['e'],a['n']),(b['e'],b['n'])]),{k:v for k,v in s.items() if k not in ['estados','perfil']}) for a,b,s in zip(posts,posts[1:],spans)]))
    write_json(D/'retenidas.geojson',gj([feature(LineString([(next(p for p in posts if p['id']==r['poste'])['e'],next(p for p in posts if p['id']==r['poste'])['n']),(r['e'],r['n'])]),r) for r in guys]))
    write_json(D/'subestaciones.geojson',gj([feature(Point(p['e'],p['n']),dict(id=name,kva=250,mt_kv=10,bt_v=380,estado='PROPUESTA, NO PREDIO CONFIRMADO')) for p,name in [(posts[0],'SE-LIM'),(posts[-1],'SE-HUA')]]))
    csvout('postes.csv',posts);csvout('vanos.csv',[dict(**{k:v for k,v in s.items() if k not in ['estados','perfil']},flecha_final_m=s['estados']['CALOR_FINAL']['flecha_vertical_m'],distancia_dem_min_m=min(st['distancia_dem_min_m'] for st in s['estados'].values()),tension_max_n=max(st['tension_max_n'] for st in s['estados'].values())) for s in spans])
    csvout('estados_mecanicos.csv',[dict(vano=s['id'],canton=s['canton'],estado=state,**v) for s in spans for state,v in s['estados'].items()])
    csvout('cantones.csv',[{k:v for k,v in s.items() if k!='estados'} for s in sections]);csvout('retenidas.csv',guys)
    csvout('demanda.csv',el['localidades']);csvout('cortocircuito.csv',el['fallas']);csvout('presupuesto.csv',bu['partidas'])
    print(json.dumps(dict(longitud_m=route.length,postes=len(posts),vanos=len(spans),cantones=len(sections),retenidas=len(guys),demanda_kw=el['p_usuarios_kw'],
      generador_kw=el['p_generador_necesaria_kw'],caida_pct=el['caida_linea_pct'],min_distancia_dem_m=min(st['distancia_dem_min_m'] for s in spans for st in s['estados'].values()),
      max_utilizacion_poste=max(p['utilizacion_poste'] for p in posts),max_rts=max(st['tension_max_n'] for s in spans for st in s['estados'].values())/C['conductor']['rts_n'],costo_pen=bu['total_con_igv_pen']),indent=2))
if __name__=='__main__':main()
