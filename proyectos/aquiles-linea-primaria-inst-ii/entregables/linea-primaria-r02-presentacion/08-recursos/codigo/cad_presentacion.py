"""Añade referencias documentales en papel y convierte LP-R02 con AutoCAD real.

No cambia el modelo de la línea ni adopta los armados como detalles constructivos.
"""
from pathlib import Path
import hashlib, io, json, math, subprocess, sys, zipfile
import ezdxf
from ezdxf.addons import Importer

P=Path(__file__).resolve().parents[2]; R=P.parents[1]
sys.path.insert(0,str(R))
from herramientas.biblioteca_dge.nativo import stream_signature
B=R/'build'/P.name/'presentacion-p01'
O=B/'LP_Limbani_Huancasayani'
EXE=Path('C:/Program Files/Autodesk/AutoCAD 2027/accoreconsole.exe')
CODIGOS=['004','008','012','016','020','026','065','065-A','065-B','066','066-A','067','068','069','071','071-A','071-B','073-A','074','076','076-A','077','078-A']


def main():
    source=P/'revisiones/lp-r02/04-planos/LP_Limbani_Huancasayani_R02.dxf'
    target=O/'04-planos'/source.name
    d=ezdxf.readfile(source); original=postes(d)
    catalogo=[]
    with zipfile.ZipFile(R/'herramientas/biblioteca_dge/entregables/Biblioteca_CAD_DGE_Peru.zip') as z:
        catalog=json.loads(z.read('Biblioteca_CAD_DGE_Peru/catalogo-armados-MT.json'))
        for code in CODIGOS:
            row=next(x for x in catalog if x['lamina']==code)
            texto=z.read('Biblioteca_CAD_DGE_Peru/'+row['cad']).decode('utf-8-sig')
            # ezdxf.readfile usa saltos universales; StringIO requiere normalizarlos.
            texto=texto.replace('\r\r\n','\n').replace('\r\n','\n').replace('\r','\n')
            src=ezdxf.read(io.StringIO(texto))
            assert len(src.modelspace())>100,('Referencia vacía',code)
            name='R02_REF_DGE_MT_'+code
            block=d.blocks.new(name); block.block_record.units=4
            importer=Importer(src,d); importer.import_entities(src.modelspace(),target_layout=block); importer.finalize()
            lay=d.layouts.new('REF-DGE-'+code)
            lay.page_setup(size=(row['ancho_hoja_mm'],row['alto_hoja_mm']),margins=(0,0,0,0),units='mm')
            lay.add_blockref(name,(0,0))
            catalogo.append({**row,'layout':'REF-DGE-'+code,'uso':'Referencia documental; no detalle CAC aprobado para LP-R02'})
    assert postes(d)==original and len(original)==111
    assert not d.audit().errors
    d.saveas(target)
    (O/'09-armados-referencia/catalogo-cad.json').write_text(json.dumps(catalogo,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    dwg=target.with_suffix('.dwg'); work=B/'autocad';work.mkdir(exist_ok=True)
    if dwg.exists(): raise FileExistsError('Conversión ya existe; conservar antes de repetir: '+str(dwg))
    ejecutar(target,work,'guardar','(command "_.SAVEAS" "_2018" "'+dwg.as_posix()+'")')
    assert dwg.read_bytes()[:6]==b'AC1032'
    back=work/'vuelta.dxf'
    ejecutar(dwg,work,'reabrir','(command "_.DXFOUT" "'+back.as_posix()+'" "16")')
    result=ezdxf.readfile(back); other=postes(result)
    assert set(original)==set(other)
    delta=max(math.dist(original[k][0],other[k][0]) for k in original)
    assert delta<1e-7 and all(original[k][1]==other[k][1] for k in original)
    before,la=stream_signature(target,prefixes=('R02_REF_DGE_',));after,lb=stream_signature(back,prefixes=('R02_REF_DGE_',))
    assert before==after and la==lb
    assert len([x for x in after if x.startswith('R02_REF_DGE_')])==23
    assert sum(x.name.startswith('LP-') for x in result.layouts)==19
    assert not result.audit().errors
    auditlog=(work/'reabrir.log').read_bytes().decode('utf-16',errors='replace')
    assert 'Total errors found 0 fixed 0' in auditlog
    report=dict(formato='DWG nativo R2018/AC1032',herramienta=str(EXE),postes=111,diferencia_maxima_xy_m=delta,
                tipos_coinciden=True,planos_linea=19,referencias_documentales_dge=23,contornos_coinciden=True,
                audit_errores=0,sha256_dxf=hashlib.sha256(target.read_bytes()).hexdigest(),sha256_dwg=hashlib.sha256(dwg.read_bytes()).hexdigest(),
                alcance='Modelo LP-R02 sin modificación; referencias DGE en layouts separados, sin aprobación de adaptación CAC.')
    (O/'04-planos/verificacion-dwg.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False),flush=True)


def postes(d):
    return {i.get_attrib_text('ID'):(tuple(i.dxf.insert)[:2],i.get_attrib_text('TIPO')) for i in d.modelspace().query('INSERT')}


def ejecutar(entrada,work,tag,comando):
    script=work/(tag+'.scr')
    script.write_text('(setvar "FILEDIA" 0)\n(setvar "CMDECHO" 0)\n(command "_.AUDIT" "_Y")\n'+comando+'\n(command "_.QUIT" "_Y")\n',encoding='ascii')
    run=subprocess.run([str(EXE),'/i',str(entrada),'/s',str(script),'/l','en-US'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
    (work/(tag+'.log')).write_bytes(run.stdout)
    assert run.returncode==0,(tag,run.returncode)


if __name__=='__main__':main()
