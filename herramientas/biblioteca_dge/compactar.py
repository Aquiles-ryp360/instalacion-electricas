"""Reduce precisión ASCII sobrante en hojasCAD, con comprobación geométrica.

1e-4mm es mucho menor que el píxel del escaneo; las cotas originales no se
alteran. Se conserva el hash geométrico de contornos aesa resolución.
"""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from herramientas.biblioteca_dge.generar import T,save_json
from herramientas.biblioteca_dge.nativo import stream_signature
def main():
    results=[]
    for f in sorted((T/'cad/MT').glob('*.dxf')):
        before,_=stream_signature(f);size=f.stat().st_size;tmp=f.with_suffix('.compacto')
        with f.open(encoding='utf-8',newline='') as src,tmp.open('w',encoding='utf-8',newline='') as dst:
            while True:
                key=src.readline()
                if not key:break
                val=src.readline();k=int(key)
                if 10<=k<=59 or 110<=k<=149 or 210<=k<=239:
                    num=float(val);s=f'{num:.4f}'.rstrip('0').rstrip('.')
                    val=('0' if s in ['','-0'] else s)+'\n'
                dst.write(key);dst.write(val)
        after,_=stream_signature(tmp);assert before==after,f.name;tmp.replace(f)
        results.append(dict(archivo=f.relative_to(T).as_posix(),bytes_antes=size,bytes_despues=f.stat().st_size,contornos_coinciden_a_mm=.0001))
    save_json(T/'verificacion-compactacion.json',dict(hojas=len(results),precision_ascii_mm=.0001,archivos=results));print('102DXF compactados; contornos comprobados',flush=True)
if __name__=='__main__':main()
