import unittest

from modules.usuarios import UsuarioFinal
from modules.reclamo import Reclamo
from modules.estadisticas import Analitica


def _crear_reclamos():
    creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                            "jperez", "estudiante", "Clave123!", id_bd=1)
    contenidos = [
        "El proyector del aula 3 no enciende",
        "La luz del aula 2 esta quemada",
        "El aire acondicionado no enfria",
        "El pizarron esta roto",
    ]
    reclamos = [Reclamo(creador, c, "maestranza") for c in contenidos]
    reclamos[0].cambiar_estado("en proceso", dias_resolucion=5)
    reclamos[1].cambiar_estado("en proceso", dias_resolucion=3)
    reclamos[2].cambiar_estado("resuelto")
    reclamos[3].cambiar_estado("inválido")
    return reclamos


class TestCalcularPorcentajeEstado(unittest.TestCase):
    def test_total_correcto(self):
        stats = Analitica(_crear_reclamos()).calcular_porcentaje_estado()
        self.assertEqual(stats["total"], 4)

    def test_porcentajes_suman_100(self):
        stats = Analitica(_crear_reclamos()).calcular_porcentaje_estado()
        suma = stats["pendientes"] + stats["en_proceso"] + stats["resueltos"] + stats["invalidos"]
        self.assertAlmostEqual(suma, 100.0)

    def test_porcentaje_en_proceso(self):
        # dos de cuatro reclamos quedaron en proceso -> 50%
        stats = Analitica(_crear_reclamos()).calcular_porcentaje_estado()
        self.assertAlmostEqual(stats["en_proceso"], 50.0)

    def test_lista_vacia_no_explota(self):
        stats = Analitica([]).calcular_porcentaje_estado()
        self.assertEqual(stats["total"], 0)


class TestCalcularPalabrasFrecuentes(unittest.TestCase):
    def test_detecta_palabra_repetida(self):
        palabras = [p for p, _ in Analitica(_crear_reclamos()).calcular_palabras_frecuentes()]
        self.assertIn("aula", palabras)

    def test_excluye_stopwords(self):
        palabras = [p for p, _ in Analitica(_crear_reclamos()).calcular_palabras_frecuentes()]
        for stopword in ("el", "la", "no", "del"):
            self.assertNotIn(stopword, palabras)


class TestCalcularMedianaTiemposResolucion(unittest.TestCase):
    def test_mediana_con_reclamos_en_proceso_y_resueltos(self):
        # dias asignados: 5 y 3 (los otros dos no tienen tiempo asignado) -> mediana 4.0
        mediana = Analitica(_crear_reclamos()).calcular_mediana_tiempos_resolucion()
        self.assertEqual(mediana, 4.0)

    def test_sin_reclamos_devuelve_cero(self):
        self.assertEqual(Analitica([]).calcular_mediana_tiempos_resolucion(), 0.0)


if __name__ == "__main__":
    unittest.main()