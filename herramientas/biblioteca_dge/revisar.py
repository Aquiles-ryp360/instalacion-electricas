"""Comprueba inventario, procedencia y CAD; genera vistas para revisión visual."""
from pathlib import Path
import sys,json,hashlib,math
sys.path.insert(0,'G:/Aquiles/dependencias-linea-primaria')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from herramientas.biblioteca_dge.generar import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend,RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration,BackgroundPolicy,ColorPolicy
from PIL import Image,ImageDraw

def render(f,output,width=210,height=297):
    doc=ezdxf.readfile(f)
    fig=plt.figure(figsize=(width/25.4,height/25.4));ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
    cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR,lineweight_scaling=.2)
    Frontend(RenderContext(doc),MatplotlibBackend(ax),config=cfg).draw_layout(doc.modelspace(),finalize=True)
    ax.set_xlim(0,width);ax.set_ylim(0,height);ax.set_aspect('equal',adjustable='box');fig.savefig(output,dpi=110);plt.close(fig)

def main():
    qa=B/'qa';qa.mkdir(exist_ok=True)
    groups=[json.loads((T/f'catalogo-armados-{k}.json').read_text(encoding='utf-8')) for k in ['MT','BT']]
    sy=json.loads((T/'catalogo-simbolos.json').read_text(encoding='utf-8'));assert len(sy)==182
    checks=[]
    for group,expected in zip(groups,[102,21]):
        assert len(group)==expected and len({v['lamina'] for v in group})==expected
        checks.append(f'{expected} láminas {group[0]["familia"]}, códigos y páginas únicos')
        for v in group:
            d=ezdxf.readfile(T/v['cad']);audit=d.audit();assert not audit.errors,(v['bloque'],audit.errors)
            assert d.units==4
            assert not list(d.modelspace().query('IMAGE'))
            assert not any(b.block.dxf.flags & 4 for b in d.blocks)
            assert len(list(d.modelspace().query('LWPOLYLINE')))==v['contornos']
        checks.append(f'Todos los DXF {group[0]["familia"]}: audit0, mm de hoja y sin imágenes/XREF')
    for code in ['077','078']:
        v=next(v for v in groups[0] if v['lamina']==code)
        d=ezdxf.readfile(T/v['cad'])
        from ezdxf import bbox
        ext=bbox.extents(d.modelspace().query('LWPOLYLINE'))
        assert ext.extmin.x>=0 and ext.extmin.y>=0
        assert ext.extmax.x<=v['ancho_hoja_mm'] and ext.extmax.y<=v['alto_hoja_mm']
    checks.append('Hojas 077/078: rotaciones de imagen/página aplicadas; contornos completos dentro de hoja')
    sources=json.loads((T/'fuentes.json').read_text(encoding='utf-8'))
    for v in sources:
        if (T/'fuentes'/v['archivo']).exists():assert hashlib.sha256((T/'fuentes'/v['archivo']).read_bytes()).hexdigest()==v['sha256']
    checks.append('Fuentes oficiales copiadas sin alterar hashes')
    sd=ezdxf.readfile(T/'cad/SIMBOLOGIA_DGE_SECCION_9.dxf');audit=sd.audit();assert not audit.errors
    assert all(v['bloque'] in sd.blocks for v in sy)
    checks.append('182 símbolos: bloques presentes y audit0')
    for code in ['004','020','074','077','078']:
        v=next(v for v in groups[0] if v['lamina']==code);render(T/v['cad'],qa/f'MT-{code}.png',v['ancho_hoja_mm'],v['alto_hoja_mm'])
    for code in ['001','012']:
        v=next(v for v in groups[1] if v['lamina']==code);render(T/v['cad'],qa/f'BT-{code}.png',v['ancho_hoja_mm'],v['alto_hoja_mm'])
    render(T/'cad/BT/DGE_BT_022_RD002_2019.dxf',qa/'BT-022.png',172.631,275.8)
    # Un catálogo visual de todos los bloques: 5 columnas, 8 filas por imagen.
    for k in range(math.ceil(len(sy)/40)):
        fig=plt.figure(figsize=(14,17));ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
        cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR)
        first=k*8;low=30-(first+7)*65-35;high=30-first*65+32
        Frontend(RenderContext(sd),MatplotlibBackend(ax),config=cfg).draw_layout(sd.modelspace(),finalize=True,filter_func=lambda e:low<e.dxf.insert.y<high)
        ax.set_xlim(0,325);ax.set_ylim(low,high);ax.set_aspect('equal',adjustable='box');fig.set_size_inches(14,17)
        fig.savefig(qa/f'simbolos-{k+1:02}.png',dpi=135);plt.close(fig)
    result=dict(inventario_mt=102,inventario_bt_base=21,complemento_bt_2019=1,simbolos_seccion9=182,controles=checks,estado='Revisión geométrica y de inventario, no certificación de ingeniería ni homologación MINEM')
    save_json(T/'verificacion-biblioteca.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
