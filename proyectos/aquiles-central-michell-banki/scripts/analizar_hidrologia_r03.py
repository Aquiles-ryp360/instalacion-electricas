"""Extracción verificable de PISCO; las estimaciones nunca se etiquetan como aforos."""
from pathlib import Path
import sys, json, csv, hashlib, shutil
import numpy as np
from datetime import date
PROY = Path(__file__).resolve().parents[1]
ROOT = PROY.parents[1]
# Dependencias aisladas, instaladas en G: sin modificar Python ni QGIS.
if Path('G:/Aquiles/dependencias-minicentral').exists():
    sys.path.insert(0, 'G:/Aquiles/dependencias-minicentral')
from netCDF4 import Dataset, num2date


def resumen(q):
    values = np.asarray(q, dtype=float)
    return {'n': len(values), 'media_m3s': float(values.mean()),
            'min_m3s': float(values.min()), 'max_m3s': float(values.max()),
            **{f'q{p}_m3s': float(np.quantile(values, 1-p/100, method='linear'))
               for p in [5,10,50,75,90,95,99]}}


def main():
    work = ROOT/'build'/PROY.name/'investigacion'
    sources = PROY/'fuentes/local/investigacion-r03'
    data = PROY/'datos/hidrologia'; data.mkdir(exist_ok=True)
    geom = json.loads((PROY/'datos/topografia-r03.json').read_text(encoding='utf-8'))
    factor = geom['factor_area']
    report = {'comid':9080887, 'indice_netcdf':None,
              'tipo':'Estimación hidrológica exploratoria; no serie medida ni disponibilidad acreditada',
              'fuente_serie':'SENAMHI / Llauca, HydroShare 2026, datos actualizados hasta 2025',
              'factor_area':factor, 'area_captacion_dem_km2':geom['puntos']['captacion_propuesta']['area_km2'],
              'area_salida_pisco_km2':geom['area_salida_pisco_km2'],
              'area_atributo_webmercator_km2':geom['area_atributo_pisco_km2'],
              'correccion_area':geom['correccion_area'],
              'control_area_salida_pct':geom['control_area_salida_pct'],
              'factor_pluviometrico_adoptado':1.0,
              'factor_pluviometrico_estado':'Hipótesis de transferencia, no calibrada: gradiente altitudinal y climático pendiente',
              'metodo':'Transposición exploratoria por área dentro del mismo tramo; PISCO ya regionaliza parámetros por similitud',
              'validada_localmente':False,'modelos':{},
              'limitaciones':['No se dispone de curva nivel-caudal de estación 260501.',
                  'El caudal PISCO corresponde a la salida del tramo, no a cada punto de su eje.',
                  'Área y modelo no calibrados en la captación propuesta; la discrepancia de área impide acreditación.',
                  'Los dos productos comparten forzantes; su contraste no es validación independiente.',
                  'Máximos diarios simulados no son crecidas de diseño ni máximos instantáneos.',
                  'Se separan series diarias ARNOVIC y mensuales GR2M; no se interpolan meses como aforos diarios.']}
    store = {}
    for name, filename in [('ARNOVIC','PISCO_ARNOVIC_v1.1.nc'),('GR2M','PISCO_GR2M_v2.0.nc')]:
        with Dataset(sources/filename) as nc:
            assert nc['flow'].units == 'm3/s'
            ids = np.asarray(nc['comid'][:])
            indexes = np.flatnonzero(ids == report['comid'])
            if len(indexes)!=1: raise ValueError('COMID no es único')
            ix = int(indexes[0]); report['indice_netcdf']=ix
            raw = nc['flow'][:,ix]
            if np.ma.isMaskedArray(raw) and np.ma.getmaskarray(raw).any():
                raise ValueError('Hay caudales faltantes; no rellenar sin método')
            qref = np.asarray(raw, dtype=float)
            if not np.isfinite(qref).all() or (qref<0).any():
                raise ValueError('Serie con valores inválidos')
            ct = num2date(nc['time'][:],nc['time'].units,nc['time'].calendar)
            dates = [date(d.year,d.month,d.day) for d in ct]
            if len(set(dates)) != len(dates) or dates!=sorted(dates):
                raise ValueError('Fechas duplicadas o desordenadas')
            if name=='ARNOVIC' and any((b-a).days!=1 for a,b in zip(dates,dates[1:])):
                raise ValueError('Serie diaria discontinua')
            if name=='GR2M' and any((b.year*12+b.month)-(a.year*12+a.month)!=1 for a,b in zip(dates,dates[1:])):
                raise ValueError('Serie mensual discontinua')
            months=np.array([d.month for d in dates]); qcapt=qref*factor
            outfile=data/('serie_diaria_estimada.csv' if name=='ARNOVIC' else 'serie_mensual_estimada.csv')
            with outfile.open('w',encoding='utf-8',newline='') as f:
                w=csv.writer(f);w.writerow(['fecha','comid','q_salida_modelada_m3s','factor_area','q_captacion_estimada_m3s','tipo_dato','fuente'])
                w.writerows([[d.isoformat(),9080887,repr(float(q)),repr(float(factor)),repr(float(q*factor)),
                    'simulado_y_transpuesto_sin_validacion_local',filename] for d,q in zip(dates,qref)])
            report['modelos'][name]={'archivo':filename,'sha256':hashlib.sha256((sources/filename).read_bytes()).hexdigest(),
                'inicio':dates[0].isoformat(),'fin':dates[-1].isoformat(),'faltantes':0,
                'unidades':'m3/s','resolucion':'diaria' if name=='ARNOVIC' else 'mensual',
                'salida_pisco':resumen(qref),'captacion_estimada':resumen(qcapt),
                'mensual':[{'mes':m,'referencia_media_m3s':float(qref[months==m].mean()),
                    'captacion_media_m3s':float(qcapt[months==m].mean()),
                    'captacion_min_m3s':float(qcapt[months==m].min()),
                    'captacion_q95_m3s':float(np.quantile(qcapt[months==m],.05)),
                    'n':int((months==m).sum())} for m in range(1,13)]}
            store[name]=(dates,qcapt)
    # Comparación temporal justa: medias mensuales de la serie diaria con GR2M.
    dd,qd=store['ARNOVIC']; dm,qm=store['GR2M']
    daily_m={}
    for d,q in zip(dd,qd):daily_m.setdefault((d.year,d.month),[]).append(q)
    agg=np.array([np.mean(daily_m[(d.year,d.month)]) for d in dm])
    report['contraste_mensual']={'n_meses':len(qm),'media_arnovic_m3s':float(agg.mean()),
        'media_gr2m_m3s':float(qm.mean()),'correlacion':float(np.corrcoef(agg,qm)[0,1]),
        'sesgo_relativo_gr2m_vs_arnovic_pct':float(100*(qm.mean()/agg.mean()-1))}
    report['metodo_curva_duracion']='Orden descendente; excedencia Weibull m/(n+1). Cuantiles interpolados linealmente para tablas.'
    (PROY/'datos/hidrologia-r03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Copias originales de respuestas pequeñas y geometría que permiten auditar el enlace espacial.
    for f in ['perfil_rio_srtm90.json','srtm90_rio_respuesta.json','tramos_candidatos.json','cuenca_9080887.geojson']:
        if not (sources/f).exists():shutil.copy2(work/f,sources/f)
    print(json.dumps({'factor_area':factor,'diaria':report['modelos']['ARNOVIC']['captacion_estimada'],
                      'mensual':report['modelos']['GR2M']['captacion_estimada'],
                      'contraste':report['contraste_mensual']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
