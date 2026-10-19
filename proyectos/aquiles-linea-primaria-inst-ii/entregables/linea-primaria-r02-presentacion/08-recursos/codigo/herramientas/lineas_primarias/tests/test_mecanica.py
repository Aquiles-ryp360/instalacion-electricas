import unittest,math
import numpy as np
from herramientas.lineas_primarias.mecanica import geometria,estado,puntos

class Mecanica(unittest.TestCase):
    def test_catenaria_horizontal_exacta(self):
        g=geometria(2000,100,0,1.5);p=puntos(g,100,0,1.5)
        expected=g['a']*(math.cosh(50/g['a'])-1)
        self.assertAlmostEqual(-p[30,2],expected,places=9)
    def test_extremos_inclinados_con_viento(self):
        g=geometria(2500,83,24,2,3);p=puntos(g,83,24,2,3)
        np.testing.assert_allclose(p[0],[0,0,0],atol=1e-10)
        np.testing.assert_allclose(p[-1],[83,0,24],atol=1e-10)
        self.assertGreater(g['longitud_m'],math.hypot(83,24))
    def test_canton_conserva_y_calor_reduce_tension(self):
        spans=[(75,13),(85,-7),(66,3)];args=(spans,2200,1.35,62000e6*49.5e-6,23e-6,15)
        h,g,res=estado(*args,55,1.35,creep=.000345)
        self.assertLess(h,2200);self.assertLess(abs(res),1e-9)
    def test_rechaza_longitudes_negativas(self):
        with self.assertRaises(ValueError):geometria(1000,-2,0,1)

if __name__=='__main__':unittest.main()
