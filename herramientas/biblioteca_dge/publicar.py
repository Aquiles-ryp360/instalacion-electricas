"""Empaqueta sólo después de las verificaciones; conserva fuentes y condiciones."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from herramientas.biblioteca_dge.generar import *
import zipfile
def main():
    assert (T/'verificacion-biblioteca.json').exists() and (T/'verificacion-dwg.json').exists()
    out=R/'herramientas/biblioteca_dge/entregables';out.mkdir(exist_ok=True)
    names=['fuentes.json','catalogo-armados-MT.json','catalogo-armados-MT.csv','catalogo-armados-BT.json','catalogo-armados-BT.csv','catalogo-complementos.json','catalogo-simbolos.json','verificacion-biblioteca.json','verificacion-dwg.json','verificacion-compactacion.json']
    for name in names:shutil.copy2(T/name,out/name)
    (T/'LEER_PRIMERO.md').write_text('# Biblioteca CAD DGE de consulta\n\n- MT: abrir cad/BIBLIOTECA_DGE_MT_COMPLETA.dwg o un DXF del directorio cad/MT.\n- BT: abrir cad/BIBLIOTECA_DGE_BT_COMPLETA.dwg; la lámina022 aprobada de 2019 está separada en cad/BT.\n- Símbolos: cad/SIMBOLOGIA_DGE_SECCION_9.dwg o DXF. Insertar bloques por código DGE.\n\nLas fuentes PDF y los catálogos por código se incluyen. Los CAD son derivados de esas fuentes, no archivos emitidos por MINEM. Las hojas usan mm de papel, sin coordenadas geográficas; las cotas originales prevalecen sobre medidas del dibujo. MT proviene de escaneos: letras y cotas son contornos editables, no TEXT/DIMENSION.\n\nLa plantilla original de terceros está en terceros/esolutions con las condiciones del fabricante. No adoptar automáticamente materiales de madera como estructuras CAC. Ver README y fuentes para límites y aplicación.\n',encoding='utf-8')
    readme=(R/'herramientas/biblioteca_dge/README.md').read_text(encoding='utf-8').replace('(entregables/','(')
    (T/'README.md').write_text(readme,encoding='utf-8')
    # El DXF maestro MT de334MB es regenerable; se entrega DWG completo y102DXF individuales.
    # Evitar duplicar esos contornos en el ZIP; ningún archivo del paquete depende de ese maestro.
    shutil.copy2(T/'cad/BIBLIOTECA_DGE_MT_COMPLETA.dwg',out/'BIBLIOTECA_DGE_MT_COMPLETA.dwg')
    with (T/'LEER_PRIMERO.md').open('a',encoding='utf-8') as stream:
        stream.write('\nEl DWG maestro MT se ofrece como descarga separada junto al ZIP en GitHub, por su tamaño. El ZIP contiene los 102 DXF individuales MT completos.\n')
    files=[f for f in sorted(T.rglob('*')) if f.is_file() and f.name not in ['BIBLIOTECA_DGE_MT_COMPLETA.dxf','BIBLIOTECA_DGE_MT_COMPLETA.dwg','manifest-paquete.json']]
    manifest=dict(estado='Biblioteca CAD derivada, no emitida por MINEM',mt=102,bt_base=21,bt_complemento2019=1,simbolos=182,archivos=[dict(ruta=f.relative_to(T).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files])
    save_json(T/'manifest-paquete.json',manifest);shutil.copy2(T/'manifest-paquete.json',out/'manifest-paquete.json')
    zpath=out/'Biblioteca_CAD_DGE_Peru.zip'
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for f in files+[T/'manifest-paquete.json']:archive.write(f,'Biblioteca_CAD_DGE_Peru/'+f.relative_to(T).as_posix())
    with zipfile.ZipFile(zpath) as archive:assert archive.testzip() is None
    assert zpath.stat().st_size<99_000_000, 'ZIP excede límite de entrega Git; dividir por familia'
    save_json(out/'verificacion-paquete.json',dict(bytes=zpath.stat().st_size,sha256=hashlib.sha256(zpath.read_bytes()).hexdigest(),archivos=len(files)+1,zip_integro=True))
    (out/'.gitattributes').write_text('** binary\n',encoding='ascii');print('Biblioteca ZIP',zpath.stat().st_size/1e6,'MB',len(files)+1,'archivos',flush=True)
if __name__=='__main__':main()
