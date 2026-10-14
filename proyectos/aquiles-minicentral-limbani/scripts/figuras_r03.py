"""Figuras científicas y esquemas editables del proyecto académico R03."""
from pathlib import Path
import sqlite3, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from shapely import wkb
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer

BLUE='#235b85';RED='#a22732';GREEN='#2e7865';ORANGE='#cc8a36';GRAY='#66717c'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'ps.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#253641',
                     'axes.titleweight':'bold','axes.titlesize':12,'legend.fontsize':8})


def guardar(fig,exp,name):
    path=exp/'figuras'/name
    fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight')
    fig.savefig(path.with_suffix('.svg'),bbox_inches='tight')
    fig.savefig(path.with_suffix('.png'),dpi=300,bbox_inches='tight')
    plt.close(fig)


def lineas(ax,geom,color,linewidth=.8,alpha=1,label=None):
    if geom.geom_type=='Polygon':
        x,y=geom.exterior.xy;ax.plot(x,y,color=color,lw=linewidth,alpha=alpha,label=label)
    elif hasattr(geom,'geoms'):
        for i,g in enumerate(geom.geoms):lineas(ax,g,color,linewidth,alpha,label if i==0 else None)
    elif hasattr(geom,'xy'):
        x,y=geom.xy;ax.plot(x,y,color=color,lw=linewidth,alpha=alpha,label=label)


def geom_gpkg(path):
    c=sqlite3.connect('file:'+str(path.resolve())+'?mode=ro&immutable=1',uri=True)
    result={}
    for table,col in c.execute('select table_name,column_name from gpkg_geometry_columns').fetchall():
        values=[]
        for (raw,) in c.execute('select "'+col+'" from "'+table+'"'):
            if raw:
                offset={0:8,1:40,2:56,3:56,4:72}[(raw[3]>>1)&7]
                values.append(wkb.loads(raw[offset:]))
        result[table]=values
    c.close();return result


def norte_escala(ax,bar=100):
    ax.annotate('N',xy=(.95,.95),xytext=(.95,.79),xycoords='axes fraction',
                ha='center',va='center',fontweight='bold',arrowprops=dict(arrowstyle='-|>',color=GRAY))
    xlo,xhi=ax.get_xlim();ylo,yhi=ax.get_ylim();x=xlo+.06*(xhi-xlo);y=ylo+.06*(yhi-ylo)
    ax.plot([x,x+bar],[y,y],color='black',lw=3)
    ax.text(x+bar/2,y+.02*(yhi-ylo),f'{bar:g} m',ha='center',fontsize=8,
            bbox=dict(facecolor='white',alpha=.75,edgecolor='none',pad=1))


def diagram_canvas(size=(11,6)):
    fig,ax=plt.subplots(figsize=size);ax.set_xlim(0,12);ax.set_ylim(0,7);ax.axis('off')
    return fig,ax


def box(ax,x,y,w,h,label,color=BLUE,fontsize=9):
    ax.add_patch(Rectangle((x,y),w,h,ec=color,fc='white',lw=1.4))
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=fontsize,color='#223641')


def connect(ax,points,color=BLUE,style='-',arrow=False):
    xs,ys=zip(*points);ax.plot(xs,ys,color=color,lw=1.4,ls=style)
    if arrow:
        ax.annotate('',xy=points[-1],xytext=points[-2],arrowprops=dict(arrowstyle='->',color=color,lw=1.4))


