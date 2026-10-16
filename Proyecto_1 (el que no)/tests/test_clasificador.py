import os
import pickle
import tempfile
import unittest
from unittest.mock import MagicMock

from modules.clasificador import ClasificadorReclamos, DEPARTAMENTOS_CLASIFICADOR
from modules.excepciones import ContenidoVacioError


class TestClasificadorReclamos(unittest.TestCase):
    def setUp(self):
        # MagicMock simula el ClaimsClassifier real
        self.clf_mock = MagicMock()
        self.adapter = ClasificadorReclamos(self.clf_mock)

    def test_clasificar_devuelve_el_string_en_una_lista(self):
        self.clf_mock.classify.return_value = ["maestranza"]
        self.adapter.clasificar("El proyector no enciende")
        self.clf_mock.classify.assert_called_once_with(["El proyector no enciende"])

    def test_clasificar_devuelve_el_primer_resultado(self):
        self.clf_mock.classify.return_value = ["soporte informático"]
        resultado = self.adapter.clasificar("No puedo entrar al campus virtual")
        self.assertEqual(resultado, "soporte informático")

    def test_contenido_vacio_string_vacio(self):
        with self.assertRaises(ContenidoVacioError):
            self.adapter.clasificar("")


class _ClfFalsoParaPickle:
    def classify(self, X):
        return ["maestranza" for _ in X]


class TestClasificadorReclamosDesdePickle(unittest.TestCase):
    def test_desde_pickle_carga_y_delega_correctamente(self):
        """
        Simula el flujo real
        """
        clf_falso = _ClfFalsoParaPickle()

        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "clf_de_prueba.pkl")
            with open(ruta, "wb") as f:
                pickle.dump(clf_falso, f)

            adapter = ClasificadorReclamos.desde_pickle(ruta)
            resultado = adapter.clasificar("El aula 3 tiene la luz quemada")
            self.assertEqual(resultado, "maestranza")


class TestDepartamentosClasificador(unittest.TestCase):
    def test_son_exactamente_los_3_documentados_por_la_catedra(self):
        self.assertEqual(
            DEPARTAMENTOS_CLASIFICADOR,
            ("soporte informático", "secretaría técnica", "maestranza"),
        )

    def test_es_una_tupla_inmutable(self):
        self.assertIsInstance(DEPARTAMENTOS_CLASIFICADOR, tuple)


if __name__ == "__main__":
    unittest.main()
