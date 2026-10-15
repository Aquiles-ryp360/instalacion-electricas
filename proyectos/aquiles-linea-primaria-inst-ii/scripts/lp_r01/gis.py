"""Ejecutar mediante python-qgis.bat; paquete QGIS autónomo y sin referencias externas."""
from pathlib import Path
import json,shutil,hashlib,os
os.environ['QT_QPA_PLATFORM']='offscreen'
from qgis.core import *
from qgis.PyQt.QtGui import QColor,QFont
P=Path(__file__).resolve().parents[2];R=P.parents[1];D=P/'datos/lp-r01';O=R/'output/linea-primaria-limbani-huancasayani';G=O/'qgis'
def build_project():
    G.mkdir(parents=True,exist_ok=True);project=QgsProject.instance()
    icons=G/'simbolos';icons.mkdir(exist_ok=True)
    (icons/'SE-DGE-09-90-09.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="30" height="20" viewBox="0 0 30 20"><rect x="1" y="1" width="28" height="18" fill="white" stroke="#a32628" stroke-width="1.5"/><path d="M29 1 L1 10 L29 19" fill="none" stroke="#a32628" stroke-width="1.5"/></svg>',encoding='utf-8')
    project.setCrs(QgsCoordinateReferenceSystem('EPSG:32719'));project.setEllipsoid('NONE')
    original=Path('C:/Users/51949/Downloads/Catastro_Limbani/qgis/Catastro-Limbani.gpkg')
    shutil.copy2(original,G/'Catastro-Limbani-original.gpkg')
    root=project.layerTreeRoot();base=root.addGroup('Catastro original conservado');lp=root.addGroup('Línea primaria proyectada LP-R01');refs=root.addGroup('Referencias públicas de gabinete')
    layers=[];summary=[]
    for name,color in [('Calles','#999999'),('Casas','#ded6ca'),('Rios-Cuencas','#55aada')]:
        layer=QgsVectorLayer(str(G/'Catastro-Limbani-original.gpkg')+'|layername='+name,name,'ogr')
        assert layer.isValid(),name
        if layer.geometryType()==Qgis.GeometryType.Polygon:layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':color,'outline_color':'#888888','outline_width':'0.10'}))
        else:layer.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':color,'line_width':'.3'}))
        project.addMapLayer(layer,False);base.addLayer(layer);layers.append(layer)
        summary.append(dict(capa=name,entidades=layer.featureCount(),crs=layer.crs().authid(),origen='ORIGINAL SIN ALTERAR'))
    ortho=Path('C:/Users/51949/Downloads/Catastro_Limbani/ortofotos/ortofoto_limbani.jpg')
    if not ortho.exists():
        found=list(Path('C:/Users/51949/Downloads/Catastro_Limbani').rglob('ortofoto_limbani.jpg'))
        if found:ortho=found[0]
    if ortho.exists():
        shutil.copy2(ortho,G/ortho.name)
        for ext in ['.jgw','.prj','.jpg.aux.xml']:
            f=ortho.with_suffix(ext) if ext!='.jpg.aux.xml' else Path(str(ortho)+'.aux.xml')
            if f.exists():shutil.copy2(f,G/f.name)
        raster=QgsRasterLayer(str(G/ortho.name),'Ortofoto antecedente, fecha por verificar')
        if raster.isValid():
            raster.setCrs(QgsCoordinateReferenceSystem('EPSG:32719'));project.addMapLayer(raster,False);base.addLayer(raster)
            root.findLayer(raster.id()).setItemVisibilityChecked(False)
    gpkg=G/'LP-Limbani-Huancasayani.gpkg'
    for i,name in enumerate(['linea','vanos','postes','retenidas','subestaciones','cruces','referencias-osm','curvas-dem']):
        source=QgsVectorLayer(str(D/(name+'.geojson')),name,'ogr');assert source.isValid(),name
        options=QgsVectorFileWriter.SaveVectorOptions();options.driverName='GPKG';options.layerName=name
        options.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteFile if i==0 else QgsVectorFileWriter.CreateOrOverwriteLayer
        err=QgsVectorFileWriter.writeAsVectorFormatV3(source,str(gpkg),project.transformContext(),options)
        assert err[0]==QgsVectorFileWriter.NoError,err
        layer=QgsVectorLayer(str(gpkg)+'|layername='+name,name,'ogr');assert layer.isValid()
        if layer.geometryType()==Qgis.GeometryType.Point:
            symbol=QgsMarkerSymbol.createSimple({'name':'triangle' if name=='cruces' else 'circle','color':'#ffffff','outline_color':'#a32625','outline_width':'.35','size':'2.4'})
            if name=='subestaciones':symbol.changeSymbolLayer(0,QgsSvgMarkerSymbolLayer.create({'name':str(icons/'SE-DGE-09-90-09.svg'),'size':'5'}))
            layer.renderer().setSymbol(symbol)
            settings=QgsPalLayerSettings();settings.fieldName='id';text=QgsTextFormat();text.setFont(QFont('Arial',9));text.setSize(9);text.setColor(QColor('#642020'))
            buffer=QgsTextBufferSettings();buffer.setEnabled(True);buffer.setSize(.7);buffer.setColor(QColor('white'));text.setBuffer(buffer);settings.setFormat(text)
            layer.setLabeling(QgsVectorLayerSimpleLabeling(settings));layer.setLabelsEnabled(True)
        else:
            colors={'linea':'#b72528','vanos':'#b72528','retenidas':'#bc8620','referencias-osm':'#94aab5'}
            layer.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':colors.get(name,'#444444'),'line_width':'.6' if name=='linea' else '.25'}))
            if name=='curvas-dem':
                layer.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'#826c47','line_width':'.13'}))
                st=QgsPalLayerSettings();st.fieldName='CASE WHEN "principal" THEN format_number("elev_m",0) END';st.isExpression=True;tf=QgsTextFormat();tf.setFont(QFont('Arial',8));tf.setSize(8);tf.setColor(QColor('#6d5835'));st.setFormat(tf);layer.setLabeling(QgsVectorLayerSimpleLabeling(st));layer.setLabelsEnabled(True)
        project.addMapLayer(layer,False);(refs if name in ['referencias-osm','curvas-dem'] else lp).addLayer(layer);layers.insert(0,layer)
        if name=='vanos':root.findLayer(layer.id()).setItemVisibilityChecked(False)
        summary.append(dict(capa=name,entidades=layer.featureCount(),crs=layer.crs().authid(),origen='PROYECTADO' if name!='referencias-osm' else 'OSM, ODbL'))
    dem=QgsRasterLayer(str(G/'DEM-gabinete-30m.tif'),'DEM público ~30m; curvas derivadas, no campo')
    assert dem.isValid();project.addMapLayer(dem,False);refs.addLayer(dem);root.findLayer(dem.id()).setItemVisibilityChecked(False)
    line=next(v for v in layers if v.name()=='linea');extent=line.extent();extent.scale(1.16)
    project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent,project.crs()))
    project.setFilePathStorage(Qgis.FilePathType.Relative)
    project.setTitle('LP-R01 Limbani - Huancasayani | Diseño académico aislado')
    project.writeEntry('LP-R01','nota','Coordenadas y cotas de gabinete. Postes no levantados. Sin SEIN.')
    layout=QgsPrintLayout(project);layout.initializeDefaults();layout.setName('Ubicación general LP-R01')
    page=layout.pageCollection().pages()[0];page.setPageSize('A3',QgsLayoutItemPage.Landscape)
    item=QgsLayoutItemMap(layout);layout.addLayoutItem(item);item.attemptMove(QgsLayoutPoint(12,25));item.attemptResize(QgsLayoutSize(270,250));item.setLayers(layers);item.zoomToExtent(extent)
    label=QgsLayoutItemLabel(layout);layout.addLayoutItem(label);label.setText('LÍNEA PRIMARIA LIMBANI - HUANCASAYANI\nEPSG:32719 · WGS84 UTM 19S · proyecto académico LP-R01\nCartografía OSM © contribuidores / catastro original\nNo acredita servidumbres, predios ni distancias de campo.');label.attemptMove(QgsLayoutPoint(287,30));label.attemptResize(QgsLayoutSize(115,45))
    project.layoutManager().addLayout(layout);assert project.write(str(G/'LP-Limbani-Huancasayani.qgz'))
    (G/'verificacion-qgis.json').write_text(json.dumps(dict(version=Qgis.QGIS_VERSION,capas=summary,original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),copia_sha256=hashlib.sha256((G/'Catastro-Limbani-original.gpkg').read_bytes()).hexdigest(),longitud_utm_m=sum(f.geometry().length() for f in line.getFeatures())),ensure_ascii=False,indent=2),encoding='utf-8')
    settings=QgsLayoutExporter.ImageExportSettings();settings.dpi=150
    imagefile=G/'vista-general.png'
    if imagefile.exists():imagefile.unlink()
    print('Proyecto guardado; renderizando QGIS',flush=True)
    print('Render QGIS',QgsLayoutExporter(layout).exportToImage(str(imagefile),settings),flush=True)
    project.clear();assert project.read(str(G/'LP-Limbani-Huancasayani.qgz'))
    assert all(l.isValid() for l in project.mapLayers().values())
    print('QGIS guardado y reabierto:',len(project.mapLayers()),'capas válidas')
    project.clear();test=R/'build'/P.name/'lp-r01/prueba-portable'
    shutil.copytree(G,test,dirs_exist_ok=True);assert project.read(str(test/'LP-Limbani-Huancasayani.qgz'))
    checks=[]
    for layer in project.mapLayers().values():
        assert layer.isValid(),layer.name()
        path=layer.source().split('|')[0];assert Path(path).resolve().is_relative_to(test.resolve()),path
        if layer.name()=='subestaciones':assert Path(layer.renderer().symbol().symbolLayer(0).path()).is_file()
        checks.append(layer.name())
    (G/'portabilidad-verificada.json').write_text(json.dumps({'version':Qgis.QGIS_VERSION,'capas_validas_en_copia':checks,'rutas_fuera_paquete':0},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Portabilidad comprobada:',len(checks),'capas')
    project.clear()
def main():
    import gc
    app=QgsApplication([],False);app.initQgis()
    build_project();gc.collect();app.exitQgis()
if __name__=='__main__':main()
