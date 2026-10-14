"""Transfiere vectores de una página PDF a entidades CAD, sin generar dibujos."""
import math
from herramientas.biblioteca_dge.generar import pdf,newdoc,PTMM,text

def convert(page):
    doc=newdoc();m=doc.modelspace()
    def xy(v):return (round(v.x*PTMM,4),round((page.rect.height-v.y)*PTMM,4))
    weights=[0,5,9,13,15,18,20,25,30,35,40,50,53,60,70,80,90,100,106,120,140,158,200,211]
    for dr in page.get_drawings():
        loops=[];sub=[]
        def finish():
            nonlocal sub
            if len(sub)>1:loops.append(sub)
            sub=[]
        for it in dr['items']:
            op=it[0]
            if op=='l':arr=it[1:3]
            elif op=='c':
                a,b,c,z=it[1:5];arr=[]
                for k in range(25):
                    t=k/24;u=1-t;arr.append(pdf.Point(u**3*a.x+3*u*u*t*b.x+3*u*t*t*c.x+t**3*z.x,u**3*a.y+3*u*u*t*b.y+3*u*t*t*c.y+t**3*z.y))
            elif op=='re':r=it[1];arr=[r.tl,r.tr,r.br,r.bl,r.tl]
            elif op=='qu':r=it[1];arr=[r.ul,r.ur,r.lr,r.ll,r.ul]
            else:raise ValueError(op)
            pp=[xy(v) for v in arr]
            if sub and math.dist(sub[-1],pp[0])>.001:finish()
            sub+=pp if not sub else pp[1:]
        finish()
        if dr.get('color') is not None:
            lw=min(weights,key=lambda w:abs(w-(dr.get('width') or .1)*PTMM*100))
            for pts in loops:
                m.add_lwpolyline(pts,close=bool(dr.get('closePath',False)),dxfattribs={'layer':'DGE_CONTORNOS','lineweight':lw})
        if dr.get('fill') is not None and loops:
            rgb=tuple(round(v*255) for v in dr['fill']);h=m.add_hatch(color=7,dxfattribs={'layer':'DGE_RELLENO','true_color':rgb[0]*65536+rgb[1]*256+rgb[2]})
            h.dxf.hatch_style=0
            for pts in loops:h.paths.add_polyline_path(pts,is_closed=True,flags=0)
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for s in line.get('spans',[]):
                if s['text'].strip():
                    di=line['dir'];ang=math.degrees(math.atan2(-di[1],di[0]))
                    m.add_text(s['text'],dxfattribs={'insert':xy(pdf.Point(s['origin'])),'height':s['size']*PTMM*.73,'rotation':ang,'style':'DGE_ARIAL','layer':'DGE_TEXTOS'})
    return doc
