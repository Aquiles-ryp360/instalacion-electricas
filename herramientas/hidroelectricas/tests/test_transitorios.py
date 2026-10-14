import unittest
import numpy as np
from herramientas.hidroelectricas.transitorios import moc_valvula


class Transitorios(unittest.TestCase):
    def test_sostiene_estado_estacionario(self):
        r=moc_valvula(.4,50,250,.5,900,.015,None,2,40)
        self.assertLess(np.ptp(r['carga_valvula_m']),1e-7)
        self.assertLess(np.max(np.abs(np.array(r['q_valvula_m3s'])-.4)),1e-9)

    def test_primer_pico_joukowsky_sin_friccion(self):
        q=.4; a=900; d=.5; h=50
        r=moc_valvula(q,h,250,d,a,0.0,0.0,.2,40)
        v=q/(np.pi*d*d/4)
        self.assertAlmostEqual(max(r['carga_valvula_m']),h+a*v/9.81,places=7)
        self.assertAlmostEqual(r['q_valvula_m3s'][-1],0)

    def test_refinamiento_cierre_lento(self):
        a=moc_valvula(.4,50,250,.5,900,.015,4.0,6.0,40)
        b=moc_valvula(.4,50,250,.5,900,.015,4.0,6.0,80)
        self.assertLess(abs(a['max_global_bar']-b['max_global_bar']),.15)

    def test_detiene_al_romper_modelo_monofasico(self):
        r=moc_valvula(.4,50,250,.5,900,.015,0,4,40,limite_presion_manometrica_m=-6.8)
        self.assertTrue(r['cavitacion_detectada'])
        self.assertLess(r['duracion_valida_s'],4)
        self.assertGreaterEqual(r['min_carga_m'],-6.8)


if __name__=='__main__':unittest.main()
