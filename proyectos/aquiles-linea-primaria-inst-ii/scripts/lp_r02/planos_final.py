"""Presentación de planos: conserva geometría, expresa condiciones sin notas de trabajo."""
from pathlib import Path
import hashlib,json,math,shutil,subprocess,sys
import ezdxf,pymupdf
from ezdxf.addons.drawing import Frontend,RenderContext,layout
from ezdxf.addons.drawing.config import Configuration,BackgroundPolicy,ColorPolicy
from ezdxf.math import BoundingBox2d
from pypdf import PdfReader,PdfWriter
from planos import ExactA3Backend,nota,texto

P=Path(__file__).resolve().parents[2];ROOT=P.parents[1]
B=ROOT/'build'/P.name/'presentacion-final';O=B/'Proyecto_Linea_Primaria'
S=P/'entregables/linea-primaria-r02-presentacion/04-planos'


def main():
    folder=O/'03_Planos';folder.mkdir(exist_ok=True)
    d=ezdxf.readfile(S/'LP_Limbani_Huancasayani_R02.dxf')
    before=postes(d)
    replacements={
        'REVISIÓN ACADÉMICA · CAMPO, EQUIPOS Y PREDIOS PENDIENTES':'PROYECTO ACADÉMICO · SISTEMA AISLADO · GEOMETRÍA DE GABINETE',
        'candidatos':'del corredor','candidato':'de la línea','Retenciones adicionales propuestas:':'Retenciones adicionales:',
        'D/C bajo capacidades supuestas. Vmin negativa: carga ascendente; capacidad axial, fijaciones y suelo pendientes.':'D/C: flexión con capacidad tipo. Vmin negativa: carga ascendente. No incluye verificación axial ni geotecnia.',
        'Tres fases; separación propuesta1.2 m':'Tres fases; separación adoptada 1.2 m',
        'como posiciones ideales pendientes.':'como posiciones geométricas ideales.',
        'cruces pendiente.':'cruces fuera del levantamiento de gabinete.',
        'revisar la propuesta R01.':'conservar el corredor de gabinete del antecedente.',
        'pendiente de placas y decisión10/22.9 kV.':'de cálculo 10 kV; contraste 22.9 kV. Sin placa verificada.',
        'Dexc y geometría por geotecnia':'Dexc: diámetro de excavación',
        'h = empotramiento por cálculo':'h = empotramiento de estudio',
        'datos necesarios para dimensionar':'esquemas y base de cálculo',
    }
    for l in d.layouts:
        if not l.name.startswith('LP-'):continue
        for e in l.query('TEXT'):
            t=e.dxf.text
            for a,b in replacements.items():t=t.replace(a,b)
            e.dxf.text=t
    # Reescribir las notas de los dos cuadros generales, sin alterar la geometría.
    l=d.layouts.get('LP-01')
    for e in list(l.query('TEXT')):
        x,y,_=e.dxf.insert
        if x>=295 and 50<y<262:l.delete_entity(e)
    y=249
    for text in ['Un eje representa la terna: 3 x AAAC 50 mm². Longitud horizontal 6696.369 m.',
                 '111 apoyos y 110 vanos. Geometría del corredor de gabinete, con perfil DEM público de aproximadamente 30 m.',
                 'Círculo naranja: apoyo con carga ascendente en algún estado. No implica aprobación de resistencia ni cimentación.',
                 'T1 y T2: posiciones académicas. Tensión de cálculo 10 kV y contraste 22.9 kV. Sin placas ni predios verificados.',
                 'R02-P019-2: interferencia cartográfica del anclaje ideal. La cota y posición no equivalen a replanteo de campo.',
                 'Cartografía OSM y catastro aportado. No certifica gálibos, cauces, predios ni servidumbres.']:
        y=nota(l,text,298,y,101,2.2)
    l=d.layouts.get('LP-18')
    for e in list(l.query('TEXT')):
        x,y,_=e.dxf.insert
        if x>=151 and 50<y<262:l.delete_entity(e)
    y=249
    for text in ['Esquema conceptual de cimentación y puesta a tierra, sin escala. El metrado contabiliza conjuntos de montaje; la cimentación tipo está incluida en el precio de poste instalado.',
                 'Base geométrica de excavación: Vexc = pi Dexc² h / 4. El volumen neto de concreto descuenta el volumen exterior desplazado por el poste. No se atribuye capacidad geotécnica al esquema.',
                 'La resistencia del anclaje depende del tiro, geometría, arrancamiento, vuelco, deslizamiento, varilla, placa y suelo. Las coordenadas de retenida son geométricas ideales.',
                 'La verificación de puesta a tierra depende de resistividad, corriente y tiempo de falla, tensiones de paso, contacto y transferencia. No se deduce resistencia por un número fijo de varillas.',
                 'La capacidad transversal tipo del poste no constituye comprobación axial ni interacción N-M. Estas verificaciones quedan fuera del modelo de flexión presentado.']:
        y=nota(l,text,151,y,245,2.7)
    l=d.layouts.get('LP-02')
    for e in l.query('TEXT'):
        if 'quedan pendientes' in e.dxf.text:
            e.dxf.text='Esquema funcional. Datos tipo de equipos; la memoria distingue impedancias de estudio y prestaciones reales.'
    target=folder/'Linea_Primaria.dxf';d.saveas(target)
    d=ezdxf.readfile(target);assert postes(d)==before;assert not d.audit().errors
    cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR,min_lineweight=.05)
    writer=PdfWriter()
    for l in d.layouts:
        if not l.name.startswith('LP-'):continue
        backend=ExactA3Backend();Frontend(RenderContext(d),backend,config=cfg).draw_layout(l,finalize=True)
        data=backend.get_pdf_bytes(layout.Page(420,297),settings=layout.Settings(fit_page=False,scale=1,output_layers=True),render_box=BoundingBox2d([(0,0),(420,297)]))
        part=B/(l.name+'.pdf');part.write_bytes(data);writer.append(PdfReader(part),outline_item=l.name)
    with (B/'planos.pdf').open('wb') as f:writer.write(f)
    # Conversión real y reapertura, sin sustituir una extensión.
    work=B/'autocad';work.mkdir(exist_ok=True);dwg=folder/'Linea_Primaria.dwg';back=work/'vuelta.dxf'
    for f in [dwg,back]:
        if f.exists():f.replace(work/(f.stem+'-anterior'+f.suffix))
    exe=Path('C:/Program Files/Autodesk/AutoCAD 2027/accoreconsole.exe')
    for tag,inputfile,command in [('guardar',target,'(command "_.SAVEAS" "_2018" "'+dwg.as_posix()+'")'),('reabrir',dwg,'(command "_.DXFOUT" "'+back.as_posix()+'" "16")')]:
        script=work/(tag+'.scr');script.write_text('(setvar "FILEDIA" 0)\n(setvar "CMDECHO" 0)\n(command "_.AUDIT" "_Y")\n'+command+'\n(command "_.QUIT" "_Y")\n',encoding='ascii')
        result=subprocess.run([str(exe),'/i',str(inputfile),'/s',str(script),'/l','en-US'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
        (work/(tag+'.log')).write_bytes(result.stdout);assert result.returncode==0
    assert dwg.read_bytes()[:6]==b'AC1032';rt=ezdxf.readfile(back);after=postes(rt)
    assert set(before)==set(after) and len(after)==111
    delta=max(math.dist(before[k][0],after[k][0]) for k in before);assert delta<1e-7 and all(before[k][1]==after[k][1] for k in before)
    assert not rt.audit().errors
    sys.path.insert(0,str(ROOT));from herramientas.biblioteca_dge.nativo import stream_signature
    a,la=stream_signature(target,prefixes=('R02_REF_DGE_',));b,lb=stream_signature(back,prefixes=('R02_REF_DGE_',));assert a==b and la==lb
    record=dict(postes=111,laminas=19,referencias_dge=23,delta_xy_m=delta,contornos_y_tipos_coinciden=True,dwg_nativo=True,audit_errores=0)
    (B/'verificacion-cad.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('CAD y planos finales verificados:',record,flush=True)


def postes(doc):return {x.get_attrib_text('ID'):(tuple(x.dxf.insert)[:2],x.get_attrib_text('TIPO')) for x in doc.modelspace().query('INSERT')}


if __name__=='__main__':main()
