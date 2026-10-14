import math
import unittest
from herramientas.hidroelectricas.calculos import (
    hidro, darcy, comprobar_longitud, trifasico, transitorio, tirante_normal,
    manning_rectangular, linea, cargas_por_modo, balance_exportacion,
    tubo_mecanico, reja, sedimentador)


class CalculosTest(unittest.TestCase):
    def test_colebrook_satisface_ecuacion(self):
        f = darcy(1e6, 0.0001)
        residuo = 1/math.sqrt(f)+2*math.log10(.0001/3.7+2.51/(1e6*math.sqrt(f)))
        self.assertAlmostEqual(residuo, 0, places=10)

    def test_balance_energia(self):
        h = hidro(.38, 52, 175, .39, .000045, 1.24e-6, 1, .84, .985, .925)
        bruto = 9.81*.38*52
        perdidas_hidraulicas = 9.81*.38*h['htotal_m']
        perdidas_conversion = h['p_hidraulica_kw']-h['p_bornes_kw']
        self.assertAlmostEqual(bruto, perdidas_hidraulicas+perdidas_conversion+h['p_bornes_kw'])
        self.assertLess(h['p_bornes_kw'], 150)

    def test_geometria_invalida_del_borrador(self):
        r = comprobar_longitud([425120,8441860,3202], [425260,8441710,3150],175)
        self.assertFalse(r['geometria_posible'])
        self.assertAlmostEqual(r['minimo_m'],211.6695537860842)

    def test_casos_fisicos_limite(self):
        self.assertEqual(darcy(1000,0),.064)
        with self.assertRaises(ValueError): darcy(3000,0)
        with self.assertRaises(ValueError): trifasico(150,1.1,.4)
        with self.assertRaises(ValueError): hidro(.38,1,175,.1,.000045,1e-6,1,.84,.985,.925)
        with self.assertRaises(ValueError): hidro(float('nan'),52,175,.39,.000045,1e-6,1,.84,.985,.925)

    def test_manobra_rapida_no_usa_michaud(self):
        r = transitorio(220,2.6,.45,.00635,52,.01)
        self.assertEqual(r['regimen'],'rapido')
        self.assertIsNone(r['dh_lento_m'])

    def test_tirante_cierra_caudal(self):
        y = tirante_normal(.42,.8,.002,.015)
        self.assertAlmostEqual(manning_rectangular(.8,y,.002,.015)['q_m3s'],.42)

    def test_linea_trifasica_sin_perdidas(self):
        r = linea(150,50,22.9,0,0)
        self.assertEqual(r['perdida_kw'],0)
        self.assertEqual(r['variacion_pct'],0)
        self.assertAlmostEqual(trifasico(150,1,.4)['i_a'],216.5063509461)

    def test_reactivo_se_suma_por_equipo_no_por_kva(self):
        filas=[dict(id='a',cantidad=2,p_unit_kw=3,fp=.8),
               dict(id='b',cantidad=1,p_unit_kw=4,fp=1)]
        r=cargas_por_modo(filas,{'a':1,'b':1})
        self.assertEqual(r['p_kw'],7)
        self.assertAlmostEqual(r['q_kvar'],2.25)
        self.assertAlmostEqual(r['s_kva'],math.hypot(7,2.25))
        with self.assertRaises(ValueError):cargas_por_modo(filas,{'a':3,'b':1})
        with self.assertRaises(ValueError):cargas_por_modo(filas,{'a':1})

    def test_exportacion_conserva_potencia_y_sensibilidad_de_auxiliares(self):
        args=dict(p_gen_kw=150,fp_gen=.85,p_aux_kw=5,q_aux_kvar=3,
                  s_tx_kva=250,p0_tx_kw=.6,pcu_tx_kw=3.5,v_mt_kv=22.9,r_ohm=1.2,x_ohm=.48)
        r=balance_exportacion(**args)
        self.assertLess(r['p_pcc_kw'],145)
        self.assertAlmostEqual(150,5+r['trafo']['p_kw']+r['linea']['perdida_kw']+r['p_pcc_kw'])
        args['p_aux_kw']=6
        self.assertLess(balance_exportacion(**args)['p_pcc_kw'],r['p_pcc_kw'])
        args.update(p_aux_kw=0,q_aux_kvar=0,p0_tx_kw=0,pcu_tx_kw=0,r_ohm=0,x_ohm=0)
        self.assertEqual(balance_exportacion(**args)['p_pcc_kw'],150)

    def test_viga_respeta_leyes_de_escala(self):
        args=dict(diametro=.5,espesor_nom=.00635,longitud=220,tolerancia_fraccion=.125,
                  corrosion_m=.001,presion_pa=8e5,angulo_codo_deg=45,delta_t_c=40)
        corta=tubo_mecanico(vano_m=4,**args)
        larga=tubo_mecanico(vano_m=8,**args)
        self.assertAlmostEqual(larga['flecha_mm']/corta['flecha_mm'],16)
        self.assertAlmostEqual(larga['sigma_flexion_mpa']/corta['sigma_flexion_mpa'],4)
        self.assertAlmostEqual(corta['espesor_ef_m'],.00455625)
        self.assertEqual(corta['masa_nom_kg'],larga['masa_nom_kg'])
        args['corrosion_m']=.01
        with self.assertRaises(ValueError):tubo_mecanico(vano_m=4,**args)

    def test_reja_incluye_porcentaje_abierto_y_bloqueo(self):
        r=reja(.42,.6,.6,.4)
        self.assertAlmostEqual(r*.6*.6*(1-.4),.42)
        self.assertGreater(r,reja(.42,.6,1,.4))
        with self.assertRaises(ValueError):reja(.42,.6,.6,1)

    def test_sedimentacion_geometrica_y_tiempos_coinciden(self):
        r=sedimentador(.42,2.6,10,1.5,.025,1.5)
        self.assertTrue(r['criterio_ideal'])
        self.assertAlmostEqual(r['relacion_tiempos'],r['area_m2']*.025/.42)
        self.assertFalse(sedimentador(.42,2.6,5,1.5,.025,1.5)['criterio_ideal'])

    def test_valores_no_finitos_en_red_y_transitorio_se_rechazan(self):
        with self.assertRaises(ValueError):linea(150,50,22.9,float('nan'),.4)
        with self.assertRaises(ValueError):transitorio(220,2.6,.45,.00635,52,4,modulo_acero=float('nan'))


if __name__ == '__main__': unittest.main()
