"""Modelo integrado R02; las entradas viven en datos y las salidas solo en build."""
from pathlib import Path
import argparse, csv, hashlib, json, math, shutil, subprocess, sys
PROY=Path(__file__).resolve().parents[1]
ROOT=PROY.parents[1]
sys.path.insert(0,str(ROOT))
from herramientas.hidroelectricas.calculos import (
    hidro, comprobar_longitud, trifasico, transitorio, tirante_normal,
    manning_rectangular, cargas_por_modo, perdidas_transformador,
    balance_exportacion, tubo_mecanico, sedimentador, vertedor, reja)
from figuras_r02 import dibujar


def tex(s):
    return ''.join({'&':r'\&','%':r'\%','_':r'\_','#':r'\#','$':r'\$',
                    '{':r'\{','}':r'\}'}.get(c,c) for c in str(s))


def tabla(cabecera,filas,columnas,caption=None):
    h=' & '.join(cabecera)+r' \\ \midrule'+'\n'
    cap=('\\caption{'+tex(caption)+'}\\\\\n') if caption else ''
    return ('\\begin{longtable}{'+columnas+'}\n'+cap+'\\toprule\n'+h+
        '\\endfirsthead\n\\toprule\n'+h+'\\endhead\n'+
        '\n'.join(' & '.join(map(tex,f))+r' \\' for f in filas)+
        '\n\\bottomrule\n\\end{longtable}\n')


