"""Análisis explícito de línea trifásica y apoyos rígidos; SI; sin datos del lugar.

Ninguna función certifica equipos ni topografía. Los estados mecánicos por vano
son compatibles con aisladores rígidos; no se comparte H entre vanos desiguales.
"""
import math
from functools import lru_cache
import numpy as np
G=9.80665

def catenaria(H,L,dz,qv,qw=0):
    if H<=0 or L<=0 or qv<=0: raise ValueError('H, vano y carga vertical deben ser positivos')
    q=math.hypot(qv,qw); ey=np.array([0.,-qw/q,qv/q]); r=np.array([L,0.,dz])
    dy=float(r@ey); dx=math.sqrt(float(r@r)-dy*dy); ex=(r-dy*ey)/dx
    a=H/q; t=dx/(2*a)
    if t>300: raise ValueError('Catenaria fuera del intervalo numérico')
    u=math.asinh(dy/(2*a*math.sinh(t))); x0=dx/2-a*u
    u0=-x0/a;u1=(dx-x0)/a
    length=a*(math.sinh(u1)-math.sinh(u0))
    integ=H*(dx/2+a/4*(math.sinh(2*u1)-math.sinh(2*u0)))
    f0=H*ex+H*math.sinh(u0)*ey
    f1=-H*ex-H*math.sinh(u1)*ey
    chord=H*r/dx
    return dict(H=H,L=L,dz=dz,qv=qv,qw=qw,a=a,dx=dx,dy=dy,x0=x0,
                longitud_m=length,integral_T_ds=integ,T0_N=float(np.linalg.norm(f0)),T1_N=float(np.linalg.norm(f1)),
                F0=f0.tolist(),F1=f1.tolist(),chord=chord.tolist(),ex=ex.tolist(),ey=ey.tolist())

def longitud_natural(g,EA):
    # Primera aproximación elástica en T/EA, conservada en ambos estados.
    return g['longitud_m']-g['integral_T_ds']/EA

@lru_cache(maxsize=65536)
def resolver_estado(L,dz,H0,q0,EA,alpha,T0,T,qv,qw=0,creep=0):
    ref=catenaria(H0,L,dz,q0)
    target=longitud_natural(ref,EA)*(1+alpha*(T-T0)+creep)
    def residual(h): return longitud_natural(catenaria(h,L,dz,qv,qw),EA)-target
    lo=max(1.,H0/50);hi=H0*8
    while residual(lo)<0 and lo>0.1:lo/=2
    while residual(hi)>0 and hi<EA/100:hi*=2
    if residual(lo)*residual(hi)>0:raise ValueError('No se pudo encerrar raíz física')
    for _ in range(70):
        mid=(lo+hi)/2
        if residual(mid)>0:lo=mid
        else:hi=mid
    g=catenaria((lo+hi)/2,L,dz,qv,qw)
    g['residuo_longitud_m']=longitud_natural(g,EA)-target
    return g

def perfil(g,n=121):
    xx=np.linspace(0,g['dx'],n);yy=g['a']*(np.cosh((xx-g['x0'])/g['a'])-math.cosh(g['x0']/g['a']))
    xyz=xx[:,None]*np.array(g['ex'])+yy[:,None]*np.array(g['ey'])
    # x proyectada creciente incluso con inclinación y viento.
    return xyz

def impedancia_linea(conductor,longitud_conductor_m,frecuencia_hz,separaciones_m,temperatura_c):
    if any(d<=0 for d in separaciones_m) or longitud_conductor_m<=0:raise ValueError('Geometría eléctrica inválida')
    dm=math.prod(separaciones_m)**(1/3)
    gmr=conductor.get('gmr_m') or .7788*conductor['diametro_mm']/2000
    R=conductor['r20_ohm_km']*(1+conductor['alpha_r']*(temperatura_c-20))*longitud_conductor_m/1000
    X=2*math.pi*frecuencia_hz*2e-4*math.log(dm/gmr)*longitud_conductor_m/1000
    return complex(R,X),dict(R_ohm_fase=R,X_ohm_fase=X,DMG_m=dm,GMR_m=gmr,longitud_electrica_m=longitud_conductor_m)

