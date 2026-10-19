"""Regresiones de cantidades y de la relación física entre armados y puentes."""
import copy
import json
import math
import unittest
from pathlib import Path

from metrados_componentes import cargar, medir

P = Path(__file__).resolve().parents[2]


class MetradoPorPoste(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((P/'revisiones/lp-r02/03-calculos/resultados.json').read_text())
        cls.catalogo, cls.criterios = cargar()
        cls.m = medir(cls.base, cls.catalogo, cls.criterios)

    def test_referencia_dge_sin_neutro(self):
        a = self.catalogo['armados']
        self.assertEqual(a['CAC-S']['coef']['PIN'], 3)
        self.assertEqual(a['CAC-A']['coef']['PIN'], 6)
        self.assertEqual(a['CAC-R']['coef']['GAN'], 6)
        self.assertEqual(a['CAC-R']['coef']['DISCO'], 12)
        self.assertEqual(a['CAC-T']['coef']['GAN'], 3)
        self.assertEqual(a['CAC-T']['coef']['DISCO'], 6)
        self.assertEqual(a['RI-A']['coef']['MOR'], 4)
        for armado in a.values():
            self.assertFalse(armado['aprobado_fabricacion'])
            self.assertFalse({'pm','j1','a8','da'} & set(armado['coef']))

    def test_totales_independientes_por_poblacion(self):
        q = self.m['resumen_compra']
        self.assertEqual(self.m['postes'],111)
        self.assertEqual(q['P13']+q['P15']+q['P17'],111)
        self.assertEqual(q['PIN'], 30*3+41*6+(22+16))
        self.assertEqual(q['DISCO'], (22+16)*12+2*6)
        self.assertEqual(q['CRU-M'], 30+(41+22+16+2)*2)
        self.assertEqual(q['MOR'],160*4)
        self.assertEqual(q['BLO-R'],160)
        self.assertEqual(q['EL-PAT'],111)

    def test_terminal_y_paso_no_se_confunden(self):
        def cantidad(p,k):
            return sum(e['cantidad'] for e in self.m['inventario']
                       if e['poste']==p and e['material']==k and e['nivel']=='COMPRA')
        self.assertEqual(cantidad('P001','DISCO'),6)
        self.assertEqual(cantidad('P001','GAN'),3)
        self.assertEqual(cantidad('P001','BLO-R'),1)
        self.assertEqual(cantidad('P002','PIN'),3)
        self.assertEqual(cantidad('P002','BLO-R'),0)
        self.assertEqual(cantidad('P003','DISCO'),12)
        self.assertEqual(cantidad('P003','BLO-R'),2)

    def test_puentes_dependen_de_la_interrupcion_electrica(self):
        self.assertEqual(self.m['conductor']['puentes_provision_m'],3*(38+2)*2)
        b=copy.deepcopy(self.base)
        for p in b['postes']:
            if p['tipo_r02']=='ANGULO': p['retenidas_r02']+=1
        otro=medir(b,self.catalogo,self.criterios)
        self.assertEqual(otro['conductor'],self.m['conductor'])
        self.assertEqual(otro['ramales']-self.m['ramales'],41)
        self.assertEqual(otro['resumen_compra']['MOR']-self.m['resumen_compra']['MOR'],164)

    def test_conductor_y_asignacion_cuadran(self):
        z=self.m['conductor']
        real=sum(v['estados']['EDS']['longitud_cable_m']*3 for v in self.base['vanos'])
        self.assertAlmostEqual(z['tendido_terna_m'],real,places=7)
        self.assertAlmostEqual(sum(a['tendido_asignado_m'] for a in self.m['asignaciones']),real,places=7)
        self.assertEqual(z['reserva_m'],616)
        self.assertEqual(z['total_compra_estudio_m'],21131)
        self.assertTrue(0<=z['redondeo_compra_m']<1)

    def test_incluidos_y_compra_separados(self):
        for e in self.m['inventario']:
            if e['nivel']=='INCLUIDO':
                self.assertTrue(e['incluido_en'])
                self.assertNotIn(e['material'],self.m['resumen_compra'])
        fisicos=sum(e['cantidad'] for e in self.m['inventario'] if e['material']=='N16')
        self.assertEqual(fisicos,self.m['resumen_incluidos']['N16'])

    def test_geometria_y_cable_retenida(self):
        a=self.m['asignaciones'][0]
        self.assertAlmostEqual(a['cable_retenida_unit_m'],10.6/math.sin(math.pi/4)+3,places=8)
        self.assertEqual(self.m['giros_especiales'],['P003','P035','P057'])
        self.assertEqual(self.criterios['capacidad_minima_retenida_kN'],60)

    def test_rechaza_funcion_sin_desglose(self):
        b=copy.deepcopy(self.base);b['postes'][0]['tipo_r02']='DESCONOCIDO'
        with self.assertRaisesRegex(ValueError,'Función sin receta'):
            medir(b,self.catalogo,self.criterios)


if __name__ == '__main__':
    unittest.main()
