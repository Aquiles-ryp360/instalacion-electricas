"""Incluye las láminas completas de referencia DGE en el CAD del proyecto.

Los bloques de lámina sólo se insertan en espacio papel (mm). El modelo
geográfico permanece en metros UTM19S. No cambia los 111 apoyos ni los vanos.
"""
from pathlib import Path
import sys,json
import ezdxf
from ezdxf.addons import Importer
P=Path(__file__).resolve().parents[2];R=P.parents[1]
sys.path.insert(0,str(Path(__file__).parent))
from adjuntar_armados import SELECTED
O=R/'output/linea-primaria-limbani-huancasayani/cad'
L=R/'build/biblioteca-dge/biblioteca'
def main():
    f=O/'LP_Limbani_Huancasayani_R01.dxf';doc=ezdxf.readfile(f)
    entries=json.loads((L/'catalogo-armados-MT.json').read_text(encoding='utf-8'));by={v['lamina']:v for v in entries}
    mapping=[]
    for j,code in enumerate(SELECTED):
        v=by[code];name=f'AN-{j+1:02}-DGE-{code}';block='LP_REF_'+v['bloque']
        if name in doc.layouts:doc.layouts.delete(name)
        source=ezdxf.readfile(L/v['cad'])
        if block in doc.blocks:target=doc.blocks[block];target.delete_all_entities()
        else:target=doc.blocks.new(block)
        target.block_record.dxf.units=4
        imp=Importer(source,doc);imp.import_entities(source.modelspace(),target_layout=target);imp.finalize()
        lay=doc.layouts.new(name);lay.page_setup(size=(v['ancho_hoja_mm'],v['alto_hoja_mm']),margins=(0,0,0,0),units='mm')
        lay.add_blockref(block,(0,0),dxfattribs={'layer':'DGE_DATOS'})
        mapping.append(dict(layout=name,bloque=block,lamina=code,unidades='mm de hoja, sólo espacio papel',estado='Referencia normativa, adaptación CAC pendiente',pdf='Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf',pagina_anexo='Ver índice y marcadores del PDF'))
    profiles=len([v for v in doc.layouts if v.name.startswith('LP-PF-')])
    assert len(list(doc.layouts))-1==12+profiles+len(SELECTED)
    assert len(list(doc.modelspace().query('INSERT[layer=="LP_POSTES"]')))==111
    assert not doc.audit().errors
    doc.saveas(f)
    (O/'indice-armados-cad.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
    print('CAD:',12+profiles,'láminas del proyecto +',len(mapping),'referencias DGE =',len(list(doc.layouts))-1,'layouts',flush=True)
if __name__=='__main__':main()
