import unittest,math,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from herramientas.lineas_primarias.revision import catenaria,resolver_estado,longitud_natural,perfil,flujo_radial,capacidad_momento,impedancia_linea
class Mecanica(unittest.TestCase):
 def test_catenaria_horizontal_solucion_cerrada(self):
  H,L,q=2000.,80.,1.4;g=catenaria(H,L,0,q);xyz=perfil(g,101)
  a=H/q;f=a*(math.cosh(L/(2*a))-1)
  self.assertAlmostEqual(-xyz[50,2],f,places=9)
  self.assertAlmostEqual(g['longitud_m'],2*a*math.sinh(L/(2*a)),places=9)
 def test_equilibrio_vectorial_inclinado_viento(self):
  g=catenaria(2205,71,21,1.32,3.4);f=np.array(g['F0'])+g['F1']
  np.testing.assert_allclose(f,[0,3.4*g['longitud_m'],-1.32*g['longitud_m']],atol=1e-8)
  np.testing.assert_allclose(perfil(g)[-1],[71,0,21],atol=1e-8)
 def test_cambio_estado_conserva_longitud(self):
  ea=62e9*49.5e-6;ref=catenaria(2205,80,20,1.32389775)
  g=resolver_estado(80.,20.,2205.,1.32389775,ea,23e-6,15.,75.,1.32389775,0.,345e-6)
  target=longitud_natural(ref,ea)*(1+23e-6*60+345e-6)
  self.assertAlmostEqual(longitud_natural(g,ea),target,places=8)
 def test_vanos_rigidos_desiguales_no_comparten_traccion(self):
  ea=62e9*49.5e-6
  a=resolver_estado(30.,0.,2205.,1.32389775,ea,23e-6,15.,5.,1.32389775,3.44,0.)
  b=resolver_estado(80.,0.,2205.,1.32389775,ea,23e-6,15.,5.,1.32389775,3.44,0.)
  self.assertGreater(abs(a['H']-b['H']),100)
 def test_desnivel_puede_arrancar_aislador(self):
  g=catenaria(2205,50,30,1.32)
  self.assertGreater(g['F0'][2],0)
  self.assertLess(g['F1'][2],0)
 def test_carga_transversal_no_es_peso_vertical(self):
  c=capacidad_momento(13,1.9,400)
  self.assertAlmostEqual(c['M_servicio_kNm'],43.8)
  self.assertAlmostEqual(c['M_resistente_estudio_kNm'],56.94)
 def test_rechaza_dato_no_fisico(self):
  with self.assertRaises(ValueError):catenaria(0,50,0,1)
class Electrica(unittest.TestCase):
 def test_flujo_coincide_con_solucion_cuadratica_resistiva(self):
  v=10000.;r=5.;p=180000.;vp=v/math.sqrt(3)
  expected=(vp+math.sqrt(vp*vp-4*r*p/3))/2*math.sqrt(3)
  f=flujo_radial(v,[complex(r,0)],[complex(p,0)])
  self.assertAlmostEqual(f['tensiones_LL_V'][1],expected,places=5)
  self.assertLess(abs(f['residuo_balance_W']),1e-5)
 def test_sin_carga_sin_perdida(self):
  f=flujo_radial(22900,[complex(5,3)],[0j])
  self.assertEqual(f['perdidas_W'][0],0)
  self.assertAlmostEqual(f['tensiones_LL_V'][-1],22900.)
 def test_resistencia_usa_longitud_real_y_temperatura(self):
  c=dict(r20_ohm_km=.671,alpha_r=.0036,diametro_mm=9)
  z,a=impedancia_linea(c,6758.12,60,[1.2,1.2,2.4],75)
  self.assertAlmostEqual(z.real,.671*(1+.0036*55)*6.75812)
 def test_elevar_tension_reduce_perdida(self):
  a=flujo_radial(10000,[complex(5.4,3.1)],[complex(171486,83054)])
  b=flujo_radial(22900,[complex(5.4,3.1)],[complex(171486,83054)])
  self.assertLess(b['perdidas_W'][0],a['perdidas_W'][0]/5)
if __name__=='__main__':unittest.main()
