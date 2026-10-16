"""Lámina geográfica de revisión: PDF/SVG, DXF UTM y KMZ con geometría común.

No define obras cuya posición no se conoce ni modifica el diseño hidráulico R03.
El sombreado y las curvas se calculan a partir del HGT público conservado.
"""
from pathlib import Path
import gzip
import hashlib
import json
import math
import sqlite3
import xml.etree.ElementTree as ET
import zipfile

import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import numpy as np
from pyproj import Transformer
from shapely.geometry import box, mapping, Point
from shapely.validation import make_valid
from figuras_r03 import geom_gpkg

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
O = R / 'build' / P.name / 'r04-emplazamiento'
BLUE = '#17647a'
GREEN = '#277c65'
RED = '#a53639'
GRAY = '#52616a'
MAPBOX = (424700., 8434700., 426700., 8436900.)


def obtener_datos():
    fuente = R / 'referencias/local/topografia-limbani/S15W070-mapzen.hgt.gz'
    original = Path('C:/Users/51949/Downloads/Catastro_Limbani/qgis/Catastro-Limbani.gpkg')
    con = sqlite3.connect('file:' + original.resolve().as_posix() + '?mode=ro&immutable=1', uri=True)
    referencias = con.execute('SELECT DISTINCT srs_id FROM gpkg_geometry_columns').fetchall()
    con.close()
    if referencias != [(32719,)]:
        raise ValueError(f'Comprobar CRS de la base antes de superponer: {referencias}')
    datos = geom_gpkg(original)
    ventana = box(*MAPBOX)
    reparadas = sum(not g.is_valid for v in datos.values() for g in v)
    # Reparar únicamente la copia geométrica de visualización; nunca el GeoPackage.
    catastro = {}
    for nombre, valores in datos.items():
        catastro[nombre] = []
        for geom in valores:
            copia = make_valid(geom) if not geom.is_valid else geom
            if copia.intersects(ventana):
                catastro[nombre].append(copia.intersection(ventana))
    dem = np.frombuffer(gzip.decompress(fuente.read_bytes()), dtype='>i2').reshape(3601, 3601)
    x = np.linspace(MAPBOX[0], MAPBOX[2], 101)
    y = np.linspace(MAPBOX[1], MAPBOX[3], 111)
    xx, yy = np.meshgrid(x, y)
    t = Transformer.from_crs(32719, 4326, always_xy=True)
    lon, lat = t.transform(xx, yy)
    rr = (-14-lat)*3600
    cc = (lon+70)*3600
    i, j = np.floor(rr).astype(int), np.floor(cc).astype(int)
    u, v = rr-i, cc-j
    if np.any(i < 0) or np.any(j < 0) or np.any(i >= 3600) or np.any(j >= 3600):
        raise ValueError('Ventana fuera del DEM')
    for di, dj in [(0,0),(0,1),(1,0),(1,1)]:
        if np.any(dem[i+di,j+dj] <= -32000):
            raise ValueError('DEM contiene vacíos en la ventana')
    zz = (dem[i,j]*(1-u)*(1-v)+dem[i+1,j]*u*(1-v)+
          dem[i,j+1]*(1-u)*v+dem[i+1,j+1]*u*v)
    geo = json.loads((P/'datos/topografia-r03.json').read_text(encoding='utf-8'))
    cap = geo['puntos']['captacion_propuesta']
    puntos = [dict(id='CAP-P', e=cap['e_original_m'], n=cap['n_original_m'], color=GREEN,
                   descripcion='Captación propuesta de estudio; no identificada en campo', fuente='R03, topografia-r03.json'),
              dict(id='CM-A', e=425580., n=8436580., color=GRAY,
                   descripcion='Casa de máquinas candidata A; no confirmada', fuente='Antecedente de memoria de línea'),
              dict(id='CM-B', e=425715., n=8436650., color=RED,
                   descripcion='Casa de máquinas candidata B; no confirmada', fuente='Antecedente CAD recibido')]
    return xx, yy, zz, catastro, puntos, fuente, original, reparadas


def lineas(geom):
    if geom.is_empty:
        return
    if geom.geom_type == 'Polygon':
        yield list(geom.exterior.coords)
        for anillo in geom.interiors:
            yield list(anillo.coords)
    elif hasattr(geom, 'geoms'):
        for parte in geom.geoms:
            yield from lineas(parte)
    elif geom.geom_type in {'LineString', 'LinearRing'}:
        yield list(geom.coords)


