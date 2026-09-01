import unittest
from datetime import datetime

from modules.usuarios import UsuarioFinal
from modules.reclamo import Reclamo, EstadoReclamo
from modules.excepciones import TransicionEstadoInvalidaError


class TestEstadoReclamo(unittest.TestCase):
    def test_valores_fijos(self):
        self.assertEqual(EstadoReclamo.PENDIENTE.value, "pendiente")
        self.assertEqual(EstadoReclamo.EN_PROCESO.value, "en proceso")
        self.assertEqual(EstadoReclamo.RESUELTO.value, "resuelto")
        self.assertEqual(EstadoReclamo.INVALIDO.value, "inválido")


class TestReclamoInicializacion(unittest.TestCase):
    def setUp(self):
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.reclamo = Reclamo(self.creador, "El proyector no enciende", "maestranza")

    def test_estado_inicial_es_pendiente(self):
        self.assertEqual(self.reclamo.estado, "pendiente")

    def test_sin_adherentes_al_crear(self):
        self.assertEqual(self.reclamo.numero_adherentes, 0)

    def test_sin_tiempo_de_resolucion_al_crear(self):
        self.assertIsNone(self.reclamo.tiempo_resolucion_asignado)

    def test_timestamp_se_asigna_automaticamente(self):
        self.assertIsInstance(self.reclamo.timestamp, datetime)

    def test_id_reclamo_setter(self):
        self.reclamo.id_reclamo = 999
        self.assertEqual(self.reclamo.id_reclamo, 999)

    def test_departamento_setter_para_derivar(self):
        self.reclamo.departamento = "soporte informático"
        self.assertEqual(self.reclamo.departamento, "soporte informático")


class TestReclamoAdhesion(unittest.TestCase):
    def setUp(self):
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.otro = UsuarioFinal("Marco", "Ruiz", "marco@fi.uner.edu.ar",
                                  "mruiz", "docente", "Clave456!", id_bd=2)
        self.reclamo = Reclamo(self.creador, "El proyector no enciende", "maestranza")

    def test_adherir_usuario(self):
        self.reclamo.agregar_adherentes(self.otro)
        self.assertEqual(self.reclamo.numero_adherentes, 1)
        self.assertIn(self.otro, self.reclamo.adherentes)

    def test_quitar_adherente(self):
        self.reclamo.agregar_adherentes(self.otro)
        self.reclamo.quitar_adherentes(self.otro)
        self.assertEqual(self.reclamo.numero_adherentes, 0)


class TestReclamoCambiarEstado(unittest.TestCase):
    def setUp(self):
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.reclamo = Reclamo(self.creador, "El proyector no enciende", "maestranza")

    def test_en_proceso_sin_dias_lanza_excepcion(self):
        with self.assertRaises(TransicionEstadoInvalidaError):
            self.reclamo.cambiar_estado("en proceso")

    def test_en_proceso_con_dias_mayor_a_15_lanza_excepcion(self):
        with self.assertRaises(TransicionEstadoInvalidaError):
            self.reclamo.cambiar_estado("en proceso", dias_resolucion=16)

    def test_en_proceso_con_dias_validos(self):
        self.reclamo.cambiar_estado("en proceso", dias_resolucion=7)
        self.assertEqual(self.reclamo.estado, "en proceso")
        self.assertEqual(self.reclamo.tiempo_resolucion_asignado, 7)

    def test_estado_invalido_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.reclamo.cambiar_estado("no_existe")

    def test_excepcion_expone_los_dias_recibidos(self):
        try:
            self.reclamo.cambiar_estado("en proceso", dias_resolucion=50)
            self.fail("debería haber lanzado TransicionEstadoInvalidaError")
        except TransicionEstadoInvalidaError as e:
            self.assertEqual(e.dias_resolucion, 50)


if __name__ == "__main__":
    unittest.main()