def raiz(funcion,objetivo,bajo=.3,alto=.5):
    if not funcion(bajo)<objetivo<funcion(alto):raise ValueError('Objetivo fuera del intervalo declarado')
    for _ in range(70):
        medio=(bajo+alto)/2
        if funcion(medio)<objetivo:bajo=medio
        else:alto=medio
    return (bajo+alto)/2


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sin-pdf',action='store_true');args=parser.parse_args()
    out=ROOT/'build'/PROY.name;exp=out/'expediente';exp.mkdir(parents=True,exist_ok=True)
    shutil.copytree(PROY/'expediente',exp,dirs_exist_ok=True)
    (exp/'generado').mkdir(exist_ok=True);(exp/'figuras').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'proyectos/aquiles/expediente/figuras/escudo-unap.png',exp/'figuras/escudo-unap.png')
    leer=lambda n:json.loads((PROY/'datos'/n).read_text(encoding='utf-8'))
    cfg=leer('parametros.json');normas=leer('normativa.json');obs=leer('observaciones.json');rev=leer('revision-r02.json')
    b={k:v['valor'] for k,v in cfg['base'].items()};a={k:v['valor'] for k,v in cfg['escenario_objetivo'].items()}
    e=cfg['electrico'];m=cfg['mecanica'];obras=cfg['obras_hidraulicas'];hb=b['z_camara']-b['z_turbina']
    def calc(q,d,longitud=None,salto=None,eps=None,eta_t=None):
        return hidro(q,hb if salto is None else salto,a['longitud'] if longitud is None else longitud,d,
            b['rugosidad'] if eps is None else eps,b['viscosidad'],b['k'],
            b['eta_t'] if eta_t is None else eta_t,b['eta_m'],b['eta_g'])
    modos={n:cargas_por_modo(cfg['auxiliares']['filas'],act) for n,act in cfg['auxiliares']['modos'].items()}
    normal=modos['generacion'];mant=modos['mantenimiento']
    tsa=perdidas_transformador(normal['p_kw'],normal['q_kvar'],e['tsa_kva'],e['tsa_p0_kw'],e['tsa_pcu_kw'])
    paux=normal['p_kw']+tsa['p_kw'];qaux=normal['q_kvar']
    def balance(h):
        return balance_exportacion(h['p_bornes_kw'],e['fp'],paux,qaux,e['placa_kva'],
            e['trafo_p0_kw'],e['trafo_pcu_kw'],e['tension_mt'],
            e['linea_km']*e['r_ohm_km'],e['linea_km']*e['x_ohm_km'])
    def mec(d,p,span=None):
        return tubo_mecanico(d,a['espesor'],a['longitud'],m['tolerancia_fraccion'],m['corrosion_m'],
            m['vano_m'] if span is None else span,p,m['angulo_codo_deg'],m['delta_t_c'],
            m['rho_acero_kg_m3'],e_acero=m['modulo_acero_pa'],alpha=m['alpha_k_inv'])
    ds=[]
    for d in cfg['comparacion_diametros_m']:
        h=calc(a['q'],d);t=transitorio(a['longitud'],h['v_ms'],d,a['espesor'],hb,a['cierre'])
        ds.append(dict(d_m=d,hidraulica=h,balance=balance(h),transitorio=t,
            mecanica_lenta=mec(d,t['p_lento_bar']*1e5),mecanica_rapida=mec(d,t['p_rapido_bar']*1e5)))
    alt=next(r for r in ds if r['d_m']==a['diametro']);ref=next(r for r in ds if r['d_m']==.45)
    h=alt['hidraulica'];bal=alt['balance'];tr=alt['transitorio'];mm=alt['mecanica_lenta']
    original=calc(b['q'],b['diametro'],b['longitud'])
    casos={'Borrador: trazo inválido':original,'Di390 con L revisada':calc(b['q'],b['diametro']),
        'Comparación Di450':ref['hidraulica'],'Estudio prioritario Di500':h}
    geom=comprobar_longitud(cfg['coordenadas_borrador']['camara'],cfg['coordenadas_borrador']['casa'],b['longitud'])
    gen=trifasico(h['p_bornes_kw'],e['fp'],e['tension_bt']);objetivo=cfg['criterio_objetivo']['p_pcc_kw']
    q150={str(d):raiz(lambda q:balance(calc(q,d))['p_pcc_kw'],objetivo) for d in [.45,.5,.55]}
    q_margen=raiz(lambda q:balance(calc(q,a['diametro']))['p_pcc_kw'],objetivo*(1+cfg['criterio_objetivo']['margen_adicional_fraccion']))
    canal=cfg['canal'];yn=tirante_normal(a['q'],canal['b_m'],canal['s_m_m'],canal['n_s_m13'])
    canal_res={**manning_rectangular(canal['b_m'],yn,canal['s_m_m'],canal['n_s_m13']),
        'yn_m':yn,'capacidad_m3s':manning_rectangular(canal['b_m'],canal['y_max_m'],canal['s_m_m'],canal['n_s_m13'])['q_m3s'],
        'borde_libre_m':canal['altura_m']-yn,'tirante_critico_m':(a['q']**2/(9.81*canal['b_m']**2))**(1/3)}
    de=obras['desarenador'];rr=obras['reja'];al=obras['aliviadero']
    obras_res=dict(desarenador=sedimentador(a['q'],de['ancho_m'],de['largo_m'],de['tirante_m'],de['ws_ms'],de['factor']),
        reja_area_m2=reja(a['q'],rr['v_libre_ms'],rr['porosidad'],rr['bloqueo']),
        ancho_vertedor_m=vertedor(a['q'],al['c_m05_s'],al['carga_m']))
    sensibilidad=[]
    for label,mod in [('Base R02',{}),('Caudal -5%',{'q':a['q']*.95}),('Salto bruto -2 m',{'salto':hb-2}),
                     ('Rendimiento turbina 80%',{'eta_t':.8}),('Rugosidad 0.15 mm',{'eps':.00015})]:
        kw=dict(q=a['q'],d=a['diametro']);kw.update(mod);hh=calc(**kw);pp=balance(hh)['p_pcc_kw']
        sensibilidad.append(dict(caso=label,q=hh['q_m3s'],hn=hh['hn_m'],p_pcc_kw=pp,margen_kw=pp-objetivo))
    phb=9.81*a['q']*hb
    libro=[('Potencia hidráulica bruta',phb),('Pérdida de conducción',phb-h['p_hidraulica_kw']),
        ('Pérdida de turbina',h['p_hidraulica_kw']-h['p_turbina_kw']),
        ('Pérdida de transmisión mecánica',h['p_turbina_kw']-h['p_acople_kw']),
        ('Pérdida de generador',h['p_acople_kw']-h['p_bornes_kw']),('Carga eléctrica auxiliar',normal['p_kw']),
        ('Pérdida TSA',tsa['p_kw']),('Pérdida transformador principal',bal['trafo']['p_kw']),
        ('Pérdida línea MT',bal['linea']['perdida_kw']),('Exportación PCC',bal['p_pcc_kw'])]
    residual=libro[0][1]-sum(v for _,v in libro[1:])
    if abs(residual)>1e-9:raise ValueError('No cierra el balance de energía')
    ec=cfg['economia_sensibilidad'];r=ec['tasa_real'];n=ec['anios']
    factor=(1-(1+r)**(-n))/r if r else n
    ganancia=bal['p_pcc_kw']-ref['balance']['p_pcc_kw']
    ganancia_limitada=min(objetivo,bal['p_pcc_kw'])-min(objetivo,ref['balance']['p_pcc_kw'])
    economia=dict(estado='sensibilidad sin tarifa ni cotizacion',factor_anualidad=factor,
        delta_p_kw=ganancia,delta_p_limitada_kw=ganancia_limitada,
        delta_masa_kg=mm['masa_nom_kg']-ref['mecanica_lenta']['masa_nom_kg'],
        filas=[dict(horas=hh,delta_e_kwh=ganancia*hh,delta_e_limitada_kwh=ganancia_limitada*hh,
                    valor_presente_kwh=ganancia*hh*factor) for hh in ec['horas_equivalentes']],
        tarifa_pen_kwh=None,sobrecosto_pen=None)
    resultados=dict(revision=cfg['revision'],estado='anteproyecto condicional',casos=casos,diametros=ds,
        geometria=geom,modos_auxiliares=modos,perdidas_tsa=tsa,generador=gen,balance=bal,
        exportacion_kw=bal['p_pcc_kw'],canal=canal_res,obras_hidraulicas=obras_res,
        caudal_para_150_pcc_m3s=q150,caudal_para_margen_m3s=q_margen,sensibilidad=sensibilidad,
        libro_energia_kw=libro,residuo_energia_kw=residual,economia_sensibilidad=economia,
        energia_anual_mwh=None,datos_impeditivos=cfg['datos_impeditivos'])
    (out/'calculos.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    vals={'Eta':100*h['eta_global'],'POriginalCincuenta':9.81*b['q']*50*h['eta_global'],
        'PBase':original['p_bornes_kw'],'MinLong':geom['minimo_m'],'DiAlt':a['diametro']*1000,
        'VelAlt':h['v_ms'],'ReAlt':h['re'],'FAlt':h['f'],'HfAlt':h['hf_m'],'HlAlt':h['hl_m'],
        'HnAlt':h['hn_m'],'PhAlt':h['p_hidraulica_kw'],'PtAlt':h['p_turbina_kw'],
        'PmAlt':h['p_acople_kw'],'PeAlt':h['p_bornes_kw'],'SGen':gen['s_kva'],'QGen':gen['q_kvar'],'IGen':gen['i_a'],
        'PAuxMax':mant['p_kw'],'QAuxMax':mant['q_kvar'],'SAuxMax':mant['s_kva'],
        'PAuxNormal':normal['p_kw'],'QAuxNormal':normal['q_kvar'],'SAuxNormal':normal['s_kva'],
        'PerdTsa':tsa['p_kw'],'PerdTrafo':bal['trafo']['p_kw'],'PerdLinea':bal['linea']['perdida_kw'],
        'PExport':bal['p_pcc_kw'],'PExportRef':ref['balance']['p_pcc_kw'],
        'MargenExport':bal['p_pcc_kw']-objetivo,'QObjetivo':q150['0.5']*1000,'QObjetivoRef':q150['0.45']*1000,
        'QMargen':q_margen*1000,'VariaLinea':bal['linea']['variacion_pct'],'ILinea':bal['linea']['i_a'],
        'Celeridad':tr['a_ms'],'TCritico':tr['tc_s'],'DHlento':tr['dh_lento_m'],'DHrapido':tr['dh_joukowsky_m'],
        'PLento':tr['p_lento_bar'],'PRapido':tr['p_rapido_bar'],'Tirante':yn,'QCanal':canal_res['capacidad_m3s'],
        'FrCanal':canal_res['fr'],'VCanal':canal_res['v_ms'],'TiranteCritico':canal_res['tirante_critico_m'],
        'BordeLibre':canal_res['borde_libre_m'],'AreaReja':obras_res['reja_area_m2'],'AnchoVertedor':obras_res['ancho_vertedor_m'],
        'EspesorEfectivo':mm['espesor_ef_m']*1000,'MasaTubo':mm['masa_nom_kg'],
        'SigmaLenta':mm['sigma_hoop_mpa'],'SigmaRapida':alt['mecanica_rapida']['sigma_hoop_mpa'],
        'Expansion':mm['expansion_libre_mm'],'TermicaBloqueada':mm['tension_termica_bloqueada_mpa'],
        'GananciaDiametro':ganancia,'DeltaMasa':economia['delta_masa_kg'],'FactorAnualidad':factor,
        'VelChorro':.97*math.sqrt(2*9.81*h['hn_m']),
        'DiametroRodete':60*.48*.97*math.sqrt(2*9.81*h['hn_m'])/(math.pi*900),
        'TorqueTurbina':h['p_turbina_kw']*1000/(2*math.pi*900/60),
        'EspesorChorro':a['q']/(.49*.97*math.sqrt(2*9.81*h['hn_m']))*1000,
        'NsTurbina':900*math.sqrt(h['p_turbina_kw'])/h['hn_m']**1.25,
        'PerdidaCalorGenerador':h['p_acople_kw']-h['p_bornes_kw'],
        'CalorSala':h['p_turbina_kw']-h['p_bornes_kw']+normal['p_kw']+tsa['p_kw']}
    def formato(k,v):
        return (f'{v:.6f}' if k in ['FAlt','DiametroRodete'] else f'{v:.3f}').rstrip('0').rstrip('.')
    (exp/'generado/valores.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+formato(k,v)+'}' for k,v in vals.items()),encoding='utf-8')
    def wt(n,head,rows,cols):
        captions={'escenarios':'Reconstrucción y alternativas con fronteras comunes',
            'diametros':'Comparación hidráulica y exportación por diámetro interior',
            'auxiliares':'Inventario propuesto y cantidades activas por modo',
            'modos_auxiliares':'Carga auxiliar por modo, antes de pérdidas TSA',
            'balance_energia':'Libro de potencia desde recurso bruto hasta PCC',
            'sensibilidad':'Sensibilidades aisladas del punto R02',
            'mecanica':'Cribado de presión, membrana y masa para tres diámetros',
            'apoyos':'Viga horizontal ideal para distintos vanos de estudio',
            'economia_diametro':'Energía marginal de 500 respecto de 450 mm, escenarios propuestos',
            'metrados':'Metrados derivados del escenario R02 y partidas pendientes',
            'matriz':'Matriz normativa: requisito, evidencia y estado'}
        (exp/'generado'/f'{n}.tex').write_text(tabla(head,rows,cols,captions[n]),encoding='utf-8')
    rows=[[k,f"{r['q_m3s']:.3f}",f"{r['l_m']:.0f}",f"{1000*r['d_m']:.0f}",f"{r['hn_m']:.3f}",f"{r['p_bornes_kw']:.3f}"] for k,r in casos.items()]
    wt('escenarios',['Escenario','Q (m$^3$/s)','L (m)','Di (mm)','Hn (m)','P (kW)'],rows,'L{4.5cm}rrrrr')
    rows=[[f"{r['d_m']*1000:.0f}",f"{r['hidraulica']['v_ms']:.3f}",f"{r['hidraulica']['htotal_m']:.3f}",f"{r['hidraulica']['hn_m']:.3f}",f"{r['hidraulica']['p_bornes_kw']:.3f}",f"{r['balance']['p_pcc_kw']:.3f}"] for r in ds]
    wt('diametros',['Di (mm)','v (m/s)','Pérdida (m)','Hn (m)','kW bornes','kW PCC'],rows,'rrrrrr')
    with (out/'comparacion.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['di_mm','v_ms','perdida_m','hn_m','p_bornes_kw','p_pcc_kw']);w.writerows(rows)
    rows=[[f['equipo'],f['cantidad'],f"{f['p_unit_kw']:.2f}",cfg['auxiliares']['modos']['generacion'][f['id']],f"{cfg['auxiliares']['modos']['generacion'][f['id']]*f['p_unit_kw']:.2f}",f"{cfg['auxiliares']['modos']['mantenimiento'][f['id']]*f['p_unit_kw']:.2f}"] for f in cfg['auxiliares']['filas']]
    wt('auxiliares',['Equipo propuesto','Inst.','kW/u','Activas','kW gen.','kW mant.'],rows,'L{6.5cm}rrrrr')
    wt('modos_auxiliares',['Modo','P (kW)','Q (kvar)','S (kVA)'],[[n,f"{v['p_kw']:.3f}",f"{v['q_kvar']:.3f}",f"{v['s_kva']:.3f}"] for n,v in modos.items()],'L{6cm}rrr')
    wt('balance_energia',['Concepto','kW'],[[k,f'{v:.3f}'] for k,v in libro],'L{10.2cm}r')
    wt('sensibilidad',['Hipótesis aislada','Q (m$^3$/s)','Hn (m)','PCC (kW)','Margen (kW)'],[[r['caso'],f"{r['q']:.3f}",f"{r['hn']:.3f}",f"{r['p_pcc_kw']:.3f}",f"{r['margen_kw']:.3f}"] for r in sensibilidad],'L{5.2cm}rrrr')
    wt('mecanica',['Di (mm)','p lenta (bar)','p rápida (bar)','$\\sigma_\\theta$ lenta (MPa)','$\\sigma_\\theta$ rápida (MPa)','Masa (kg)'],[[f"{r['d_m']*1000:.0f}",f"{r['transitorio']['p_lento_bar']:.2f}",f"{r['transitorio']['p_rapido_bar']:.2f}",f"{r['mecanica_lenta']['sigma_hoop_mpa']:.1f}",f"{r['mecanica_rapida']['sigma_hoop_mpa']:.1f}",f"{r['mecanica_lenta']['masa_nom_kg']:.0f}"] for r in ds if r['d_m'] in [.45,.5,.55]],'rrrrrr')
    rows=[]
    for span in [4.,6.,8.]:
        x=mec(a['diametro'],tr['p_lento_bar']*1e5,span)
        rows.append([f'{span:.0f}',f"{x['mmax_kn_m']:.2f}",f"{x['sigma_flexion_mpa']:.2f}",f"{x['flecha_mm']:.2f}",f"{x['reaccion_kn']:.2f}"])
    wt('apoyos',['Vano (m)','M (kN m)','Flexión (MPa)','Flecha (mm)','R/apoyo (kN)'],rows,'rrrrr')
    wt('economia_diametro',['Horas equivalentes','Incremento (kWh)','Con tope 150 kW (kWh)','VP de energía (kWh)'],
        [[x['horas'],f"{x['delta_e_kwh']:.0f}",f"{x['delta_e_limitada_kwh']:.0f}",f"{x['valor_presente_kwh']:.0f}"] for x in economia['filas']],'rrrr')
    with (PROY/'datos/metrados.csv').open(encoding='utf-8-sig',newline='') as f:
        metrados=list(csv.DictReader(f))
    cantidades={'TF01':a['longitud'],'TF02':mm['masa_nom_kg'],'MT01':3*e['linea_km']*1000}
    for partida in metrados:
        if partida['codigo'] in cantidades:partida['cantidad']=f"{cantidades[partida['codigo']]:.3f}"
    with (out/'metrados_calculados.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(metrados[0]));w.writeheader();w.writerows(metrados)
    wt('metrados',['Partida','Unidad','Cantidad','Base y condición'],
        [[p['descripcion'],p['unidad'],p['cantidad'] or 'Pendiente',p['base']+'; '+p['estado']] for p in metrados],
        'L{3.7cm}L{1.6cm}L{2.1cm}L{7cm}')
    wt('matriz',['Regla / artículo','Criterio aplicable','Evidencia y estado'],[[f[0]+' / '+f[1],f[2],f[3]+'. '+f[4]] for f in normas['matriz']],'L{3.2cm}L{5.5cm}L{5.7cm}')
    bib=[r'\subsection*{'+tex(f['id']+' - '+f['titulo'])+'}\n'+tex(f['lectura'])+'\n\n'+r'\href{'+f['url']+'}{Consultar fuente primaria en línea.}\n' for f in normas['fuentes']]
    (exp/'generado/fuentes.tex').write_text('\n'.join(bib),encoding='utf-8')
    audit=[];md=['# Observaciones al borrador recibido','24 hallazgos al borrador; tratamiento actualizado R02. Páginas impresas.']
    for ident,nivel,pag,problema,accion,evidencia in obs:
        audit.append(r'\par\noindent\begin{minipage}{\linewidth}'+'\n'+r'\section{'+tex(ident+' - '+nivel+' - páginas '+pag)+'}\n'+r'\textbf{Hallazgo.} '+tex(problema)+'\n\n'+r'\textbf{Tratamiento.} '+tex(accion)+'\n\n'+r'\textbf{Evidencia.} '+tex(evidencia)+'\n'+r'\end{minipage}\par\vspace{.6em}'+'\n')
        md.extend(['',f'## {ident} | {nivel} | páginas {pag}',problema,'',f'**Tratamiento:** {accion}',f'**Evidencia:** {evidencia}'])
    (exp/'generado/observaciones.tex').write_text('\n'.join(audit),encoding='utf-8');(out/'observaciones.md').write_text('\n'.join(md),encoding='utf-8')
    (exp/'generado/revision-r02.tex').write_text('\n'.join(r'\par\noindent\begin{minipage}{\linewidth}'+'\n'+r'\section{'+tex(f['id']+' - '+f['tema'])+'}\n'+r'\textbf{Hallazgo en R01.} '+tex(f['hallazgo'])+'\n\n'+r'\textbf{Corrección R02.} '+tex(f['correccion'])+'\n\n'+r'\textbf{Validación / límite.} '+tex(f['validacion'])+'\n'+r'\end{minipage}\par\vspace{.6em}' for f in rev),encoding='utf-8')
    inputs=[f for f in sorted(PROY.rglob('*')) if f.is_file() and '__pycache__' not in f.parts]
    inputs+=[ROOT/'herramientas/hidroelectricas/calculos.py',ROOT/'proyectos/aquiles/expediente/figuras/escudo-unap.png']
    inputs+=[ROOT/f['local'] for f in normas['fuentes'] if f.get('local') and (ROOT/f['local']).exists()]
    manifest=[dict(ruta=f.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size) for f in inputs]
    (out/'manifest-entradas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    dibujar(exp,cfg,calc,balance,ds,libro)
    if not args.sin_pdf:
        if not shutil.which('pdflatex'):raise RuntimeError('pdflatex no disponible')
        for doc in ['main.tex','observaciones.tex']:
            for n in range(3 if doc=='main.tex' else 2):
                p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',doc],cwd=exp,capture_output=True)
                (exp/(Path(doc).stem+f'-pasada-{n+1}.txt')).write_bytes(p.stdout+p.stderr)
                if p.returncode:raise RuntimeError(f'Falló LaTeX: {exp/(Path(doc).stem+".log")}')
    print(json.dumps(dict(salidas=str(out),revision=cfg['revision'],p_bornes_kw=gen['p_kw'],p_pcc_kw=bal['p_pcc_kw'],p_aux_kw=normal['p_kw'],perdida_tsa_kw=tsa['p_kw'],residuo_kw=residual),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
