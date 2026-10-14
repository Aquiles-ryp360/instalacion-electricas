"""Plantas georreferenciadas PC/PN/CV y perfil SRTM referencial para Rev. 5."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import ezdxf
import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
TRANS = Transformer.from_crs(4326, 32719, always_xy=True)
MM = 72 / 25.4
BLUE = HexColor("#245b91")
RED = HexColor("#c63434")
CYAN = HexColor("#157899")
AMBER = HexColor("#cd7a19")
INK = HexColor("#24313f")


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _layout(doc, name):
    layout = doc.layouts.new(name)
    layout.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
    return layout


def _paper_text(layout, x, y, text, height=2.4, layer="TEXT"):
    layout.add_text(str(text), dxfattribs={"height": height, "layer": layer}).set_placement((x, y))


def _draw_frame(c, code, title, subtitle):
    c.setStrokeColor(INK); c.setLineWidth(.5)
    c.rect(8*MM, 8*MM, 404*MM, 281*MM, stroke=1, fill=0)
    c.line(8*MM, 39*MM, 412*MM, 39*MM)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 13)
    c.drawString(14*MM, 281*MM, f"{code} | {title}")
    c.setFont("Helvetica", 7.5)
    c.drawString(14*MM, 270*MM, subtitle)
    c.setFillColor(RED); c.setFont("Helvetica-Bold", 8)
    c.drawString(14*MM, 28*MM, "ANTEPROYECTO ACADEMICO - NO APTO PARA CONSTRUCCION")
    c.setFillColor(INK); c.setFont("Helvetica", 6.5)
    c.drawString(14*MM, 16*MM, "WGS84 / UTM 19S EPSG:32719 | Modelo DXF en metros | Presentacion A3 en milimetros")


def _map_transform(points, x, y, width, height):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys)
    dx, dy = max(xmax-xmin, 1), max(ymax-ymin, 1)
    scale = min((width-16)/dx, (height-16)/dy)
    ox = x + (width-dx*scale)/2
    oy = y + (height-dy*scale)/2
    return lambda p:(ox+(p[0]-xmin)*scale, oy+(p[1]-ymin)*scale), scale, (xmin,xmax,ymin,ymax)


def _label(layout, c, x, y, text, color, size=6):
    layout.add_text(str(text), dxfattribs={"height": size*.27, "layer":"TEXT"}).set_placement((x,y))
    c.setFillColor(color); c.setFont("Helvetica", size)
    c.drawString(x*MM, y*MM, str(text))


def make_plant(output: Path, segment: int, line: list[tuple[float,float]],
               pc: list[dict], pn: list[dict], cv: list[dict]):
    code = f"CL-07-S{segment}"
    pdf_path = output/"05_PLANOS_PDF"/f"{code}_REV5.pdf"
    dxf_path = output/"06_PLANOS_EDITABLES"/f"{code}_REV5.dxf"
    png_path = output/"09_CONTROL_DE_CALIDAD"/f"{code}_REV5.png"
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 6
    for name, aci in [("EJE_KML",5),("PC_GISEM",1),("PN_CANDIDATO",4),("CV_OSM",30),("MARCO",7),("TEXT",7)]:
        doc.layers.new(name, dxfattribs={"color":aci})
    layout = _layout(doc, code+"_A3")
    for name in ["EJE_KML","PC_GISEM","PN_CANDIDATO","CV_OSM","MARCO","TEXT"]:
        layout.add_line((0,0),(0,0),dxfattribs={"layer":name}) if False else None
    pdf = canvas.Canvas(str(pdf_path), pagesize=(420*MM,297*MM), invariant=1)
    _draw_frame(pdf, code, f"Planta del segmento {segment}: referencias y sitios a verificar",
                "Eje KML en azul; PC: estructura GIS de referencia; PN: sitio por replantear; CV: alerta OSM")
    c = pdf
    # Marco del mapa y puntos, con ajuste de escala uniforme en metros proyectados.
    map_x,map_y,map_w,map_h=14,62,258,192
    c.setStrokeColor(INK); c.setLineWidth(.35); c.rect(map_x*MM,map_y*MM,map_w*MM,map_h*MM)
    layout.add_lwpolyline([(map_x,map_y),(map_x+map_w,map_y),(map_x+map_w,map_y+map_h),
                           (map_x,map_y+map_h),(map_x,map_y)],dxfattribs={"layer":"MARCO"})
    pc_xy=[(float(r["este_m"]),float(r["norte_m"])) for r in pc]
    pn_xy=[(float(r["este_utm19s_m"]),float(r["norte_utm19s_m"])) for r in pn]
    cv_xy=[(float(r["este_utm19s_m"]),float(r["norte_utm19s_m"])) for r in cv]
    all_xy=list(line)+pc_xy+pn_xy+cv_xy
    transform,scale,bounds=_map_transform(all_xy,map_x,map_y,map_w,map_h)
    msp=doc.modelspace()
    msp.add_lwpolyline(line,dxfattribs={"layer":"EJE_KML"})
    layout.add_lwpolyline([transform(p) for p in line],dxfattribs={"layer":"EJE_KML"})
    # PDF axis from the source coordinates; same projection and transformation as DXF model.
    path=pdf.beginPath(); p0=transform(line[0]); path.moveTo(p0[0]*MM,p0[1]*MM)
    for xy in line[1:]:
        px,py=transform(xy); path.lineTo(px*MM,py*MM)
    c.setStrokeColor(BLUE); c.setLineWidth(.9); c.drawPath(path)
    for row,xy in zip(pc,pc_xy):
        msp.add_circle(xy,2.2,dxfattribs={"layer":"PC_GISEM"})
        px,py=transform(xy); c.setStrokeColor(RED); c.setLineWidth(.65)
        c.circle(px*MM,py*MM,1.35*MM,stroke=1,fill=0)
        layout.add_circle((px,py),1.35,dxfattribs={"layer":"PC_GISEM"})
    for row,xy in zip(pn,pn_xy):
        msp.add_circle(xy,2.8,dxfattribs={"layer":"PN_CANDIDATO"})
        px,py=transform(xy); c.setStrokeColor(CYAN); c.setLineWidth(.8)
        c.circle(px*MM,py*MM,1.8*MM,stroke=1,fill=0)
        layout.add_circle((px,py),1.8,dxfattribs={"layer":"PN_CANDIDATO"})
    for xy in cv_xy:
        msp.add_point(xy,dxfattribs={"layer":"CV_OSM"})
        px,py=transform(xy); c.setStrokeColor(AMBER); c.setLineWidth(.55)
        c.line((px-1.0)*MM,py*MM,(px+1.0)*MM,py*MM)
        c.line(px*MM,(py-1.0)*MM,px*MM,(py+1.0)*MM)
        layout.add_line((px-1.0,py),(px+1.0,py),dxfattribs={"layer":"CV_OSM"})
        layout.add_line((px,py-1.0),(px,py+1.0),dxfattribs={"layer":"CV_OSM"})
    # Sparse PN labels keep the map legible; every identifier and coordinate is in its table.
    placed=[]
    for row,xy in zip(pn,pn_xy):
        px,py=transform(xy)
        if all(math.dist((px,py),q)>13 for q in placed):
            _label(layout,c,px+2.2,py+1.7,row["id"],CYAN,5.6); placed.append((px,py))
    # North arrow and a scale bar in paper coordinates.
    _label(layout,c,map_x+map_w-13,map_y+map_h-10,"N",INK,8)
    c.setStrokeColor(INK); c.setLineWidth(.9)
    c.line((map_x+map_w-10)*MM,(map_y+map_h-13)*MM,(map_x+map_w-10)*MM,(map_y+map_h-22)*MM)
    c.line((map_x+map_w-10)*MM,(map_y+map_h-13)*MM,(map_x+map_w-12)*MM,(map_y+map_h-17)*MM)
    c.line((map_x+map_w-10)*MM,(map_y+map_h-13)*MM,(map_x+map_w-8)*MM,(map_y+map_h-17)*MM)
    layout.add_line((map_x+map_w-10,map_y+map_h-13),(map_x+map_w-10,map_y+map_h-22),dxfattribs={"layer":"MARCO"})
    layout.add_line((map_x+map_w-10,map_y+map_h-13),(map_x+map_w-12,map_y+map_h-17),dxfattribs={"layer":"MARCO"})
    layout.add_line((map_x+map_w-10,map_y+map_h-13),(map_x+map_w-8,map_y+map_h-17),dxfattribs={"layer":"MARCO"})
    extent=max(bounds[1]-bounds[0],bounds[3]-bounds[2])
    target=extent/5
    exponent=10**math.floor(math.log10(target))
    scale_len=max(exponent,round(target/exponent)*exponent)
    bar_mm=scale_len*scale
    if bar_mm>map_w*.35: scale_len/=2; bar_mm=scale_len*scale
    bx,by=map_x+8,map_y+8
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.line(bx*MM,by*MM,(bx+bar_mm)*MM,by*MM)
    layout.add_line((bx,by),(bx+bar_mm,by),dxfattribs={"layer":"MARCO"})
    _label(layout,c,bx,by+2,f"{scale_len:g} m",INK,5.8)
    _label(layout,c,map_x+3,map_y+2,f"E {bounds[0]:.0f}-{bounds[1]:.0f} m | N {bounds[2]:.0f}-{bounds[3]:.0f} m",INK,5.3)
    # Legend symbols appear in both PDF and editable paper layout.
    legend=[("PC",RED,"PC_GISEM"),("PN",CYAN,"PN_CANDIDATO"),("CV",AMBER,"CV_OSM")]
    for j,(label,color,layer) in enumerate(legend):
        lx,ly=map_x+6+j*44,map_y+map_h-7
        c.setFillColor(color); c.setFont("Helvetica",5.7); c.drawString(lx*MM,ly*MM,label)
        _paper_text(layout,lx,ly,label,1.6,"TEXT")
        if layer=="CV_OSM":
            c.setStrokeColor(color); c.line((lx-3)*MM,(ly+1)*MM,(lx-1)*MM,(ly+1)*MM)
            layout.add_line((lx-3,ly+1),(lx-1,ly+1),dxfattribs={"layer":layer})
        else:
            c.setStrokeColor(color); c.circle((lx-2)*MM,(ly+1)*MM,1.4*MM,stroke=1,fill=0)
            layout.add_circle((lx-2,ly+1),1.4,dxfattribs={"layer":layer})
    # Data table separated by class; no implicit conversion of PC into new poles.
    tx,ty,tw=280,254,126
    c.setStrokeColor(INK); c.rect(tx*MM,ty*MM,tw*MM,1)
    _label(layout,c,tx,ty+3,"CUADRO DE PUNTOS | progresiva según cada fuente",INK,6.5)
    yy=ty-5
    def heading(label):
        nonlocal yy
        _label(layout,c,tx,yy,label,INK,5.8); yy-=4.8
        _label(layout,c,tx,yy,"ID / GISEM o funcion",INK,4.9)
        _label(layout,c,tx+46,yy,"PK m",INK,4.9)
        _label(layout,c,tx+64,yy,"E",INK,4.9)
        _label(layout,c,tx+91,yy,"N",INK,4.9)
        yy-=4.6
    heading(f"PC | {len(pc)} referencias GIS; PK acumulado GIS; validar existencia")
    for row in pc:
        desc=f"{row['id']} {row['codigo_gisem']}"
        _label(layout,c,tx,yy,desc,RED,4.6)
        _label(layout,c,tx+46,yy,f"{float(row['estacion_m']):.0f}",INK,4.6)
        _label(layout,c,tx+64,yy,f"{float(row['este_m']):.0f}",INK,4.6)
        _label(layout,c,tx+91,yy,f"{float(row['norte_m']):.0f}",INK,4.6)
        yy-=4.6
    if not pc:
        _label(layout,c,tx,yy,"Sin referencias PC en este segmento",INK,4.7); yy-=5
    heading(f"PN | {len(pn)} sitios candidatos; PK local KML; NO instalar")
    for row in pn:
        desc=f"{row['id']} {row['funcion_preliminar'][:18]}"
        _label(layout,c,tx,yy,desc,CYAN,4.6)
        _label(layout,c,tx+46,yy,f"{float(row['progresiva_kml_m']):.0f}",INK,4.6)
        _label(layout,c,tx+64,yy,f"{float(row['este_utm19s_m']):.0f}",INK,4.6)
        _label(layout,c,tx+91,yy,f"{float(row['norte_utm19s_m']):.0f}",INK,4.6)
        yy-=4.6
    _label(layout,c,tx,55,"UTM EPSG:32719 (m); lat/lon y fuente en CSV PC/PN.",INK,5.0)
    _label(layout,c,tx,49,"PC: PK GIS acumulado. PN: PK KML local; brechas no unidas.",INK,5.0)
    _label(layout,c,map_x+3,map_y-7,"Marcas PC/PN son cartograficas; PN no representa poste aprobado.",RED,6)
    # Same paper layout entities for editable CAD deliverable.
    layout.add_lwpolyline([(8,8),(412,8),(412,289),(8,289),(8,8)],dxfattribs={"layer":"MARCO"})
    _paper_text(layout,14,281,f"{code} | Planta segmento {segment} | REV5",4.0)
    _paper_text(layout,14,16,"ANTEPROYECTO - PC GIS y PN de gabinete; verificar en campo antes de diseño",2.0,"TEXT")
    pdf.showPage(); pdf.save(); doc.saveas(dxf_path)
    with fitz.open(pdf_path) as pdf_doc:
        if len(pdf_doc)!=1: raise ValueError(f"PDF {code} invalido")
        pdf_doc[0].get_pixmap(matrix=fitz.Matrix(125/72,125/72),alpha=False).save(png_path)


def make_profile(output: Path, source: dict):
    samples=source["samples"]
    station=np.asarray([float(r["chainage_m"]) for r in samples])
    elevation=np.asarray([float(r["elevation_m"]) for r in samples])
    if len(samples)!=57 or not np.all(np.diff(station)>0):
        raise ValueError("Muestras SRTM inesperadas o progresivas no monótonas")
    code="CL-08"
    pdf_path=output/"05_PLANOS_PDF/CL-08_REV5.pdf"
    dxf_path=output/"06_PLANOS_EDITABLES/CL-08_REV5.dxf"
    png_path=output/"09_CONTROL_DE_CALIDAD/CL-08_REV5.png"
    fig=plt.figure(figsize=(16.54,11.69),layout="constrained")
    grid=fig.add_gridspec(2,1,height_ratios=[.18,.82])
    ax_title=fig.add_subplot(grid[0]); ax_title.axis("off")
    ax_title.text(.01,.83,"CL-08 | Perfil SRTM referencial sobre el eje GIS alternativo",fontsize=19,weight="bold")
    ax_title.text(.01,.48,"57 muestras SRTM30m bilineales | paso nominal 250 m | chainage del GIS: 0 a 13.834 km",fontsize=11)
    ax_title.text(.01,.12,"NO corresponde al KML manual; elevacion y datum vertical no verificados; no usar para vanos, flechas o galibos.",fontsize=10,color="#ad2424",weight="bold")
    ax=fig.add_subplot(grid[1])
    ax.plot(station/1000,elevation,color="#245b91",linewidth=1.1,linestyle="--",label="Union ilustrativa entre muestras")
    ax.scatter(station/1000,elevation,s=12,color="#c63434",label="Muestra SRTM30m")
    ax.set_xlabel("Chainage sobre ruta GIS alternativa (km)")
    ax.set_ylabel("Elevacion informada por SRTM (m; referencia vertical no documentada)")
    ax.set_title(f"Rango muestreado: {elevation.min():.0f}-{elevation.max():.0f} m | terreno de resolucion nominal ~30 m")
    ax.grid(True,alpha=.3); ax.legend(loc="best"); ax.margins(x=.02,y=.1)
    ax.text(.01,.015,"Fuente local: sources/srtm30m_route_samples.json; descargada 2026-10-14; chainage y coordenadas asociados a derived/route.json.",transform=ax.transAxes,fontsize=8)
    fig.savefig(pdf_path,format="pdf",metadata={"Title":"CL-08 SRTM referencial - no topografia de diseno","Author":"Proyecto Capachica-Llachon"})
    fig.savefig(png_path,dpi=140)
    plt.close(fig)
    doc=ezdxf.new("R2010"); doc.header["$INSUNITS"]=6
    for name,aci in [("SRTM_PUNTOS",1),("INTERPOLACION_VISUAL",8),("MARCO",7),("TEXT",7)]:
        doc.layers.new(name,dxfattribs={"color":aci})
    paper=_layout(doc,"CL-08_A3")
    paper.add_lwpolyline([(8,8),(412,8),(412,289),(8,289),(8,8)],dxfattribs={"layer":"MARCO"})
    _paper_text(paper,14,281,"CL-08 | Perfil SRTM referencial sobre eje GIS | REV5",4,"TEXT")
    _paper_text(paper,14,270,"57 muestras; 250 m nominal; chainage GIS 0-13.834 km; no corresponde al KML manual",2.3,"TEXT")
    _paper_text(paper,14,257,"NO usar para vanos, flechas, despejes ni diseno; datum vertical no verificado",2.7,"TEXT")
    model=doc.modelspace()
    coords=list(zip(station.tolist(),elevation.tolist()))
    model.add_lwpolyline(coords,dxfattribs={"layer":"INTERPOLACION_VISUAL"})
    for pt in coords:
        model.add_circle(pt,8,dxfattribs={"layer":"SRTM_PUNTOS"})
    # Editable presentation axes with pronounced, declared vertical exaggeration.
    xmin,xmax=0,float(station[-1]); ymin,ymax=float(elevation.min()-5),float(elevation.max()+5)
    x0,y0=25,65; width,height=365,165
    sx=width/(xmax-xmin); sy=height/(ymax-ymin)
    paper.add_line((x0,y0),(x0+width,y0),dxfattribs={"layer":"MARCO"})
    paper.add_line((x0,y0),(x0,y0+height),dxfattribs={"layer":"MARCO"})
    view=[(x0+float(s)*sx,y0+(float(z)-ymin)*sy) for s,z in coords]
    paper.add_lwpolyline(view,dxfattribs={"layer":"INTERPOLACION_VISUAL"})
    for x,y in view:
        paper.add_circle((x,y),.8,dxfattribs={"layer":"SRTM_PUNTOS"})
    hscale=xmax/(width/1000); vscale=(ymax-ymin)/(height/1000)
    _paper_text(paper,x0,y0-9,"Chainage GIS (m)",2.2)
    _paper_text(paper,x0,y0+height+5,"Elevacion (m)",2.2)
    _paper_text(paper,25,48,f"Escalas graficas aproximadas: H 1:{hscale:.0f}; V 1:{vscale:.0f}; VE {hscale/vscale:.1f}x",2.1)
    _paper_text(paper,25,40,"La linea entre puntos solo facilita lectura; no representa terreno muestreado continuamente.",2.1)
    _paper_text(paper,14,16,"ANTEPROYECTO ACADEMICO - SRTM30m; no perfil topografico constructivo",2.0,"TEXT")
    doc.saveas(dxf_path)
    with fitz.open(pdf_path) as pdf_doc:
        if len(pdf_doc)!=1: raise ValueError("PDF CL-08 invalido")


def make_google_earth_overlay(output: Path, lines, gis, pc, pn, cv, samples):
    from lxml import etree
    ns="http://www.opengis.net/kml/2.2"
    q=lambda name:f"{{{ns}}}{name}"
    root=etree.Element(q("kml"),nsmap={None:ns})
    document=etree.SubElement(root,q("Document"))
    etree.SubElement(document,q("name")).text="Capachica-Llachon Rev5 - PC GIS y PN candidatos"
    etree.SubElement(document,q("description")).text="Datos de gabinete. PC son referencias GISEM; PN son sitios por replantear; CV son alertas OSM. No usar como ubicacion aprobada de postes. SRTM pertenece a ruta GIS alternativa."
    styles={"kml":("ff915b24","4"),"gis":("ff808080","3"),"pc":("ff3434c6","1"),
            "pn":("ff997815","0"),"cv":("ff197acd","0"),"srtm":("ff555555","0")}
    for name,(color,scale) in styles.items():
        st=etree.SubElement(document,q("Style"),id=name)
        ls=etree.SubElement(st,q("LineStyle")); etree.SubElement(ls,q("color")).text=color; etree.SubElement(ls,q("width")).text="2"
        icon=etree.SubElement(st,q("IconStyle")); etree.SubElement(icon,q("color")).text=color; etree.SubElement(icon,q("scale")).text="0.8"
        ico=etree.SubElement(icon,q("Icon")); etree.SubElement(ico,q("href")).text="http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
    def folder(name,description):
        f=etree.SubElement(document,q("Folder")); etree.SubElement(f,q("name")).text=name; etree.SubElement(f,q("description")).text=description; return f
    def placemark(parent,name,description,coords,style,geometry="Point"):
        p=etree.SubElement(parent,q("Placemark")); etree.SubElement(p,q("name")).text=str(name)
        etree.SubElement(p,q("description")).text=str(description); etree.SubElement(p,q("styleUrl")).text="#"+style
        if geometry=="Point":
            point=etree.SubElement(p,q("Point")); etree.SubElement(point,q("coordinates")).text=f"{coords[0]:.9f},{coords[1]:.9f},0"
        else:
            ls=etree.SubElement(p,q("LineString")); etree.SubElement(ls,q("tessellate")).text="1"
            etree.SubElement(ls,q("coordinates")).text=" ".join(f"{lon:.9f},{lat:.9f},0" for lon,lat in coords)
    f=folder("01 KML manual original - cuatro trazos","Geometria original; segmentos separados, sin enlaces inventados.")
    inverse=Transformer.from_crs(32719,4326,always_xy=True)
    for i,line in enumerate(lines,1):
        placemark(f,f"KML segmento {i}","Fuente original; no levantado para construccion.",[inverse.transform(*p) for p in line],"kml","LineString")
    f=folder("02 Eje GIS alternativo","Ruta GIS inferida, distinta al KML manual.")
    placemark(f,"Eje GIS alternativo","No aprobado como eje de obra.",[inverse.transform(*p) for p in gis],"gis","LineString")
    for name,records,style,desc,coordcols in [
        ("03 PC referencias de estructura GIS",pc,"pc","Referencia GIS; validar existencia, codigo y estado. No equivale a poste nuevo.",("longitud","latitud")),
        ("04 PN sitios candidatos para replanteo",pn,"pn","Sitio geométrico de gabinete; no es poste aprobado ni se debe instalar sin diseño.",("longitud","latitud")),
        ("05 CV alertas de cruces OSM",cv,"cv","Interseccion cartografica OSM; verificar clase, cota, titular y permiso.",("longitud","latitud"))]:
        f=folder(name,desc)
        for r in records:
            extra=f"ID {r['id']}; segmento {r['segmento']}; progresiva {r.get('estacion_m',r.get('progresiva_kml_m',''))} m; estado pendiente."
            placemark(f,r["id"],desc+" "+extra,(float(r[coordcols[0]]),float(r[coordcols[1]])),style)
    f=folder("06 Muestras SRTM sobre eje GIS alternativo","57 puntos de un DEM; elevación informada solo en descripción. No es perfil constructivo ni corresponde al KML.")
    for r in samples:
        placemark(f,f"SRTM PK {r['chainage_m']} m",f"Elevación SRTM informada: {r['elevation_m']} m; datum vertical y precisión local no comprobados.",(float(r["lon"]),float(r["lat"])),"srtm")
    dest=output/"02_DATOS_Y_CRITERIOS/fuentes/GIS_REV5_ABRIR_EN_GOOGLE_EARTH.kml"
    etree.ElementTree(root).write(str(dest),encoding="UTF-8",xml_declaration=True,pretty_print=True)


def generate(output: Path):
    source_root=ROOT/"sources"
    srtm=json.loads((source_root/"srtm30m_route_samples.json").read_text(encoding="utf-8"))
    # The SRTM metadata records the exact derived GIS route.json hash, not the
    # published GISEM source feature collection hash.
    route_sha=hashlib.sha256((ROOT/"derived/route.json").read_bytes()).hexdigest()
    expected=json.loads((ROOT/"derived/reconciliacion_corredores_rev3.json").read_text(encoding="utf-8"))["gis_sha256"]
    if srtm["route_sha256"]!=route_sha or route_sha!=expected:
        raise ValueError("El muestreo SRTM no coincide con el eje GIS fuente registrado")
    package_data=output/"02_DATOS_Y_CRITERIOS/fuentes"
    (package_data/"SRTM30M_MUESTRAS.json").write_bytes((source_root/"srtm30m_route_samples.json").read_bytes())
    pc=rows(package_data/"PC_REFERENCIAS_GIS.csv")
    pn=rows(package_data/"PN_SITIOS_REPLANTEO.csv")
    cv=rows(package_data/"CV_ALERTAS_OSM.csv")
    # Use input geometry via Rev5 source dataset referenced by the package.
    from generar_entrega_rev4 import read_inputs
    lines,gis,pc2,pn2,cv2,gaps,report,*_=read_inputs()
    if (len(pc),len(pn),len(cv))!=(40,27,44): raise ValueError("Conteos PC/PN/CV cambiaron")
    for segment,line in enumerate(lines,1):
        make_plant(output,segment,line,[r for r in pc if int(r["segmento"])==segment],
                   [r for r in pn if int(r["segmento"])==segment],
                   [r for r in cv if int(r["segmento"])==segment])
    make_profile(output,srtm)
    make_google_earth_overlay(output,lines,gis,pc,pn,cv,srtm["samples"])
    write=output/"02_DATOS_Y_CRITERIOS/SRTM30M_MUESTRAS.csv"
    with write.open("w",encoding="utf-8-sig",newline="") as fh:
        fields=["chainage_m","lon","lat","easting_m","northing_m","elevation_m"]
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(srtm["samples"])
    meta=output/"02_DATOS_Y_CRITERIOS/TOPOGRAFIA_SRTM.md"
    meta.write_text(f"""# Muestras topográficas de contexto\n\nFuente: SRTM30m mediante OpenTopoData; consulta {srtm['retrieved_at_utc']}; interpolación {srtm['interpolation']}; {len(srtm['samples'])} muestras, intervalo nominal 250 m, chainage 0–{srtm['samples'][-1]['chainage_m']:.2f} m de ruta GIS alternativa; rango {min(x['elevation_m'] for x in srtm['samples'])}–{max(x['elevation_m'] for x in srtm['samples'])} m. Huella de fuente GIS: {route_sha}.\n\nLa fuente advierte que no sirve para gálibos ni spotting. No es levantamiento topográfico, no está asociada al KML manual de cuatro segmentos y el datum vertical/precisión local no está comprobado. CL-08 solo comunica contexto del relieve de la ruta GIS. Los puntos y elevaciones originales se conservan en `SRTM30M_MUESTRAS.json`/`.csv`.\n\nGoogle Earth Pro no se encontró instalado en las rutas habituales de esta estación. `fuentes/GIS_REV5_ABRIR_EN_GOOGLE_EARTH.kml` reúne los puntos y ejes con estilos y advertencias para que se abra en Google Earth Pro por el usuario.\n""",encoding="utf-8")


