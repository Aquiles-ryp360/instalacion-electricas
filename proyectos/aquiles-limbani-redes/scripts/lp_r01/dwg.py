"""Conversión nativa DXF→DWG y vuelta a DXF con AutoCAD Core Console instalado."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parents[2];R=P.parents[1];O=R/'output/linea-primaria-limbani-huancasayani/cad';B=R/'build'/P.name/'lp-r01/cad'
EXE=Path('C:/Program Files/Autodesk/AutoCAD 2027/accoreconsole.exe')
def run(input_file,script,log):
    process=subprocess.run([str(EXE),'/i',str(input_file),'/s',str(script),'/l','en-US'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    log.write_bytes(process.stdout);print('Core Console',process.returncode,log)
    return process.returncode
def main():
    if not EXE.exists():raise FileNotFoundError(EXE)
    B.mkdir(parents=True,exist_ok=True);dxf=O/'LP_Limbani_Huancasayani_R01.dxf';dwg=O/'LP_Limbani_Huancasayani_R01.dwg'
    script=B/'guardar.scr'
    # LISP evita prompts dependientes del idioma y mantiene formato nativo R2018.
    script.write_text('(setvar "FILEDIA" 0)\n(setvar "CMDECHO" 0)\n(command "_.AUDIT" "_Y")\n(command "_.SAVEAS" "_2018" "'+dwg.as_posix()+'")\n(command "_.QUIT" "_Y")\n',encoding='ascii')
    if dwg.exists():
        # Copia anterior conserva el resultado, sin eliminación recursiva ni tocar originales.
        dwg.rename(B/'DWG-anterior.dwg') if not (B/'DWG-anterior.dwg').exists() else dwg.replace(B/'DWG-anterior.dwg')
    run(dxf,script,B/'guardar.log')
    if not dwg.exists() or dwg.stat().st_size<1000:raise RuntimeError('AutoCAD no produjo DWG válido; revisar log')
    header=dwg.read_bytes()[:6].decode('ascii');assert header=='AC1032',header
    back=B/'verificacion-vuelta.dxf'
    if back.exists():back.unlink()
    script=B/'comprobar.scr'
    script.write_text('(setvar "FILEDIA" 0)\n(setvar "CMDECHO" 0)\n(command "_.AUDIT" "_Y")\n(command "_.DXFOUT" "'+back.as_posix()+'" "16")\n(command "_.QUIT" "_Y")\n',encoding='ascii')
    run(dwg,script,B/'comprobar.log')
    if not back.exists():raise RuntimeError('DWG guardado, pero falta DXF de vuelta para verificar geometría')
    import ezdxf
    original=ezdxf.readfile(dxf);roundtrip=ezdxf.readfile(back)
    def poles(doc):
        return {ins.get_attrib_text('ID'):tuple(ins.dxf.insert)[:2] for ins in doc.modelspace().query('INSERT[layer=="LP_POSTES"]')}
    a,b=poles(original),poles(roundtrip);assert set(a)==set(b)
    maxdiff=max(abs(x-y) for k in a for x,y in zip(a[k],b[k]));assert maxdiff<1e-6,maxdiff
    assert len(list(original.layouts))==len(list(roundtrip.layouts))
    audit=roundtrip.audit();assert not audit.errors
    result=dict(formato='DWG nativo AutoCAD R2018 AC1032',herramienta=str(EXE),postes=len(b),diferencia_maxima_xy_m=maxdiff,
                layouts=len(list(roundtrip.layouts))-1,audit_errores=len(audit.errors),roundtrip=str(back))
    (O/'verificacion-dwg.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
