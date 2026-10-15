"""Construye memoria, planos y apoyo de exposición del proyecto académico R03."""
from pathlib import Path
import argparse, json, csv, shutil, subprocess, hashlib, math, re
import numpy as np
from modelo_r03 import model, PROY, ROOT, read_json
from presupuesto_r03 import calcular as presupuesto


def texto(s):
    s=str(s).replace('–','-').replace('—','-').replace('\u2011','-')
    return ''.join({'&':r'\&','%':r'\%','_':r'\_','#':r'\#','$':r'\$',
        '{':r'\{','}':r'\}'}.get(c,c) for c in s)


def prosa(s):
    """Normaliza separación de símbolos en fichas antiguas, sin cambiar URLs o IDs."""
    s=str(s)
    s=re.sub(r'(?<=[a-záéíóúñ])(?=[A-ZÁÉÍÓÚÑ])',' ',s)
    s=re.sub(r'(?<=[a-zA-Záéíóúñ])(?=\d)',' ',s)
    s=re.sub(r'(\d)(kW|kVA|kV|mm|m3|m2|l/s|W|A|V|Hz|p\b)',r'\1 \2',s)
    s=re.sub(r'(kW|kVA|kV|mm|m3|m2|l/s|W|A|V|Hz)(?=[a-záéíóúñ])',r'\1 ',s)
    s=re.sub(r'([,;:])(?=[A-Za-záéíóúñ])',r'\1 ',s)
    s=s.replace('sinSEIN','sin SEIN').replace('sinfuente','sin fuente').replace('artículo','artículo ')
    return s


