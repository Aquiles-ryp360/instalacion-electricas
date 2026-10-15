"""Trazado de gabinete a partir de vías OSM y antecedentes, sin topografía ficticia."""
from pathlib import Path
import json,xml.etree.ElementTree as ET,heapq,math,gzip
import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString,Point,mapping

P=Path(__file__).resolve().parents[2];ROOT=P.parents[1]
S=P/'fuentes/local/lp-r01';D=P/'datos/lp-r01';B=ROOT/'build'/P.name/'lp-r01'

def osm():
    tree=ET.parse(D/'osm_bbox.xml' if (D/'osm_bbox.xml').exists() else S/'osm_bbox.xml');xy=Transformer.from_crs(4326,32719,always_xy=True)
    nodes={n.get('id'):xy.transform(float(n.get('lon')),float(n.get('lat'))) for n in tree.findall('node')}
    ways=[]
    for w in tree.findall('way'):
        tags={t.get('k'):t.get('v') for t in w.findall('tag')}
        ids=[n.get('ref') for n in w.findall('nd')]
        if all(n in nodes for n in ids):ways.append(dict(id=w.get('id'),tags=tags,ids=ids,xy=[nodes[n] for n in ids]))
    return nodes,ways

def elevation(x,y):
    source=ROOT/'referencias/local/topografia-limbani/S15W070-mapzen.hgt.gz'
    if not hasattr(elevation,'grid'):
        elevation.grid=np.frombuffer(gzip.decompress(source.read_bytes()),dtype='>i2').reshape(3601,3601)
        elevation.t=Transformer.from_crs(32719,4326,always_xy=True)
    lon,lat=elevation.t.transform(x,y);r=(-14-lat)*3600;c=(lon+70)*3600
    i,j=int(r),int(c);u,v=r-i,c-j;z=elevation.grid
    if not 0<=i<3600 or not 0<=j<3600:raise ValueError('Fuera DEM')
    vals=np.array([z[i,j],z[i+1,j],z[i,j+1],z[i+1,j+1]],dtype=float)
    if (vals<=-32000).any():raise ValueError('DEM sin dato')
    return float(vals@np.array([(1-u)*(1-v),u*(1-v),(1-u)*v,u*v]))

def shortest(nodes,ways,start,end):
    graph={}
    for w in ways:
        if 'highway' not in w['tags']:continue
        for a,b in zip(w['ids'],w['ids'][1:]):
            length=math.dist(nodes[a],nodes[b])
            graph.setdefault(a,[]).append((b,length));graph.setdefault(b,[]).append((a,length))
    a=min(graph,key=lambda k:Point(nodes[k]).distance(start))
    b=min(graph,key=lambda k:Point(nodes[k]).distance(end))
    todo=[(0,a)];dist={a:0};prev={}
    while todo:
        cost,k=heapq.heappop(todo)
        if cost!=dist[k]:continue
        if k==b:break
        for nxt,l in graph[k]:
            new=cost+l
            if new<dist.get(nxt,float('inf')):dist[nxt]=new;prev[nxt]=k;heapq.heappush(todo,(new,nxt))
    if b not in dist:raise ValueError('Vías sin conexión entre extremos; no crear enlace ficticio')
    ids=[b]
    while ids[-1]!=a:ids.append(prev[ids[-1]])
    ids.reverse()
    return LineString([nodes[k] for k in ids]),ids

def main():
    D.mkdir(parents=True,exist_ok=True);B.mkdir(parents=True,exist_ok=True)
    nodes,ways=osm();t=Transformer.from_crs(4326,32719,always_xy=True)
    start=Point(425715,8436650);end=Point(*t.transform(-69.7048438,-14.1917532))
    road,ids=shortest(nodes,ways,start,end)
    route=LineString([start.coords[0]]+list(road.coords)+[end.coords[0]]).simplify(10,preserve_topology=True)
    data=dict(crs='EPSG:32719',metodo='Camino vial OSM más corto y simplificación de 10 m; corredor preliminar, no eje aprobado',
        inicio=list(start.coords[0]),fin=list(end.coords[0]),nodos_osm=ids,
        longitud_vial_m=road.length,longitud_corredor_m=route.length,
        distancia_inicio_via_m=start.distance(Point(road.coords[0])),distancia_fin_via_m=end.distance(Point(road.coords[-1])),
        geometria=mapping(route),vertices_dem=[dict(e=x,n=y,z_dem_m=elevation(x,y)) for x,y in route.coords])
    (D/'corredor-vial.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k not in ['geometria','vertices_dem','nodos_osm']},ensure_ascii=False,indent=2))
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,9))
    for w in ways:
        if w['tags'].get('highway'):ax.plot(*np.array(w['xy']).T,color='.75',lw=.6)
        if w['tags'].get('waterway'):ax.plot(*np.array(w['xy']).T,color='skyblue',lw=1)
    ax.plot(*np.array(route.coords).T,color='firebrick',lw=1.7)
    ax.scatter([start.x,end.x],[start.y,end.y]);ax.set_aspect('equal');ax.ticklabel_format(style='plain',useOffset=False)
    fig.savefig(B/'investigacion/corredor-inicial.png',dpi=160,bbox_inches='tight')

if __name__=='__main__':main()
