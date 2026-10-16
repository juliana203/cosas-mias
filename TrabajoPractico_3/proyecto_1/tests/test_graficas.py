import unittest
from modules.graficas import Graficas


class TestGraficas(unittest.TestCase):
    def setUp(self):
        self.graficas = Graficas()

    def _assert_es_data_uri_png(self, resultado):
        self.assertTrue(resultado.startswith("data:image/png;base64,"))
        self.assertGreater(len(resultado), 500)

    def test_grafica_tor_con_datos(self):
        stats = {"total": 4, "pendientes": 0, "en_proceso": 50.0, "resueltos": 25.0, "invalidos": 25.0}
        self._assert_es_data_uri_png(self.graficas.generar_grafica_tor(stats))

    def test_grafica_tiem(self):
        self._assert_es_data_uri_png(self.graficas.generar_grafica_tiem(4.5))

    def test_grafica_pf_con_datos(self):
        palabras = [("aula", 3), ("proyector", 2), ("luz", 1)]
        self._assert_es_data_uri_png(self.graficas.generar_grafica_pf(palabras))


if __name__ == "__main__":
    unittest.main()