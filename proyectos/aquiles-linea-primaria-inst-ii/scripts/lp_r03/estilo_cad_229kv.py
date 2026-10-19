#!/usr/bin/env python3
"""Prepara copia gráfica de revisión LP-R03 a 22.9 kV. No altera cálculos ni origen.
La lámina LP-20 expresa el nuevo criterio, pero las LP-01..LP-19/M01 siguen históricas
hasta un rediseño técnico sincronizado de todas las láminas. Sin aprobación de obra.
"""
import argparse, hashlib, json
from pathlib import Path
import ezdxf

CAPAS={
    "TEXTO":(7,18),"MARCO":(7,25),"EJE":(1,35),"POSTES":(30,25),
    "ALERTA":(1,25),"TERRENO":(8,13),"CABLE":(3,35),
    "RETENIDA":(6,25),"GRILLA":(9,9),"CASAS":(8,18),
    "AGUA":(4,18),"VIA":(9,13),
}
CAPA_R03="R03-CONTROL"
def firma(doc):
    return {b.get_attrib_text("ID"):(tuple(round(x,7) for x in b.dxf.insert[:2]),b.get_attrib_text("TIPO"))
            for b in doc.modelspace().query("INSERT") if b.get_attrib_text("ID")}
def txt(layout,s,x,y,h=2.0):
    return layout.add_text(s,dxfattribs={"insert":(x,y),"height":h,"layer":CAPA_R03})
def pol(layout,pts):
    return layout.add_lwpolyline(pts,dxfattribs={"layer":CAPA_R03})
def marco(layout,x1,y1,x2,y2):
    pol(layout,[(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)])
def leyenda(layout):
    marco(layout,296,49,406,108)
    pol(layout,[(296,99),(406,99)])
    txt(layout,"SIMBOLOGIA | PLANTA Y PERFIL",300,102,2.6)
    items=[
        ("EJE","EJE DE LINEA",303,92),
        ("POSTES","APOYO P001...P111",303,82),
        ("TERRENO","PERFIL DEM",303,72),
        ("RETENIDA","RETENIDA IDEAL",303,62),
        ("CABLE","CONDUCTOR T/F",358,92),
        ("AGUA","RIO/QUEBRADA",358,82),
        ("VIA","ACCESOS/VIA",358,72),
        ("ALERTA","REVISION",358,62)
    ]
    for capa,n,x,y in items:
        layout.add_line((x,y),(x+10,y),dxfattribs={"layer":capa,"color":256})
        ent=txt(layout,n,x+12,y-0.5,1.65);ent.dxf.layer="TEXTO"
    txt(layout,"EJE DE GABINETE. SIN REPLANTEO.",300,52.8,1.55)
def revision(layout):
    # Marco lateral en blanco, siguiendo formato A01; evitar cambiar elementos originales.
    marco(layout,295,27,406,40)
    for x in (331,369):pol(layout,[(x,27),(x,40)])
    pol(layout,[(295,34),(406,34)])
    for x,h,v in [(298,"REVISION","R03-229"),(335,"ESTADO","REDISENO"),(373,"FECHA","19/10/2026")]:
        txt(layout,h,x,36.2,1.5);txt(layout,v,x,29.3,1.55)
