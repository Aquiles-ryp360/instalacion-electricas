"""Contraste exploratorio de rendimiento y selección T12; no modifica R03.

SKAT (1993), vol. 3, pp. impresas 19, 30, 32 y 35-38.
Las ecuaciones de ancho y velocidad son específicas del T12 de 300 mm.
No son una norma de fabricación ni se trasladan a cualquier turbina Banki.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

PROY = Path(__file__).resolve().parents[1]
ROOT = PROY.parents[1]
sys.path.insert(0, str(ROOT))
from herramientas.hidroelectricas.calculos import hidro


def main():
    entrada = PROY / 'datos/parametros-r03.json'
    cfg = json.loads(entrada.read_text(encoding='utf-8'))
    h = cfg['hidraulica']
    eta_t12 = 0.70

    def balance(q):
        return hidro(q, h['salto_bruto_m'], h['longitud_presion_m'],
                     h['diametro_interior_m'], h['rugosidad_m'],
                     h['viscosidad_m2s'], h['k_local'], eta_t12,
                     h['eta_m'], h['eta_g_nominal'])

    casos = []
    for unidades in (1, 2, 3):
        objetivo = unidades * 200.0
        # Se busca el caudal teórico requerido para detectar excedencias;
        # el resultado no amplía el caudal de diseño adoptado en R03.
        bajo, alto = 0.0, 3.0
        if balance(alto)['p_bornes_kw'] <= objetivo:
            raise ValueError('El intervalo de contraste no encierra la potencia objetivo')
        for _ in range(70):
            medio = (bajo + alto) / 2
            if balance(medio)['p_bornes_kw'] < objetivo:
                bajo = medio
            else:
                alto = medio
        b = balance((bajo + alto) / 2)
        qu = b['q_m3s'] / unidades
        ancho = 3.623 * qu * 1000 / math.sqrt(b['hn_m'])
        n = 40 / 0.3 * math.sqrt(b['hn_m'])
        peje = b['p_turbina_kw'] / unidades
        assert math.isclose(b['p_bornes_kw'], objetivo, abs_tol=1e-7)
        assert math.isclose(b['hb_m'] - b['htotal_m'], b['hn_m'], abs_tol=1e-10)
        casos.append(dict(
            unidades=unidades, potencia_objetivo_bornes_kw=objetivo,
            q_teorico_total_m3s=b['q_m3s'], q_unitario_m3s=qu,
            supera_q_diseno_r03=b['q_m3s'] > h['q_diseno_m3s'],
            salto_neto_m=b['hn_m'], perdidas_m=b['htotal_m'],
            potencia_eje_turbina_unitaria_kw=peje,
            potencia_acople_generador_unitaria_kw=b['p_acople_kw'] / unidades,
            seleccion_t12=dict(diametro_exterior_m=0.3, ancho_entrada_b0_mm=ancho,
                velocidad_referencia_rpm=n, velocidad_generador_r03_rpm=cfg['grupo']['velocidad_rpm'],
                desviacion_velocidad_generador_pct=100*(cfg['grupo']['velocidad_rpm']/n-1),
                torque_referencia_nm=peje*1000/(2*math.pi*n/60),
                limites_rectangulares_del_manual=(4 <= b['hn_m'] <= 50 and
                    100 <= qu*1000 <= 820 and 10 <= peje <= 250 and 100 <= ancho <= 1120),
                campo_conjunto_y_discos='Comprobar gráficas 0-8 y 9; límites rectangulares solos no validan selección',
                transmision='Cotejar línea d-d del gráfico 9; no adoptar polea sobre eje sin comprobar'),
        ))
    resultado = dict(
        revision='Contraste de trabajo R04; no sustituye la entrega R03',
        fecha='2026-10-16', tipo='Cálculo con hipótesis; no ensayo ni dato de central existente',
        entrada_r03_sha256=hashlib.sha256(entrada.read_bytes()).hexdigest(),
        fuente='SKAT 1993, Cross Flow Turbine Design and Equipment Engineering, vol. 3',
        pagina_editor='https://skat.ch/publications/cross-flow-turbine-design-volume-3',
        eta_turbina_r03=h['eta_t_nominal'], eta_turbina_t12_manual=eta_t12,
        eta_mecanica_r03=h['eta_m'], eta_generador_r03=h['eta_g_nominal'],
        salto_bruto_gabinete_m=h['salto_bruto_m'], longitud_tuberia_m=h['longitud_presion_m'],
        diametro_tuberia_m=h['diametro_interior_m'], q_max_diseno_r03_m3s=h['q_diseno_m3s'],
        casos=casos, balance_al_q_max_r03=balance(h['q_diseno_m3s']),
        limites=[
            'Se conserva la tubería R03 para aislar el efecto del rendimiento; no está optimizada para una sola unidad.',
            'El 70% es el valor de cálculo del modelo T12; no se atribuye a todas las Banki.',
            'El 84% de R03 sigue siendo una hipótesis comercial por verificar, no una prestación demostrada.',
            'Ancho b0 es ancho de entrada del T12, no espesor de chorro ni longitud de eje.',
            'No se deduce potencia firme, energía anual ni costo de estas cuentas nominales.',
            'No se dispone todavía del juego íntegro de planos de taller: el PDF recuperado contiene 44 páginas de manual.',
        ],
    )
    salida = PROY / 'datos/turbina/contraste-t12-r04.json'
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(archivo=str(salida), casos=[dict(
        unidades=c['unidades'], q_total_m3s=round(c['q_teorico_total_m3s'], 4),
        supera_q_max=c['supera_q_diseno_r03']) for c in casos],
        potencia_al_q_max_kw=round(resultado['balance_al_q_max_r03']['p_bornes_kw'], 2)),
        ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
