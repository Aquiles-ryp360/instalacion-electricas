"""MOC académico de reservorio, tubería uniforme y válvula equivalente.

Fricción cuasiestacionaria; sin cavitación, chimenea, turbina ni aire atrapado.
El aviso de presión negativa NO permite interpretar una simulación como segura.
"""
import math
import numpy as np
from .calculos import positivo, no_negativo


def moc_valvula(q0_m3s, salto_m, longitud_m, diametro_m, celeridad_ms,
                factor_darcy, cierre_s, duracion_s=15.0, celdas=100,
                limite_presion_manometrica_m=None):
    for name, val in [('Q',q0_m3s),('H',salto_m),('L',longitud_m),
                      ('D',diametro_m),('a',celeridad_ms),('T',duracion_s)]:
        positivo(name,val)
    no_negativo('f',factor_darcy)
    if cierre_s is not None: no_negativo('Tiempo de cierre',cierre_s)
    if not isinstance(celdas,int) or celdas<10: raise ValueError('Malla insuficiente')
    g=9.81; area=math.pi*diametro_m**2/4
    dx=longitud_m/celdas; dt=dx/celeridad_ms
    b=celeridad_ms/(g*area)
    r=factor_darcy*dx/(2*g*diametro_m*area**2)
    hf=factor_darcy*longitud_m/diametro_m*(q0_m3s/area)**2/(2*g)
    if hf>=salto_m: raise ValueError('Pérdida consume el salto')
    x=np.linspace(0,longitud_m,celdas+1)
    h=salto_m-hf*x/longitud_m
    z=salto_m*(1-x/longitud_m)
    q=np.full(celdas+1,q0_m3s)
    hmin=(h-z).copy(); hmax=(h-z).copy()
    k0=q0_m3s/math.sqrt(salto_m-hf)
    times=[0.0]; downstream=[float(h[-1])]; discharges=[q0_m3s]
    stride=max(1,int(0.015/dt))
    nsteps=int(math.ceil(duracion_s/dt))
    cavitation_time=None
    last_valid_time=0.0
    for step in range(1,nsteps+1):
        t=step*dt
        cp=h[:-1]+b*q[:-1]-r*q[:-1]*np.abs(q[:-1])
        cm=h[1:]-b*q[1:]+r*q[1:]*np.abs(q[1:])
        hn=np.empty_like(h); qn=np.empty_like(q)
        hn[1:-1]=(cp[:-1]+cm[1:])/2
        qn[1:-1]=(cp[:-1]-cm[1:])/(2*b)
        hn[0]=salto_m
        qn[0]=(salto_m-cm[0])/b
        tau=1.0 if cierre_s is None else (0.0 if cierre_s==0 else max(0.0,1-t/cierre_s))
        k=k0*tau
        if k==0:
            qn[-1]=0; hn[-1]=cp[-1]
        else:
            # Q=k*sqrt(H), H=C+ - BQ. La frontera es válvula equivalente.
            if cp[-1]<0:
                raise ArithmeticError('Frontera de válvula fuera del modelo monofásico')
            y=(-b*k+math.sqrt((b*k)**2+4*cp[-1]))/2
            hn[-1]=y*y; qn[-1]=k*y
        h,q=hn,qn
        phead=h-z
        if limite_presion_manometrica_m is not None and phead.min()<limite_presion_manometrica_m:
            cavitation_time=t
            # No continuar a presiones absolutas imposibles ni simular colapso de cavidades.
            break
        hmin=np.minimum(hmin,phead); hmax=np.maximum(hmax,phead)
        last_valid_time=t
        if step%stride==0 or step==nsteps:
            times.append(t); downstream.append(float(h[-1])); discharges.append(float(q[-1]))
    return {'dt_s':dt,'dx_m':dx,'cfl':1.0,'celdas':celdas,
            'tiempo_s':times,'carga_valvula_m':downstream,'q_valvula_m3s':discharges,
            'x_m':x.tolist(),'presion_max_m':hmax.tolist(),'presion_min_m':hmin.tolist(),
            'max_global_bar':float(hmax.max()*1000*g/1e5),
            'min_global_bar':float(hmin.min()*1000*g/1e5),
            'min_carga_m':float(hmin.min()), 'cierre_s':cierre_s,
            'duracion_valida_s':last_valid_time,
            'cavitacion_detectada':cavitation_time is not None,
            'tiempo_limite_monofasico_s':cavitation_time,
            'negativas':bool((hmin < -0.01).any()),
            'estado':'MOC de válvula equivalente, no transitorio de turbina real'}
