"""Controles independientes entre resultados, CAD, DWG, GIS, CSV y PDFs."""
from pathlib import Path
import json,math,csv,hashlib,sqlite3,sys
sys.path.insert(0,'G:/Aquiles/dependencias-linea-primaria')
import pymupdf
import ezdxf
from pypdf import PdfReader
from shapely.geometry import shape
P=Path(__file__).resolve().parents[2];R=P.parents[1];D=P/'datos/lp-r01';O=R/'output/linea-primaria-limbani-huancasayani'
def main():
    a=json.loads((D/'resultados.json').read_text(encoding='utf-8'));c=json.loads((D/'parametros.json').read_text(encoding='utf-8'))
    ps=a['postes'];vs=a['vanos'];cs=a['cantones'];checks=[]
    def check(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(name)
    check('111 IDs de poste únicos y110vanos',len(ps)==111 and len(vs)==110 and len({p['id'] for p in ps})==111)
    check('Identificadores consecutivos',all(p['id']==f'P{i+1:03}' for i,p in enumerate(ps)) and all(v['id']==f'V{i+1:03}' for i,v in enumerate(vs)))
    check('Continuidad de cada vano',all(v['desde']==ps[i]['id'] and v['hasta']==ps[i+1]['id'] for i,v in enumerate(vs)))
    check('Longitudes geométricas independientes',all(abs(v['longitud_m']-math.hypot(ps[i+1]['e']-ps[i]['e'],ps[i+1]['n']-ps[i]['n']))<1e-7 for i,v in enumerate(vs)))
    check('Longitud de eje=vanos=progresiva final',abs(sum(v['longitud_m'] for v in vs)-a['linea_longitud_m'])<1e-6 and abs(ps[-1]['progresiva_m']-a['linea_longitud_m'])<1e-6)
    check('Eje sin autointersecciones',shape(a['geometria']).is_simple)
    check('Vanos10–85m sin apoyos casi coincidentes',all(10<v['longitud_m']<=85.00001 for v in vs))
    check('Cantones de retención<600m',all(v['longitud_m']<=600 for v in cs) and len(cs)==sum(p['retencion'] for p in ps)-1)
    check('Seis estados por vano',all(set(v['estados'])=={s['id'] for s in c['clima']} for v in vs))
    check('Residuo mecánico de conservación de longitud',max(abs(s['residuo_longitud_m']) for ct in cs for s in ct['estados'].values())<1e-7)
    check('Margen>=7.5m frente a envolventeDEM, sin certificarcampo',min(s['distancia_dem_min_m'] for v in vs for s in v['estados'].values())>=7.5)
    check('Tensión máxima<40%RTS, objetivo de estudio',max(s['tension_max_n'] for v in vs for s in v['estados'].values())<.4*c['conductor']['rts_n'])
    check('Flexión poste tipo dentro de capacidad supuesta',max(p['utilizacion_poste'] for p in ps)<1)
    check('Retenidas dimensionadas con resistencia0.9',all(g['tiro_estudio_kn']<=.9*g['resistencia_rotura_kn'] for g in a['retenidas']))
    check('No postes/anclajes sobre eje de cauce buffer8m de estudio',all(p['distancia_cauce_m']>=8 for p in ps) and all(g['distancia_cauce_m']>=8 for g in a['retenidas']))
    check('No sobrevuelo de casas del catastro+4m',a['trazado']['cruces_inmuebles_m']<.01)
    check('Armados especiales>90grados identificados',all(p['armado']=='ESP-RET' for p in ps if p['angulo_deg']>90))
    el=a['electrico'];bu=a['presupuesto']
    check('Demanda353usuarios y171.486kW',el['usuarios']==353 and abs(el['p_usuarios_kw']-171.486)<1e-7)
    check('Balance de potencia con pérdidas y auxiliares',abs(el['p_generador_necesaria_kw']-el['p_usuarios_kw']-el['perdida_tx_salida_kw']-el['perdida_tx_llegada_kw']-el['perdida_linea_kw']-5)<1e-6)
    check('FlujoPQ convergente',el['flujo_pq']['residuo_v']<1e-6)
    check('Caso base BT dentro de objetivo±5%',abs(el['flujo_pq']['desviacion_bt_pct'])<5)
    check('Conductor capacidad de estudio holgada',el['corriente_250kva_a']<el['ampacidad_modelo_a'])
    check('Falla sostenida menor a carga, protege51V',next(f['ik3_a'] for f in el['fallas'] if f['estado']=='SOSTENIDO' and f['punto']=='SE-HUA_MT')<el['corriente_demanda_a'])
    check('ReservaLimbani25kW reporta déficit',next(s['margen_kw'] for s in el['reservas'] if s['reserva_limbani_kw']==25)<0)
    check('Metrado conductor3fases+catenaria+reserva',bu['partidas'][0]['cantidad']==math.ceil(3*sum(v['estados']['EDS']['longitud_conductor_m'] for v in vs)*1.03))
    check('Presupuesto corresponde a partidas',abs(sum(v['parcial_pen'] for v in bu['partidas'])-bu['directo_pen'])<1e-5)
    cad=ezdxf.readfile(O/'cad/LP_Limbani_Huancasayani_R01.dxf');audit=cad.audit()
    check('DXFsin errores de auditoría',not audit.errors);check('DXFmetros INSUNITS6',cad.header['$INSUNITS']==6)
    ins=list(cad.modelspace().query('INSERT[layer=="LP_POSTES"]'));byid={i.get_attrib_text('ID'):i for i in ins}
    check('CAD IDs coinciden con cálculo',set(byid)=={p['id'] for p in ps})
    check('CAD XY y altura/armado coinciden',all(abs(byid[p['id']].dxf.insert.x-p['e'])<1e-7 and abs(byid[p['id']].dxf.insert.y-p['n'])<1e-7 and byid[p['id']].get_attrib_text('ARMADO')==p['armado'] and float(byid[p['id']].get_attrib_text('POSTE_M'))==p['poste_m'] for p in ps))
    check('Un eje MT, sin tres líneas paralelas en planta',len(list(cad.modelspace().query('LWPOLYLINE[layer=="LP_EJE"]')))==1 and 'LP_CONDUCTORES' not in cad.layers)
    check('Todas las funciones dibujan círculo CACnormativo',all(len(list(cad.blocks['LP_'+kind].query('CIRCLE')))==1 for kind in ['SUSPENSION','ANGULO','ANCLAJE','TERMINAL']))
    check('128 retenidas en CAD',len(list(cad.modelspace().query('INSERT[layer=="LP_RETENIDAS"]')))==len(a['retenidas']))
    se=list(cad.modelspace().query('INSERT[layer=="LP_SE"]'));check('DosSE identificadas en CAD',set(v.get_attrib_text('ID') for v in se)=={'SE-LIM','SE-HUA'})
    check('19láminas del proyecto y23 referencias DGE en CAD',len(list(cad.layouts))-1==42)
    dwg=json.loads((O/'cad/verificacion-dwg.json').read_text(encoding='utf-8'))
    check('DWG nativo reabierto: coordenadas y 23 referencias DGE conservadas',dwg['postes']==111 and dwg['diferencia_maxima_xy_m']<1e-6 and dwg['audit_errores']==0 and dwg['referencias_dge_verificadas']==23 and dwg['contornos_referencias_y_modelo_coinciden'])
    check('DWGencabezadoAC1032',(O/'cad'/dwg['archivo']).read_bytes()[:6]==b'AC1032' and dwg['layouts']==42)
    gis=json.loads((O/'qgis/verificacion-qgis.json').read_text(encoding='utf-8'));portable=json.loads((O/'qgis/portabilidad-verificada.json').read_text(encoding='utf-8'))
    check('QGISlongitud idéntica a cálculo',abs(gis['longitud_utm_m']-a['linea_longitud_m'])<1e-6)
    check('Catastro original no modificado',gis['original_sha256']==gis['copia_sha256'])
    check('QGISportable reabierto13capas',len(portable['capas_validas_en_copia'])==13 and portable['rutas_fuera_paquete']==0)
    con=sqlite3.connect(O/'qgis/LP-Limbani-Huancasayani.gpkg')
    rows=con.execute('SELECT id,e,n,poste_m,armado FROM postes').fetchall();con.close()
    gr={r[0]:r[1:] for r in rows};check('GPKG IDs ycoordenadas/armados iguales a CAD',set(gr)==set(byid) and all(math.isclose(gr[p['id']][0],p['e'],abs_tol=1e-7) and math.isclose(gr[p['id']][1],p['n'],abs_tol=1e-7) and gr[p['id']][2]==p['poste_m'] and gr[p['id']][3]==p['armado'] for p in ps))
    with (O/'tablas/postes.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    check('CSVcoincide111IDs yalturas',len(rows)==111 and all(row['id']==p['id'] and float(row['poste_m'])==p['poste_m'] for row,p in zip(rows,ps)))
    originals=json.loads((P/'fuentes/local/lp-r01/antecedente/manifest-originales.json').read_text(encoding='utf-8'))
    backup=P/'fuentes/local/lp-r01/antecedente'
    check('Copias originales conservan cinco hashes',all(hashlib.sha256((backup/Path(v['ruta']).name).read_bytes()).hexdigest()==v['sha256'] for v in originals))
    pages={}
    for suffix in ['expediente','calculos','planos']:
        f=R/f'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_{suffix}.pdf';reader=PdfReader(f);pages[suffix]=len(reader.pages)
        check('PDF'+suffix+'válido',len(reader.pages)>0)
    anexo=PdfReader(R/'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf')
    presentation=json.loads((D/'presentacion-academica.json').read_text(encoding='utf-8'))
    check('Expediente integra memoria completa, anexo27 y planos19',pages['expediente']==presentation['hojas_memoria']+len(anexo.pages)+pages['planos'] and pages['calculos']==presentation['hojas_calculos'] and len(anexo.pages)==27 and pages['planos']==19)
    vector=pymupdf.open(R/'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf')
    check('Anexo de armados sin imágenes raster',all(not p.get_images(full=True) for p in vector))
    check('23 láminas A3 con geometría PDF vectorial',all(len(p.get_drawings())>5 and abs(min(p.rect.width,p.rect.height)-297*72/25.4)<.1 and abs(max(p.rect.width,p.rect.height)-420*72/25.4)<.1 for p in list(vector)[4:]))
    check('23referencias DGE identificadas en CAD',len([v for v in cad.layouts if v.name.startswith('AN-')])==23)
    import zipfile,xml.etree.ElementTree as ET
    from pyproj import Transformer
    ns={'k':'http://www.opengis.net/kml/2.2'}
    with zipfile.ZipFile(O/'google-earth/LP_Limbani_Huancasayani_R01.kmz') as z:
        check('KMZ íntegro y recursos internos',z.testzip() is None and all(f'files/PF-{i:02}.png' in z.namelist() for i in range(1,8)))
        root=ET.fromstring(z.read('doc.kml'));folder=next(n for n in root.findall('.//k:Folder',ns) if n.find('k:name',ns).text.startswith('02 |'))
        transformer=Transformer.from_crs(4326,32719,always_xy=True);kmzp={}
        for node in folder.findall('k:Placemark',ns):
            key=node.find('k:name',ns).text.split(' /')[0];lo,la,_=map(float,node.find('k:Point/k:coordinates',ns).text.split(','));kmzp[key]=transformer.transform(lo,la)
        check('111postes KMZ coinciden con CAD/cálculo enUTM',set(kmzp)==set(byid) and all(math.dist(kmzp[p['id']],(p['e'],p['n']))<.001 for p in ps))
    curves=json.loads((D/'curvas-dem.geojson').read_text(encoding='utf-8'))['features']
    check('208curvas y68niveles DEM20/100m',len(curves)==208 and len({v['properties']['elev_m'] for v in curves})==68 and all(v['properties']['elev_m']%20==0 for v in curves))
    result=dict(revision='LP-R01',controles_aprobados=len(checks),controles=checks,paginas=pages,
        advertencia='Controles del modelo y coherencia documental; no sustituyen campo, certificados, permisos ni ajustes de relés')
    (O/'verificacion-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'controles_aprobados':len(checks),'paginas':pages},ensure_ascii=False))
if __name__=='__main__':main()
