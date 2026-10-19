"""Catenaria elástica en el plano de carga para vanos inclinados, unidades SI."""
import math
import numpy as np

def geometria(h, distancia, desnivel, q_vertical, q_viento=0):
    if h<=0 or distancia<=0 or q_vertical<=0:raise ValueError('Datos físicos inválidos')
    q=math.hypot(q_vertical,q_viento);dy=desnivel*q_vertical/q
    dx=math.sqrt(distancia**2+desnivel**2-dy**2);a=h/q
    u=math.asinh(dy/(2*a*math.sinh(dx/(2*a))))
    x0=dx/2-a*u;u1=-x0/a;u2=(dx-x0)/a
    length=a*(math.sinh(u2)-math.sinh(u1))
    integral_t=h*(dx/2+a/4*(math.sinh(2*u2)-math.sinh(2*u1)))
    return dict(a=a,dx=dx,dy=dy,x0=x0,longitud_m=length,
                integral_t_ds=integral_t,t_inicial_n=h*math.cosh(u1),t_final_n=h*math.cosh(u2))

def sin_tension(g,ea):
    return g['longitud_m']-g['integral_t_ds']/ea

def estado(vanos,h_ref,q_ref,ea,alpha,t_ref,t,qv,qh=0,creep=0):
    """Conserva longitud sin tensión en un cantón; elasticidad lineal y fluencia explícita."""
    l0=sum(sin_tension(geometria(h_ref,a,dz,q_ref),ea) for a,dz in vanos)
    target=l0*(1+alpha*(t-t_ref)+creep)
    lo,hi=max(200,h_ref/20),h_ref*8
    def actual(h):return sum(sin_tension(geometria(h,a,dz,qv,qh),ea) for a,dz in vanos)
    while actual(lo)<target and lo>1:lo/=2
    while actual(hi)>target and hi<ea/10:hi*=2
    if actual(lo)<target or actual(hi)>target:raise ValueError('Estado fuera del intervalo físico')
    for _ in range(75):
        mid=(lo+hi)/2
        if actual(mid)>target:lo=mid
        else:hi=mid
    h=(lo+hi)/2
    return h,[geometria(h,a,dz,qv,qh) for a,dz in vanos],actual(h)-target

def puntos(g,distancia,desnivel,qv,qh=0,n=61):
    """Coordenadas locales: longitudinal, transversal a viento y vertical."""
    q=math.hypot(qv,qh);ey=np.array([0.,-qh/q,qv/q])
    r=np.array([distancia,0.,desnivel]);ex=(r-g['dy']*ey)/g['dx']
    x=np.linspace(0,g['dx'],n)
    y=g['a']*(np.cosh((x-g['x0'])/g['a'])-math.cosh(g['x0']/g['a']))
    return x[:,None]*ex+y[:,None]*ey
