"""Figuras vectoriales de las hipótesis del anteproyecto, sin georreferenciación ficticia."""
def dibujar(exp,cfg,calc,balance,ds,libro):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                         'pdf.fonttype':42,'ps.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False})
    a={k:v['valor'] for k,v in cfg['escenario_objetivo'].items()}
    fig,ax=plt.subplots(figsize=(8,4.4));qs=[.15+i*.005 for i in range(65)]
    for d in [.45,.50,.55]:ax.plot(qs,[balance(calc(q,d))['p_pcc_kw'] for q in qs],label=f'Di = {d*1000:.0f} mm')
    ax.axhline(cfg['criterio_objetivo']['p_pcc_kw'],color='#a92732',ls='--',label='Objetivo en PCC')
    ax.axvline(a['q'],color='#74848c',ls=':',label='Q de estudio, sin aforo')
    ax.set(xlabel='Caudal turbinado (m³/s)',ylabel='Potencia exportada (kW)',title='Sensibilidad en PCC: auxiliares y pérdidas incluidas')
    ax.legend(fontsize=10);ax.grid(alpha=.2)
    fig.text(.5,.01,'Rendimientos constantes e hipótesis eléctricas. No es duración de caudales ni garantía.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(exp/'figuras/sensibilidad.pdf');plt.close(fig)
    h=next(r for r in ds if r['d_m']==a['diametro'])['hidraulica'];xs=[0,a['longitud']]
    fig,ax=plt.subplots(figsize=(8,3.8))
    ax.plot(xs,[h['hb_m'],0],color='#798b88',lw=3,label='Eje recto hipotético')
    ax.plot(xs,[h['hb_m'],h['hn_m']],color='#235b85',lw=2,label='Línea de energía simplificada')
    ax.plot(xs,[h['hb_m']-h['v_ms']**2/(2*9.81),h['hn_m']-h['v_ms']**2/(2*9.81)],color='#a92732',ls='--',label='Piezométrica en tubería llena')
    ax.set(xlabel='Longitud de estudio (m)',ylabel='Cota relativa / carga (m)',title='H-01. Perfil conceptual: no reproduce topografía')
    ax.legend(loc='lower left',fontsize=10);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(exp/'figuras/perfil.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.5));ax.set_xlim(0,12);ax.set_ylim(0,7);ax.axis('off')
    def box(x,y,w,hh,label):
        ax.add_patch(FancyBboxPatch((x,y),w,hh,boxstyle='round,pad=.08',facecolor='#edf4f8',edgecolor='#235b85'))
        ax.text(x+w/2,y+hh/2,label,ha='center',va='center',fontsize=11)
    def wire(points):ax.plot([p[0] for p in points],[p[1] for p in points],color='#235b85',lw=1.8)
    box(.25,4.1,1.7,1.25,'G1 síncrono\n250 kVA\ncandidato\n400 V / 60 Hz')
    box(2.5,4.1,1.2,1.25,'52G\nProtección\ngenerador')
    wire([(1.95,4.72),(2.42,4.72)]);wire([(3.78,4.72),(5,4.72)]);wire([(5,3.9),(5,5.4)])
    ax.text(5,5.75,'BARRA BT 400 V',ha='center',fontsize=10,weight='bold')
    box(6.15,4.1,1.7,1.25,'52T + T1\n250 kVA\ncandidato\n0.4 / 22.9 kV')
    box(9,4.1,2.5,1.25,'52MT / TC / TV\nLínea 1.2 km\nPCC por aprobar')
    wire([(5,4.72),(6.07,4.72)]);wire([(7.93,4.72),(8.92,4.72)])
    box(4.1,1.85,1.8,1.1,'Protección + TSA\n15 kVA candidato\n400/230 V, aislado')
    wire([(5,3.9),(5,3.03)])
    box(7.1,1.8,2.2,1.2,'Tablero auxiliar\n5.10 kW generación\nRelés, cargador y CC')
    wire([(5.98,2.4),(7.02,2.4)])
    box(.25,1.85,2.1,1.1,'Neutro G1\nImpedancia\npor estudio\nCNE-S 132');wire([(1.1,4.02),(1.1,3.03)])
    ax.text(6,6.55,'E-01. Unifilar conceptual con barra y derivación auxiliar',ha='center',weight='bold',fontsize=13)
    ax.text(6,.7,'Con red disponible, T1 puede energizar barra y TSA con 52G abierto.\nNeutros, tierra, grupo vectorial y ajustes necesitan estudio.',ha='center',fontsize=11)
    fig.tight_layout();fig.savefig(exp/'figuras/unifilar-funcional.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.6,3.6));ax.set_xlim(0,12);ax.set_ylim(0,5);ax.axis('off')
    for label,x in [('Captación\n+ caudal ecológico',.2),('Desarenador\n2 cámaras propuestas',3.1),('Canal libre\n+ cámara de carga',6.1),('Tubería + grupo\n+ restitución',9.1)]:
        ax.add_patch(FancyBboxPatch((x,2),2.6,1.25,boxstyle='round,pad=.08',facecolor='#edf4f8',edgecolor='#235b85'))
        ax.text(x+1.3,2.625,label,ha='center',va='center',fontsize=11)
    for x in [2.85,5.85,8.85]:ax.annotate('',xy=(x+.2,2.6),xytext=(x-.05,2.6),arrowprops={'arrowstyle':'->','color':'#235b85'})
    ax.text(6,4.3,'H-00. Secuencia hidráulica y restitución',ha='center',fontsize=13,weight='bold')
    ax.text(6,1.1,'El tramo derivado conserva caudal ecológico y derechos de terceros.\nPurgas, avenidas y aliviaderos requieren descargas seguras.',ha='center',fontsize=11)
    fig.tight_layout();fig.savefig(exp/'figuras/esquema-hidraulico.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.6,4.8));top=libro[0][1]
    for i,(_,v) in enumerate(libro):
        if i in [0,len(libro)-1]:ax.bar(i,v,color='#235b85');base=0
        else:base=top-v;ax.bar(i,v,bottom=base,color='#a92732');top=base
        ax.text(i,base+v+1.5,f'{v:.2f}',ha='center',fontsize=10,rotation=35 if 4<i<9 else 0)
    ax.set_xticks(range(10),['Bruta','Tubería','Turbina','Transmisión','Generador','Auxiliares','TSA','T1','Línea','PCC'],rotation=35,ha='right')
    ax.set(ylabel='Potencia activa (kW)',title='Balance R02: recurso bruto y exportación')
    ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(exp/'figuras/balance-energia.pdf');plt.close(fig)
