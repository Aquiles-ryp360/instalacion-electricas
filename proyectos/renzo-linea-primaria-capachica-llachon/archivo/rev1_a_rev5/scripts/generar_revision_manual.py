"""Cinco láminas de revisión del KML. No sustituye ingeniería constructiva."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lxml import etree
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "plans"
TO_UTM = Transformer.from_crs(4326, 32719, always_xy=True)
NAMES = {
    "CL-01": "Ubicación y corredor manual",
    "CL-02": "Planta e inventario de apoyos GIS cercanos",
    "CL-03": "Perfil longitudinal pendiente de topografía",
    "CL-04": "Simbología y tabla de puntos de inspección",
    "CL-05": "Esquema eléctrico preliminar",
}


def inputs():
    for rel in ("sources/ruta topografica capachica llachon.kml", "datos/estaciones_corredor.csv",
                "datos/ubicaciones_postes_preliminares.csv", "derived/auditoria_corredor_manual.json"):
        if not (ROOT / rel).is_file():
            raise FileNotFoundError(f"Entrada obligatoria ausente: {rel}")
    tree = etree.parse(str(ROOT / "sources/ruta topografica capachica llachon.kml"))
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    lines = []
    for node in tree.xpath("//k:LineString/k:coordinates", namespaces=ns):
        lonlat = [tuple(float(v) for v in t.split(",")[:2]) for t in node.text.split()]
        lines.append([TO_UTM.transform(*p) for p in lonlat])
    with (ROOT / "datos/ubicaciones_postes_preliminares.csv").open(encoding="utf-8-sig", newline="") as f:
        posts = list(csv.DictReader(f))
    with (ROOT / "datos/estaciones_corredor.csv").open(encoding="utf-8-sig", newline="") as f:
        stations = list(csv.DictReader(f))
    report = json.loads((ROOT / "derived/auditoria_corredor_manual.json").read_text(encoding="utf-8"))
    return lines, posts, stations, report


def dxf_sheet(number, lines, posts, stations, report):
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    for name, color in [("KML_MANUAL", 5), ("PUNTOS_GIS_POR_VERIFICAR", 1),
                        ("ROTULO", 7), ("PENDIENTE", 2), ("MARCO", 7)]:
        doc.layers.new(name, dxfattribs={"color": color})
    model = doc.modelspace()
    if number in ("CL-01", "CL-02"):
        for line in lines:
            model.add_lwpolyline(line, dxfattribs={"layer": "KML_MANUAL"})
        for p in posts:
            model.add_circle((float(p["este_m"]), float(p["norte_m"])), 10,
                             dxfattribs={"layer": "PUNTOS_GIS_POR_VERIFICAR"})
        if number == "CL-01":
            model.add_circle(TO_UTM.transform(-69.8316111, -15.6421333), 30,
                             dxfattribs={"layer": "PENDIENTE"})
    layout = doc.layouts.new(number + "_A3")
    layout.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
    layout.add_lwpolyline([(8,8),(412,8),(412,289),(8,289),(8,8)], dxfattribs={"layer":"MARCO"})
    layout.add_line((8,38),(412,38),dxfattribs={"layer":"MARCO"})
    for txt, y, h in [(number + " | " + NAMES[number], 27, 5),
                      ("CAPACHICA - LLACHON | REV 2 | 14 OCT 2026 | A3 horizontal", 19, 3),
                      ("PRELIMINAR - NO APTO PARA CONSTRUCCION | WGS84 / UTM 19S | modelo: m", 12, 2.7)]:
        layout.add_text(txt, dxfattribs={"layer":"ROTULO","height":h}).set_placement((14,y))
    if number in ("CL-01", "CL-02"):
        allxy = [p for line in lines for p in line]
        x0,x1 = min(p[0] for p in allxy), max(p[0] for p in allxy)
        y0,y1 = min(p[1] for p in allxy), max(p[1] for p in allxy)
        h = max((y1-y0)*1.2, (x1-x0)*220/375*1.2)
        layout.add_viewport(center=(205,159),size=(375,220),view_center_point=((x0+x1)/2,(y0+y1)/2),
                            view_height=h)
        layout.add_text("N ^",dxfattribs={"layer":"ROTULO","height":4}).set_placement((370,272))
        layout.add_text("Eje KML manual; cortes entre segmentos sin interpolar",dxfattribs={"layer":"PENDIENTE","height":2.8}).set_placement((14,45))
    else:
        notes = {
            "CL-03": ["Eje horizontal: estación acumulada por segmento KML (m).",
                      "No hay cotas de levantamiento topográfico para este corredor.",
                      "Las 57 muestras SRTM previas siguen al corredor GIS distinto.",
                      "Flechas, vanos y despejes: PENDIENTES."],
            "CL-04": [f"{len(posts)} estructuras GISEM a <=25 m del KML: candidatas a inspección.",
                      "Tipos de alineamiento, ángulo, retención y terminal: PENDIENTES.",
                      "Tabla completa y coordenadas: datos/ubicaciones_postes_preliminares.csv.",
                      "Ningún punto representa un poste nuevo aprobado."],
            "CL-05": ["Punto de alimentación candidato: TMT001868169 (TRAMO GIS).",
                      "Tensión, fases, demanda, conductor y capacidad: SIN CONFIRMAR.",
                      "Protección, seccionamiento, aislamiento y PAT: PENDIENTES.",
                      "Esquema no constructivo; solicitar unifilar y factibilidad a Electro Puno."],
        }[number]
        for i, note in enumerate(notes):
            layout.add_text(note,dxfattribs={"layer":"PENDIENTE","height":3.4}).set_placement((18,258-i*16))
        if number == "CL-03":
            layout.add_line((25,95),(395,95),dxfattribs={"layer":"ROTULO"})
            total = float(stations[-1]["fin_m"])
            for s in stations:
                x = 25 + 370*float(s["inicio_m"])/total
                layout.add_line((x,89),(x,101),dxfattribs={"layer":"ROTULO"})
                layout.add_text(str(s["segmento"]),dxfattribs={"layer":"ROTULO","height":3}).set_placement((x,105))
            layout.add_text("Estaciones (m); elevación no disponible",dxfattribs={"layer":"ROTULO","height":3}).set_placement((115,80))
        if number == "CL-04":
            for i, p in enumerate(posts[:16]):
                col = i//8; row = i%8
                layout.add_text(f"{p['id']}  {p['codigo_gisem']}  PK {float(p['estacion_m']):.1f} m",
                                dxfattribs={"layer":"ROTULO","height":2.8}).set_placement((18+195*col,170-13*row))
    path = OUT / f"{number}_REV2_MANUAL.dxf"
    if path.exists(): raise FileExistsError(path)
    doc.saveas(path)
    check = ezdxf.readfile(path)
    auditor = check.audit()
    if auditor.has_errors or check.header["$INSUNITS"] != 6 or number+"_A3" not in check.layouts:
        raise AssertionError(f"DXF inválido: {path}")
    if number in ("CL-01","CL-02") and len(check.modelspace().query("LWPOLYLINE")) != len(lines):
        raise AssertionError("DXF sin los segmentos KML esperados")
    return path


def raster_sheet(number, lines, posts, stations, report):
    fig = plt.figure(figsize=(16.54,11.69), dpi=150)
    fig.suptitle(f"{number} | {NAMES[number]}", fontsize=20, fontweight="bold", y=.965)
    fig.text(.05,.925,"CAPACHICA - LLACHÓN  |  REV 2  |  14 OCT 2026  |  WGS84 / UTM 19S",fontsize=10)
    fig.text(.05,.045,"BORRADOR CARTOGRÁFICO - NO APTO PARA CONSTRUCCIÓN", color="darkred",fontsize=11,weight="bold")
    if number in ("CL-01","CL-02"):
        ax=fig.add_axes((.06,.10,.88,.78))
        for i,line in enumerate(lines,1):
            ax.plot([p[0] for p in line],[p[1] for p in line],lw=2,label=f"KML segmento {i}")
            ax.scatter([line[0][0],line[-1][0]],[line[0][1],line[-1][1]],s=22)
        if number=="CL-01":
            x,y=TO_UTM.transform(-69.8316111,-15.6421333)
            ax.scatter([x],[y],marker="*",s=160,color="red",label="Conexión candidata")
        else:
            ax.scatter([float(p["este_m"]) for p in posts],[float(p["norte_m"]) for p in posts],
                       s=18,color="red",label=f"{len(posts)} estructuras GIS cercanas")
            for p in posts[::max(1,len(posts)//12)]:
                ax.annotate(p["id"],(float(p["este_m"]),float(p["norte_m"])),fontsize=6)
        ax.set_aspect("equal",adjustable="datalim");ax.grid(alpha=.2)
        ax.set_xlabel("Este UTM 19S (m)");ax.set_ylabel("Norte UTM 19S (m)")
        ax.legend(loc="upper right",fontsize=8)
        ax.text(.01,.02,"N ↑   Fuente: KML manual, GISEM; segmentos no empalmados artificialmente",
                transform=ax.transAxes,fontsize=8,bbox={"facecolor":"white","alpha":.85})
    elif number=="CL-03":
        ax=fig.add_axes((.08,.22,.84,.55));total=float(stations[-1]["fin_m"])
        ax.set_xlim(0,total);ax.set_ylim(0,1);ax.set_yticks([]);ax.set_xlabel("Estación acumulada KML (m)")
        for s in stations:
            ax.axvline(float(s["inicio_m"]),color="gray",ls="--")
            ax.text(float(s["inicio_m"])+20,.65,"S"+str(s["segmento"]))
        ax.text(total/2,.35,"ELEVACIONES NO DISPONIBLES",ha="center",fontsize=18,color="darkred")
        fig.text(.08,.13,"Las muestras SRTM existentes corresponden al corredor GIS, no a estas estaciones manuales.",fontsize=10)
    elif number=="CL-04":
        ax=fig.add_axes((.06,.13,.88,.72));ax.axis("off")
        rows=[[p["id"],p["codigo_gisem"],f"{float(p['estacion_m']):.1f}",
               f"{float(p['distancia_eje_m']):.1f}","Pendiente"] for p in posts]
        table=ax.table(cellText=rows[:30],colLabels=["ID","Código GIS","Estación m","Separación eje m","Tipo"],
                       loc="center",cellLoc="center",colWidths=[.12,.25,.16,.21,.18])
        table.auto_set_font_size(False);table.set_fontsize(7);table.scale(1,1.2)
        fig.text(.08,.08,f"{len(posts)} puntos GIS para inspección; tabla íntegra en CSV. No son postes nuevos aprobados.",fontsize=10)
    else:
        ax=fig.add_axes((.08,.22,.84,.58));ax.axis("off")
        ax.annotate("Tramo GIS\nTMT001868169",(.08,.55),ha="center",va="center",bbox=dict(boxstyle="round",fc="#e8f1f7"),fontsize=13)
        ax.annotate("Alimentador y\nprotección pendientes",(.48,.55),ha="center",va="center",bbox=dict(boxstyle="round",fc="#fff1dc"),fontsize=13)
        ax.annotate("Demanda / red\npor definir",(.88,.55),ha="center",va="center",bbox=dict(boxstyle="round",fc="#fff1dc"),fontsize=13)
        ax.annotate("",(.37,.55),(.19,.55),arrowprops=dict(arrowstyle="->",lw=2))
        ax.annotate("",(.77,.55),(.59,.55),arrowprops=dict(arrowstyle="->",lw=2))
        ax.text(.5,.24,"Esquema conceptual; tensión, fases, conductor, PAT y capacidad sin confirmar.",ha="center",fontsize=12)
    for ext in ("pdf","png"):
        path=OUT/f"{number}_REV2_MANUAL.{ext}"
        if path.exists(): raise FileExistsError(path)
        fig.savefig(path,dpi=150)
    plt.close(fig)


def main():
    lines,posts,stations,report=inputs()
    for number in NAMES:
        dxf_sheet(number,lines,posts,stations,report)
        raster_sheet(number,lines,posts,stations,report)
    print(f"5 DXF + 5 PDF + 5 PNG; {len(posts)} puntos GIS próximos al KML")


if __name__=="__main__": main()