def flujo_radial(Vs_LL,zs,cargas_va,max_iter=500):
    """Barrido atrás/adelante por fase; cargas trifásicas PQ y fuente fija."""
    if Vs_LL<=0 or len(zs)!=len(cargas_va):raise ValueError('Red inválida')
    v0=complex(Vs_LL/math.sqrt(3));v=[v0]*(len(zs)+1)
    for it in range(max_iter):
        currents=[0j]*len(zs);down=0j
        for j in range(len(zs)-1,-1,-1):
            if abs(v[j+1])<.15*abs(v0):raise ValueError('Tensión fuera de dominio del flujo PQ')
            down+=(cargas_va[j]/(3*v[j+1])).conjugate();currents[j]=down
        nv=[v0]
        for z,i in zip(zs,currents):nv.append(nv[-1]-z*i)
        err=max(abs(a-b) for a,b in zip(nv,v));v=[.7*a+.3*b for a,b in zip(nv,v)]
        if err<1e-8:break
    else:raise ValueError('Flujo radial no converge')
    currents=[(v[j]-v[j+1])/zs[j] if abs(zs[j])>0 else 0j for j in range(len(zs))]
    # Las ramas Z=0 se reconstruyen por KCL.
    if any(abs(z)==0 for z in zs):
        down=0j
        for j in range(len(zs)-1,-1,-1):down+=(cargas_va[j]/(3*v[j+1])).conjugate();currents[j]=down
    losses=[3*abs(i)**2*z for i,z in zip(currents,zs)]
    s_in=3*v0*currents[0].conjugate();s_out=sum(cargas_va)
    return dict(tensiones_LL_V=[abs(x)*math.sqrt(3) for x in v],corrientes_A=[abs(i) for i in currents],
                perdidas_W=[s.real for s in losses],perdidas_var=[s.imag for s in losses],
                P_entrada_W=s_in.real,Q_entrada_var=s_in.imag,
                residuo_balance_W=(s_in-s_out-sum(losses)).real,
                residuo_balance_var=(s_in-s_out-sum(losses)).imag,iteraciones=it+1,residuo_V=err)

def flujo_sistema(kv,p_kw,fp,z_linea,e,tap=1):
    if e['trafo_salida_kva']!=e['trafo_llegada_kva']:
        raise ValueError('Este modelo exige TX de igual potencia; ampliar con impedancias separadas antes de comparar equipos distintos')
    base=e['trafo_salida_kva'];v=kv*1000;zb=v*v/(base*1000)
    r=e['trafo_pcu_kw']/base;x=math.sqrt(e['trafo_uk_pu']**2-r*r);zt=complex(r,x)*zb
    shunt=complex(e['trafo_p0_kw'],e.get('trafo_q0_kvar',2.5))*1000
    load=complex(p_kw,p_kw*math.tan(math.acos(fp)))*1000
    f=flujo_radial(v*tap,[zt,z_linea,zt],[shunt,shunt,load])
    f.update(kV=kv,toma_pu=tap,P_carga_kW=p_kw,FP=fp,MT_salida_kV=f['tensiones_LL_V'][1]/1000,
             MT_llegada_kV=f['tensiones_LL_V'][2]/1000,BT_llegada_V=f['tensiones_LL_V'][3]*e.get('bt_v',380)/v,
             caida_linea_pct=100*(f['tensiones_LL_V'][1]-f['tensiones_LL_V'][2])/f['tensiones_LL_V'][1],
             perdida_linea_kW=f['perdidas_W'][1]/1000,P_generacion_kW=f['P_entrada_W']/1000+e['aux_generacion_estudio_kw'],
             S_generador_kVA=abs(complex(f['P_entrada_W']/1000+e['aux_generacion_estudio_kw'],f['Q_entrada_var']/1000)))
    return f

