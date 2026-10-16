import unittest
# Archivo de test para realizar pruebas unitarias de edificios y agentes
from modules.Alimentos import Manzana,Kiwi,Papa,Zanahoria
from modules.Maquinaria import Cajon,Cinta,Calculadora

class TestCinta(unittest.TestCase):
    def test_transportar(self):
        cinta = Cinta()
        alimentos_detectados = cinta.transportar()
        self.assertIn(alimentos_detectados["alimento"], ["kiwi", "manzana", "papa", "zanahoria", "undefined"])
        self.assertLessEqual(alimentos_detectados["peso"], 0.60)

class TestAlimentos(unittest.TestCase):
    
    def test_calcularaw(self):
        kiwi = Kiwi(0.2)
        manzana = Manzana(0.2)
        papa = Papa(0.2)
        zanahoria = Zanahoria(0.2)
        self.assertAlmostEqual(kiwi.calcularaw(), 0.91, places=2)
        self.assertAlmostEqual(manzana.calcularaw(), 0.87, places=2)
        self.assertAlmostEqual(papa.calcularaw(), 0.86, places=2)
        self.assertAlmostEqual(zanahoria.calcularaw(), 0.83, places=2)


class TestCajon(unittest.TestCase):
    def test_cargarcajon(self):
        kiwi = Kiwi(0.2)
        manzana = Manzana(0.2)
        papa = Papa(0.2)
        zanahoria = Zanahoria(0.2)
        cajon = Cajon()
        cajon.cargaralimento(kiwi)
        cajon.cargaralimento(manzana)
        cajon.cargaralimento(papa)
        cajon.cargaralimento(zanahoria)
        alimentos = list(cajon)
        self.assertEqual(len(alimentos), 4)
        self.assertAlmostEqual(cajon.getpeso(), 0.8, places=2)
        for alimento in alimentos:
            self.assertIn(alimento.getmasa(), [0.2])
            

class TestCalculadora(unittest.TestCase):
    def setUp(self):
        self.cajon = Cajon()
        self.cajon.cargaralimento(Kiwi(0.2))
        self.cajon.cargaralimento(Manzana(0.2))
        self.cajon.cargaralimento(Papa(0.2))
        self.cajon.cargaralimento(Zanahoria(0.2))
        self.calculadora = Calculadora(self.cajon)

    def test_calcularprom(self):
        result = self.calculadora.calcularprom()
        self.assertAlmostEqual(result["awkiwiprom"], 0.91, places=2)
        self.assertAlmostEqual(result["awmanzanaprom"], 0.87, places=2)
        self.assertAlmostEqual(result["awpapaprom"], 0.86, places=2)
        self.assertAlmostEqual(result["awzanahoriaprom"], 0.83, places=2)
        self.assertAlmostEqual(result["awfrutasprom"], (0.91 + 0.87) / 2, places=2)
        self.assertAlmostEqual(result["awverdurasprom"], round((0.86 + 0.83) / 2,2), places=2)
        self.assertAlmostEqual(result["awprom"], round((0.91 + 0.87 + 0.86 + 0.83) / 4,2), places=3)

if __name__ == '__main__':
    unittest.main()