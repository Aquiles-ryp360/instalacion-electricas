"""KMZ autónomo de línea, apoyos, vanos, curvas DEM y recorrido 3D.

No extrae topografía de Google Earth: usa el mismo DEM público de los cálculos.
El modo relativo muestra alturas de estudio sobre el terreno del visor; no
garantiza cotas absolutas ni una catenaria levantada en campo.
"""
from pathlib import Path
import sys,json,math,zipfile,xml.etree.ElementTree as ET
import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString,mapping
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource,Normalize
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[2];R=P.parents[1];D=P/'datos/lp-r01';O=R/'output/linea-primaria-limbani-huancasayani';G=O/'google-earth';B=R/'build'/P.name/'lp-r01'
sys.path.insert(0,str(Path(__file__).parent))
from trazado import elevation
K='http://www.opengis.net/kml/2.2';GX='http://www.google.com/kml/ext/2.2';ET.register_namespace('',K);ET.register_namespace('gx',GX)
def e(parent,tag,value=None,**attrs):
    node=ET.SubElement(parent,'{'+K+'}'+tag,attrs)
    if value is not None:node.text=str(value)
    return node
def gx(parent,tag,value=None):
    node=ET.SubElement(parent,'{'+GX+'}'+tag)
    if value is not None:node.text=str(value)
    return node
def coords(vs):return ' '.join(','.join(f'{n:.9f}' for n in v) for v in vs)
def look(parent,lon,lat,range_=9000,tilt=55,heading=195):
    n=e(parent,'LookAt')
    for t,v in [('longitude',lon),('latitude',lat),('altitude',0),('heading',heading),('tilt',tilt),('range',range_),('altitudeMode','relativeToGround')]:e(n,t,v)
def folder(parent,name,visible=1):
    n=e(parent,'Folder');e(n,'name',name);e(n,'visibility',visible);return n
def line(parent,name,vs,style,description='',mode='clampToGround'):
    n=e(parent,'Placemark');e(n,'name',name)
    if description:e(n,'description',description)
    e(n,'styleUrl','#'+style)
    g=e(n,'LineString');e(g,'tessellate',1 if mode=='clampToGround' else 0);e(g,'altitudeMode',mode);e(g,'coordinates',coords(vs));return n
def point(parent,name,lon,lat,style,description='',alt=0,mode='clampToGround',lod=False):
    n=e(parent,'Placemark');e(n,'name',name);e(n,'description',description);e(n,'styleUrl','#'+style)
    if lod:
        reg=e(n,'Region');bb=e(reg,'LatLonAltBox')
        for t,v in [('north',lat+.0007),('south',lat-.0007),('east',lon+.0007),('west',lon-.0007)]:e(bb,t,v)
        lev=e(reg,'Lod');e(lev,'minLodPixels',30);e(lev,'maxLodPixels',-1)
    g=e(n,'Point');e(g,'altitudeMode',mode);e(g,'coordinates',coords([(lon,lat,alt)]));return n
def table(rows):return '<table>'+''.join('<tr><td><b>'+str(k)+'</b></td><td>'+str(v)+'</td></tr>' for k,v in rows)+'</table>'
def styles(doc):
    for id_,color,width in [('eje','ff3030dd',4),('cable','ff20bfff',2),('poste3d','ffffffff',3),('curva','ff6e9879',1),('principal','ff316647',2),('via','ffaaaaaa',1),('agua','ffffbb55',2),('ret','ff30c0d0',1.5)]:
        s=e(doc,'Style',id=id_);l=e(s,'LineStyle');e(l,'color',color);e(l,'width',width)
    for id_,icon,color,scale in [('poste','files/poste-cac.png','ffffffff',.85),('especial','files/poste-cac.png','ffcc33aa',1.1),('se','files/subestacion.png','ffffffff',1.3)]:
        s=e(doc,'Style',id=id_);n=e(s,'IconStyle');e(n,'color',color);e(n,'scale',scale);e(e(n,'Icon'),'href',icon);e(n,'hotSpot',None,x='.5',y='.5',xunits='fraction',yunits='fraction');lab=e(s,'LabelStyle');e(lab,'scale',.8);ball=e(s,'BalloonStyle');e(ball,'bgColor','fffdfdfd')
    s=e(doc,'Style',id='cota');lab=e(s,'LabelStyle');e(lab,'scale',.7);e(lab,'color','ff316647');e(e(s,'IconStyle'),'scale',0)