def table(headers, rows, widths, caption=None):
    cols=''.join('L{'+str(w)+'cm}' for w in widths)
    header=' & '.join(headers)+r' \\ \midrule'+'\n'
    caption=('\\caption{'+texto(caption)+'}\\\\\n') if caption else ''
    return ('\\begin{longtable}{'+cols+'}\n'+caption+'\\toprule\n'+header+
        '\\endfirsthead\n\\toprule\n'+header+'\\endhead\n'+
        '\n'.join(' & '.join(texto(x) for x in row)+r' \\' for row in rows)+
        '\n\\bottomrule\n\\end{longtable}\n')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sin-pdf',action='store_true');args=parser.parse_args()
    out=ROOT/'build'/PROY.name/'r03';exp=out/'expediente'
    (exp/'generado').mkdir(parents=True,exist_ok=True);(exp/'figuras').mkdir(exist_ok=True)
    for fn in ['main.tex','main-r03.tex','preambulo.tex','planos-r03.tex','exposicion-r03.tex']:
        if (PROY/'expediente'/fn).exists():shutil.copy2(PROY/'expediente'/fn,exp/fn)
    if (PROY/'expediente/r03').exists():shutil.copytree(PROY/'expediente/r03',exp/'r03',dirs_exist_ok=True)
    shutil.copy2(ROOT/'recursos/identidad/escudo-unap.png',exp/'figuras/escudo-unap.png')
    for source,target in [('ubicacion_departamento_puno.jpg','ubicacion-puno.jpg'),
                          ('ubicacion_provincia_sandia.jpg','ubicacion-sandia.jpg')]:
        shutil.copy2(ROOT/'recursos/ubicacion/limbani'/source,exp/'figuras'/target)
    r,series,hc,balance=model();p=presupuesto(r);r['presupuesto']=p
    cfg=r['cfg'];h=cfg['hidraulica'];e=cfg['electrico'];g=cfg['grupo'];o=cfg['obras'];m=cfg['mecanica'];a=cfg['auxiliares']
    hyd=r['hidrologia'];geo=read_json('topografia-r03.json');norm=read_json('normativa-r03.json');sources=read_json('fuentes-r03.json')
    (out/'calculos-r03.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def wt(name,headers,rows,widths,caption):
        (exp/'generado'/f'{name}.tex').write_text(table(headers,rows,widths,caption),encoding='utf-8')
    def f(x,n=2):return f'{x:.{n}f}'
    dn=r['demanda'];rn=r['nominal'];bn=r['balance_nominal'];of=r['oferta']['ARNOVIC'];eg=r['electrico']
    slow=next(t for t in r['transitorios'] if t['estado_pared']=='fin_vida' and t['cierre_s']==m['cierre_s'])
    fast=next(t for t in r['transitorios'] if t['estado_pared']=='fin_vida' and t['cierre_s']==0)
    rod=60*.48*.97*math.sqrt(2*9.81*rn['hn_m'])/(math.pi*g['velocidad_rpm'])
    vals={'Hb':h['salto_bruto_m'],'Hn':rn['hn_m'],'Qdesign':h['q_diseno_m3s'],'Qnom':r['caudal_nominal_m3s'],
          'Qunit':r['caudal_nominal_m3s']/g['unidades'],'LongPipe':h['longitud_presion_m'],'Di':h['diametro_interior_m']*1000,
          'Vel':rn['v_ms'],'Re':rn['re'],'Fdarcy':rn['f'],'Hf':rn['hf_m'],'Hloc':rn['hl_m'],
          'Ph':rn['p_hidraulica_kw'],'Pt':rn['p_turbina_kw'],'Pacople':rn['p_acople_kw'],'PG':bn['p_bornes_kw'],
          'Pusers':bn['p_usuarios_kw'],'Paux':bn['aux_kw'],'Qaux':bn['aux_kvar'],'LossCable':bn['cables_perdida_kw'],
          'LossTsa':bn['tsa']['p_kw'],'LossT1':bn['balance_mt']['trafo']['p_kw'],'LossMT':bn['balance_mt']['linea']['perdida_kw'],
          'LossSED':bn['sed']['p_kw'],'PMT':bn['balance_mt']['p_pcc_kw'],
          'Demand':dn['max_kw'],'Dom':dn['domestica_kw'],'AP':dn['alumbrado_kw'],'Special':dn['servicios_kw'],
          'Users':dn['usuarios_proyectados'],'PopBase':dn['poblacion_base'],'PopProj':dn['poblacion_proyectada'],
          'VivsBase':dn['viviendas_base'],'Eload':dn['energia_anual_mwh'],'DailyE':dn['energia_diaria_kwh'],
          'LoadFactor':dn['factor_carga']*100,'EHidro':of['energia_hidro_servida_mwh'],
          'Epotential':of['energia_disponible_mwh'],'Edef':of['energia_no_cubierta_hidro_mwh'],
          'HydroShare':100*of['fraccion_energia_hidro'],'Pfirmstudy':of['p95_usuarios_kw'],
          'PMin':of['p_min_usuarios_kw'],'DaysZero':of['dias_sin_generacion_equiv_anual'],
          'PJulMean':of['mensual'][6]['p_media_usuarios_kw'],'PJulLow':of['mensual'][6]['p95_usuarios_kw'],
          'Qmean':hyd['modelos']['ARNOVIC']['captacion_estimada']['media_m3s'],
          'Qlow':hyd['modelos']['ARNOVIC']['captacion_estimada']['q95_m3s'],
          'Qmin':hyd['modelos']['ARNOVIC']['captacion_estimada']['min_m3s'],
          'Qhigh':hyd['modelos']['ARNOVIC']['captacion_estimada']['max_m3s'],
          'Aref':hyd['area_salida_pisco_km2'],'Acapt':hyd['area_captacion_dem_km2'],
          'Amerc':hyd['area_atributo_webmercator_km2'],'Alpha':hyd['factor_area'],
          'ElevationLocal':geo['puntos']['captacion_propuesta']['altitud_media_m'],
          'ElevationRef':geo['altitud_media_poligono_pisco_dem_m'],
          'ControlArea':geo['control_area_salida_pct'],'NestedPct':100*geo['control_anidamiento_captacion_fraccion'],
          'PmonthlyLow':r['oferta']['GR2M']['p95_usuarios_kw'],
          'MonthlyBias':hyd['contraste_mensual']['sesgo_relativo_gr2m_vs_arnovic_pct'],
          'CanalY':r['obras']['canal']['yn_m'],'CanalV':r['obras']['canal']['v_ms'],
          'CanalFr':r['obras']['canal']['fr'],'CanalCap':r['obras']['canal']['capacidad_m3s'],
          'CanalFree':r['obras']['canal']['borde_libre_m'],'RejaArea':r['obras']['reja_area_m2'],
          'VertAncho':r['obras']['aliviadero_ancho_m'],'CamSeconds':r['obras']['reserva_camara_s'],
          'EspEf':(m['espesor_nominal_m']*(1-m['tolerancia'])-m['corrosion_m'])*1000,
          'PNslow':slow['max_global_bar'],'PNfast':fast['max_global_bar'],
          'SigmaHoop':r['mecanica']['sigma_hoop_mpa'],'SigmaVM':r['acciones']['sigma_vm_membrana_mpa'],
          'SigmaAllow':r['acciones']['admisible_estudio_mpa'],'MassPipe':r['mecanica']['masa_nom_kg']/1000,
          'Expansion':r['acciones']['expansion_m']*1000,'AnchorVol':r['acciones']['volumen_gravedad_equiv_m3'],
          'Iunit':eg['ig_unitaria_a'],'Ibus':eg['i_bus_placa_a'],'Itrafo':eg['i_trafo_placa_bt_a'],
          'IKH':eg['ik_hidro_inicial_a']/1000,'IKB':eg['ik_respaldo_inicial_a']/1000,
          'IKmax':eg['ik_barra_max_a']/1000,'IKMT':eg['ik_mt_hidro_inicial_a'],
          'DropMT':bn['balance_mt']['linea']['variacion_pct'],'DropBT':eg['bt_rama']['variacion_pct'],
          'DropCable':eg['cable_generador']['variacion_pct'],'DCtime':eg['autonomia_cc_h'],
          'PBackupUsers':eg['respaldo_usuarios_kw'],'Rodete':rod*1000,
          'Torque':(rn['p_turbina_kw']/g['unidades'])*1000/(2*math.pi*g['velocidad_rpm']/60),
          'JetWidth':r['caudal_nominal_m3s']/g['unidades']/(.75*.97*math.sqrt(2*9.81*rn['hn_m']))*1000,
          'Heat':r['ventilacion']['calor_estudio_kw'],'AirFlow':r['ventilacion']['caudal_aire_m3s'],
          'FanPower':r['ventilacion']['potencia_ventiladores_requerida_kw'],
          'CapexM':p['total_pen']/1e6,'CapexLowM':p['rango_costo_pen'][0]/1e6,'CapexHighM':p['rango_costo_pen'][1]/1e6,
          'Lcoe':p['costo_equilibrio_pen_kwh'],'DieselE':p['energia_respaldo_bornes_kwh_anio']/1000,
          'DieselLitres':p['combustible_l_anio']/1000,'FuelCostM':p['combustible_pen_anio']/1e6,
          'OpexM':p['opex_sin_combustible_pen_anio']/1e6,'AreaHouse':o['casa_l_m']*o['casa_b_m'],
          'Margin':bn['p_usuarios_kw']-dn['max_kw']}
    integers={'Users','PopBase','PopProj','VivsBase','Di','LongPipe','Re','AreaHouse'}
    decimals={'Fdarcy':6,'Alpha':4,'Qmin':3,'Qlow':3,'Qnom':3,'Qunit':3,'Qdesign':2,'Hf':3,'Hloc':3,'Di':0,
              'Vel':3,'Re':0,'SigmaHoop':1,'SigmaVM':1,'SigmaAllow':1,'PNslow':2,'PNfast':2}
    texvals=[]
    for key,value in vals.items():
        text=f(value,0 if key in integers else decimals.get(key,2))
        texvals.append(r'\expandafter\def\csname dato'+key+r'\endcsname{'+text+'}')
    (exp/'generado/valores.tex').write_text('\n'.join(texvals)+'\n',encoding='utf-8')
    wt('poblacion',['Localidad / código INEI','Habitantes 2017','Viviendas ocupadas','Usuarios 2026','Demanda doméstica (kW)'],
        [[v['nombre']+' / '+v['codigo'],v['poblacion'],v['viviendas_ocupadas'],v['usuarios_potenciales_proyectados'],f(v['demanda_kw'],1)] for v in dn['filas']],
        [4.8,1.8,2.1,1.8,2.3],'Población censada y escenario de conexiones potenciales, sin duplicar el total distrital')
    wt('proyeccion',['Año','Usuarios potenciales','Pico de escenario (kW)'],
        [[v['anio'],v['usuarios'],f(v['demanda_kw'],1)] for v in dn['proyecciones']],
        [2,5,5],'Crecimiento supuesto: viviendas 1% anual y consumo por usuario 1.5% anual desde 2026')
    wt('servicios',['Servicio propuesto','P coincidente (kW)','Factor de potencia'],
        [[v['nombre'],f(v['kw_coincidente'],1),f(v['fp'])] for v in cfg['demanda']['servicios']],
        [7,3,3],'Cargas comunitarias y productivas hipotéticas, pendientes de inventario')
    wt('hidro_estadisticas',['Producto / escala','Media','Q50','Q90','Q95','Mínimo','Máximo'],
        [[name+' / '+('diaria' if name=='ARNOVIC' else 'mensual')]+[f(hyd['modelos'][name]['captacion_estimada'][key],3) for key in ['media_m3s','q50_m3s','q90_m3s','q95_m3s','min_m3s','max_m3s']] for name in ['ARNOVIC','GR2M']],
        [3.5,1.6,1.6,1.6,1.6,1.6,1.6],'Caudales transpuestos de estudio (m3/s). Excedencias de distinta resolución no son intercambiables')
    wt('hidro_meses',['Mes','Q natural medio','Q utilizable medio','P95 usuarios','P mínima','E disponible','E hidro servida'],
        [[v['mes'],f(v['q_media_m3s'],3),f(v['q_usable_m3s'],3),f(v['p95_usuarios_kw'],1),f(v['p_min_usuarios_kw'],1),f(v['energia_disponible_mwh'],1),f(v['energia_servida_mwh'],1)] for v in of['mensual']],
        [.7,2,2.1,2,1.6,2.1,2.1],'Escenario diario ARNOVIC: Q en m3/s, P en kW, energía climatológica en MWh/mes normalizado')
    wt('alternativas',['Hidro instalada','Unidades','Máximo usuarios','P95 diario','E servida','Déficit hidro'],
        [[f(v['potencia_instalada_kw'],0),v['unidades'],f(v['p_max_usuarios_kw'],1),f(v['p95_usuarios_kw'],1),f(v['energia_hidro_servida_mwh'],1),f(v['energia_deficit_mwh'],1)] for v in r['alternativas']],
        [2,1.7,2.4,2,2.2,2.2],'Comparación de potencia (kW) y energía anual (MWh), con fronteras y demanda comunes')
    wt('sesgo',['Factor sobre caudal estimado','P95 usuarios (kW)','E servida (MWh/año)','Déficit (MWh/año)'],
        [[f(v['factor_sesgo']),f(v['p95_kw'],1),f(v['energia_servida_mwh'],1),f(v['energia_deficit_mwh'],1)] for v in r['sensibilidad_sesgo']],
        [3.7,3,3.5,3],'Sensibilidad al sesgo de transposición; factores de estudio, sin intervalo estadístico de confianza')
    wt('diametros',['Di (mm)','v (m/s)','Pérdidas (m)','Hn (m)','Potencial bornes (kW)','Masa nominal (t)'],
        [[f(v['di_m']*1000,0),f(v['hidraulica']['v_ms'],2),f(v['hidraulica']['htotal_m'],2),f(v['hidraulica']['hn_m'],2),f(v['hidraulica']['p_bornes_kw'],1),f(v['mecanica']['masa_nom_kg']/1000,1)] for v in r['diametros']],
        [1.5,1.8,2.1,1.8,3,2.3],'Comparación a Q máximo de diseño 1.90 m3/s, 350 m y espesor nominal 16 mm')
    wt('auxiliares',['Equipo','Instalados','kW/unitario','Activos a plena carga','P a plena carga (kW)'],
        [[v['equipo'],v['cantidad'],f(v['p_unit_kw']),3 if v['id']=='GOB' else cfg['auxiliares']['activas_base'][v['id']],f(v['p_unit_kw']*(3 if v['id']=='GOB' else cfg['auxiliares']['activas_base'][v['id']]),2)] for v in a['filas']],
        [5.6,1.8,2.1,2.4,2],'Inventario auxiliar propuesto; una bomba de drenaje en reserva, sin mantenimiento simultáneo')
    wt('fallas_remotas',['Condición hidráulica','SED (kVA)','I fin MT (A)','I BT SED (A)','I fin BT (A)'],
        [[v['estado'],f(v['sed_kva'],0),f(v['ik_mt_fin_a'],1),f(v['ik_sed_bt_a'],1),f(v['ik_bt_fin_a'],1)]
         for v in eg['fallas_remotas_trifasicas']],
        [4.1,2,2.3,2.6,2.6],'Fallas trifásicas de estudio: MT 8 km y rama BT 150 m; uk SED supuesto 4%, sin SEIN ni motores')
    wt('balance',['Frontera / pérdida','Potencia (kW)'],[[name,f(value,2)] for name,value in bn['libro_kw']],
        [10.7,3],'Balance desde bornes hasta usuarios en el sistema aislado, con cargas y pérdidas separadas')
    wt('moc',['Estado pared','Cierre (s)','Máxima válida (bar)','Mínima válida (bar)','Fin válido / s','Límite del modelo'],
        [[t['estado_pared'].replace('_',' '),f(t['cierre_s'],1),f(t['max_global_bar'],2),f(t['min_global_bar'],2),f(t['duracion_valida_s'],2),
          'Cavitación: se detiene' if t['cavitacion_detectada'] else 'Monofásico en perfil ideal'] for t in r['transitorios']],
        [2.6,1.3,2.3,2.3,1.7,3.5],'MOC a 1.90 m3/s: no se publican presiones posteriores a la ruptura del modelo monofásico')
    wt('apoyos',['Vano (m)','Momento (kN m)','Flexión (MPa)','Flecha (mm)','R por apoyo (kN)'],
        [[f(v['vano_m'],0),f(v['mmax_kn_m'],2),f(v['sigma_flexion_mpa'],2),f(v['flecha_mm'],2),f(v['reaccion_kn'],2)] for v in r['apoyos']],
        [1.6,2.7,2.7,2.5,3],'Viga ideal bajo agua y peso propio, pared efectiva y cierre controlado')
    wt('tierra',['Resistividad supuesta (ohm m)','Rg aproximada (ohm)','GPR para 10 A (V)'],
        [[f(v['rho_ohm_m'],0),f(v['rg_screen_ohm'],2),f(v['gpr_screen_v'],1)] for v in eg['pat_sensibilidad']],
        [4.8,4.4,4.2],'Sensibilidad de tierra. GPR no equivale a tensión de contacto ni certifica seguridad')
    wt('presupuesto',['Partida','Unidad','Cantidad','PU estimado S/','Parcial S/ mil'],
        [[v['descripcion'],v['unidad'],f(v['cantidad'],1),f(v['precio_unitario_pen'],0),f(v['parcial_pen']/1000,1)] for v in p['partidas']],
        [6.2,1.4,2,2.2,2.4],'Presupuesto académico: cantidades derivadas y precios de partidas estimados, sin cotización firme')
    wt('resumen_costos',['Concepto','S/ millones'],
        [[label,f(p[key]/1e6,2)] for label,key in [('Partidas directas','subtotal_pen'),('Transporte/montaje adicional de generación','transporte_montaje_pen'),('Estudios/supervisión','estudios_supervision_pen'),('Contingencia','contingencia_pen'),('Total del escenario','total_pen')]],
        [10.5,3],'Costos estimados con alcances y bases de recargos expresos')
    wt('viabilidad',['Ingreso supuesto (S/kWh)','Ingreso anual (S/ millones)','VAN de escenario (S/ millones)'],
        [[f(v['ingreso_escenario_pen_kwh']),f(v['ingreso_anual_pen']/1e6,2),f(v['van_hibrido_pen']/1e6,2)] for v in p['escenarios']],
        [4.1,4.3,5],'Sensibilidad financiera de cobertura híbrida, 20 años y tasa real 10%; no tarifas aprobadas')
    wt('matriz',['Identificador / disposición','Requisito y evidencia prevista','Estado de comprobación'],
        [[row[0]+' / '+prosa(row[1]),prosa(row[2])+' '+prosa(row[3]),prosa(row[4])] for row in norm['matriz']],
        [3.2,6,5.2],'Matriz de 40 requisitos aplicables y evidencia; presencia de una norma no demuestra cumplimiento')
    bib=[]
    for source in norm['fuentes']+sources['fuentes']:
        label=source['id']+' - '+prosa(source['titulo'])
        url=source['url'].replace('%',r'\%').replace('#',r'\#').replace('&',r'\&')
        bib.extend([r'\Needspace{8\baselineskip}',r'\subsection*{'+texto(label)+'}',texto(prosa(source['lectura'])),
                    r'\par\href{'+url+r'}{Consultar fuente y procedencia.}\par'])
    (exp/'generado/fuentes.tex').write_text('\n'.join(bib),encoding='utf-8')
    # Tablas de respaldo para recalcular y revisar en otros programas.
    def csvout(name,rows):
        with (out/name).open('w',encoding='utf-8-sig',newline='') as file:
            writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    csvout('presupuesto-metrados-r03.csv',p['partidas'])
    csvout('oferta-mensual-r03.csv',of['mensual'])
    csvout('comparacion-potencias-r03.csv',r['alternativas'])
    csvout('perfil-demanda-r03.csv',[dict(hora=i,demanda_kw=float(v),prioritaria_kw=float(dn['perfil_critico_kw'][i])) for i,v in enumerate(dn['perfil_kw'])])
    s=series['ARNOVIC']
    csvout('balance-diario-estimado-r03.csv',[dict(fecha=d.isoformat(),q_natural_estimado_m3s=float(s['q'][i]),
        q_reserva_ecologica_estudio_m3s=float(s['eco'][i]),q_otros_usos_estudio_m3s=float(s['other'][i]),
        q_posible_turbina_m3s=float(s['used'][i]),q_remanente_capacidad_m3s=float(s['spill'][i]),
        potencia_disponible_usuarios_kw=float(s['net'][i]),grupos_para_capacidad=int(s['nact'][i]),
        tipo_dato='simulado_transpuesto_no_validado') for i,d in enumerate(s['dates'])])
    from figuras_r03 import dibujar
    dibujar(exp,r,series,geo)
    manifest=[]
    paths=[f for f in PROY.rglob('*') if f.is_file() and not
           {'__pycache__','fuentes','archivo','entregables'}.intersection(f.relative_to(PROY).parts)]
    paths.extend(ROOT/'herramientas/hidroelectricas'/name for name in ['calculos.py','cuencas_dem.py','transitorios.py'])
    # Incluye originales usados, con lectura por bloques para archivos grandes.
    paths.extend(PROY/'fuentes/local/investigacion-r03'/f['local'] for f in sources['fuentes'] if f.get('local'))
    paths.extend(ROOT/f['local'] for f in norm['fuentes'] if f.get('local'))
    paths.extend([PROY/'fuentes/local/investigacion-r03/riv_pisco_gr2m_v2.0.gpkg',
                  PROY/'fuentes/local/investigacion-r03/cat_pisco_gr2m_v2.0.gpkg',
                  Path('C:/Users/51949/Downloads/Catastro_Limbani/qgis/Catastro-Limbani.gpkg')])
    paths.extend([ROOT/'recursos/identidad/escudo-unap.png',
                  ROOT/'recursos/ubicacion/limbani/ubicacion_departamento_puno.jpg',
                  ROOT/'recursos/ubicacion/limbani/ubicacion_provincia_sandia.jpg'])
    for path in sorted(set(paths)):
        if path.exists():
            manifest.append(dict(ruta=str(path.resolve()),sha256=sha(path),bytes=path.stat().st_size))
    (out/'manifest-r03.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not args.sin_pdf:
        for doc,passes in [('main.tex',3),('planos-r03.tex',2),('exposicion-r03.tex',2)]:
            if not (exp/doc).exists():raise FileNotFoundError(doc)
            for n in range(passes):
                proc=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',doc],cwd=exp,capture_output=True)
                (exp/(Path(doc).stem+f'-pasada-{n+1}.txt')).write_bytes(proc.stdout+proc.stderr)
                if proc.returncode:raise RuntimeError(f'Falló LaTeX: {exp/(Path(doc).stem+".log")}')
    print(json.dumps(dict(revision='R03',salidas=str(out),potencia_hidro_kw=bn['p_bornes_kw'],
        p_usuarios_nominal_kw=bn['p_usuarios_kw'],pico_demanda_kw=dn['max_kw'],p95_diario_estudio_kw=of['p95_usuarios_kw'],
        energia_hidro_servida_mwh=of['energia_hidro_servida_mwh'],deficit_hidro_mwh=of['energia_no_cubierta_hidro_mwh'],
        presupuesto_estimado_pen=p['total_pen']),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
