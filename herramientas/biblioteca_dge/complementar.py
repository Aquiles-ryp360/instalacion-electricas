"""Incorpora el anexo gráfico aprobado de 2019 y su procedencia verificable."""
from herramientas.biblioteca_dge.generar import *
from herramientas.biblioteca_dge.vector_pdf import convert
def main():
    f=S/'rd002-2019-elperuano.pdf';p=pdf.open(f)[1];d=convert(p)
    text(d.modelspace(),'CAD DERIVADO / RD002-2019 / LAMINA022 / mm de hoja',12,11,1.7)
    out=T/'cad/BT/DGE_BT_022_RD002_2019.dxf';d.saveas(out)
    shutil.copy2(f,T/'fuentes'/f.name)
    sources=json.loads((T/'fuentes.json').read_text(encoding='utf-8'));sources=[v for v in sources if v['id']!='DGE-BT-2019']
    sources.append(dict(id='DGE-BT-2019',norma='RD 002-2019-MEM/DGE',archivo=f.name,url='https://busquedas.elperuano.pe/dispositivo/NL/1729284-1',descarga='https://busquedas.elperuano.pe/api/archivo/file/8hHgogfW4yn9xOMJ6kAHt0/*/1729284-1.pdf',sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size,fecha_descarga='2026-10-14',origen='El Peruano 9 enero 2019, páginas39-40; lámina022 aprobada',estado='aprobada'))
    save_json(T/'fuentes.json',sources)
    save_json(T/'catalogo-complementos.json',[dict(familia='BT',lamina='022',titulo='Identificación y codificación',norma='RD002-2019-MEM/DGE',pagina_pdf=2,cad=out.relative_to(T).as_posix(),estado='PDF oficial aprobado de2019; geometría vectorial y textos, no forma parte de las21hojas base2003')])
    print('022complemento',len(d.modelspace()),out.stat().st_size)
if __name__=='__main__':main()