def verify(output: Path):
    """Reapertura de los archivos nuevos; software/forma, no aprobación técnica."""
    package_data=output/"02_DATOS_Y_CRITERIOS/fuentes"
    all_pc=rows(package_data/"PC_REFERENCIAS_GIS.csv")
    all_pn=rows(package_data/"PN_SITIOS_REPLANTEO.csv")
    all_cv=rows(package_data/"CV_ALERTAS_OSM.csv")
    for segment in range(1,5):
        code=f"CL-07-S{segment}_REV5"
        doc=ezdxf.readfile(output/"06_PLANOS_EDITABLES"/(code+".dxf"))
        if doc.audit().has_errors or doc.header["$INSUNITS"]!=6:
            raise ValueError(f"DXF invalido {code}")
        msp=doc.modelspace()
        counts={layer:sum(e.dxf.layer==layer for e in msp) for layer in ("EJE_KML","PC_GISEM","PN_CANDIDATO","CV_OSM")}
        if counts["EJE_KML"]!=1: raise ValueError(f"Eje ausente {code}")
        expected={"PC_GISEM":len([r for r in all_pc if int(r["segmento"])==segment]),
                  "PN_CANDIDATO":len([r for r in all_pn if int(r["segmento"])==segment]),
                  "CV_OSM":len([r for r in all_cv if int(r["segmento"])==segment])}
        if any(counts[layer]!=count for layer,count in expected.items()):
            raise ValueError(f"Conteo DXF/source distinto en {code}: {counts} / {expected}")
        for layer,source,cols in [
            ("PC_GISEM",all_pc,("este_m","norte_m")),
            ("PN_CANDIDATO",all_pn,("este_utm19s_m","norte_utm19s_m")),
            ("CV_OSM",all_cv,("este_utm19s_m","norte_utm19s_m"))]:
            expected_xy={(round(float(r[cols[0]]),3),round(float(r[cols[1]]),3))
                         for r in source if int(r["segmento"])==segment}
            entities=[e for e in msp if e.dxf.layer==layer]
            actual_xy={(round(float(e.dxf.center.x),3),round(float(e.dxf.center.y),3))
                       if e.dxftype()=="CIRCLE" else
                       (round(float(e.dxf.location.x),3),round(float(e.dxf.location.y),3))
                       for e in entities}
            if expected_xy!=actual_xy:
                raise ValueError(f"Coordenadas {layer} no coinciden con CSV en {code}")
        for ext in ("pdf","png"):
            if not (output/("05_PLANOS_PDF" if ext=="pdf" else "09_CONTROL_DE_CALIDAD")/f"{code}.{ext}").is_file():
                raise ValueError(f"Falta {ext} {code}")
        with fitz.open(output/"05_PLANOS_PDF"/(code+".pdf")) as pdf:
            text=pdf[0].get_text()
            if len(pdf)!=1 or f"segmento {segment}" not in text or "NO APTO" not in text:
                raise ValueError(f"PDF sin etiqueta/advertencia {code}")
            if abs(pdf[0].rect.width-420*MM)>1 or abs(pdf[0].rect.height-297*MM)>1:
                raise ValueError(f"PDF {code} no es A3 horizontal")
            ids=[r["id"] for r in all_pc+all_pn if int(r["segmento"])==segment]
            if any(identifier not in text for identifier in ids):
                raise ValueError(f"Tabla PDF incompleta en {code}")
    doc=ezdxf.readfile(output/"06_PLANOS_EDITABLES/CL-08_REV5.dxf")
    profile_lines=[e for e in doc.modelspace()
                   if e.dxftype()=="LWPOLYLINE" and e.dxf.layer=="INTERPOLACION_VISUAL"]
    if doc.audit().has_errors or len(profile_lines)!=1:
        raise ValueError("DXF perfil SRTM inválido")
    with fitz.open(output/"05_PLANOS_PDF/CL-08_REV5.pdf") as pdf:
        text=pdf[0].get_text()
        if len(pdf)!=1 or "NO corresponde al KML manual" not in text or "SRTM" not in text:
            raise ValueError("Advertencia SRTM ausente")
        if abs(pdf[0].rect.width-420*MM)>1 or abs(pdf[0].rect.height-297*MM)>1:
            raise ValueError("PDF CL-08 no tiene tamaño A3 horizontal")
    from lxml import etree
    overlay=output/"02_DATOS_Y_CRITERIOS/fuentes/GIS_REV5_ABRIR_EN_GOOGLE_EARTH.kml"
    xml=etree.parse(str(overlay))
    ns={"k":"http://www.opengis.net/kml/2.2"}
    counts={"Placemark":len(xml.findall(".//k:Placemark",ns)),
            "PC":len(xml.xpath(".//k:Folder[k:name='03 PC referencias de estructura GIS']//k:Placemark",namespaces=ns)),
            "PN":len(xml.xpath(".//k:Folder[k:name='04 PN sitios candidatos para replanteo']//k:Placemark",namespaces=ns)),
            "CV":len(xml.xpath(".//k:Folder[k:name='05 CV alertas de cruces OSM']//k:Placemark",namespaces=ns)),
            "SRTM":len(xml.xpath(".//k:Folder[k:name='06 Muestras SRTM sobre eje GIS alternativo']//k:Placemark",namespaces=ns))}
    if counts!={"Placemark":173,"PC":40,"PN":27,"CV":44,"SRTM":57}:
        raise ValueError(f"KML overlay no conserva conteos fuente: {counts}")
    return True