def main():
    G.mkdir(exist_ok=True,parents=True);assets=G/'files';assets.mkdir(exist_ok=True)
    a=json.loads((D/'resultados.json').read_text(encoding='utf-8'));ps=a['postes'];ss=a['vanos'];to_ll=Transformer.from_crs(32719,4326,always_xy=True);to_xy=Transformer.from_crs(4326,32719,always_xy=True)
    ll=[to_ll.transform(p['e'],p['n']) for p in ps];west=min(v[0] for v in ll)-.006;east=max(v[0] for v in ll)+.006;north=max(v[1] for v in ll)+.005;south=min(v[1] for v in ll)-.005
    elevation(ps[0]['e'],ps[0]['n']);full=elevation.grid
    r0=max(0,math.floor((-14-north)*3600));r1=min(3600,math.ceil((-14-south)*3600));c0=max(0,math.floor((west+70)*3600));c1=min(3600,math.ceil((east+70)*3600))
    z=np.array(full[r0:r1+1,c0:c1+1],dtype=float);assert np.all(z>-32000)
    lon=-70+np.arange(c0,c1+1)/3600;lat=-14-np.arange(r0,r1+1)/3600
    np.save(B/'dem-google-earth.npy',z.astype(np.float32))
    rastermeta=dict(geotransform=[float(lon[0]-1/7200),1/3600,0,float(lat[0]+1/7200),0,-1/3600],epsg=4326,source='Mapzen Terrain Tiles / datos globales USGS, HGT S15W070 ~30m',zmin=float(z.min()),zmax=float(z.max()),intervalo_curvas_m=20,principal_m=100)
    (D/'topografia-gabinete.json').write_text(json.dumps(rastermeta,ensure_ascii=False,indent=2),encoding='utf-8')
    rgb=LightSource(azdeg=315,altdeg=45).shade(z,cmap=plt.get_cmap('terrain'),vert_exag=1,dx=30*math.cos(math.radians(float(lat.mean()))),dy=30,blend_mode='soft')
    Image.fromarray((rgb[:,:,:3]*255).astype(np.uint8)).resize((z.shape[1]*4,z.shape[0]*4),Image.Resampling.BICUBIC).save(assets/'relieve-dem.png')
    fig,ax=plt.subplots();levels=np.arange(math.ceil(z.min()/20)*20,math.floor(z.max()/20)*20+1,20);cs=ax.contour(lon,lat,z,levels=levels);curves=[]
    for level,segments in zip(cs.levels,cs.allsegs):
        for seg in segments:
            if len(seg)<2:continue
            x,y=to_xy.transform(seg[:,0],seg[:,1]);geom=LineString(np.column_stack([x,y]))
            if geom.length<20:continue
            curves.append(dict(type='Feature',geometry=mapping(geom),properties=dict(id=f'CN{len(curves)+1:04}',elev_m=float(level),principal=int(round(level))%100==0,fuente='DEM publico ~30m; curvas derivadas, no levantadas')))
    plt.close(fig)
    geo=dict(type='FeatureCollection',crs={'type':'name','properties':{'name':'EPSG:32719'}},features=curves)
    (D/'curvas-dem.geojson').write_text(json.dumps(geo,ensure_ascii=False),encoding='utf-8')
    # Símbolos geométricos de plano DGE: círculoCAC ySE proyectada.
    im=Image.new('RGBA',(64,64),(255,255,255,0));dr=ImageDraw.Draw(im);dr.ellipse((12,12,52,52),fill='white',outline='#a32625',width=5);im.save(assets/'poste-cac.png')
    im=Image.new('RGBA',(80,60),(255,255,255,0));dr=ImageDraw.Draw(im);dr.rectangle((6,9,74,51),fill='white',outline='#a32625',width=4);dr.line([(74,9),(6,30),(74,51)],fill='#a32625',width=4);im.save(assets/'subestacion.png')
    leg=Image.new('RGBA',(570,260),(255,255,255,232));dr=ImageDraw.Draw(leg);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23)
    dr.text((15,12),'LÍNEA PRIMARIA LIMBANI - HUANCASAYANI',font=bold,fill='#17344d')
    for j,(color,s) in enumerate([('#dd3030','Eje: 6.696 km /111 apoyos /110 vanos'),('#ffbf20','Cable 3D: altura relativa de estudio'),('#477031','Curvas DEM: cada 20 m / principales 100 m'),('#a32625','Poste CAC / SE: simbología DGE'),('#333333','DEM de aproximadamente 30 m; cotas y suelos sin verificación'),('#333333','Sistema aislado; predios y tensión por confirmar')]):
        y=52+j*31;dr.line((17,y+10,48,y+10),fill=color,width=5);dr.text((61,y),s,font=font,fill='#243344')
    leg.save(assets/'leyenda.png')
    root=ET.Element('{'+K+'}kml');doc=e(root,'Document');e(doc,'name','LP-R01 | Limbani - Huancasayani | Modelo académico')
    desc='Proyecto académico aislado. EPSG:32719 en cálculos; KML en WGS84 geográfico. Postes y SE propuestos, sin replanteo. Curvas derivadas del DEM Mapzen/USGS ~30 m: intervalos de 20/100 m NO son exactitud topográfica. La visualización3D relativa adopta alturas de estudio sobre el terrenoGoogle Earth; éste puede diferir del DEM. No acredita distancias de seguridad ni cotas de obra.'
    e(doc,'description',desc);look(doc,sum(v[0] for v in ll)/len(ll),sum(v[1] for v in ll)/len(ll),10500,55);styles(doc)
    base=folder(doc,'01 | Eje y subestaciones propuestas');line(base,'Línea primaria: 6.696 km / 10 kV de estudio',[(lo,la,0) for lo,la in ll],'eje',desc)
    for p,(lo,la),name in [(ps[0],ll[0],'SE-LIM'),(ps[-1],ll[-1],'SE-HUA')]:point(base,name,lo,la,'se',table([('Ubicación','Propuesta, no predio identificado'),('E/N UTM 19S',f"{p['e']:.3f} / {p['n']:.3f}m"),('Transformación','250 kVA de estudio, sobre piso'),('Estado','Antecedentes de captación/CM y llegada por verificar')]))
    poles=folder(doc,'02 | 111 postes y fichas');g3=folder(doc,'03 | Postes y cables 3D relativos (visualización)',1);absolute=folder(doc,'04 | Cables absolutos DEM (comparar datums)',0)
    for i,(p,(lo,la)) in enumerate(zip(ps,ll)):
        image=f'files/PF-{min(7,int(p["progresiva_m"]//1000)+1):02}.png';src=B/'perfiles-explicitos'/f'{12+min(7,int(p["progresiva_m"]//1000)+1):02}-LP-PF-{min(7,int(p["progresiva_m"]//1000)+1):02}.png'
        if src.exists():
            import shutil;shutil.copy2(src,assets/Path(image).name)
        descp=table([('Poste',p['id']),('Función /armado',p['estructura']+' / '+p['armado']),('Progresiva',f"{p['progresiva_m']:.1f}m"),('E /N',f"{p['e']:.3f} /{p['n']:.3f}m EPSG32719"),('Cota DEM',f"{p['z_dem_m']:.1f}m, datum vertical no confirmado"),('Poste /amarre',f"{p['poste_m']}m total /{p['amarre_m']:.1f}m sobre DEM"),('Ángulo /retenidas',f"{p['angulo_deg']:.1f}° /{p['retenidas_num']}"),('Estado','Ubicación de gabinete, no levantada')])+f'<p>Perfil del tramo:</p><img src="{image}" width="720"/>'
        point(poles,p['id']+' /'+p['armado'],lo,la,'especial' if p['armado']=='ESP-RET' else 'poste',descp,lod=True)
        line(g3,p['id']+' /amarre',[(lo,la,0),(lo,la,p['amarre_m'])],'poste3d',descp,'relativeToGround')
    for i,v in enumerate(ss):
        pa,pb=ps[i],ps[i+1];fract=v['perfil']['fraction'];alt=v['perfil']['conductor_m'];positions=[];relative=[]
        for t,zz in zip(fract,alt):
            xx=pa['e']+t*(pb['e']-pa['e']);yy=pa['n']+t*(pb['n']-pa['n']);lo,la=to_ll.transform(xx,yy);positions.append((lo,la,zz));relative.append((lo,la,zz-elevation(xx,yy)))
        description=table([('Vano',v['id']+' /'+v['desde']+' - '+v['hasta']),('L horizontal',f"{v['longitud_m']:.2f}m"),('Flecha75°C',f"{v['estados']['CALOR_FINAL']['flecha_vertical_m']:.2f}m"),('SeparaciónDEM75°C',f"{v['estados']['CALOR_FINAL']['distancia_dem_min_m']:.2f}m"),('Mínimo6estados',f"{min(st['distancia_dem_min_m'] for st in v['estados'].values()):.2f}m, de modelo"),('Cantón',v['canton']),('Lectura 3D','Un cable representa la terna. Relativo a terrenoGoogle Earth; no certifica catenaria de campo.')])
        line(g3,v['id'],relative,'cable',description,'relativeToGround');line(absolute,v['id']+' /cotaDEM',positions,'cable',description,'absolute')
    cf=folder(doc,'05 | Curvas de nivel DEM20m (principales 100 m)',1);lab=folder(doc,'06 | Cotas de curvas principales',0)
    for v in curves:
        pr=v['properties'];arr=v['geometry']['coordinates'];x,y=zip(*arr);lo,la=to_ll.transform(x,y);vs=list(zip(lo,la,[0]*len(lo)))
        line(cf,f"{pr['elev_m']:.0f}m /{pr['id']}",vs,'principal' if pr['principal'] else 'curva','Curva derivada deDEM de aproximadamente 30 m; equidistancia de 20 m no implica precisión20m. No levantamiento de campo.')
        if pr['principal']:
            k=len(lo)//2;point(lab,f"{pr['elev_m']:.0f}m",lo[k],la[k],'cota',lod=True)
    over=e(doc,'GroundOverlay');e(over,'name','07 | Relieve sombreado DEM público (transparencia)');e(over,'visibility',0);e(over,'color','90ffffff');e(e(over,'Icon'),'href','files/relieve-dem.png');bb=e(over,'LatLonBox')
    for t,val in [('north',float(lat[0]+1/7200)),('south',float(lat[-1]-1/7200)),('west',float(lon[0]-1/7200)),('east',float(lon[-1]+1/7200))]:e(bb,t,val)
    ref=folder(doc,'08 | Vías y cauces OSM de referencia',0)
    for v in json.loads((D/'referencias-osm.geojson').read_text(encoding='utf-8'))['features']:
        x,y=zip(*v['geometry']['coordinates']);lo,la=to_ll.transform(x,y);water=v['properties']['clase'] in ['river','stream','ditch','drain'];line(ref,str(v['properties'].get('nombre','Referencia OSM')),list(zip(lo,la,[0]*len(lo))),'agua' if water else 'via','©OpenStreetMap contributors /ODbL. No catastro legal.')
    screen=e(doc,'ScreenOverlay');e(screen,'name','09 | Leyenda y limitaciones');e(e(screen,'Icon'),'href','files/leyenda.png');e(screen,'overlayXY',None,x='0',y='1',xunits='fraction',yunits='fraction');e(screen,'screenXY',None,x='.015',y='.97',xunits='fraction',yunits='fraction');e(screen,'size',None,x='420',y='0',xunits='pixels',yunits='pixels')
    tour=gx(doc,'Tour');e(tour,'name','10 | Recorrido 3D hacia Huancasayani');play=gx(tour,'Playlist')
    for k in range(8):
        target=min(ps,key=lambda p:abs(p['progresiva_m']-k*1000));lo,la=to_ll.transform(target['e'],target['n']);fly=gx(play,'FlyTo');gx(fly,'duration',4);gx(fly,'flyToMode','smooth');look(fly,lo,la,1800,65,195);wait=gx(play,'Wait');gx(wait,'duration',1)
    kml=G/'LP_Limbani_Huancasayani_R01.kml';ET.ElementTree(root).write(kml,encoding='utf-8',xml_declaration=True)
    kmz=G/'LP_Limbani_Huancasayani_R01.kmz'
    with zipfile.ZipFile(kmz,'w',zipfile.ZIP_DEFLATED) as zf:
        zf.write(kml,'doc.kml')
        for f in assets.iterdir():zf.write(f,'files/'+f.name)
    with zipfile.ZipFile(kmz) as zf:
        assert zf.testzip() is None;loaded=ET.fromstring(zf.read('doc.kml'))
        for href in loaded.findall('.//{'+K+'}href'):assert href.text in zf.namelist()
    result=dict(postes=111,vanos=110,curvas=len(curves),niveles_distintos=len({v['properties']['elev_m'] for v in curves}),intervalo_curvas_m=20,principales_m=100,relieve_resolution_aprox_m=30,kmz_bytes=kmz.stat().st_size,coordenadas_origen='EPSG32719',coordenadas_kml='EPSG4326',modo3d='relativo para presentación; cotaDEM absoluta opcional sin datum confirmado',zip_integro=True,recursos_internos_verificados=True)
    (G/'verificacion-google-earth.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (G/'LEER_PRIMERO.md').write_text('# Google Earth: LP Limbani - Huancasayani\n\nAbrir el KMZ en Google Earth Pro mediante Archivo > Abrir. Contiene todos sus iconos, relieve y perfiles. Activar el terreno 3D del visor. Doble clic en el nombre del proyecto para la vista general y reproducir el recorrido 3D. Al acercarse aparecen los IDs; al pulsar un poste o vano se abre su ficha y el perfil del tramo.\n\nCurvas cada 20 m, principales 100 m: derivadas del mismo DEM público de aproximadamente 30 m de los cálculos. Se omiten segmentos menores de 20 m para legibilidad. No son topografía de campo ni datos extraídos de Google Earth. La equidistancia gráfica no es exactitud vertical.\n\nLa vista 3D relativa traslada la altura de estudio al terreno del visor; no preserva necesariamente una catenaria absoluta porque Google Earth puede usar otro relieve. La carpeta de cables absolutos DEM queda desactivada y permite comparar esta diferencia. No modificar cotas para hacerlos coincidir. Activar el sombreado o las cotas principales según la escala de vista. Un cable representa la terna; no implica que haya un solo conductor.\n\nFuente DEM: Mapzen Terrain Tiles/USGS, tesela S15W070. OSM © contribuidores, ODbL. KML en WGS84 y datos de cálculo en UTM 19S. Normas/antecedentes y equipos son de estudio; se mantienen los pendientes de campo.\n\nReferencia oficial del formato: https://developers.google.com/kml/documentation/kmlreference ; importación: https://support.google.com/earth/answer/176685?hl=es-419\n',encoding='utf-8')
    # Vista propia de gabinete para revisar las curvas sin requerir la aplicación.
    fig,ax=plt.subplots(figsize=(9,12));xx,yy=to_xy.transform(*np.meshgrid(lon,lat));ax.pcolormesh(xx,yy,z,cmap='terrain',shading='auto',alpha=.65)
    for v in curves:
        xs,ys=zip(*v['geometry']['coordinates']);ax.plot(xs,ys,color='#4b614c',lw=.55 if v['properties']['principal'] else .18,alpha=.65)
    ax.plot([p['e'] for p in ps],[p['n'] for p in ps],color='#c62b26',lw=2);ax.scatter([p['e'] for p in ps],[p['n'] for p in ps],s=9,facecolors='white',edgecolors='#a32625');ax.set_aspect('equal');ax.ticklabel_format(style='plain',useOffset=False);ax.set_xlabel('Este UTM 19S (m)');ax.set_ylabel('Norte UTM 19S (m)');ax.set_title('Limbani - Huancasayani: línea y curvas de nivel DEM\nCada 20 m /principales 100 m · gabinete, sin levantamiento');fig.savefig(G/'vista-topografica.png',dpi=150,bbox_inches='tight');plt.close(fig)
    print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
