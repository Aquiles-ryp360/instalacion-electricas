"""Delimitación cartográfica exploratoria; originales locales siempre en lectura."""
from pathlib import Path
import sys, gzip, json, shutil, argparse
import numpy as np
from pyproj import Transformer, Geod
from shapely.geometry import shape, Point, mapping
from shapely.geometry.polygon import orient
from shapely import contains_xy
from shapely.ops import transform

PROY = Path(__file__).resolve().parents[1]
ROOT = PROY.parents[1]
sys.path.insert(0, str(ROOT))
from herramientas.hidroelectricas.cuencas_dem import drenaje_d8, cuenca_receptora


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--paso-arcsec',type=int,choices=[1,3],default=3)
    args=parser.parse_args()
    work = ROOT / 'build' / PROY.name / 'investigacion'
    work.mkdir(parents=True,exist_ok=True)
    sources = PROY / 'fuentes/local/investigacion-r03'
    source = sources / 'S15W070-mapzen.hgt.gz'
    if not source.exists():
        raise FileNotFoundError('Recuperar tesela original según H04: '+str(source))
    content = gzip.decompress(source.read_bytes())
    side = int(np.sqrt(len(content) // 2))
    assert side == 3601, (side, len(content))
    full = np.frombuffer(content, dtype='>i2').reshape(side, side)
    # Dominio contiene toda la subcuenca PISCO 9080887 y un margen de relieve.
    # Muestreo cada 3 segundos: aproximadamente 90 m, en vez de 30 m.
    r0, r1 = 20, 1500
    c0, c1 = 550, 1600
    step = args.paso_arcsec
    z = full[r0:r1:step, c0:c1:step].astype(float)
    if (z <= -32000).any():
        raise ValueError('Hay vacíos de elevación; no delimitar sin tratarlos')
    lats = -14 - np.arange(r0, r1, step) / 3600
    lons = -70 + np.arange(c0, c1, step) / 3600
    geod=Geod(ellps='WGS84')
    latref=float(lats.mean());lonref=float(lons.mean())
    dx=geod.inv(lonref,latref,lonref+step/3600,latref)[2]
    dy=geod.inv(lonref,latref,lonref,latref+step/3600)[2]
    filled, rec, acc = drenaje_d8(z, dx, dy)
    xy = Transformer.from_crs(4326, 32719, always_xy=True)
    xx, yy = xy.transform(*np.meshgrid(lons, lats))
    rows = json.loads((sources / 'tramos_candidatos.json').read_text(encoding='utf-8'))
    reference=shape(json.loads((sources/'cuenca_9080887.geojson').read_text(encoding='utf-8'))['geometry'])
    polygons=list(reference.geoms) if hasattr(reference,'geoms') else [reference]
    reference_area=sum(abs(geod.geometry_area_perimeter(orient(poly,sign=1))[0]) for poly in polygons)/1e6
    mercator_area=transform(Transformer.from_crs(4326,3857,always_xy=True).transform,reference).area/1e6
    river = transform(xy.transform, shape(rows[0]['geometria']))
    station = Point(*xy.transform(-69.6902, -14.1481))
    cm = Point(425715, 8436650)
    position = river.project(cm)
    # Punto de derivación aproximado de estudio, NO captación existente verificada.
    capt = river.interpolate(position - 500)
    end = Point(list(list(shape(rows[0]['geometria']).geoms)[0].coords)[-1])
    model_out = Point(*xy.transform(end.x, end.y))
    points = {'captacion_propuesta': capt, 'casa_candidata_cad': cm,
              'estacion_limbani': station, 'salida_tramo_pisco': model_out}
    report = {'dem': f'Mapzen/Terrain Tiles S15W070, HGT 1 segundo, análisis a {step} segundos',
              'datum_horizontal': 'WGS84', 'sistema_trabajo': 'EPSG:32719',
              'vertical': 'Alturas de DEM; datum vertical de la composición no verificado',
              'dx_m': float(dx), 'dy_m': float(dy), 'paso_arcsec': step,
              'area_salida_pisco_km2': reference_area,
              'area_atributo_pisco_km2': rows[0]['Tot_Drain_'] / 1e6,
              'area_poligono_webmercator_km2': mercator_area,
              'correccion_area':'El atributo corresponde a WebMercator; se usa área geodésica WGS84 para comparar con celdas terrestres.',
              'puntos': {}, 'limitaciones': [
                  'Sin acondicionamiento por cauces ni validación de campo.',
                  'El punto de captación es una propuesta cartográfica para el modelo.',
                  'No se usa la cota de una celda como nivel hidráulico medido.',
                  'La delimitación de área no valida los parámetros lluvia-escorrentía de PISCO.']}
    masks = {}
    for name, p in points.items():
        distance = np.hypot(xx - p.x, yy - p.y)
        within = distance <= 250
        # Snap al cauce de mayor acumulación dentro de 250 m, explícito y trazable.
        scores = np.where(within, acc, -1)
        idx = int(np.argmax(scores))
        rr, cc = np.unravel_index(idx, z.shape)
        mask = cuenca_receptora(rec, idx)
        masks[name] = mask
        touching = bool(mask[0].any() or mask[-1].any() or mask[:, 0].any() or mask[:, -1].any())
        if touching:
            raise ValueError('Cuenca truncada por dominio: ' + name)
        report['puntos'][name] = {
            'e_original_m': p.x, 'n_original_m': p.y,
            'lon_snap': float(lons[cc]), 'lat_snap': float(lats[rr]),
            'e_snap_m': float(xx[rr, cc]), 'n_snap_m': float(yy[rr, cc]),
            'snap_m': float(distance[rr, cc]), 'indice_fila': int(rr), 'indice_columna': int(cc),
            'z_celda_m': float(z[rr, cc]), 'area_km2': float(mask.sum() * dx * dy / 1e6),
            'celdas': int(mask.sum()), 'truncada': touching,
            'altitud_media_m': float(z[mask].mean()),
            'altitud_min_m': float(z[mask].min()), 'altitud_max_m': float(z[mask].max())}
        assert int(mask.sum()) == int(acc[rr, cc])
    report['factor_area_dem_ambos'] = (report['puntos']['captacion_propuesta']['area_km2'] /
                                      report['puntos']['salida_tramo_pisco']['area_km2'])
    report['factor_area'] = (report['puntos']['captacion_propuesta']['area_km2'] /
                             report['area_salida_pisco_km2'])
    report['control_area_salida_pct'] = 100 * (
        report['puntos']['salida_tramo_pisco']['area_km2'] /
        report['area_salida_pisco_km2'] - 1)
    report['control_area_aceptado'] = abs(report['control_area_salida_pct']) <= 10
    report['limitaciones'].append(
        'El área D8 en la salida difiere de PISCO. No se considera validada la '
        'transposición por área; solo escenario exploratorio con sensibilidad de sesgo.')
    longrid,latgrid=np.meshgrid(lons,lats)
    within_reference=contains_xy(reference,longrid,latgrid)
    report['control_anidamiento_captacion_fraccion']=float(within_reference[masks['captacion_propuesta']].mean())
    report['altitud_media_poligono_pisco_dem_m']=float(z[within_reference].mean())
    report['area_raster_poligono_pisco_km2']=float(within_reference.sum()*dx*dy/1e6)
    report['control_area_mercator_error_relativo']=mercator_area/report['area_atributo_pisco_km2']-1
    suffix='' if step==3 else '-1arcsec'
    np.savez_compressed(work / ('dem_delimitacion'+suffix+'.npz'), z=z, filled=filled, receiver=rec,
                        accumulation=acc, lats=lats, lons=lons, xx=xx, yy=yy, **masks)
    (PROY / 'datos' / ('topografia-r03'+suffix+'.json')).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
