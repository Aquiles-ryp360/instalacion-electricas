"""Proyecto QGIS nativo portable sobre la geometría LP-R02; ejecutar con PyQGIS."""
from pathlib import Path
import gc, hashlib, json, math, os, shutil
os.environ['QT_QPA_PLATFORM']='offscreen'
from qgis.core import *
from qgis.PyQt.QtGui import QColor, QFont, QFontDatabase
from qgis.PyQt.QtCore import QSize

P=Path(__file__).resolve().parents[2];R=P.parents[1]
B=R/'build'/P.name/'presentacion-p01';O=B/'LP_Limbani_Huancasayani'
G=O/'04-planos/QGIS'


def main():
    app=QgsApplication([],False);app.initQgis()
    for nombre in ['arial.ttf','arialbd.ttf']:
        font=Path('C:/Windows/Fonts')/nombre
        if font.exists():QFontDatabase.addApplicationFont(str(font))
    construir();gc.collect();app.exitQgis()


def construir():
    G.mkdir(exist_ok=True)
    r=json.loads((O/'03-calculos/resultados.json').read_text(encoding='utf-8'))
    proyecto=QgsProject.instance();proyecto.setCrs(QgsCoordinateReferenceSystem('EPSG:32719'));proyecto.setEllipsoid('NONE')
    original=Path('C:/Users/51949/Downloads/Catastro_Limbani/qgis/Catastro-Limbani.gpkg')
    copia=G/'Catastro-original.gpkg';shutil.copy2(original,copia)
    crs={'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::32719'}}
    ps={p['id']:p for p in r['postes']}
    def feature(tipo,xy,attrs):return dict(type='Feature',geometry=dict(type=tipo,coordinates=xy),properties=attrs)
    def guardar(nombre,items):
        path=G/(nombre+'.geojson');path.write_text(json.dumps(dict(type='FeatureCollection',crs=crs,features=items),ensure_ascii=False),encoding='utf-8');return path
    vanos=guardar('vanos',[feature('LineString',[[ps[v['desde']]['e'],ps[v['desde']]['n']],[ps[v['hasta']]['e'],ps[v['hasta']]['n']]],
        {k:v[k] for k in ['id','desde','hasta','longitud_m','desnivel_m']}) for v in r['vanos']])
    retenidas=guardar('retenidas-ideales',[feature('LineString',[[ps[g['poste']]['e'],ps[g['poste']]['n']],[g['e'],g['n']]],g) for g in r['retenidas']])
    subestaciones=guardar('subestaciones',[feature('Point',[p['e'],p['n']],dict(id=n,estado='PROPUESTA; UBICACION/PLACA/PREDIO PENDIENTES'))
        for n,p in [('T1',r['postes'][0]),('T2',r['postes'][-1])]])
    sources=[('eje',O/'04-planos/eje_R02_UTM19S.geojson'),('postes',O/'04-planos/postes_R02_UTM19S.geojson'),
        ('vanos',vanos),('retenidas-ideales',retenidas),('subestaciones',subestaciones),
        ('curvas-dem',P/'datos/lp-r01/curvas-dem.geojson'),('referencias-osm',P/'datos/lp-r01/referencias-osm.geojson')]
    gpkg=G/'LP-R02.gpkg'
    root=proyecto.layerTreeRoot();lp=root.addGroup('LP-R02 — estudio de gabinete');base=root.addGroup('Catastro original conservado');refs=root.addGroup('Relieve y referencias públicas')
    summary=[];layers=[]
    for i,(nombre,path) in enumerate(sources):
        src=QgsVectorLayer(str(path),nombre,'ogr');assert src.isValid(),nombre
        opciones=QgsVectorFileWriter.SaveVectorOptions();opciones.driverName='GPKG';opciones.layerName=nombre
        opciones.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteFile if i==0 else QgsVectorFileWriter.CreateOrOverwriteLayer
        error=QgsVectorFileWriter.writeAsVectorFormatV3(src,str(gpkg),proyecto.transformContext(),opciones)
        assert error[0]==QgsVectorFileWriter.NoError,error
        layer=QgsVectorLayer(str(gpkg)+'|layername='+nombre,nombre,'ogr');assert layer.isValid()
        if layer.geometryType()==Qgis.GeometryType.Point:
            layer.renderer().setSymbol(QgsMarkerSymbol.createSimple(dict(name='square' if nombre=='subestaciones' else 'circle',color='white',outline_color='#af202d',outline_width='.3',size='3.4' if nombre=='subestaciones' else '1.8')))
            settings=QgsPalLayerSettings();settings.fieldName='id'
            if nombre=='postes':
                settings.fieldName='CASE WHEN @map_scale < 8000 OR to_int(substr("id",2)) % 10 = 1 THEN "id" END';settings.isExpression=True
            text=QgsTextFormat();text.setFont(QFont('Arial',8));text.setSize(8)
            buffer=QgsTextBufferSettings();buffer.setEnabled(True);buffer.setSize(.6);buffer.setColor(QColor('white'));text.setBuffer(buffer);settings.setFormat(text)
            layer.setLabeling(QgsVectorLayerSimpleLabeling(settings));layer.setLabelsEnabled(True)
        else:
            color={'eje':'#b7222a','vanos':'#b7222a','retenidas-ideales':'#cf8a1b','curvas-dem':'#91764d','referencias-osm':'#7c959e'}[nombre]
            layer.renderer().setSymbol(QgsLineSymbol.createSimple(dict(line_color=color,line_width='.55' if nombre=='eje' else '.13')))
        proyecto.addMapLayer(layer,False);(refs if nombre in ['curvas-dem','referencias-osm'] else lp).addLayer(layer);layers.append(layer)
        if nombre in ['vanos','retenidas-ideales']:root.findLayer(layer.id()).setItemVisibilityChecked(False)
        summary.append(dict(capa=nombre,entidades=layer.featureCount(),crs=layer.crs().authid()))
    for nombre,color in [('Calles','#979797'),('Casas','#d8cebd'),('Rios-Cuencas','#4a9dcb')]:
        layer=QgsVectorLayer(str(copia)+'|layername='+nombre,nombre,'ogr');assert layer.isValid(),nombre
        if layer.geometryType()==Qgis.GeometryType.Polygon:layer.renderer().setSymbol(QgsFillSymbol.createSimple(dict(color=color,outline_color='#777777',outline_width='.1')))
        else:layer.renderer().setSymbol(QgsLineSymbol.createSimple(dict(line_color=color,line_width='.25')))
        proyecto.addMapLayer(layer,False);base.addLayer(layer);layers.append(layer)
        summary.append(dict(capa=nombre,entidades=layer.featureCount(),crs=layer.crs().authid(),origen='Original sin modificar'))
    eje=proyecto.mapLayersByName('eje')[0];postes=proyecto.mapLayersByName('postes')[0]
    longitud=sum(f.geometry().length() for f in eje.getFeatures());assert abs(longitud-r['longitud_horizontal_m'])<1e-6
    datos={f['id']:f for f in postes.getFeatures()};assert len(datos)==len(ps)==111
    delta=max(math.dist((datos[k].geometry().asPoint().x(),datos[k].geometry().asPoint().y()),(p['e'],p['n'])) for k,p in ps.items());assert delta<1e-7
    assert all(datos[k]['tipo_r02']==p['tipo_r02'] for k,p in ps.items())
    dem_origen=R/'output/linea-primaria-limbani-huancasayani/qgis/DEM-gabinete-30m.tif'
    if dem_origen.exists():
        dem=G/dem_origen.name;shutil.copy2(dem_origen,dem)
        layer=QgsRasterLayer(str(dem),'DEM público ~30 m — antecedente de gabinete');assert layer.isValid()
        proyecto.addMapLayer(layer,False);refs.addLayer(layer);root.findLayer(layer.id()).setItemVisibilityChecked(False)
    extent=eje.extent();extent.scale(1.15)
    proyecto.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent,proyecto.crs()))
    proyecto.setFilePathStorage(Qgis.FilePathType.Relative);proyecto.setTitle('LP-R02 Limbani–Huancasayani | Línea primaria aislada — revisión académica')
    proyecto.writeEntry('LP-R02','limitaciones','Coordenadas de gabinete; no levantamiento. Tensión y potencia firmes pendientes. R02-P019-2 requiere replanteo. Catastro parcial no acredita servidumbre.')
    file=G/'Linea_Primaria_LP_R02.qgz';assert proyecto.write(str(file))
    config=QgsMapSettings();config.setDestinationCrs(proyecto.crs());config.setExtent(extent);config.setOutputSize(QSize(1000,1500))
    config.setBackgroundColor(QColor('white'));config.setLayers([proyecto.mapLayersByName(n)[0] for n in ['subestaciones','postes','eje','Casas','Calles','Rios-Cuencas','referencias-osm','curvas-dem']])
    job=QgsMapRendererParallelJob(config);job.start();job.waitForFinished();assert job.renderedImage().save(str(G/'vista-general.png'))
    proyecto.clear();assert proyecto.read(str(file));assert all(l.isValid() for l in proyecto.mapLayers().values())
    proyecto.clear();test=B/'qgis-portabilidad';shutil.copytree(G,test,dirs_exist_ok=True);assert proyecto.read(str(test/file.name))
    for layer in proyecto.mapLayers().values():
        assert layer.isValid(),layer.name()
        assert Path(layer.source().split('|')[0]).resolve().is_relative_to(test.resolve()),layer.source()
    informe=dict(version_qgis=Qgis.QGIS_VERSION,crs='EPSG:32719',longitud_horizontal_m=longitud,postes=111,vanos=110,retenidas_ideales=160,
        diferencia_maxima_xy_m=delta,tipos_poste_coinciden=True,catastro_original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
        copia_catastro_sha256=hashlib.sha256(copia.read_bytes()).hexdigest(),capas=summary,capas_validas_tras_traslado=len(proyecto.mapLayers()),rutas_fuera_paquete=0,
        estado='Proyecto QGIS nativo verificado; geometría académica, sin replanteo de campo')
    (G/'verificacion-qgis.json').write_text(json.dumps(informe,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (G/'README.md').write_text('# QGIS LP-R02\n\nAbrir Linea_Primaria_LP_R02.qgz; todas las rutas son relativas. EPSG:32719, WGS 84 / UTM 19S. El eje, los 111 postes, 110 vanos, 160 retenidas ideales y T1/T2 proceden del mismo resultado LP-R02 que el CAD. Una línea representa la terna. El catastro se conserva sin modificación y su cobertura es parcial. Curvas y DEM de gabinete heredados no son levantamiento de campo. Los símbolos de este visor son convenciones cartográficas; la simbología eléctrica se consulta en los planos CAD. Verificación de reapertura y traslado en verificacion-qgis.json.\n',encoding='utf-8')
    proyecto.clear();print(json.dumps(informe,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