def dibujar(exp,r,series,geo):
    root=exp.parents[3];proy=root/'proyectos/aquiles-minicentral-limbani'
    # En build/<id>/r03/expediente, parents[3] es la raíz del repositorio.
    src=proy/'fuentes/local/investigacion-r03';work=root/'build/aquiles-minicentral-limbani/investigacion'
    cfg=r['cfg'];h=cfg['hidraulica'];g=cfg['grupo'];e=cfg['electrico'];o=cfg['obras']
    xy=Transformer.from_crs(4326,32719,always_xy=True)
    candidates=json.loads((src/'tramos_candidatos.json').read_text(encoding='utf-8'))
    river=transform(xy.transform,shape(candidates[0]['geometria']))
    ref=transform(xy.transform,shape(json.loads((src/'cuenca_9080887.geojson').read_text(encoding='utf-8'))['geometry']))
    if not (work/'dem_delimitacion.npz').exists():
        import subprocess,sys
        subprocess.run([sys.executable,str(proy/'scripts/analizar_dem_r03.py')],check=True,capture_output=True)
    dem=np.load(work/'dem_delimitacion.npz')
    fig,ax=plt.subplots(figsize=(8.5,7.2))
    ax.contourf(dem['xx'],dem['yy'],dem['z'],levels=14,cmap='Greys',alpha=.32)
    ax.contourf(dem['xx'],dem['yy'],dem['captacion_propuesta'].astype(float),levels=[.5,1.5],colors=[ORANGE],alpha=.35)
    lineas(ax,ref,GRAY,1.3,label=f'Polígono PISCO: {geo["area_salida_pisco_km2"]:.0f} km² geodésicos')
    lineas(ax,river,BLUE,1.5,label='Tramo COMID 9080887')
    for name,color,label in [('captacion_propuesta',RED,'Punto de captación de estudio'),('estacion_limbani',GREEN,'Estación HLG 260501')]:
        pt=geo['puntos'][name];ax.scatter(pt['e_original_m'],pt['n_original_m'],color=color,s=45,zorder=5,label=label)
    b=ref.bounds;ax.set_xlim(b[0]-800,b[2]+800);ax.set_ylim(b[1]-800,b[3]+800)
    ax.set_aspect('equal');ax.ticklabel_format(style='plain',useOffset=False);ax.tick_params(labelsize=8)
    ax.set_xlabel('Este UTM 19S (m)');ax.set_ylabel('Norte UTM 19S (m)')
    ax.set_title('Cuenca de referencia y delimitación exploratoria en captación')
    ax.legend(loc='lower left',framealpha=.95);norte_escala(ax,5000)
    fig.text(.5,.005,'Mapzen / USGS y PISCO, Llauca–SENAMHI. WGS84 / EPSG:32719. Sin validación hidrológica local.',ha='center',fontsize=8)
    guardar(fig,exp,'cuenca-r03')
    # Base del avance original: no incorpora viviendas sintetizadas por otros agentes.
    original=Path('C:/Users/51949/Downloads/Catastro_Limbani/qgis/Catastro-Limbani.gpkg')
    layers=geom_gpkg(original)
    fig,ax=plt.subplots(figsize=(7.4,8.5))
    for table,geoms in layers.items():
        color=BLUE if 'Rios' in table else (ORANGE if table=='Casas' else '#b2b8bc')
        for gg in geoms:lineas(ax,gg,color,.8 if 'Rios' in table else .5)
    pts=[('CM-A: antecedente de memoria',425580,8436580,GRAY),('CM-B: antecedente CAD',425715,8436650,RED),
         ('Captación propuesta de estudio',geo['puntos']['captacion_propuesta']['e_original_m'],geo['puntos']['captacion_propuesta']['n_original_m'],GREEN)]
    for label,x,y,c in pts:
        ax.scatter(x,y,color=c,s=30,zorder=8)
    # Leyenda aparte evita desplazar etiquetas sobre huellas o río.
    for label,x,y,c in pts:ax.plot([],[],marker='o',ls='',color=c,label=label)
    ax.plot([],[],color=ORANGE,label='Huellas del avance original, sin padrón de usuarios')
    ax.plot([],[],color=BLUE,label='Cauces de la base recibida')
    ax.set_xlim(425050,426050);ax.set_ylim(8434300,8437050);ax.set_aspect('equal')
    ax.ticklabel_format(style='plain',useOffset=False);ax.tick_params(labelsize=8)
    ax.set_xlabel('Este UTM 19S (m)');ax.set_ylabel('Norte UTM 19S (m)');ax.set_title('Emplazamiento: antecedentes y propuesta diferenciados')
    ax.legend(loc='upper left',bbox_to_anchor=(1.04,1),fontsize=8);norte_escala(ax,200)
    fig.text(.5,.005,'Base catastral recibida. Casa de máquinas existente y captación sin identificación confirmada.',ha='center',fontsize=8)
    guardar(fig,exp,'emplazamiento-r03')
    # Ubicación territorial hasta Huancasayani; líneas de vinculación, sin traza constructiva.
    fig,ax=plt.subplots(figsize=(8.2,6.5))
    ax.contourf(dem['xx'],dem['yy'],dem['z'],levels=16,cmap='Greys',alpha=.25)
    lineas(ax,river,BLUE,1.6,label='Eje fluvial del producto PISCO')
    osm=json.loads((src/'huancasayani_osm.json').read_text(encoding='utf-8'))
    p0=(425715,8436650);ax.scatter(*p0,color=RED,s=45)
    ax.annotate('Casa candidata CM-B',p0,xytext=(12,12),textcoords='offset points',fontsize=9)
    for entry in osm:
        if entry.get('category')!='place':continue
        pp=xy.transform(float(entry['lon']),float(entry['lat']))
        ax.scatter(*pp,color=GREEN,s=40)
        ax.annotate(entry['name'],pp,xytext=(12,-12),textcoords='offset points',fontsize=9)
        ax.plot([p0[0],pp[0]],[p0[1],pp[1]],ls=':',color=GRAY,lw=1)
    ax.set_xlim(422000,427500);ax.set_ylim(8429000,8437800);ax.set_aspect('equal')
    ax.ticklabel_format(style='plain',useOffset=False);ax.tick_params(labelsize=8)
    ax.set_title('Ámbito del suministro aislado: Limbani y Huancasayani')
    ax.set_xlabel('Este UTM 19S (m)');ax.set_ylabel('Norte UTM 19S (m)');norte_escala(ax,1000)
    fig.text(.5,.005,'Ubicación OSM referencial. Líneas punteadas vinculan localidades; no son rutas aprobadas ni postes.',ha='center',fontsize=8)
    guardar(fig,exp,'corredor-r03')
    s=series['ARNOVIC'];sm=series['GR2M'];dates=s['dates']
    fig,(ax,ax2)=plt.subplots(2,1,figsize=(9,6.8),gridspec_kw={'height_ratios':[1.1,1]})
    ax.plot(dates,s['q'],color=BLUE,lw=.45)
    ax.set_ylabel('Q estimado (m³/s)');ax.set_title('Serie diaria transpuesta de estudio, 1981–2025')
    ax.grid(alpha=.2);ax.set_ylim(bottom=0)
    months=np.arange(1,13)
    md=[s['q'][s['months']==i].mean() for i in months]
    mm=[sm['q'][sm['months']==i].mean() for i in months]
    ax2.bar(months-.18,md,width=.36,color=BLUE,label='Media mensual de ARNOVIC diario')
    ax2.bar(months+.18,mm,width=.36,color=ORANGE,label='GR2M mensual')
    ax2.set_xticks(months,['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'])
    ax2.set_ylabel('Q medio estimado (m³/s)');ax2.grid(axis='y',alpha=.2);ax2.legend(loc='upper right')
    fig.tight_layout();guardar(fig,exp,'caudales-r03')
    fig,ax=plt.subplots(figsize=(9,5.4))
    for values,label,col in [(s['q'],'Natural estimado',BLUE),(s['usable'],'Tras reservas de estudio',GREEN)]:
        desc=np.sort(values)[::-1];percent=np.arange(1,len(desc)+1)/(len(desc)+1)*100
        ax.plot(percent,desc,label=label,color=col,lw=1.4)
    ax.axhline(h['q_diseno_m3s'],ls='--',color=RED,label='Q máximo hidráulico de diseño')
    ax.set_yscale('symlog',linthresh=.1);ax.set_xlim(0,100);ax.set_ylim(bottom=0)
    ax.set_xlabel('Excedencia empírica (%)');ax.set_ylabel('Q estimado (m³/s)')
    ax.set_title('Curva de duración de datos diarios simulados y transpuestos')
    ax.legend();ax.grid(alpha=.25);fig.tight_layout();guardar(fig,exp,'duracion-r03')
    fig,(ax,ax2)=plt.subplots(2,1,figsize=(9,7.3),gridspec_kw={'height_ratios':[1,1.1]})
    dn=r['demanda'];of=r['oferta']['ARNOVIC'];hours=np.arange(24)
    ax.plot(hours,dn['perfil_kw'],color=RED,lw=2,label='Perfil de demanda supuesto 2026')
    ax.axhline(r['balance_nominal']['p_usuarios_kw'],color=BLUE,ls='--',label='Máximo hidro en usuarios')
    ax.axhline(of['p95_usuarios_kw'],color=ORANGE,ls=':',label='P95 diaria de estudio (sin falla de equipo)')
    ax.plot(hours,dn['perfil_critico_kw'],color=GREEN,lw=1,label='Demanda prioritaria propuesta')
    ax.set_xticks(np.arange(0,24,2));ax.set_ylabel('Potencia (kW)');ax.set_xlabel('Hora (Perú)')
    ax.set_title('La potencia de placa no garantiza el suministro en estiaje');ax.legend(fontsize=8);ax.grid(alpha=.2)
    rows=of['mensual'];eh=np.array([v['energia_servida_mwh'] for v in rows]);days=np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    demand=np.array(days)*dn['energia_diaria_kwh']/1000
    ax2.bar(months,eh,color=BLUE,label='Hidro servida estimada')
    ax2.bar(months,np.maximum(0,demand-eh),bottom=eh,color=ORANGE,label='Déficit que requiere respaldo')
    ax2.set_xticks(months,['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'])
    ax2.set_ylabel('Energía (MWh/mes)');ax2.legend();ax2.grid(axis='y',alpha=.2)
    fig.tight_layout();guardar(fig,exp,'oferta-demanda-r03')
    fig,(ax,ax2)=plt.subplots(2,1,figsize=(9,7.2))
    for close,col in [(0,RED),(1,ORANGE),(4,GRAY),(8,BLUE)]:
        rr=next(t for t in r['transitorios'] if t['estado_pared']=='fin_vida' and t['cierre_s']==close)
        ax.plot(rr['tiempo_s'],np.array(rr['carga_valvula_m'])*.0981,color=col,label=f'Cierre {close:g} s')
        if rr['cavitacion_detectada']:
            ax.plot(rr['tiempo_s'][-1],rr['carga_valvula_m'][-1]*.0981,'x',color=col,ms=7)
    ax.axhline(40,color=GREEN,ls=':',label='PN40 candidata, sin garantía del conjunto')
    ax.set_xlim(0,15);ax.set_ylim(bottom=-1);ax.set_xlabel('Tiempo (s)');ax.set_ylabel('Presión de válvula (bar)')
    ax.set_title('MOC a Q máximo de diseño; se detiene al perder validez monofásica')
    ax.legend(ncol=2);ax.grid(alpha=.2)
    slow=next(t for t in r['transitorios'] if t['estado_pared']=='fin_vida' and t['cierre_s']==8)
    ax2.plot(slow['x_m'],np.array(slow['presion_max_m'])*.0981,color=RED,label='Máximo, cierre 8 s')
    ax2.plot(slow['x_m'],np.array(slow['presion_min_m'])*.0981,color=BLUE,label='Mínimo, cierre 8 s')
    ax2.set_xlabel('Distancia de tubería (m)');ax2.set_ylabel('Presión manométrica (bar)')
    ax2.legend();ax2.grid(alpha=.2);fig.tight_layout();guardar(fig,exp,'transitorio-r03')
    fig,ax=plt.subplots(figsize=(10,5.6))
    capz=3285.;camz=3284.3;cmz=3239.
    ax.plot([0,150],[capz,camz],color=BLUE,lw=3,label='Canal de estudio 150 m')
    ax.plot([150,500],[camz,cmz],color=GREEN,lw=3,label='Tubería: longitud de conducto 350 m')
    ax.scatter([0,150,500],[capz,camz,cmz],color=RED,s=45,zorder=5)
    ax.annotate('Captación / desarenador\nReferencia DEM 3285 m',xy=(0,capz),xytext=(12,20),textcoords='offset points',fontsize=9)
    ax.annotate('Cámara propuesta\n3284.3 m: nivel supuesto',xy=(150,camz),xytext=(50,-25),textcoords='offset points',fontsize=9)
    ax.annotate('Turbina / descarga\nReferencia DEM 3239 m',xy=(500,cmz),xytext=(-170,15),textcoords='offset points',fontsize=9)
    ax.annotate('',xy=(470,camz),xytext=(470,cmz),arrowprops=dict(arrowstyle='<->',color=GRAY))
    ax.text(450,(camz+cmz)/2,f'Hb = {h["salto_bruto_m"]:.1f} m',ha='right',color=GRAY)
    ax.set_xlim(-20,540);ax.set_ylim(3230,3303);ax.set_xlabel('Abscisa de longitud del recorrido (m), no distancia horizontal topográfica')
    ax.set_ylabel('Referencia de elevación (m)');ax.set_title('Perfil hidráulico académico, con cotas de mapa e hipótesis diferenciadas')
    ax.legend(loc='lower left');ax.grid(alpha=.2);fig.tight_layout();guardar(fig,exp,'perfil-hidraulico-r03')
    fig,ax=diagram_canvas((11,4.5))
    for x,label in [(0,'Derivación\nQmáx 1.90 m³/s'),(2.45,'Desarenador\n2 cámaras 29×4 m'),(4.9,'Canal\n150 m, b1.60 m'),(7.35,'Cámara de carga\n8×5 m'),(9.8,'Tubería\nDi1000, L350 m')]:
        box(ax,x,4.1,2.05,1.45,label)
        if x>0:connect(ax,[(x-.4,4.82),(x,4.82)],arrow=True)
    box(ax,9.8,1.3,2.05,1.45,'Casa de máquinas\n3×200 kW')
    connect(ax,[(10.82,4.1),(10.82,2.75)],arrow=True)
    box(ax,6.2,1.3,2.1,1.45,'Restitución\nSin uso consuntivo')
    connect(ax,[(9.8,2.03),(8.3,2.03)],arrow=True)
    connect(ax,[(1,4.1),(1,2.03),(6.2,2.03)],color=GREEN,arrow=True)
    ax.text(3.3,2.3,'Reserva ecológica y remanente en cauce',fontsize=9,ha='center',color=GREEN)
    ax.text(0,.35,'Esquema funcional sin escala. La crecida del río se estudia por separado del caudal de generación.',fontsize=9)
    guardar(fig,exp,'obras-r03')
    # Planta de sala y equipos: dimensiones de propuesta, ninguna coordenada de campo.
    fig,ax=plt.subplots(figsize=(11,5.8));ax.set_xlim(-1,38);ax.set_ylim(-1,15);ax.set_aspect('equal')
    ax.add_patch(Rectangle((0,0),20,12,fill=False,ec=GRAY,lw=2))
    for n,x in enumerate([3,9,15],1):
        ax.add_patch(Rectangle((x-1.4,3.5),2.8,2,ec=BLUE,fc='#e6f0f5'))
        ax.text(x,4.5,f'T{n}\nBanki',ha='center',va='center',fontsize=8)
        ax.add_patch(Rectangle((x-1.4,6.1),2.8,1.9,ec=BLUE,fc='white'))
        ax.text(x,7.1,f'G{n}\n200 kW / 250 kVA',ha='center',va='center',fontsize=8)
        ax.plot([x,x],[5.5,6.1],color=GRAY,lw=2)
        ax.plot([x,x],[1.7,3.5],color=BLUE,lw=1.5)
    ax.plot([1,18],[1.7,1.7],color=BLUE,lw=3);ax.text(10,.8,'Colector de presión y válvulas de grupo',ha='center',fontsize=8)
    ax.add_patch(Rectangle((1,10),17,1,ec=RED,fc='white'));ax.text(9.5,10.5,'Maniobra / protección / regulación / CC',ha='center',fontsize=8)
    ax.add_patch(Rectangle((1,8.5),17,1.5,ec=ORANGE,fc='none',ls='--'));ax.text(9.5,9.15,'Pasillo frontal de trabajo 1.50 m',ha='center',fontsize=8,color=ORANGE)
    for x in [0,20]:ax.annotate('Salida',xy=(x,8.5),xytext=(x+(-.6 if x==0 else .6),13),ha='center',fontsize=8,arrowprops=dict(arrowstyle='->',color=GRAY))
    ax.annotate('',xy=(20,-.5),xytext=(0,-.5),arrowprops=dict(arrowstyle='<->',color=GRAY));ax.text(10,-.9,'20.00 m',ha='center',fontsize=9)
    ax.annotate('',xy=(-.5,12),xytext=(-.5,0),arrowprops=dict(arrowstyle='<->',color=GRAY));ax.text(-.7,6,'12.00 m',rotation=90,ha='center',va='center',fontsize=9)
    ax.add_patch(Rectangle((23,7),10,5,ec=GRAY,fc='none',ls='--'))
    ax.text(28,9.5,'Patio exterior cercado\nT1 800 kVA y celdas 10 kV\nDimensiones de patio por confirmar',ha='center',va='center',fontsize=9)
    for i,x in enumerate([23,28,33],1):
        ax.add_patch(Rectangle((x,1),4,3.5,ec=ORANGE,fc='white'))
        ax.text(x+2,2.75,f'B{i}\nDiésel\n200 kW',ha='center',va='center',fontsize=8)
    ax.text(29.5,5.4,'Respaldo exterior: ventilación, ruido y combustible\nsegún fabricante y estudio ambiental',ha='center',fontsize=8)
    ax.set_xlabel('Coordenada relativa X de la propuesta (m)');ax.set_ylabel('Coordenada relativa Y (m)')
    ax.set_title('Disposición académica de casa de máquinas; equipos y emplazamiento por confirmar')
    ax.grid(alpha=.12);fig.tight_layout();guardar(fig,exp,'casa-maquinas-r03')
    fig,ax=diagram_canvas((12.2,7.4))
    # Diagrama unifilar: potencias agregadas, sin representar una fuente SEIN.
    box(ax,.2,4.95,2.2,1.35,'G1–G3 síncronos\n3×200 kW / 250 kVA\n380 V / 60 Hz',fontsize=9)
    box(ax,.2,2.7,2.2,1.35,'B1–B3 respaldo\n3×200 kW\n750 kVA total',ORANGE,9)
    connect(ax,[(2.4,5.62),(3.3,5.62),(3.3,4.4)])
    connect(ax,[(2.4,3.37),(3.3,3.37),(3.3,4.4)],ORANGE)
    ax.plot([3.3,5.4],[4.4,4.4],lw=3,color=BLUE)
    ax.text(4.4,4.85,'Barra 380 V\nPtotal ≤ 600 kW',ha='center',fontsize=9)
    box(ax,5.7,3.68,2.4,1.45,'52T + T1 800 kVA\n0.38 → 10 kV\nATΔ / BTy(n)',fontsize=9)
    connect(ax,[(5.4,4.4),(5.7,4.4)])
    box(ax,8.55,3.68,2.95,1.45,'Celda MT + red aislada\n10 kV, AAAC95\n8 km indicativos',fontsize=9)
    connect(ax,[(8.1,4.4),(8.55,4.4)])
    box(ax,8.55,.75,2.95,1.45,'6 SED: 730 kVA total\n380/220 V\nLimbani + Huancasayani',fontsize=9)
    connect(ax,[(10.0,3.68),(10.0,2.2)],arrow=True)
    box(ax,3.2,.75,3.5,1.45,'TSA20 kVA, aislador 380/380-220 V\nCC24 V y auxiliares\nN de utilización independiente',fontsize=8)
    connect(ax,[(4.4,4.4),(4.4,2.2)])
    ax.text(.2,1.3,'Neutros G: NGR\nMT: ZT + NGR\nSED: neutro de BT',fontsize=8,color=GREEN)
    ax.text(.2,6.65,'Esquema unifilar funcional, sin escala. Transformador definido desde AT, sin conexión inicial al SEIN.',fontsize=9)
    ax.text(.2,.15,'52G/52B con sincronismo entre unidades. Protección diferencial, tierra y 51V según estudio. No son ajustes aprobados.',fontsize=8)
    guardar(fig,exp,'unifilar-r03')
    fig,ax=plt.subplots(figsize=(10,5.7));ax.set_xlim(-1,34);ax.set_ylim(-2.2,14);ax.set_aspect('equal')
    for x in np.arange(0,20.01,4):ax.plot([x,x],[0,12],color=GREEN,lw=1)
    for y in np.arange(0,12.01,4):ax.plot([0,20],[y,y],color=GREEN,lw=1)
    rod_points=[(0,0),(10,0),(20,0),(20,6),(20,12),(10,12),(0,12),(0,6)]
    for pnt in rod_points:ax.plot(*pnt,'o',color=GREEN,ms=5)
    ax.text(10,13,'Malla conceptual 20×12 m, retícula 4 m',ha='center',fontsize=10)
    ax.text(10,-1.9,'Cu50 mm² propuesto; 152 m de malla + conexiones\n8 varillas de 2.4 m. Resistencia y potenciales por verificar.',ha='center',fontsize=9)
    labels=[('Neutros de generación','NGR propuesto\nSin puente sólido a PE'),('Neutro de servicios','TSA de aislamiento\nN–PE en origen definido'),('Neutro de distribución','SED con BT aterrada\nNo unir PEN a N de generación')]
    for y,(head,label) in zip([10,6.2,2.4],labels):
        ax.text(25,y+1.5,head,fontsize=9,fontweight='bold',ha='center',color=BLUE)
        ax.text(25,y,label,fontsize=8.5,ha='center',va='center')
    ax.axis('off');guardar(fig,exp,'puesta-tierra-r03')
    fig,ax=diagram_canvas((11,5.4))
    box(ax,.15,4.0,3.1,1.6,'Variación de carga\nMedición P / f\nBarra aislada de 60 Hz')
    box(ax,4.4,4.0,3.1,1.6,'ELC + balasto por grupo\nRespuesta rápida propuesta\nAbsorción transitoria')
    box(ax,8.8,4.0,3.1,1.6,'Gobernador hidráulico\nAjusta caudal lentamente\nCierre de estudio 8 s')
    connect(ax,[(3.25,4.8),(4.4,4.8)],arrow=True);connect(ax,[(7.5,4.8),(8.8,4.8)],arrow=True)
    box(ax,.15,.85,3.1,1.6,'AVR / reparto de Q\nRegulación de tensión\nLímites de excitación',GREEN)
    box(ax,4.4,.85,3.1,1.6,'Un líder de frecuencia\nOtros grupos en reparto\nSin dos lazos isócronos rígidos',GREEN)
    box(ax,8.8,.85,3.1,1.6,'Disparo independiente\nSobrevelocidad / 87G / 64G\nParada manual accesible',RED)
    ax.text(.15,6.2,'Regulación de un sistema aislado: frecuencia, tensión y agua se coordinan',fontsize=11,fontweight='bold',color=BLUE)
    ax.text(.15,.2,'Esquema funcional sin escala. Inercia, dinámica, ajustes y rechazo total requieren curvas y pruebas de fabricante.',fontsize=8)
    guardar(fig,exp,'regulacion-r03')
    p=r['presupuesto'];codes=['CV','TF','MQ','EC','RD']
    labels=['Obras civiles','Tubería y válvulas','Grupos y respaldo','Eléctrico central','Distribución']
    totals=[sum(x['parcial_pen'] for x in p['partidas'] if x['codigo'].startswith(code))/1e6 for code in codes]
    fig,ax=plt.subplots(figsize=(8.8,4.9));bars=ax.barh(labels,totals,color=[BLUE,GRAY,ORANGE,GREEN,BLUE])
    for bar,value in zip(bars,totals):ax.text(value+.04,bar.get_y()+bar.get_height()/2,f'{value:.2f}',va='center',fontsize=9)
    ax.set_xlabel('Costo directo estimado (S/ millones)');ax.set_xlim(0,max(totals)*1.25)
    ax.set_title('Costos por componente: precios estimados, sin ofertas de suministro')
    ax.grid(axis='x',alpha=.2);fig.tight_layout();guardar(fig,exp,'costos-r03')