def nueva_lamina(doc):
    if "LP-20" in doc.layouts:raise RuntimeError("LP-20 ya existe")
    lay=doc.layouts.new("LP-20")
    lay.page_setup(size=(420,297),margins=(0,0,0,0),units="mm")
    marco(lay,10,10,410,287)
    for y in (273,252,43):pol(lay,[(10,y),(410,y)])
    txt(lay,"LINEA PRIMARIA LIMBANI - HUANCASAYANI",16,278,4.0)
    txt(lay,"LP-20",363,278,4.0)
    txt(lay,"CRITERIO DE REDISENO ELECTRICO Y CONTROL DE PLANOS",16,260,3.15)
    txt(lay,"22.9 kV NOMINAL ENTRE FASES | 60 Hz | 3 FASES | SISTEMA AISLADO",16,240,3.15)
    txt(lay,"BASE: LP-R02/M01 111 APOYOS, 110 VANOS | GEOMETRIA NO VALIDADA EN CAMPO",16,230,2.25)
    txt(lay,"LEYENDA DE CAPAS",16,210,3.0)
    items={"EJE":"EJE","POSTES":"POSTES","TERRENO":"RELIEVE DEM","CABLE":"CONDUCTOR",
           "RETENIDA":"RETENIDA","AGUA":"AGUA","VIA":"VIA","GRILLA":"UTM","ALERTA":"REVISION"}
    for i,(c,n) in enumerate(items.items()):
        x=20+(i//5)*193;y=194-(i%5)*17
        lay.add_line((x,y),(x+25,y),dxfattribs={"layer":c,"color":256})
        txt(lay,n,x+30,y-1,2.1)
    txt(lay,"CONDICIONES ABIERTAS DE LP-R03",16,86,3.0)
    notes=[
        "T1: V GENERADOR / 22.9 kV. PLACAS, GRUPO Y AISLAMIENTO POR VERIFICAR.",
        "T2: 22.9/0.38 kV SOLO COMO INTERFAZ DE ESTUDIO. TOMAS POR VALIDAR.",
        "LP-01...LP-19 CONTIENEN DATOS DE BASE M01/10 kV: ACTUALIZACION INTEGRAL PENDIENTE.",
        "46 APOYOS CON CARGA ASCENDENTE; P003 P035 P057 CON GIRO MAYOR DE 90 GRADOS.",
        "R02-P019-2: ANCLAJE CON INTERFERENCIA CARTOGRAFICA. REDISENAR EN CAMPO.",
        "AISLAMIENTO, BIL, TIERRAS, PROTECCIONES, GALIBOS Y CIMENTACIONES PENDIENTES.",
        "23 REFERENCIAS DGE SON DOCUMENTALES, NO PLANOS CAC HOMOLOGADOS.",
        "ESTE PLANO NO HABILITA CONSTRUCCION. REQUIERE FIRMA Y REVISION COMPETENTE."
    ]
    for i,s in enumerate(notes):txt(lay,s,17,78-i*5.0,2.05)
    txt(lay,"INSTALACIONES ELECTRICAS II | REVISION LP-R03-229KV",16,27,2.25)
    txt(lay,"A3 / 420 x 297 mm | ESCALA: SIN ESCALA",16,18,2.0)
def generar(entrada,salida,informe):
    if entrada.resolve()==salida.resolve() or salida.exists():raise FileExistsError("Salida ya existe o coincide con origen")
    d=ezdxf.readfile(entrada);base=firma(d)
    if len(base)!=111:raise ValueError(f"Se esperaban 111 apoyos, encontrados {len(base)}")
    refs={x.name:len(x) for x in d.layouts if x.name.startswith("REF-DGE-")}
    if len(refs)!=23:raise ValueError(f"Se esperaban 23 referencias DGE, hay {len(refs)}")
    nombres=[x.name for x in d.layouts if x.name.startswith("LP-")]
    if len(nombres)!=19:raise ValueError(f"Se esperaban 19 planos LP, hay {len(nombres)}")
    for n,(color,lw) in CAPAS.items():
        if n in d.layers:
            capa=d.layers.get(n);capa.color=color;capa.dxf.lineweight=lw
    if CAPA_R03 not in d.layers:d.layers.new(CAPA_R03,dxfattribs={"color":7,"lineweight":18})
    for i in (1,5,6,7,8,9,10,11):leyenda(d.layout(f"LP-{i:02d}"))
    for i in range(1,20):revision(d.layout(f"LP-{i:02d}"))
    nueva_lamina(d)
    if d.audit().errors:raise ValueError("DXF con errores de auditoria")
    salida.parent.mkdir(parents=True,exist_ok=True);d.saveas(salida)
    q=ezdxf.readfile(salida)
    if firma(q)!=base:raise ValueError("Se alteraron postes")
    if {x.name:len(x) for x in q.layouts if x.name.startswith("REF-DGE-")}!=refs:
        raise ValueError("Se alteraron las referencias DGE")
    if q.audit().errors:raise ValueError("DXF resultante con errores")
    rec={"revision":"LP-R03-229KV","tension_diseno_kv":22.9,"apoyos":111,
         "planos_lp":20,"referencias_DGE":23,"origen_sha256":hashlib.sha256(entrada.read_bytes()).hexdigest(),
         "salida_sha256":hashlib.sha256(salida.read_bytes()).hexdigest(),
         "aprobado_para_construccion":False,"tipo":"COPIA GRAFICA PRELIMINAR 22.9kV"}
    if informe:
        informe.parent.mkdir(parents=True,exist_ok=True)
        informe.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return rec
def main():
    p=argparse.ArgumentParser()
    p.add_argument("entrada",type=Path)
    p.add_argument("salida",type=Path)
    p.add_argument("--informe",type=Path)
    a=p.parse_args()
    print(json.dumps(generar(a.entrada,a.salida,a.informe),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
