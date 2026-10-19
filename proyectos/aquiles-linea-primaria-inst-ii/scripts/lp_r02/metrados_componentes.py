"""M01: despiece trazable por armado/poste; no certifica una adaptación CAC."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import math
from pathlib import Path

P = Path(__file__).resolve().parents[2]


def cargar():
    carpeta = P / 'datos/metrados-m01'
    return tuple(json.loads((carpeta / f).read_text(encoding='utf-8'))
                 for f in ('catalogo.json', 'criterios.json'))


def medir(base, catalogo=None, criterios=None):
    """Cantidades físicas, compras y componentes incluidos son niveles distintos."""
    if catalogo is None or criterios is None:
        catalogo, criterios = cargar()
    materiales = catalogo['materiales']
    armados = catalogo['armados']
    if not 0 < criterios['ang_retenida_grados'] < 90:
        raise ValueError('Ángulo de retenida fuera del intervalo geométrico')
    if criterios['capacidad_minima_retenida_kN'] < 60:
        raise ValueError('No reducir la resistencia mínima de retenida de LP-R02')
    postes = base['postes']
    ids = [p['id'] for p in postes]
    if len(ids) != len(set(ids)):
        raise ValueError('Identificadores de poste duplicados')
    tendido = Counter({p: 0.0 for p in ids})
    fases = criterios['fases']
    for v in base['vanos']:
        longitud = v['estados']['EDS']['longitud_cable_m'] * fases
        if longitud <= 0:
            raise ValueError('Longitud no positiva: ' + v['id'])
        for extremo in ('desde', 'hasta'):
            if v[extremo] not in tendido:
                raise ValueError('Vano con extremo desconocido: ' + v['id'])
            tendido[v[extremo]] += longitud / 2
    inventario, asignaciones = [], []
    compra, incluidos, cuenta_armados = Counter(), Counter(), Counter()
    longitud_puentes = 0.0
    for p in postes:
        try:
            codigo = criterios['mapa_funciones'][p['tipo_r02']]
        except KeyError:
            raise ValueError('Función sin receta: ' + str(p['tipo_r02'])) from None
        cuenta_armados[codigo] += 1
        n_retenidas = p['retenidas_r02']
        if int(n_retenidas) != n_retenidas or n_retenidas < 0:
            raise ValueError('Número inválido de retenidas: ' + p['id'])
        if p['tipo_r02'] == 'SUSPENSION' and abs(p['angulo_deg']) > 5:
            raise ValueError('Suspensión fuera del intervalo de referencia: ' + p['id'])
        if p['tipo_r02'] == 'ANGULO' and not 5 < abs(p['angulo_deg']) <= 30:
            raise ValueError('Ángulo fuera del intervalo de referencia: ' + p['id'])
        puente = (fases * criterios['longitud_puente_por_fase_m']
                  if p['tipo_r02'] in criterios['casos_con_puentes'] else 0.0)
        longitud_puentes += puente
        cable_retenida = (p['amarre_m'] / math.sin(math.radians(criterios['ang_retenida_grados']))
                           + criterios['colas_retenida_por_ramal_m'])
        asignacion = dict(poste=p['id'],funcion=p['tipo_r02'],armado=codigo,
                         referencia=armados[codigo]['variante'],altura_m=p['poste_m'],
                         progresiva_m=p['progresiva_m'],angulo_deg=p['angulo_deg'],
                         ramales=n_retenidas,tendido_asignado_m=tendido[p['id']],
                         puentes_colas_m=puente,cable_retenida_unit_m=cable_retenida,
                         giro_especial=abs(p['angulo_deg']) > 90,
                         nota=('Giro >90°: coeficientes base PR3-3; detalle específico de geometría.'
                               if abs(p['angulo_deg']) > 90 else ''))
        asignaciones.append(asignacion)

        def agregar(material, unidad, multiplicador, conjunto, fuente, nivel='COMPRA', padre=''):
            if material not in materiales:
                raise ValueError('Material desconocido: ' + material)
            cantidad = unidad * multiplicador
            if not math.isfinite(cantidad) or cantidad < 0:
                raise ValueError('Cantidad inválida: ' + material)
            if not cantidad:
                return
            e = materiales[material]
            inventario.append(dict(poste=p['id'],armado=conjunto,material=material,
                                   descripcion=e['descripcion'],unidad=e['unidad'],
                                   consumo_unitario=unidad,multiplicador=multiplicador,
                                   cantidad=cantidad,nivel=nivel,incluido_en=padre,
                                   fuente=fuente,codigo_referencia=e['codigo_referencia']))
            (compra if nivel == 'COMPRA' else incluidos)[material] += cantidad
            if nivel == 'COMPRA':
                for sub, q in e['incluye'].items():
                    agregar(sub, q * unidad, multiplicador, conjunto, fuente,
                            nivel='INCLUIDO', padre=material)

        agregar('P' + str(int(p['poste_m'])), 1, 1, 'POSTE', 'Modelo LP-R02: altura y capacidad tipo')
        for material, q in armados[codigo]['coef'].items():
            agregar(material, q, 1, codigo, armados[codigo]['fuente_cantidades'])
        for material, q in armados['RI-A']['coef'].items():
            agregar(material, q, n_retenidas, 'RI-A', armados['RI-A']['fuente_cantidades'])
        agregar('GUY', cable_retenida, n_retenidas, 'RI-A', 'Geometría ideal + colas de montaje M01')
        if 'PAT-P' in armados:
            for material, q in armados['PAT-P']['coef'].items():
                agregar(material, q, 1, 'PAT-P', armados['PAT-P']['fuente_cantidades'])
            if 'CU-PAT' in materiales:
                agregar('CU-PAT', p['amarre_m'] + criterios['cola_bajante_pat_m'], 1,
                        'PAT-P', 'Longitud de bajante desde amarre + conexión enterrada M01')
                agregar('FI-PAT', math.ceil(p['amarre_m'] / criterios['paso_fijacion_pat_m']) + 1,
                        1, 'PAT-P', 'Coeficiente de proyecto: fijaciones cada metro y extremos')

    total_tendido = math.fsum(tendido.values())
    reserva = math.ceil((total_tendido + longitud_puentes) * criterios['reserva_conductor'])
    suministro = math.ceil(total_tendido + longitud_puentes + reserva)
    return dict(revision='LP-R02-M01',base_tecnica='LP-R02',aprobacion_ingenieria=False,
                asignaciones=asignaciones,inventario=inventario,
                resumen_compra=dict(compra),resumen_incluidos=dict(incluidos),
                cuenta_armados=dict(cuenta_armados),
                conductor=dict(tendido_terna_m=total_tendido,puentes_provision_m=longitud_puentes,
                               reserva_m=reserva,total_compra_estudio_m=suministro,
                               redondeo_compra_m=suministro-total_tendido-longitud_puentes-reserva),
                postes=len(ids),ramales=sum(p['retenidas_r02'] for p in postes),
                giros_especiales=[p['poste'] for p in asignaciones if p['giro_especial']])


def actualizar_resultados_para_documento(base):
    """Una vista M01 actualiza suministro, sin tocar el JSON técnico histórico."""
    r = deepcopy(base)
    m = medir(base)
    r['conductor'].update(m['conductor'])
    r['revision_metrado'] = m['revision']
    return r


def capitulo(base, tabla, tex, n):
    """Fuentes documentales, receta por armado e inventario de los 111 apoyos."""
    cat, c = cargar()
    m = medir(base, cat, c)
    materiales, armados = cat['materiales'], cat['armados']
    codigos = [k for k in armados if k.startswith('CAC-')]
    s = r'''\chapter{METRADOS DESARROLLADOS}
\section{Organización del inventario}
El metrado se desarrolla desde la pieza hacia el conjunto: catálogo de componentes,
consumo por armado, asignación a cada poste y resumen de compra. Las fichas identifican
el código, la descripción, la unidad y la cantidad. Los accesorios incluidos con un
perno o abrazadera se desglosan para inspección, sin volver a comprarlos por separado.

Las recetas de referencia son trifásicas sin neutro: DGE 004 (PS1-3), 008 (PA1-3),
020 (PR3-3), 026 (PTH-3) y 074 (RI-A). Se conserva el poste CAC del modelo. Para
el metrado académico se adopta cruceta metálica de 2.50 m y abrazadera CAC para
cada par de riostras; se excluyen el poste de madera, los tirafondos y los accesorios
del neutro de las láminas originales. El PAC de Electro Puno 2024, p.59, documenta
la familia de crucetas metálicas para CAC. Las cantidades de sus adaptadores son
coeficientes de proyecto declarados, sujetos a ajuste con el plano del fabricante.

El detalle no acredita capacidad resistente del armado ni convierte los anclajes
ideales en cimentaciones verificadas. Diámetro de abrazaderas, perforaciones de
fábrica, capacidad de herrajes y selección de aislamiento se coordinan con el suministro.
El cálculo mecánico LP-R02 conserva su carga tipo de aisladores y accesorios de 300 N
por apoyo. Este despiece no certifica esa hipótesis: se requiere la masa de cada pieza
y recalcular acciones y separaciones con la configuración suministrada. No se presenta
el despiece como una verificación resistente adicional.
En P003, P035 y P057 el giro mayor de 90 grados requiere detalle geométrico específico;
su inventario usa la base de retención PR3-3, sin atribuirle aprobación constructiva.

\section{Asignación de armados}
'''
    s += tabla(['Código M01','Función / referencia','Cantidad de apoyos'],
               [[tex(k),tex(armados[k]['nombre']+' / '+armados[k]['variante']),m['cuenta_armados'].get(k,0)]
                for k in codigos],[1,3.6,1], 'footnotesize')
    s += ('Se mantienen '+str(m['postes'])+' postes y '+str(m['ramales'])+
          ' ramales de retenida. Un apoyo de retención y sus dos retenidas se miden como elementos distintos.\n')
    s += r'\section{Despiece por unidad de armado}'+'\n'
    for codigo in armados:
        a = armados[codigo]
        s += '\\subsection{'+tex(codigo+' — '+a['nombre'])+'}\n'
        s += tex(a['fuente_cantidades'])+'.\n'
        rows = []
        for k, q in a['coef'].items():
            e = materiales[k]
            rows.append([tex(k),tex(e['descripcion']),tex(e['unidad']),n(q,2)])
        s += tabla(['Código','Componente','Un.','Por unidad'],rows,[1.1,4.5,.5,.9],'footnotesize')
    s += r'''\section{Resumen general de suministro}
La tabla suma las cantidades de compra de todas las fichas. Las tuercas,
contratuercas y arandelas incluidas se informan en sus fichas y en una hoja separada
del Excel; no se añaden como suministros adicionales. El precio del armado o retenida
por conjunto comprende su despiece: no se vuelve a sumar el costo de cada pieza.
'''
    rows=[]
    grupos=['Postes','Crucetas y soportes','Aisladores','Pernos y accesorios',
            'Conexiones y amarres','Retenida','Puesta a tierra de apoyo']
    orden=sorted(m['resumen_compra'],key=lambda k:(grupos.index(materiales[k]['grupo']),list(materiales).index(k)))
    anterior=None
    for k in orden:
        q=m['resumen_compra'][k]
        grupo=materiales[k]['grupo']
        if grupo!=anterior:
            rows.append(['',r'\textbf{'+tex(grupo.upper())+'}','',''])
            anterior=grupo
        e=materiales[k];rows.append([tex(k),tex(e['descripcion']),tex(e['unidad']),n(q,3 if e['unidad']=='m' else 0)])
    rows.append(['AAAC-50','Conductor AAAC 50 mm$^2$, suministro total','m',n(m['conductor']['total_compra_estudio_m'],0)])
    s += tabla(['Código','Material para suministro','Un.','Cantidad'],rows,[1.1,4.4,.5,1],'footnotesize')
    s += r'''\section{Medición del conductor por armado}
La retención interrumpe las tres fases y necesita un puente por fase; el terminal
necesita una cola por fase. La suspensión y el ángulo de paso mantienen continuidad.
El número de ramales de retenida no determina el número de puentes eléctricos.
'''
    nr=sum(a['funcion'] in ('ANCLAJE','ANCLAJE_PROPUESTO') for a in m['asignaciones'])
    nt=sum(a['funcion']=='TERMINAL' for a in m['asignaciones'])
    z=m['conductor']
    s += r'\begin{align}'+'\n'+rf'N_{{puente}}&=3({nr}),\quad N_{{cola}}=3({nt}),\\'+'\n'
    s += rf'L_{{aux}}&=3({nr}+{nt})({c["longitud_puente_por_fase_m"]})={n(z["puentes_provision_m"],0)}\ \mathrm{{m}},\\'+'\n'
    s += rf'L_{{tendido}}&=3\sum_i L_{{c,i}}={n(z["tendido_terna_m"])}\ \mathrm{{m}},\\'+'\n'
    s += rf'L_{{res}}&=\lceil0.03(L_{{tendido}}+L_{{aux}})\rceil={n(z["reserva_m"],0)}\ \mathrm{{m}},\\'+'\n'
    s += rf'L_{{suministro}}&=\lceil L_{{tendido}}+L_{{aux}}+L_{{res}}\rceil=\boxed{{{n(z["total_compra_estudio_m"],0)}\ \mathrm{{m}}}}.'+'\n'+r'\end{align}'+'\n'
    s += r'''La ficha distribuye contablemente la mitad de cada vano a cada poste extremo.
Esa asignación permite conciliar el total; no prescribe cortes ni empalmes de conductor.
La longitud del cable de retenida se calcula con el amarre ideal a 45 grados y una
provisión de 3 m por ramal para lazos y regulación. El cable se exige con rotura mínima
de 60 kN; no se deduce esa resistencia de un diámetro de referencia de la lámina DGE.

'''
    s += r'\section{Planilla de medición de los 110 vanos}'+'\n'
    s += 'Se conserva el desarrollo de longitudes por vano: proyección horizontal, catenaria de una fase y terna completa. La reserva y los puentes se agregan después, sin repetirlos en cada vano.\n'
    vanos=[[v['id'],v['desde'],v['hasta'],n(v['longitud_m']),n(v['estados']['EDS']['longitud_cable_m']),
            n(3*v['estados']['EDS']['longitud_cable_m'])] for v in base['vanos']]
    vanos.append(['TOTAL','--','--',n(sum(v['longitud_m'] for v in base['vanos'])),n(z['tendido_terna_m']/3),n(z['tendido_terna_m'])])
    s += tabla(['Vano','Desde','Hasta','L XY m','Cable/fase m','Terna m'],vanos,[1,1,1,1.2,1.5,1.5],'footnotesize')
    s += r'\section{Planilla de postes y armados}'+'\n'
    s += tabla(['Poste','Altura m','Armado','Ret. ud','Puentes/colas m'],
               [[a['poste'],a['altura_m'],tex(a['armado']),a['ramales'],n(a['puentes_colas_m'],0)]
                for a in m['asignaciones']],[1,1,1.4,1,1.5],'footnotesize')
    s += r'\section{Inventario individual por poste}'+'\n'
    s += 'Cada ficha reúne poste, armado, retenidas y sus accesorios. Las filas de cantidad incluida no se compran de nuevo.\n'
    for a in m['asignaciones']:
        s += '\\clearpage\\phantomsection\\pdfbookmark[2]{'+a['poste']+' — Inventario}{m01-'+a['poste']+'}\n'
        s += '\\begingroup\\small\\setlength{\\parskip}{3pt}\\renewcommand{\\arraystretch}{1.05}\n'
        s += '\\textbf{\\large FICHA DE METRADO — '+a['poste']+'}\\\\[4pt]\n'
        s += tex(f"Poste CAC {a['altura_m']} m / 600 daN; progresiva {a['progresiva_m']:.3f} m; giro {a['angulo_deg']:.2f}°")+r'\\'+'\n'
        s += tex(f"Armado {a['armado']} ({a['referencia']}); retenidas RI-A: {a['ramales']} ramal(es)")+r'\\'+'\n'
        if a['nota']:s += tex(a['nota'])+r'\\'+'\n'
        rows=[]
        for line in m['inventario']:
            if line['poste']!=a['poste'] or line['nivel']!='COMPRA':continue
            prefijo={'RI-A':'R: ','PAT-P':'T: ','POSTE':'P: '}.get(line['armado'],'A: ')
            rows.append([tex(line['material']),tex(prefijo+line['descripcion']),tex(line['unidad']),n(line['consumo_unitario'],2 if line['unidad']=='m' else 0),
                         n(line['multiplicador'],0),n(line['cantidad'],2 if line['unidad']=='m' else 0)])
        rows += [['AAAC-T','Conductor tendido: mitad de los vanos adyacentes','m',n(a['tendido_asignado_m'],2),'1',n(a['tendido_asignado_m'],2)],
                 ['AAAC-P','Puentes o colas de las tres fases','m',n(a['puentes_colas_m'],0),'1',n(a['puentes_colas_m'],0)]]
        s += tabla(['Código','Componente '+a['poste'],'Un.','Coef.','N.º','Cantidad'],rows,[1.0,3.7,.45,.65,.45,.8],'scriptsize')
        sub=Counter()
        for line in m['inventario']:
            if line['poste']==a['poste'] and line['nivel']=='INCLUIDO':sub[line['material']]+=line['cantidad']
        detalle='; '.join(f'{k}: {int(v)}' for k,v in sub.items())
        s += '\\begingroup\\scriptsize\n\\textbf{Accesorios incluidos (ud):} '+tex(detalle)+'.\\\\\n'
        s += tex('N16/C16: tuerca/contratuerca M16; N13/C13: M13; B75: perno de abrazadera; A16INC/A13INC: arandelas incluidas. No sumar como compra adicional.')+r'\\'+'\n'
        s += tex('A: armado; R: retenida; T: tierra; P: poste. Coeficientes M01 y adaptación CAC declarada en el catálogo; no es plano de fabricación.')+'\n\\endgroup\\endgroup\n'
    return s
