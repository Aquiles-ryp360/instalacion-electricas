"""Plano de ubicación a partir de límites oficiales IGN y eje académico LP-R02."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon, Rectangle
from matplotlib.ticker import FuncFormatter, MaxNLocator
from pyproj import Transformer
from shapely.geometry import shape, Point, LineString, box
from shapely.ops import transform

P=Path(__file__).resolve().parents[2];ROOT=P.parents[1]
FUENTES=ROOT/'recursos/linea-primaria-limbani/2026-10-19/ubicacion-ign'
AZUL='#254D73';ROJO='#C34531';GRIS='#DCE4EA';TINTA='#263540'


def cargar():
    procedencia=json.loads((FUENTES/'procedencia.json').read_text())
    for f in procedencia:
        assert hashlib.sha256((FUENTES/f['nombre']).read_bytes()).hexdigest()==f['sha256']
    datos={n:json.loads((FUENTES/(n+'.geojson')).read_text())['features']
           for n in ['departamentos','provincias-puno','distritos-sandia']}
    # El servicio incluye una entidad adicional sin nombre/código. Se conserva
    # en el GeoJSON original y sólo se dibujan las 25 entidades identificadas.
    datos['departamentos']=[f for f in datos['departamentos'] if f['properties']['CCDD']]
    assert len(datos['departamentos'])==25 and len(datos['provincias-puno'])==13 and len(datos['distritos-sandia'])==10
    return datos


def poligonos(ax,g,**kw):
    partes=list(g.geoms) if hasattr(g,'geoms') else [g]
    for q in partes:
        if q.geom_type!='Polygon':continue
        ax.add_patch(PatchPolygon(np.asarray(q.exterior.coords),closed=True,**kw))


def marco(ax,titulo):
    ax.set_title(titulo,loc='left',fontsize=10,fontweight='bold',color=AZUL,pad=9)
    ax.set_facecolor('#F5F9FC');ax.tick_params(labelsize=6,color='#CCD6DD')
    for spine in ax.spines.values():spine.set_edgecolor('#B7C6D0')
    ax.grid(color='#DCE5EC',linewidth=.4,zorder=0);ax.set_axisbelow(True)
    ax.annotate('N',xy=(.94,.88),xytext=(.94,.75),xycoords='axes fraction',
                ha='center',fontsize=8,color=AZUL,arrowprops=dict(arrowstyle='-|>',color=AZUL,lw=1))


def limites(ax,g,margen=.06):
    x0,y0,x1,y1=g.bounds;dx=x1-x0;dy=y1-y0
    ax.set_xlim(x0-dx*margen,x1+dx*margen);ax.set_ylim(y0-dy*margen,y1+dy*margen)
    ax.set_aspect('equal',adjustable='box')


def escala(ax,metros):
    x0,x1=ax.get_xlim();y0,y1=ax.get_ylim();x=x0+.05*(x1-x0);y=y0+.07*(y1-y0)
    ax.plot([x,x+metros],[y,y],color=TINTA,lw=2)
    for xx in [x,x+metros/2,x+metros]:ax.plot([xx,xx],[y-(y1-y0)*.015,y+(y1-y0)*.015],color=TINTA,lw=.8)
    ax.text(x+metros/2,y+(y1-y0)*.025,f'{metros/1000:g} km',ha='center',fontsize=7,color=TINTA,
            bbox=dict(facecolor='white',edgecolor='none',alpha=.8,pad=1))


def generar(b):
    b=Path(b);salida=b/'ubicacion';salida.mkdir(exist_ok=True)
    datos=cargar();r=json.loads((P/'revisiones/lp-r02/03-calculos/resultados.json').read_text())
    xy=[(p['e'],p['n']) for p in r['postes']];eje=LineString(xy)
    inv=Transformer.from_crs(32719,4326,always_xy=True);directa=Transformer.from_crs(4326,32719,always_xy=True)
    lonlat=[inv.transform(*q) for q in xy]
    dep=next(f for f in datos['departamentos'] if f['properties']['NOMBDEP'].upper()=='PUNO')
    prov=next(f for f in datos['provincias-puno'] if f['properties']['NOMBPROV'].upper()=='SANDIA')
    dist=next(f for f in datos['distritos-sandia'] if f['properties']['UBIGEO']=='211203')
    gd,gp,gl=map(lambda f:shape(f['geometry']),[dep,prov,dist])
    distritos=[]
    for f in datos['distritos-sandia']:
        g=transform(directa.transform,shape(f['geometry']))
        longitud=eje.intersection(g).length
        if longitud>1:distritos.append(dict(distrito=f['properties']['NOMBDIST'],longitud_eje_interseccion_m=longitud))
    assert gl.covers(Point(lonlat[0])) and gl.covers(Point(lonlat[-1])), 'Revisar la ubicación distrital del corredor.'
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
    fig=plt.figure(figsize=(420/25.4,297/25.4),facecolor='white')
    fig.text(.035,.955,'UBICACIÓN POLÍTICA Y GEOGRÁFICA',fontsize=20,fontweight='bold',color=AZUL)
    fig.text(.035,.924,'Línea primaria Limbani–Huancasayani  |  Sandia · Puno · Perú  |  Instalaciones Eléctricas II',fontsize=11,color=TINTA)
    a=fig.add_axes([.035,.49,.21,.37]);marco(a,'A. PERÚ / DEPARTAMENTO DE PUNO')
    for f in datos['departamentos']:
        g=shape(f['geometry']);sel=f['properties']['NOMBDEP'].upper()=='PUNO'
        poligonos(a,g,facecolor=AZUL if sel else GRIS,edgecolor='white',linewidth=.45,zorder=2)
    cajas=[shape(f['geometry']).bounds for f in datos['departamentos']]
    # Para encuadrar basta la envolvente. No se fuerza unión/reparación de la
    # topología de los polígonos simplificados que entrega el servicio.
    nacional=box(min(q[0] for q in cajas),min(q[1] for q in cajas),max(q[2] for q in cajas),max(q[3] for q in cajas))
    limites(a,nacional)
    pp=gd.representative_point();a.annotate('PUNO',xy=(pp.x,pp.y),xytext=(-77,-17),fontsize=9,fontweight='bold',color=AZUL,
                   arrowprops=dict(arrowstyle='->',color=AZUL,lw=.8))
    a.text(-80,-12,'OCÉANO\nPACÍFICO',fontsize=7,color='#6D879B',ha='center')
    a.xaxis.set_major_locator(MaxNLocator(4));a.yaxis.set_major_locator(MaxNLocator(5))
    a.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{abs(v):.0f}° O'))
    a.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{abs(v):.0f}° '+('S' if v<0 else 'N')))

    a=fig.add_axes([.285,.49,.24,.37]);marco(a,'B. PUNO / PROVINCIA DE SANDIA')
    for f in datos['provincias-puno']:
        g=transform(directa.transform,shape(f['geometry']));sel=f['properties']['NOMBPROV'].upper()=='SANDIA'
        poligonos(a,g,facecolor=AZUL if sel else GRIS,edgecolor='white',linewidth=.55,zorder=2)
        q=g.representative_point();a.text(q.x,q.y,f['properties']['NOMBPROV'].title().replace('San Antonio De Putina','S. A. de Putina'),
                    ha='center',va='center',fontsize=5.5,color='white' if sel else TINTA,zorder=3)
    limites(a,transform(directa.transform,gd));a.ticklabel_format(style='plain',useOffset=False)
    a.xaxis.set_major_locator(MaxNLocator(3));a.yaxis.set_major_locator(MaxNLocator(4));escala(a,50000)
    a.set_xlabel('UTM 19 S · m',fontsize=6)

    a=fig.add_axes([.575,.49,.39,.37]);marco(a,'C. SANDIA / DISTRITO DE LIMBANI')
    for f in datos['distritos-sandia']:
        g=transform(directa.transform,shape(f['geometry']));sel=f['properties']['UBIGEO']=='211203'
        poligonos(a,g,facecolor=AZUL if sel else GRIS,edgecolor='white',linewidth=.7,zorder=2)
        q=g.representative_point();a.text(q.x,q.y,f['properties']['NOMBDIST'].title().replace('San Pedro De Putina Punco','San Pedro de\nPutina Punco'),
               ha='center',va='center',fontsize=6.5,fontweight='bold' if sel else 'normal',color='white' if sel else TINTA,zorder=3)
    a.plot(*eje.xy,color=ROJO,lw=2,zorder=5)
    limites(a,transform(directa.transform,gp));a.ticklabel_format(style='plain',useOffset=False)
    a.xaxis.set_major_locator(MaxNLocator(4));a.yaxis.set_major_locator(MaxNLocator(4));escala(a,20000)
    a.set_xlabel('UTM 19 S · m',fontsize=6)

    a=fig.add_axes([.05,.185,.56,.23]);marco(a,'D. CORREDOR DE GABINETE LIMBANI–HUANCASAYANI')
    x0,y0,x1,y1=eje.bounds
    alto=y1-y0+2000;ancho=max(x1-x0+2400,alto*(.56*420)/(.23*297));centro=(x0+x1)/2
    recorte=box(centro-ancho/2,y0-1000,centro+ancho/2,y1+1000)
    for f in datos['distritos-sandia']:
        g=transform(directa.transform,shape(f['geometry'])).intersection(recorte)
        if not g.is_empty:
            poligonos(a,g,facecolor='#EAF2F7',edgecolor='#A4B5C2',linewidth=.8,zorder=1)
            q=g.representative_point()
            a.text(q.x,q.y,f['properties']['NOMBDIST'].title(),fontsize=7,color='#7A8E9B',ha='center',zorder=2)
    a.plot(*eje.xy,color=ROJO,lw=1.5,zorder=4,label='Eje académico LP-R02')
    a.scatter(*np.array(xy).T,s=4,color=AZUL,zorder=5,label='111 apoyos')
    for n,q in [(0,'T1 / P001\nSalida de estudio'),(-1,'T2 / P111\nLlegada de estudio')]:
        x,y=xy[n];a.scatter([x],[y],s=25,color=ROJO,zorder=6)
        a.annotate(q,(x,y),xytext=(10,-23 if n==0 else 10),textcoords='offset points',fontsize=7,
                   color=AZUL,bbox=dict(facecolor='white',edgecolor='#CCD8E0',boxstyle='round,pad=.3'))
    limites(a,recorte,margen=0);escala(a,1000);a.ticklabel_format(style='plain',useOffset=False)
    a.xaxis.set_major_locator(MaxNLocator(5));a.yaxis.set_major_locator(MaxNLocator(3))
    a.set_xlabel('Este UTM · m',fontsize=7);a.set_ylabel('Norte UTM · m',fontsize=7)
    a.legend(loc='upper left',fontsize=6,framealpha=.9)

    ax=fig.add_axes([.655,.185,.31,.23]);ax.axis('off')
    tabla=[['País / departamento','Perú / Puno'],['Provincia / distrito','Sandia / Limbani'],['Ubigeo distrital','211203'],
           ['Referencia local','WGS 84 · UTM 19 S · EPSG:32719'],['Inicio P001',f'E {xy[0][0]:,.3f} / N {xy[0][1]:,.3f} m'],
           ['Final P111',f'E {xy[-1][0]:,.3f} / N {xy[-1][1]:,.3f} m'],['Eje horizontal',f'{r["longitud_horizontal_m"]:,.3f} m · 110 vanos'],
           ['Latitud / longitud inicial',f'{lonlat[0][1]:.6f}° / {lonlat[0][0]:.6f}°'],['Fuente administrativa','IGN · límites referenciales'],['Eje / emplazamientos','Modelo académico LP-R02, sin replanteo']]
    t=ax.table(cellText=tabla,colWidths=[.38,.62],bbox=[0,0,1,1]);t.auto_set_font_size(False);t.set_fontsize(7)
    for (i,j),cell in t.get_celld().items():
        cell.set_edgecolor('#CAD6DF');cell.set_linewidth(.4);cell.set_text_props(ha='left',color=TINTA)
        cell.set_facecolor('#EAF2F7' if j==0 else 'white')
    fig.text(.035,.123,'FUENTES: Instituto Geográfico Nacional, servicio DATOS_GEOESPACIALES/LÍMITES, capas 3, 4 y 5. Consulta: 19/10/2026.',fontsize=8,color=TINTA)
    fig.text(.035,.104,'Elaboración del plano: proyecto académico Aquiles · Límites referenciales; no establece demarcación legal ni certifica ubicación de equipos.',fontsize=8,color=TINTA)
    fig.text(.035,.085,'Mapas B, C y D: WGS 84 / UTM 19 S. Mapa A: coordenadas geográficas WGS 84. Las escalas gráficas corresponden a cada marco.',fontsize=8,color=TINTA)
    fig.text(.035,.045,'UNIVERSIDAD NACIONAL DEL ALTIPLANO · AQU ILES TAYLOR RAMOS YAPO · 227368'.replace('AQU ILES','AQUILES'),fontsize=8,color=AZUL)
    fig.text(.965,.045,'UB-01  |  UBICACIÓN  |  A3  |  M01',ha='right',fontsize=10,fontweight='bold',color=AZUL)
    for ext in ['pdf','svg','png']:fig.savefig(salida/('Plano_Ubicacion.'+ext),dpi=180)
    plt.close(fig)
    informe=dict(fuente='IGN, límites referenciales',pais='Perú',departamento='Puno',provincia='Sandia',distrito='Limbani',ubigeo='211203',
                 epsg_local=32719,epsg_nacional=4326,coordenadas_inicio=list(xy[0]),coordenadas_final=list(xy[-1]),
                 inicio_lon_lat=lonlat[0],final_lon_lat=lonlat[-1],intersecciones_distritales=distritos,
                 contencion_extremos_limbani=True,aprobacion_topografica=False,
                 sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in salida.glob('Plano_Ubicacion.*')})
    (salida/'validacion-ubicacion.json').write_text(json.dumps(informe,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Plano UB-01 generado con límites IGN y verificación espacial de los extremos.',flush=True)
    return salida


if __name__=='__main__':
    import sys
    generar(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build'/P.name/'metrados-m01')
