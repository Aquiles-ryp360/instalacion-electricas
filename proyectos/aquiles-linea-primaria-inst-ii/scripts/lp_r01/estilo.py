"""Presentación técnica: jerarquía, paleta sobria y tablas claras en espacio papel."""
from pathlib import Path
import json,sys
import ezdxf
P=Path(__file__).resolve().parents[2];R=P.parents[1];O=R/'output/linea-primaria-limbani-huancasayani';D=P/'datos/lp-r01'
def fill(page,x,y,w,h,color):
    obj=page.add_hatch(color=7,dxfattribs={'layer':'PRESENTACION','true_color':color});obj.paths.add_polyline_path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],is_closed=True);return obj
def main(doc=None):
    f=O/'cad/LP_Limbani_Huancasayani_R01.dxf'
    if doc is None:doc=ezdxf.readfile(f)
    if 'PRESENTACION' not in doc.layers:doc.layers.new('PRESENTACION')
    if 'Arial-Bold' not in doc.styles:doc.styles.new('Arial-Bold',dxfattribs={'font':'arialbd.ttf'})
    for name,rgb in [('ROTULO',0x18364A),('DETALLE',0x33434D),('PF_GRID',0xDEE6EA),('PF_COTA',0x367DB4),('PF_EJE_DEM',0x53856E),('PERFIL_TERRENO',0x976F49),('PERFIL_CONDUCTOR',0xC53643)]:
        if name in doc.layers:doc.layers.get(name).dxf.true_color=rgb
    a=json.loads((D/'resultados.json').read_text(encoding='utf-8'));summary=json.loads((D/'perfiles-explicitos.json').read_text(encoding='utf-8'))
    for lay in doc.layouts:
        if lay.name=='Model' or lay.name.startswith('AN-'):continue
        for ent in list(lay.query('*[layer=="PRESENTACION"]')):lay.delete_entity(ent)
        backgrounds=[fill(lay,8,263,404,27,0xEEF4F7),fill(lay,8,8,404,15,0xEEF4F7),fill(lay,8,263,3,27,0x287D89)]
        for en in lay.query('TEXT'):
            if en.dxf.insert.y>=275:en.dxf.style='Arial-Bold';en.dxf.true_color=0x18364A
            if en.dxf.text=='NO APTO PARA CONSTRUCCIÓN SIN ESTUDIOS DE CAMPO':
                en.dxf.text='Proyecto académico | coordenadas y cotas de gabinete | verificación de campo pendiente';en.dxf.height=2.5;en.dxf.true_color=0x526B7B
        if lay.name.startswith('LP-PF-'):
            k=int(lay.name[-2:])-1;info=summary[k];n=len(info['vanos']);cell=349/n
            backgrounds += [fill(lay,14,64,390,7,0xE6EEF2),fill(lay,14,37,390,27,0xF6F8FA),fill(lay,291,133,112,19,0xEEF4F7)]
            critical=info['vanos'].index(info['vano_critico_75']);backgrounds.append(fill(lay,50+critical*cell,37,cell,34,0xFFF1D8))
            for en in lay.query('TEXT'):
                if 64<=en.dxf.insert.y<=70:en.dxf.style='Arial-Bold'
                if en.dxf.text.startswith('DETALLE DEL VANO'):en.dxf.style='Arial-Bold';en.dxf.true_color=0x18364A
            for row in range(8):lay.add_line((14,37+row*5),(404,37+row*5),dxfattribs={'layer':'PRESENTACION','true_color':0xDEE6EA})
            for j in range(n+1):lay.add_line((50+j*cell,37),(50+j*cell,71),dxfattribs={'layer':'PRESENTACION','true_color':0xDEE6EA})
        # Los fondos se dibujan antes del contenido; sus handles de orden son válidos.
        lay.set_redraw_order({v.dxf.handle:format(i+1,'X') for i,v in enumerate(backgrounds)})
    doc.saveas(f);print('Estilo aplicado a19láminas, fuentesArial y paleta técnica;23DGE sin alterar')
    return doc
if __name__=='__main__':main()
