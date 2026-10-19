"""Memorias LaTeX portables con el formato de vivienda elegido por el estudiante.

El contenido y los metadatos pertenecen al proyecto. Este módulo solo adapta
presentación, espaciado y exportación; comprueba que no cambien los números.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PLANTILLA = ROOT / 'recursos/plantillas/expediente-aquiles'
LOGO = ROOT / 'recursos/identidad/escudo-unap.png'

SIMBOLOS = {
    '\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
    '#': r'\#', '_': r'\_\allowbreak{}', '{': r'\{', '}': r'\}',
    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
    '–': '--', '—': '---', '−': '-', '‑': '-', '\u00a0': '~',
    'α': r'\ensuremath{\alpha}', 'Δ': r'\ensuremath{\Delta}',
    'Σ': r'\ensuremath{\Sigma}', 'ε': r'\ensuremath{\varepsilon}',
    'π': r'\ensuremath{\pi}', 'φ': r'\ensuremath{\phi}',
    'ρ': r'\ensuremath{\rho}', 'η': r'\ensuremath{\eta}',
    'ω': r'\ensuremath{\omega}', 'Ω': r'\ensuremath{\Omega}',
    '∫': r'\ensuremath{\int}', '≈': r'\ensuremath{\approx}',
    '≤': r'\ensuremath{\leq}', '≥': r'\ensuremath{\geq}',
    '×': r'\ensuremath{\times}', '±': r'\ensuremath{\pm}',
    '°': r'\ensuremath{^\circ}', 'º': r'\textsuperscript{o}',
    '²': r'\textsuperscript{2}', '³': r'\textsuperscript{3}',
    '′': r'\ensuremath{^{\prime}}', '″': r'\ensuremath{^{\prime\prime}}',
    '·': r'\ensuremath{\cdot}', '©': r'\textcopyright{}',
    '√': r'\ensuremath{\surd}',
}


def limpiar(texto):
    numeros = re.findall(r'\d+(?:[.,]\d+)*', texto)
    # Espacios de redacción: evitar alterar identificadores P019, V037 o R20.
    palabras=('de|del|en|con|a|y|por|para|desde|hasta|entre|usando|cada|viviendas|usuarios|poste|postes|masa|diámetro|factor|Base|AAAC|RTS|'
              'exactamente|amarre|ángulo|estudio|simultaneidad|sea|fijan|supone|efectiva|repartidas|nominal|total|libre|tipo|fuese|'
              'comparación|divisor|iguales|ejercen|ideal|sin|dividir|heredada|equivalente|corresponde|simultáneamente|horizontal|'
              'vertical|viento|mínimo|identifica|cable|recorre|separación|inicial|mayores|hoja|bloque|zona|referencia|asignatura|'
              'académico|supera|devolvía|aprobado|bien|diferencias|sistema|anexos|trasladar')
    texto = re.sub(r'\b('+palabras+r')(?=\d)', r'\1 ', texto, flags=re.I)
    texto = re.sub(r'(?<=\d)(?=(?:mm|kVA|kW|kV|daN|kgf|kg|kN|GPa|Hz|pu|ohm|microstrain|N|V|A|m)\b)', ' ', texto)
    for a,b in [('laespecificación','la especificación'),('los160anclajes','los 160 anclajes'),
                ('laausencia','la ausencia'),('yrecalcularse','y recalcularse'),
                ('delSINIA','del SINIA'),('elZIP','el ZIP'),('elplanos','los planos'),
                ('los tresZIP','los tres ZIP'),('lógica51 V','lógica 51V'),
                ('lógica 51 V','lógica 51V'),('sincotización','sin cotización'),('enanexos','en anexos')]:
        texto = texto.replace(a,b)
    if re.findall(r'\d+(?:[.,]\d+)*', texto) != numeros:
        raise AssertionError('El ajuste editorial alteró números')
    return texto


def tex(texto):
    partes = re.split(r'(https?://[^\s]+)', str(texto))
    resultado = []
    for parte in partes:
        if parte.startswith(('http://','https://')):
            resultado.append(r'\url{'+parte+'}')
        else:
            resultado.append(''.join(SIMBOLOS.get(c,c) for c in parte))
    return ''.join(resultado)


def metadatos(meta):
    def macro(k,v):return '\\newcommand{\\'+k+'}{'+v+'}\n'
    filas = [('Estudiante:',meta['autor']),('Código:',meta['codigo']),
             ('Docente del curso:',meta['docente']),('Ubicación:',meta['ubicacion']),
             ('Revisión técnica:',meta['revision']),('Edición de presentación:','18 de octubre de 2026')]
    if meta.get('grupo'):filas.insert(3,('Sección:',meta['grupo']))
    filas.append(('Naturaleza:','Proyecto académico estudiantil'))
    ficha='\n'.join(tex(k)+' & '+tex(v)+r' \\' for k,v in filas)
    return ''.join(macro(k,v) for k,v in {
        'ProyectoCabecera':tex(meta['cabecera']), 'CursoCabecera':meta['curso_celda'],
        'DocumentoPie':tex(meta['pie']), 'AutorDocumento':tex(meta['autor']),
        'CursoCaratula':tex(meta['curso']), 'TituloCaratula':tex(meta['titulo']),
        'UbicacionCaratula':tex(meta['ubicacion_titulo']),
        'TipoDocumentoCaratula':tex(meta['tipo_documento']), 'FichaCaratula':ficha,
    }.items())


def preparar(out, meta):
    out.mkdir(parents=True,exist_ok=True)
    (out/'plantilla').mkdir(exist_ok=True);(out/'figuras').mkdir(exist_ok=True)
    for f in ['estilo.tex','caratula.tex']:shutil.copy2(PLANTILLA/f,out/'plantilla'/f)
    shutil.copy2(LOGO,out/'figuras/escudo-unap.png')
    (out/'metadatos.tex').write_text(metadatos(meta),encoding='utf-8')


def convertir_bloque(lineas):
    salida=[];i=0
    while i<len(lineas):
        linea=lineas[i].strip()
        if not linea:i+=1;continue
        if linea.startswith('|'):
            tabla=[]
            while i<len(lineas) and lineas[i].strip().startswith('|'):
                c=[x.strip() for x in lineas[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',x.replace(' ','')) for x in c):tabla.append(c)
                i+=1
            n=len(tabla[0]);assert all(len(row)==n for row in tabla)
            spec='*{'+str(n)+'}{L{\\dimexpr\\linewidth/'+str(n)+'-2\\tabcolsep\\relax}}'
            head=' & '.join(r'\textbf{'+tex(v)+'}' for v in tabla[0])+r' \\ \midrule'
            salida += [r'\begingroup\small\setlength{\LTpre}{4pt}\setlength{\LTpost}{6pt}',
                r'\begin{longtable}{'+spec+'}',r'\toprule',head,r'\endfirsthead',r'\toprule',head,r'\endhead']
            salida += [' & '.join(tex(v) for v in row)+r' \\' for row in tabla[1:]]
            salida += [r'\bottomrule\end{longtable}\endgroup',''];continue
        h=re.match(r'^(#{2,4})\s+(.*)',linea)
        if h:
            nivel=len(h[1]);numero=re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?\.?\s+(.*)',h[2])
            titulo=numero[4] if numero else h[2]
            if numero and nivel==2:salida.append(r'\setcounter{section}{'+str(int(numero[1])-1)+'}')
            if numero and nivel==3 and numero[2]:salida.append(r'\setcounter{subsection}{'+str(int(numero[2])-1)+'}')
            cmd={2:'section',3:'subsection',4:'subsubsection'}[nivel]
            salida.append('\\'+cmd+'{'+tex(titulo)+'}');i+=1;continue
        if linea.startswith('# '):i+=1;continue
        # El Markdown exportado no contiene listas anidadas ni código ejecutable.
        par=[]
        while i<len(lineas) and lineas[i].strip() and not lineas[i].lstrip().startswith(('#','|')):
            par.append(lineas[i].strip());i+=1
        salida += [tex(' '.join(par)),'']
    return '\n'.join(salida)+'\n'


def desde_markdown(entrada, out, meta):
    original=Path(entrada).read_text(encoding='utf-8-sig')
    texto=limpiar(original)
    preparar(out,meta);(out/'capitulos').mkdir(exist_ok=True)
    partes=re.split(r'(?=^## )',texto,flags=re.M)
    nombres=[];preludio=''
    for n,parte in enumerate(partes):
        if not parte.startswith('## '):
            lineas=[x for x in parte.splitlines() if not x.startswith('# ') and not x.startswith('LP-R02')]
            preludio=convertir_bloque(lineas)
            continue
        titulo=parte.splitlines()[0][3:]
        slug=re.sub(r'[^a-z0-9]+','-',titulo.lower())[:65].strip('-')
        name=f'{len(nombres)+1:02}-{slug}'
        (out/'capitulos'/f'{name}.md').write_text(parte,encoding='utf-8')
        (out/'capitulos'/f'{name}.tex').write_text(convertir_bloque(parte.splitlines()),encoding='utf-8')
        nombres.append(name)
    (out/'contenido.md').write_text(texto,encoding='utf-8')
    cuerpo='\n'.join('\\input{capitulos/'+n+'}' for n in nombres)
    main=(r'\documentclass[12pt,letterpaper]{report}'+'\n'+r'\input{metadatos}\input{plantilla/estilo}'+'\n'+
        r'\renewcommand{\thesection}{\arabic{section}.}\renewcommand{\thesubsection}{\arabic{section}.\arabic{subsection}.}'+'\n'+
        r'\begin{document}\hypersetup{pageanchor=false}\pagenumbering{gobble}\input{plantilla/caratula}'+'\n'+
        r'\clearpage\hypersetup{pageanchor=true}\pagenumbering{arabic}\tableofcontents\clearpage'+'\n'+
        r'\chapter*{'+tex(meta['titulo_interior'])+'}'+r'\addcontentsline{toc}{chapter}{'+tex(meta['titulo_interior'])+'}'+'\n'+
        preludio+'\n'+cuerpo+'\n'+r'\end{document}'+'\n')
    (out/'main.tex').write_text(main,encoding='utf-8')
    return dict(fuente=str(entrada),fuente_sha256=hashlib.sha256(original.encode('utf-8')).hexdigest(),
                capitulos=len(nombres),numeros_preservados=True)


def compilar(out, documento='main.tex'):
    for n in range(3):
        p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',documento],
                         cwd=out,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/f'compilacion-{n+1}.txt').write_bytes(p.stdout)
        if p.returncode:raise RuntimeError('Falló LaTeX: '+str(out/f'compilacion-{n+1}.txt'))
    log=(out/(Path(documento).stem+'.log')).read_text(encoding='utf-8',errors='replace')
    graves=re.findall(r'^.*(?:Missing character|Undefined control|Fatal error|Overfull \\[hv]box).*$',log,flags=re.M)
    if graves:raise RuntimeError('Revisar composición: '+json.dumps(graves,ensure_ascii=False))
    return out/Path(documento).with_suffix('.pdf')