def main():
    O.mkdir(parents=True, exist_ok=True)
    xx, yy, zz, catastro, puntos, fuente, original, reparadas = obtener_datos()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig = plt.figure(figsize=(420/25.4, 297/25.4), facecolor='white')
    # Rectángulo de mapa exactamente 200 x 220 mm y extensión 2000 x 2200 m.
    # Escala física 1:10000; no usar bbox_inches='tight' al guardar.
    ax = fig.add_axes([20/420, 53/297, 200/420, 220/297])
    sombra = np.flipud(LightSource(azdeg=315, altdeg=42).hillshade(np.flipud(zz), vert_exag=1, dx=20, dy=20))
    ax.imshow(sombra, extent=(MAPBOX[0],MAPBOX[2],MAPBOX[1],MAPBOX[3]), origin='lower', cmap='gray', alpha=.46, vmin=0, vmax=1)
    niveles = np.arange(math.floor(zz.min()/20)*20, math.ceil(zz.max()/20)*20+1, 20)
    contornos = ax.contour(xx, yy, zz, levels=niveles, colors='#8d8170', linewidths=.42, alpha=.82)
    principales = ax.contour(xx, yy, zz, levels=[z for z in niveles if int(z)%100 == 0], colors='#6c6254', linewidths=.9)
    ax.clabel(principales, inline=True, fontsize=6.5, fmt='%d', inline_spacing=5)
    for nombre, geoms in catastro.items():
        color = BLUE if 'Rios' in nombre else ('#b18d56' if nombre == 'Casas' else '#8f989e')
        for geom in geoms:
            for coords in lineas(geom):
                a = np.asarray(coords)
                ax.plot(a[:,0], a[:,1], color=color, lw=1.35 if 'Rios' in nombre else .58, zorder=4)
    for pt in puntos:
        ax.plot(pt['e'], pt['n'], marker='^' if pt['id']=='CAP-P' else 's', markersize=7,
                mec='white', mew=.7, color=pt['color'], zorder=9)
        desplazamiento = {'CAP-P':(-8,-24), 'CM-A':(-48,-17), 'CM-B':(11,8)}[pt['id']]
        ax.annotate(pt['id'], (pt['e'],pt['n']), xytext=desplazamiento, textcoords='offset points',
                    fontsize=8.5, fontweight='bold', zorder=10,
                    bbox=dict(facecolor='white',edgecolor='none',alpha=.9,pad=1.4),
                    arrowprops=dict(arrowstyle='-',lw=.7,color=pt['color']))
    a,b = puntos[1:]
    ax.plot([a['e'],b['e']],[a['n'],b['n']],ls='--',color=RED,lw=1,zorder=6)
    distancia = math.hypot(a['e']-b['e'],a['n']-b['n'])
    ax.set_xlim(MAPBOX[0],MAPBOX[2]);ax.set_ylim(MAPBOX[1],MAPBOX[3]);ax.set_aspect('equal')
    ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=7,length=3)
    ax.set_xticks(np.arange(424800,426701,400));ax.set_yticks(np.arange(8434800,8436901,400))
    ax.grid(color='white',lw=.65,alpha=.75)
    ax.set_xlabel('Este UTM 19S (m)',fontsize=8);ax.set_ylabel('Norte UTM 19S (m)',fontsize=8)
    ax.annotate('N\nUTM', xy=(426500,8436720), xytext=(426500,8436410),ha='center',fontsize=8,
                arrowprops=dict(arrowstyle='-|>',lw=1.2,color='#1d2c33'),
                bbox=dict(facecolor='white',edgecolor='none',alpha=.8,pad=2))
    ax.plot([424850,425050,425250],[8434850]*3,color='black',lw=2)
    for value in (0,200,400):
        ax.text(424850+value,8434785,str(value),fontsize=7,ha='center',
                bbox=dict(facecolor='white',edgecolor='none',pad=1))
    ax.text(425350,8434832,'m',fontsize=7)

    def ft(x,y,text,size=9,color='#23353f',weight='normal'):
        fig.text(x/420,y/297,text,fontsize=size,color=color,fontweight=weight,va='top')
    def fl(x1,y1,x2,y2,lw=.6):
        fig.add_artist(plt.Line2D([x1/420,x2/420],[y1/297,y2/297],transform=fig.transFigure,color='#344851',lw=lw))
    ft(12,289,'MINICENTRAL LIMBANI',14,weight='bold')
    ft(12,281,'Emplazamiento, relieve y discrepancias de antecedentes',10)
    ft(408,289,'',9)
    fl(10,277,410,277,.9)
    ft(236,270,'REFERENCIAS DE EMPLAZAMIENTO',10,weight='bold')
    ft(236,261,'Punto       Este (m)          Norte (m)',8,weight='bold')
    for k,pt in enumerate(puntos):
        ft(236,252-k*8,f'{pt["id"]:<7}   {pt["e"]:.0f}             {pt["n"]:.0f}',8,color=pt['color'])
    ft(236,224,'WGS84 / UTM zona 19 sur · EPSG:32719',8)
    fl(236,216,407,216)
    ft(236,210,'QUÉ REPRESENTA CADA PUNTO',9,weight='bold')
    ft(236,200,'CAP-P  Propuesta cartográfica de captación.\n             No corresponde a una obra levantada.',8)
    ft(236,184,'CM-A   Posición de la memoria de línea.\nCM-B   Posición del antecedente CAD.',8)
    ft(236,167,f'Distancia CM-A ↔ CM-B: {distancia:.1f} m',10,color=RED,weight='bold')
    ft(236,157,'La línea discontinua compara posiciones.\nNo representa canal ni tubería.',8)
    fl(236,144,407,144)
    ft(236,138,'LECTURA DEL RELIEVE',9,weight='bold')
    ft(236,128,'Curvas cada 20 m; principales cada 100 m.\nDEM Mapzen / USGS, paso nativo ≈30 m.\nInterpolación de dibujo: 20 m; no añade precisión.\nAlturas del modelo: datum vertical sin confirmar.',8)
    ft(236,103,'Cauce: base catastral aportada.\nHuellas: catastro original, sin padrón de usuarios.\nCoordenadas de cámara y restitución pendientes.',8)
    fl(236,85,407,85)
    ft(236,79,'ALCANCE DE ESTA LÁMINA',9,weight='bold')
    ft(236,69,'Revisión de gabinete. Sin rasante ni traza definitiva.\nEl relieve no acredita salto hidráulico medido.\nNo se fijan obras para forzar una potencia.',8)
    fl(10,38,410,38,.9);fl(10,11,410,11,.9);fl(10,11,10,38);fl(410,11,410,38)
    fl(230,11,230,38);fl(327,11,327,38);fl(372,11,372,38)
    ft(13,34,'PROYECTO ACADÉMICO · CENTRALES HIDROELÉCTRICAS',8,weight='bold')
    ft(13,27,'Aquiles Taylor Ramos Yapo · Estudiante 227368 · Grupo A',8)
    ft(13,20,'Docente: Mg. Ing. Gregorio Meza Marocho',8)
    ft(234,34,'EMPLAZAMIENTO / RELIEVE',8,weight='bold')
    ft(234,26,'Revisión de trabajo R04 · 16/10/2026',8)
    ft(234,19,'No sustituye la entrega R03',7)
    ft(331,34,'ESCALA',7);ft(331,27,'1:10 000',9,weight='bold');ft(331,19,'A3 · 420 × 297 mm',7)
    ft(377,34,'LÁMINA',7);ft(377,27,'UG-02',11,weight='bold');ft(377,19,'En desarrollo',7)
    pdf = O/'Limbani_R04_UG-02_emplazamiento_revision.pdf'
    fig.savefig(pdf, metadata={'Title':'Limbani UG-02: revisión geográfica R04','Author':'Aquiles Taylor Ramos Yapo'})
    fig.savefig(O/'Limbani_R04_UG-02_emplazamiento_revision.svg')
    fig.savefig(O/'Limbani_R04_UG-02_emplazamiento_revision.png',dpi=150)
    segmentos = [(float(z),s) for z,ls in zip(contornos.levels,contornos.allsegs) for s in ls if len(s)>1]
    plt.close(fig)

    # El modelo CAD conserva XY UTM en metros; la presentación se configura en mm.
    doc = ezdxf.new('R2018');doc.units=6
    for nombre,color in [('CURVAS_20M',8),('CURVAS_100M',32),('CAUCE_BASE',5),('CATASTRO_BASE',9),('REFERENCIAS',1),('ROTULO',7)]:
        doc.layers.new(nombre,dxfattribs={'color':color})
    ms=doc.modelspace()
    for z,s in segmentos:
        ms.add_lwpolyline(s.tolist(),dxfattribs={'layer':'CURVAS_100M' if round(z)%100==0 else 'CURVAS_20M','elevation':z})
    for nombre,geoms in catastro.items():
        for geom in geoms:
            for coords in lineas(geom):
                ms.add_lwpolyline([(c[0],c[1]) for c in coords],dxfattribs={'layer':'CAUCE_BASE' if 'Rios' in nombre else 'CATASTRO_BASE'})
    for pt in puntos:
        ms.add_circle((pt['e'],pt['n']),12,dxfattribs={'layer':'REFERENCIAS'})
        ms.add_text(pt['id'],dxfattribs={'height':25,'insert':(pt['e']+20,pt['n']+20),'layer':'REFERENCIAS'})
    doc.layouts.rename('Layout1','UG-02');layout=doc.layouts.get('UG-02')
    layout.page_setup(size=(420,297),margins=(0,0,0,0),units='mm')
    vp=layout.add_viewport(center=(120,163),size=(200,220),view_center_point=((MAPBOX[0]+MAPBOX[2])/2,(MAPBOX[1]+MAPBOX[3])/2),view_height=2200)
    vp.dxf.flags |= 16384
    layout.add_lwpolyline([(10,11),(410,11),(410,38),(10,38)],close=True,dxfattribs={'layer':'ROTULO'})
    for x in [230,327,372]:layout.add_line((x,11),(x,38),dxfattribs={'layer':'ROTULO'})
    for x,y,text,height in [(12,286,'MINICENTRAL LIMBANI - EMPLAZAMIENTO Y RELIEVE',4),
        (13,31,'CENTRALES HIDROELECTRICAS - AQUILES TAYLOR RAMOS YAPO',2.7),
        (13,23,'Estudiante 227368 - Grupo A - Mg. Ing. Gregorio Meza Marocho',2.5),
        (234,31,'REVISION DE TRABAJO R04 - 16/10/2026',2.7),
        (234,22,'No sustituye la entrega R03',2.7),(331,27,'1:10 000 - A3',3),
        (376,27,'UG-02',4)]:
        layout.add_text(text,dxfattribs={'insert':(x,y),'height':height,'layer':'ROTULO'})
    notas='REFERENCIAS UTM 19S (m)\n\n'+ '\n'.join(f'{p["id"]}: E {p["e"]:.0f} / N {p["n"]:.0f}' for p in puntos)
    notas+=f'\n\nCM-A / CM-B: {distancia:.1f} m.\nPosiciones sin confirmar. No son centro del pueblo.\n\nCURVAS: 20 m / principales 100 m.\nDEM Mapzen / USGS ~30 m.\nLa interpolacion no mejora la precision.\nDatum vertical sin confirmar.\n\nCauce y huellas: catastro original.\nCAP-P: propuesta cartografica de estudio.\nCamara y restitucion: ubicacion pendiente.\n\nNo hay traza ni perfil de campo.\nEl DEM no acredita salto hidraulico medido.'
    layout.add_mtext(notas,dxfattribs={'insert':(237,260),'char_height':3,'width':163,'layer':'ROTULO'})
    cad=O/'Limbani_R04_UG-02_emplazamiento_revision.dxf';doc.saveas(cad)
    reopened=ezdxf.readfile(cad);audit=reopened.audit()
    if audit.errors:raise AssertionError(audit.errors)
    centros=[(e.dxf.center.x,e.dxf.center.y) for e in reopened.modelspace().query('CIRCLE[layer=="REFERENCIAS"]')]
    assert len(centros)==len(puntos) and all(min(math.dist((p['e'],p['n']),xy) for xy in centros)<1e-7 for p in puntos)

    # GeoJSON y Google Earth comparten los puntos y contornos del PDF/CAD.
    tr=Transformer.from_crs(32719,4326,always_xy=True)
    features=[dict(type='Feature',geometry=mapping(Point(pt['e'],pt['n'])),properties={k:v for k,v in pt.items() if k!='color'}) for pt in puntos]
    (O/'referencias_emplazamiento_UTM19S.geojson').write_text(json.dumps(dict(type='FeatureCollection',
        crs=dict(type='name',properties=dict(name='urn:ogc:def:crs:EPSG::32719')),features=features),ensure_ascii=False,indent=2),encoding='utf-8')
    ns='http://www.opengis.net/kml/2.2';ET.register_namespace('',ns)
    def el(parent,name,text=None):
        x=ET.SubElement(parent,'{'+ns+'}'+name)
        if text is not None:x.text=str(text)
        return x
    kml=ET.Element('{'+ns+'}kml');d=el(kml,'Document');el(d,'name','Minicentral Limbani - UG-02 / revisión R04')
    el(d,'description','Gabinete. Coordenadas candidatas sin confirmar; curvas DEM, no topografía de campo. No sustituye R03.')
    for ident,color,ancho in [('rio','ff7a6417',2),('huellas','ff568db1',1),('curvas','ff70818d',1)]:
        st=el(d,'Style');st.set('id',ident);ls=el(st,'LineStyle');el(ls,'color',color);el(ls,'width',ancho)
    view=el(d,'LookAt');el(view,'longitude',-69.689);el(view,'latitude',-14.145);el(view,'range',4000);el(view,'tilt',40)
    for pt in puntos:
        f=el(d,'Placemark');el(f,'name',pt['id']);el(f,'description',pt['descripcion']+'; '+pt['fuente']+f'; E={pt["e"]:.1f}, N={pt["n"]:.1f} m; EPSG:32719.')
        st=el(f,'Style');ic=el(st,'IconStyle');rgb=pt['color'].lstrip('#');el(ic,'color','ff'+rgb[4:6]+rgb[2:4]+rgb[0:2]);el(ic,'scale',1.2)
        point=el(f,'Point');el(point,'altitudeMode','clampToGround');lon,lat=tr.transform(pt['e'],pt['n']);el(point,'coordinates',f'{lon:.9f},{lat:.9f},0')
    folder=el(d,'Folder');el(folder,'name','Curvas DEM 20 m / principales 100 m - gabinete');el(folder,'visibility','0')
    for z,s in segmentos:
        f=el(folder,'Placemark');el(f,'name',f'{z:.0f} m (DEM)');el(f,'styleUrl','#curvas');el(f,'description','Cota de modelo, datum vertical sin verificar. Visualización sobre terreno de Google Earth.')
        line=el(f,'LineString');el(line,'tessellate','1');el(line,'altitudeMode','clampToGround')
        lon,lat=tr.transform(s[:,0],s[:,1]);el(line,'coordinates',' '.join(f'{x:.9f},{y:.9f},0' for x,y in zip(lon,lat)))
    for nombre,geoms in catastro.items():
        if 'Rios' not in nombre and nombre!='Casas':continue
        fo=el(d,'Folder');el(fo,'name',nombre+' - catastro recibido');el(fo,'visibility',1 if 'Rios' in nombre else 0)
        for geom in geoms:
            for coords in lineas(geom):
                f=el(fo,'Placemark');el(f,'styleUrl','#rio' if 'Rios' in nombre else '#huellas')
                line=el(f,'LineString');el(line,'tessellate',1);el(line,'altitudeMode','clampToGround')
                valores=[tr.transform(c[0],c[1]) for c in coords];el(line,'coordinates',' '.join(f'{x:.9f},{y:.9f},0' for x,y in valores))
    kmz=O/'Limbani_R04_UG-02_emplazamiento_revision.kmz'
    with zipfile.ZipFile(kmz,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('doc.kml',ET.tostring(kml,encoding='utf-8',xml_declaration=True))
    with zipfile.ZipFile(kmz) as z:
        assert z.testzip() is None
        tree=ET.fromstring(z.read('doc.kml'))
    punto_kml=tree.findall('.//{'+ns+'}Placemark/{'+ns+'}Point/{'+ns+'}coordinates')
    vuelta=Transformer.from_crs(4326,32719,always_xy=True)
    assert len(punto_kml)==len(puntos)
    error_kml=max(math.dist(vuelta.transform(*map(float,k.text.split(',')[:2])),(pt['e'],pt['n'])) for pt,k in zip(puntos,punto_kml))
    assert error_kml<.001
    resultado=dict(estado='Lámina de trabajo revisable, no nueva entrega integral',crs='EPSG:32719',
        pagina_mm=[420,297],escala_pdf=10000,extension_utm_m=list(MAPBOX),
        intervalo_curvas_m=20,principales_m=100,paso_dem_nativo_aprox_m=30,paso_interpolacion_m=20,
        distancia_entre_casas_candidatas_m=distancia,referencias=puntos,
        segmentos_curvas=len(segmentos),niveles_dem=len(niveles),errores_dxf=len(audit.errors),
        geometrias_invalidas_reparadas_solo_para_visualizacion=reparadas,
        diferencia_maxima_kml_utm_m=error_kml,referencias_dxf_reabiertas=len(centros),
        origen_dem=str(fuente.relative_to(R)),dem_sha256=hashlib.sha256(fuente.read_bytes()).hexdigest(),
        catastro_sha256=hashlib.sha256(original.read_bytes()).hexdigest())
    (O/'verificacion-ug02.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(salidas=str(O),segmentos_curvas=len(segmentos),distancia_cm_m=round(distancia,2),errores_dxf=len(audit.errors)),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
