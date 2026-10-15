"""GeoTIFF del DEM de presentación, ejecutar con PythonOSGeo4W."""
from pathlib import Path
import json,numpy as np
from osgeo import gdal,osr
P=Path(__file__).resolve().parents[2];R=P.parents[1];B=R/'build'/P.name/'lp-r01';G=R/'output/linea-primaria-limbani-huancasayani/qgis';G.mkdir(exist_ok=True,parents=True)
z=np.load(B/'dem-google-earth.npy');meta=json.loads((P/'datos/lp-r01/topografia-gabinete.json').read_text(encoding='utf-8'));s=osr.SpatialReference();s.ImportFromEPSG(4326)
f=G/'DEM-gabinete-30m.tif';ds=gdal.GetDriverByName('GTiff').Create(str(f),z.shape[1],z.shape[0],1,gdal.GDT_Float32,['COMPRESS=DEFLATE']);ds.SetGeoTransform(meta['geotransform']);ds.SetProjection(s.ExportToWkt());ds.GetRasterBand(1).WriteArray(z);ds.GetRasterBand(1).SetNoDataValue(-32768);ds.FlushCache();ds=None;print('GeoTIFF',f)
