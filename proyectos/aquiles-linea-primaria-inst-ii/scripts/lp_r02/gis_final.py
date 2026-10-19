"""Normaliza el nombre del GeoPackage y comprueba el QGIS final tras trasladarlo."""
from pathlib import Path
import gc,json,math,os,shutil
os.environ['QT_QPA_PLATFORM']='offscreen'
from qgis.core import QgsApplication,QgsProject,Qgis

P=Path(__file__).resolve().parents[2];ROOT=P.parents[1]
B=ROOT/'build'/P.name/'presentacion-final';G=B/'Proyecto_Linea_Primaria/04_Cartografia/QGIS'


def main():
    app=QgsApplication([],False);app.initQgis();project=QgsProject.instance()
    old=G/'LP-R02.gpkg';new=G/'Linea_Primaria.gpkg';shutil.copy2(old,new)
    filename=G/'Linea_Primaria.qgz';assert project.read(str(filename))
    for layer in project.mapLayers().values():
        source=layer.source()
        if 'LP-R02.gpkg' in source:
            renderer=layer.renderer().clone();labels=layer.labeling().clone() if layer.labeling() else None
            layer.setDataSource(source.replace('LP-R02.gpkg',new.name),layer.name(),'ogr')
            layer.setRenderer(renderer)
            if labels:layer.setLabeling(labels)
        assert layer.isValid(),layer.name()
    project.setFilePathStorage(Qgis.FilePathType.Relative);project.setTitle('Línea primaria Limbani - Huancasayani | Proyecto académico aislado')
    assert project.write(str(filename));project.clear()
    old.replace(B/'geopackage-anterior.gpkg')
    portable=B/'ensayo-qgis-final';shutil.copytree(G,portable,dirs_exist_ok=True)
    assert project.read(str(portable/filename.name))
    for layer in project.mapLayers().values():
        assert layer.isValid(),layer.name()
        assert Path(layer.source().split('|')[0]).resolve().is_relative_to(portable.resolve()),layer.source()
    r=json.loads((P/'revisiones/lp-r02/03-calculos/resultados.json').read_text(encoding='utf-8'))
    posts=project.mapLayersByName('postes')[0];features={f['id']:f for f in posts.getFeatures()};assert len(features)==111
    delta=max(math.dist((features[p['id']].geometry().asPoint().x(),features[p['id']].geometry().asPoint().y()),(p['e'],p['n'])) for p in r['postes']);assert delta<1e-7
    eje=project.mapLayersByName('eje')[0];length=sum(f.geometry().length() for f in eje.getFeatures());assert abs(length-r['longitud_horizontal_m'])<1e-6
    result=dict(version=Qgis.QGIS_VERSION,capas_validas=len(project.mapLayers()),postes=111,diferencia_xy_m=delta,longitud_horizontal_m=length,rutas_externas=0,reabierto_tras_traslado=True)
    (B/'verificacion-qgis-final.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(result,flush=True)
    project.clear();gc.collect();app.exitQgis()


if __name__=='__main__':main()
