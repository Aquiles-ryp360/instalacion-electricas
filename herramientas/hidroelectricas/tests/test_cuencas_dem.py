import unittest
import numpy as np
from herramientas.hidroelectricas.cuencas_dem import drenaje_d8, cuenca_receptora


class CuencasDEM(unittest.TestCase):
    def test_conservacion_y_cuenca(self):
        # Ladera inclinada con vaguada, prueba independiente del caso Limbani.
        z = np.array([[8,7,8,9,10],[7,6,7,8,9],[6,5,6,7,8],
                      [5,4,5,6,7],[4,3,4,5,6]], dtype=float)
        _, rec, acc = drenaje_d8(z, 30, 30)
        self.assertEqual(int(acc.ravel()[rec.ravel() < 0].sum()), z.size)
        mask = cuenca_receptora(rec, 21)
        self.assertEqual(int(mask.sum()), int(acc.ravel()[21]))
        self.assertGreater(int(mask.sum()), 1)

    def test_relleno_depresion(self):
        z = np.ones((5,5))*10
        z[2,2] = -5
        filled, rec, acc = drenaje_d8(z, 90, 90)
        self.assertEqual(filled[2,2], 10)
        self.assertGreaterEqual(rec[2,2], 0)
        self.assertEqual(int(acc.ravel()[rec.ravel() < 0].sum()), 25)

    def test_rechaza_vacios(self):
        with self.assertRaises(ValueError):
            drenaje_d8([[1,float('nan'),2]]*3, 30, 30)


if __name__ == '__main__':
    unittest.main()
