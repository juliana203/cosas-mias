import unittest
import dataclasses

from modules.usuarios import UsuarioFinal, Departamento
from modules.reclamos import Reclamo, EstadoReclamo
from modules.analitica import Analitica, Datos, Graf_torta, Graf_tiempo, Palabras_frecuentes


def _crear_reclamos_de_prueba():
    creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                            "jperez", "estudiante", "Clave123!", id_bd=1)
    depto = Departamento("maestranza", id=1)

    contenidos = [
        "El proyector del aula 3 no enciende",
        "La luz del aula 2 esta quemada",
        "El aire acondicionado no enfria",
        "El pizarron esta roto",
    ]
    reclamos = [
        Reclamo(creador, contenido, depto, id_reclamo=i)
        for i, contenido in enumerate(contenidos)
    ]
    reclamos[0].cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=5)
    reclamos[1].cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=3)
    reclamos[2].cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=7)
    reclamos[2].cambiar_estado(EstadoReclamo.RESUELTO)
    reclamos[3].cambiar_estado(EstadoReclamo.INVALIDO)
    return reclamos


class TestDatos(unittest.TestCase):
    def test_es_inmutable(self):
        datos = Datos(
            total=0, pct_pendiente=0, pct_en_proceso=0, pct_resuelto=0, pct_invalido=0,
            mediana_tiempo_en_proceso=None, mediana_tiempo_resuelto=None, palabras_frecuentes=[],
        )
        with self.assertRaises(dataclasses.FrozenInstanceError):
            datos.total = 5

class TestAnaliticaCalculardatos(unittest.TestCase):
    def setUp(self):
        self.analitica = Analitica()
        self.reclamos = _crear_reclamos_de_prueba()

    def test_total_correcto(self):
        datos = self.analitica.calculardatos(self.reclamos)
        self.assertEqual(datos.total, 4)

    def test_porcentajes_suman_100(self):
        datos = self.analitica.calculardatos(self.reclamos)
        suma = datos.pct_pendiente + datos.pct_en_proceso + datos.pct_resuelto + datos.pct_invalido
        self.assertAlmostEqual(suma, 100.0)

    def test_porcentaje_en_proceso(self):
        # reclamos[0] y reclamos[1] quedaron EN_PROCESO -> 2/4 = 50%
        datos = self.analitica.calculardatos(self.reclamos)
        self.assertAlmostEqual(datos.pct_en_proceso, 50.0)

    def test_porcentaje_resuelto(self):
        # sólo reclamos[2] quedó RESUELTO -> 1/4 = 25%
        datos = self.analitica.calculardatos(self.reclamos)
        self.assertAlmostEqual(datos.pct_resuelto, 25.0)

    def test_mediana_tiempo_en_proceso(self):
        # dias: 5 y 3 -> mediana 4.0
        datos = self.analitica.calculardatos(self.reclamos)
        self.assertEqual(datos.mediana_tiempo_en_proceso, 4.0)

    def test_mediana_tiempo_resuelto(self):
        # sólo un resuelto, con 7 dias -> mediana 7.0
        datos = self.analitica.calculardatos(self.reclamos)
        self.assertEqual(datos.mediana_tiempo_resuelto, 7.0)

    def test_lista_vacia_no_explota(self):
        datos = self.analitica.calculardatos([])
        self.assertEqual(datos.total, 0)
        self.assertEqual(datos.pct_pendiente, 0.0)
        self.assertIsNone(datos.mediana_tiempo_en_proceso)
        self.assertIsNone(datos.mediana_tiempo_resuelto)
        self.assertEqual(datos.palabras_frecuentes, [])

    def test_palabras_frecuentes_detecta_palabra_repetida(self):
        datos = self.analitica.calculardatos(self.reclamos)
        palabras = [p for p, _ in datos.palabras_frecuentes]
        self.assertIn("aula", palabras)  # aparece en 2 de los 4 reclamos

    def test_palabras_frecuentes_excluye_stopwords(self):
        datos = self.analitica.calculardatos(self.reclamos)
        palabras = [p for p, _ in datos.palabras_frecuentes]
        for stopword in ("el", "la", "no", "del"):
            self.assertNotIn(stopword, palabras)

    def test_palabras_frecuentes_maximo_15(self):
        creador = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass", id_bd=1)
        depto = Departamento("maestranza", id=1)
        # generamos 20 palabras distintas para forzar el corte en 15
        contenido = " ".join(f"palabraunica{i}" for i in range(20))
        reclamo = Reclamo(creador, contenido, depto, id_reclamo=1)
        datos = self.analitica.calculardatos([reclamo])
        self.assertLessEqual(len(datos.palabras_frecuentes), 15)


class TestGraficas(unittest.TestCase):
    def setUp(self):
        self.analitica = Analitica()
        self.datos_con_reclamos = self.analitica.calculardatos(_crear_reclamos_de_prueba())
        self.datos_vacios = self.analitica.calculardatos([])

    def _assert_es_data_uri_png(self, resultado):
        self.assertTrue(resultado.startswith("data:image/png;base64,"))
        self.assertGreater(len(resultado), 500)

    def test_graf_torta_con_datos(self):
        self._assert_es_data_uri_png(Graf_torta().generar_grafica(self.datos_con_reclamos))

    def test_graf_torta_sin_datos_no_explota(self):
        self._assert_es_data_uri_png(Graf_torta().generar_grafica(self.datos_vacios))

    def test_graf_tiempo_con_datos(self):
        self._assert_es_data_uri_png(Graf_tiempo().generar_grafica(self.datos_con_reclamos))

    def test_graf_tiempo_sin_datos_no_explota(self):
        """Medianas en None (sin reclamos resueltos/en proceso) no debe romper el gráfico."""
        self._assert_es_data_uri_png(Graf_tiempo().generar_grafica(self.datos_vacios))

    def test_palabras_frecuentes_grafica_con_datos(self):
        self._assert_es_data_uri_png(Palabras_frecuentes().generar_grafica(self.datos_con_reclamos))

    def test_palabras_frecuentes_grafica_sin_datos_no_explota(self):
        self._assert_es_data_uri_png(Palabras_frecuentes().generar_grafica(self.datos_vacios))


class TestAnaliticaMetodosDelegados(unittest.TestCase):
    def test_generar_grafica_tor_delega_en_graf_torta(self):
        analitica = Analitica()
        datos = analitica.calculardatos(_crear_reclamos_de_prueba())
        resultado = analitica.generar_grafica_tor(datos)
        self.assertTrue(resultado.startswith("data:image/png;base64,"))

    def test_generar_grafica_tie_delega_en_graf_tiempo(self):
        analitica = Analitica()
        datos = analitica.calculardatos(_crear_reclamos_de_prueba())
        resultado = analitica.generar_grafica_tie(datos)
        self.assertTrue(resultado.startswith("data:image/png;base64,"))

    def test_generar_grafica_pa_delega_en_palabras_frecuentes(self):
        analitica = Analitica()
        datos = analitica.calculardatos(_crear_reclamos_de_prueba())
        resultado = analitica.generar_grafica_pa(datos)
        self.assertTrue(resultado.startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