def capacidad_momento(longitud_m,empotramiento_m,carga_dan,punto_ensayo_bajo_cima_m=.15,factor_rotura=2,phi=.65):
    brazo=longitud_m-empotramiento_m-punto_ensayo_bajo_cima_m
    if brazo<=0 or carga_dan<=0:raise ValueError('Poste inválido')
    return dict(brazo_ensayo_m=brazo,M_servicio_kNm=carga_dan*10*brazo/1000,
                M_rotura_tipo_kNm=carga_dan*10*factor_rotura*brazo/1000,
                M_resistente_estudio_kNm=phi*carga_dan*10*factor_rotura*brazo/1000)

def fuerzas_globales(g,azimut,extremo):
    local=np.array(g['F0'] if extremo==0 else g['F1']);ch=np.array(g['chord'])*(1 if extremo==0 else -1)
    def rot(a):return np.array([math.cos(azimut)*a[0]-math.sin(azimut)*a[1],math.sin(azimut)*a[0]+math.cos(azimut)*a[1],a[2]])
    return rot(local),rot(ch)

def envolvente_poste(apoyo,adyacentes,estados,config,conductor):
    """Equilibrio 3D, reacción con signo, viento 360°, caso con/sin retenidas ideales."""
    Hlibre=apoyo['poste_m']-apoyo['empotramiento_m'];h=apoyo['amarre_m'];rows=[]
    for st in estados:
        angles=range(0,360,15) if st['viento_ms'] else [0]
        for ang in angles:
            wind=np.array([math.cos(math.radians(ang)),math.sin(math.radians(ang)),0.])
            carga=np.zeros(3);ideal=np.zeros(3);guy_comp=0.;tiros=[]
            for entry in adyacentes:
                L,dz,az,end=entry['L'],entry['dz'],entry['az'],entry['end']
                n=np.array([-math.sin(az),math.cos(az),0.]);qw=st['presion_pa']*st['diametro_cargado_m']*float(wind@n)
                g=resolver_estado(L,dz,config['H0_N'],config['q0_N_m'],config['EA_N'],conductor['alpha_termica'],config['T0_C'],st['temperatura_c'],st['qv_N_m'],qw,st['creep'])
                f,ch=fuerzas_globales(g,az,end);dist=f-ch
                fact=3*(config['gamma_tension']*ch+np.array([config['gamma_viento']*dist[0],config['gamma_viento']*dist[1],config['gamma_vertical']*dist[2]]))
                carga+=fact
                horizontal=3*config['gamma_tension']*ch[:2];force=np.linalg.norm(horizontal)
                ideal[:2]-=horizontal
                guy_comp+=force*math.tan(math.radians(config['angulo_retenida_deg']))
                tiros.append(force/math.cos(math.radians(config['angulo_retenida_deg']))/1000)
            # Poste cónico de diámetro lineal: integración exacta A*y dy.
            dt=config['diametro_cima_m'];db=config['diametro_base_m'];slope=(db-dt)/apoyo['poste_m'];dground=dt+slope*Hlibre
            Mposte=st['presion_pa']*config['gamma_viento']*(dground*Hlibre**2/2-slope*Hlibre**3/3)/1000
            mvec=np.array([carga[0]*h,carga[1]*h])/1000+wind[:2]*Mposte
            residual=np.array([(carga[0]+ideal[0])*h,(carga[1]+ideal[1])*h])/1000+wind[:2]*Mposte
            nvert=-carga[2]+config['gamma_vertical']*config['peso_herrajes_N']
            rows.append(dict(estado=st['id'],viento_az_deg=ang,F_E_kN=carga[0]/1000,F_N_kN=carga[1]/1000,
                    vertical_conductores_herrajes_kN=nvert/1000,compresion_con_retenidas_kN=(nvert+guy_comp)/1000,
                    M_sin_retenidas_kNm=float(np.linalg.norm(mvec)),M_con_retenidas_ideales_kNm=float(np.linalg.norm(residual)),
                    tiro_max_retenida_kN=max(tiros,default=0),M_viento_poste_kNm=Mposte))
    return rows
