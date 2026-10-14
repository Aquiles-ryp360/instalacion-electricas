"""Comprobaciones de conservación, coherencia y entregables del modelo R03."""
from pathlib import Path
import json,csv,math,hashlib,re
from pypdf import PdfReader

P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
OUT=ROOT/'build'/P.name/'r03'


def main():
    r=json.loads((OUT/'calculos-r03.json').read_text(encoding='utf-8'))
    d=r['demanda'];b=r['balance_nominal'];h=r['cfg']['hidraulica'];p=r['presupuesto']
    checks=[]
    def check(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(name)
    check('Operación inicial aislada',r['cfg']['modo']=='aislado' and not r['cfg']['sein_inicial'])
    check('Potencia nominal y pérdidas conservadas',abs(b['residual_kw'])<1e-8 and abs(b['p_bornes_kw']-600)<1e-8)
    check('No se fuerza caudal sobre diseño',0<r['caudal_nominal_m3s']<=h['q_diseno_m3s'])
    check('Censo sin duplicación distrital',d['poblacion_base']==2046 and d['viviendas_base']==946 and d['usuarios_proyectados']==1037)
    check('Potencia en usuarios supera pico solo nominalmente',b['p_usuarios_kw']>d['max_kw'] and r['oferta']['ARNOVIC']['p95_usuarios_kw']<150)
    for name,o in r['oferta'].items():
        check('Balance de energía '+name,abs(o['energia_hidro_servida_mwh']+o['energia_no_cubierta_hidro_mwh']-d['energia_anual_mwh'])<1e-7)
    rows=list(csv.DictReader((OUT/'balance-diario-estimado-r03.csv').open(encoding='utf-8-sig')))
    check('Serie diaria completa 1981-2025',len(rows)==16436 and rows[0]['fecha']=='1981-01-01' and rows[-1]['fecha']=='2025-12-31')
    for v in rows:
        q=float(v['q_natural_estimado_m3s'])
        balance=sum(float(v[k]) for k in ['q_reserva_ecologica_estudio_m3s','q_otros_usos_estudio_m3s','q_posible_turbina_m3s','q_remanente_capacidad_m3s'])
        if abs(q-balance)>1e-9:raise AssertionError('Balance hídrico '+v['fecha'])
        if not 0<=float(v['potencia_disponible_usuarios_kw'])<=b['p_usuarios_kw']+1e-8:raise AssertionError('Potencia fuera de placa')
    check('Conservación hídrica y límites en todos los días',True)
    check('Se detiene MOC rápido ante cavitación',any(v['cavitacion_detectada'] and v['cierre_s']<=1 for v in r['transitorios']))
    check('Cierre lento conserva modelo monofásico ideal',all(not v['cavitacion_detectada'] for v in r['transitorios'] if v['cierre_s']==8))
    check('Malla y geometría consistentes',r['electrico']['pat_malla_longitud_m']==152 and h['diametro_interior_m']==1)
    check('Red débil documentada con seis casos remotos',len(r['electrico']['fallas_remotas_trifasicas'])==6)
    check('Costo directo corresponde a partidas',abs(sum(v['parcial_pen'] for v in p['partidas'])-p['subtotal_pen'])<1e-6)
    check('Costo total con recargos explícitos',abs(p['total_pen']-sum(p[k] for k in ['subtotal_pen','transporte_montaje_pen','estudios_supervision_pen','contingencia_pen']))<1e-6)
    ex=OUT/'expediente'
    pages={}
    for name,expected in [('main',None),('planos-r03',8),('exposicion-r03',13)]:
        pdf=PdfReader(ex/(name+'.pdf'));pages[name]=len(pdf.pages)
        check('Páginas '+name,len(pdf.pages)==expected if expected else len(pdf.pages)>=45)
        log=(ex/(name+'.log')).read_text(encoding='utf-8',errors='replace')
        check('Sin errores de composición '+name,not re.search(r'Overfull|Missing character|Undefined control|Fatal error',log))
    manifest=json.loads((OUT/'manifest-r03.json').read_text(encoding='utf-8'))
    for item in manifest:
        path=Path(item['ruta']);digest=hashlib.sha256()
        with path.open('rb') as file:
            for chunk in iter(lambda:file.read(1024*1024),b''):digest.update(chunk)
        if digest.hexdigest()!=item['sha256']:raise AssertionError('Entrada modificada tras construir: '+str(path))
    check('Huellas de todas las entradas verificadas',True)
    result=dict(comprobaciones=len(checks),estados=checks,paginas=pages,entradas_con_huella=len(manifest),estado='OK')
    (OUT/'verificacion-r03.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
