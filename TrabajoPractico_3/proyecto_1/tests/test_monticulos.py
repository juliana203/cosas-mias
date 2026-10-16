import unittest
from modules.monticulos import MonticuloMinimos, MonticuloMaximos


class TestMonticuloMinimos(unittest.TestCase):

    def test_infiltracion_arriba_camino_largo(self):
        heap = MonticuloMinimos()
        for val in [50, 40, 30, 20, 10]:
            heap.insertar(val)
        heap.insertar(1)
        self.assertEqual(heap.obtener_raiz(), 1)
        self.assertEqual(heap.tamano(), 6)

    def test_infiltracion_arriba_se_detiene(self):
        heap = MonticuloMinimos()
        for val in [10, 50, 20, 60, 70]:
            heap.insertar(val)
        self.assertEqual(heap.obtener_raiz(), 10)

    def test_eliminar_y_reorganizar(self):
        heap = MonticuloMinimos()
        for val in [10, 5, 20, 15, 2, 8]:
            heap.insertar(val)
        self.assertEqual(heap.eliminar_raiz(), 2)
        self.assertEqual(heap.obtener_raiz(), 5)
        self.assertEqual(heap.tamano(), 5)

    def test_valores_duplicados(self):
        heap = MonticuloMinimos()
        heap.insertar(5)
        heap.insertar(5)
        heap.insertar(1)
        self.assertEqual(heap.eliminar_raiz(), 1)
        self.assertEqual(heap.eliminar_raiz(), 5)
        self.assertEqual(heap.eliminar_raiz(), 5)
        self.assertTrue(heap.esta_vacio())

    def test_vacio(self):
        heap = MonticuloMinimos()
        self.assertTrue(heap.esta_vacio())
        self.assertIsNone(heap.obtener_raiz())
        self.assertIsNone(heap.eliminar_raiz())


class TestMonticuloMaximos(unittest.TestCase):

    def test_infiltracion_arriba_camino_largo(self):
        heap = MonticuloMaximos()
        for val in [1, 2, 3, 4, 5]:
            heap.insertar(val)
        heap.insertar(100)
        self.assertEqual(heap.obtener_raiz(), 100)
        self.assertEqual(heap.tamano(), 6)

    def test_eliminar_y_reorganizar(self):
        heap = MonticuloMaximos()
        for val in [10, 50, 5, 15, 20]:
            heap.insertar(val)
        self.assertEqual(heap.eliminar_raiz(), 50)
        self.assertEqual(heap.obtener_raiz(), 20)

    def test_hijo_prioritario_derecha(self):
        heap = MonticuloMaximos()
        for val in [5, 10, 20, 15, 8]:
            heap.insertar(val)
        self.assertEqual(heap.eliminar_raiz(), 20)
        self.assertEqual(heap.obtener_raiz(), 15)


if __name__ == "__main__":
    unittest.main()