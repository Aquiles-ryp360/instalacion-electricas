"""Convierte y reabre CAD de la biblioteca con AutoCAD, sin simular extensiones."""
from pathlib import Path
import subprocess,json,sys,hashlib,re
import ezdxf
from ezdxf import bbox
R=Path(__file__).resolve().parents[2];B=R/'build/biblioteca-dge';L=B/'biblioteca';EXE=Path('C:/Program Files/Autodesk/AutoCAD 2027/accoreconsole.exe')
def signature(doc):
    names=[b.name for b in doc.blocks if b.name.startswith('DGE_')]
    if not names:names=['*Model_Space']
    values={}
    for name in names:
        b=doc.modelspace() if name=='*Model_Space' else doc.blocks[name]
        pol=[e for e in b if e.dxftype()=='LWPOLYLINE']
        # Contornos geométricos, no handles que AutoCAD modifica al guardar.
        data=sorted(tuple((round(x,4),round(y,4)) for x,y,*_ in e.get_points()) for e in pol)
        values[name]=dict(polilineas=len(pol),vertices=sum(len(e) for e in pol),geometria=hashlib.sha256(repr(data).encode('ascii')).hexdigest())
    return values
def stream_signature(path,prefixes=('DGE_',)):
    """Lee DXF por pares, sin cargar dos maestros de334MB en memoria.

    Polilíneas: conserva la secuencia. HATCH: comprueba el conjunto de puntos
    de sus contornos; AutoCAD puede ordenar y marcar límites al guardar.
    """
    values={};parts={};block=None;section=None;entity=None;pts=[];x=None;layouts=0;is_block_header=False
    def end_entity():
        nonlocal pts,x
        if entity in ['LWPOLYLINE','HATCH'] and block and pts:
            cloud=tuple(sorted(set(pts))) if entity=='HATCH' else tuple(pts)
            parts.setdefault(block,[]).append((entity,cloud))
        pts=[];x=None
    def end_block():
        nonlocal parts
        if block and block in parts:
            data=sorted(parts.pop(block));values[block]=dict(entidades=len(data),geometria=hashlib.sha256(repr(data).encode('ascii')).hexdigest())
    with path.open(encoding='utf-8',errors='replace') as f:
        while True:
            k=f.readline()
            if not k:break
            v=f.readline().strip();k=int(k)
            if k==0:
                end_entity()
                if v=='BLOCK':end_block();block=None;is_block_header=True
                elif v=='ENDBLK':end_block();block=None;is_block_header=False
                elif v=='LAYOUT':layouts+=1
                entity=v
            elif k==2 and entity=='SECTION':
                section=v
                if section=='ENTITIES':block='*Model_Space'
            elif k==2 and is_block_header and entity=='BLOCK':
                block=v if v.startswith(prefixes) else None;is_block_header=False
            elif entity in ['LWPOLYLINE','HATCH']:
                if k==10:x=round(float(v),4)
                elif k==20 and x is not None:pts.append((x,round(float(v),4)));x=None
        end_entity();end_block()
    return values,layouts-1
def main():
    results=[]
    for stem in ['BIBLIOTECA_DGE_MT_COMPLETA','BIBLIOTECA_DGE_BT_COMPLETA','SIMBOLOGIA_DGE_SECCION_9','BT/DGE_BT_022_RD002_2019']:
        src=L/'cad'/(stem+'.dxf');dwg=src.with_suffix('.dwg');tag=src.stem;work=B/'autocad'/tag;work.mkdir(parents=True,exist_ok=True)
        if dwg.exists():dwg.replace(work/'anterior.dwg')
        script=work/'guardar.scr';script.write_text('(setvar "FILEDIA" 0)\n(setvar "CMDECHO" 0)\n(command "_.AUDIT" "_Y")\n(command "_.SAVEAS" "_2018" "'+dwg.as_posix()+'")\n(command "_.QUIT" "_Y")\n',encoding='ascii')
        r=subprocess.run([str(EXE),'/i',str(src),'/s',str(script),'/l','en-US'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600);(work/'guardar.log').write_bytes(r.stdout)
        assert r.returncode==0 and dwg.exists() and dwg.read_bytes()[:6]==b'AC1032',tag
        back=work/'vuelta.dxf'
        if back.exists():back.unlink()
        script=work/'reabrir.scr';script.write_text('(setvar "FILEDIA" 0)\n(setvar "CMDECHO" 0)\n(command "_.AUDIT" "_Y")\n(command "_.DXFOUT" "'+back.as_posix()+'" "16")\n(command "_.QUIT" "_Y")\n',encoding='ascii')
        r=subprocess.run([str(EXE),'/i',str(dwg),'/s',str(script),'/l','en-US'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600);(work/'reabrir.log').write_bytes(r.stdout)
        assert r.returncode==0 and back.exists(),tag
        print('Comparando contornos por lectura secuencial',tag,flush=True)
        a,la=stream_signature(src);b,lb=stream_signature(back)
        assert a==b,(tag,'diferencia en contornos')
        assert la==lb
        log=(work/'reabrir.log').read_bytes().decode('utf-16',errors='replace')
        assert 'Total errors found 0 fixed 0' in log,tag
        rec=dict(archivo=dwg.relative_to(L).as_posix(),formato='DWG nativo R2018/AC1032',herramienta=str(EXE),layouts=lb,bloques_verificados=len(b),entidades_geometricas=sum(v['entidades'] for v in b.values()),geometria_contornos_coincide=True,audit_errores=0,bytes=dwg.stat().st_size)
        results.append(rec);print(json.dumps(rec,ensure_ascii=False),flush=True)
    (L/'verificacion-dwg.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
