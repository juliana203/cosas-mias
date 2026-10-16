import unittest
from datetime import datetime

from modules.usuarios import UsuarioFinal, Departamento
from modules.reclamos import Reclamo, EstadoReclamo
from modules.excepciones import AutoAdhesionError, AdhesionDuplicadaError, TransicionEstadoInvalidaError


class TestEstadoReclamo(unittest.TestCase):
    def test_valores_fijos(self):
        self.assertEqual(EstadoReclamo.PENDIENTE.value, "pendiente")
        self.assertEqual(EstadoReclamo.EN_PROCESO.value, "en_proceso")
        self.assertEqual(EstadoReclamo.RESUELTO.value, "resuelto")
        self.assertEqual(EstadoReclamo.INVALIDO.value, "invalido")

    def test_str_devuelve_el_value(self):
        self.assertEqual(str(EstadoReclamo.PENDIENTE), "pendiente")

    def test_construir_desde_string_invalida_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            EstadoReclamo("estado_que_no_existe")


class TestReclamoInicializacion(unittest.TestCase):
    def setUp(self):
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.depto = Departamento("maestranza", id=1)
        self.reclamo = Reclamo(self.creador, "El proyector no enciende", self.depto, id_reclamo=100)

    def test_estado_inicial_es_pendiente(self):
        self.assertEqual(self.reclamo.estado, EstadoReclamo.PENDIENTE)

    def test_sin_adherentes_al_crear(self):
        self.assertEqual(self.reclamo.adherentes, [])

    def test_sin_tiempo_de_resolucion_al_crear(self):
        self.assertIsNone(self.reclamo.tiempo_resolucion_asignado)

    def test_con_imagen_adjunta(self):
        reclamo_con_foto = Reclamo(self.creador, "El proyector no enciende", self.depto,
                                    ruta_imagen="uploads/abc123_foto.jpg")
        self.assertEqual(reclamo_con_foto.ruta_imagen, "uploads/abc123_foto.jpg")

    def test_timestamp_se_asigna_automaticamente(self):
        self.assertIsInstance(self.reclamo.timestamp, datetime)

    def test_id_reclamo_setter(self):
        self.reclamo.id_reclamo = 999
        self.assertEqual(self.reclamo.id_reclamo, 999)

    def test_departamento_setter_para_derivar(self):
        nuevo_depto = Departamento("soporte informático", id=2)
        self.reclamo.departamento = nuevo_depto
        self.assertEqual(self.reclamo.departamento, nuevo_depto)

    def test_adherentes_devuelve_copia_defensiva(self):
        """Modificar la lista devuelta no debe afectar al reclamo real"""
        copia = self.reclamo.adherentes
        copia.append("algo")
        self.assertEqual(self.reclamo.adherentes, [])


class TestReclamoAdhesion(unittest.TestCase):
    def setUp(self):
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.otro = UsuarioFinal("Marco", "Ruiz", "marco@fi.uner.edu.ar",
                                  "mruiz", "docente", "Clave456!", id_bd=2)
        self.depto = Departamento("maestranza", id=1)
        self.reclamo = Reclamo(self.creador, "El proyector no enciende", self.depto, id_reclamo=100)

    def test_creador_no_puede_adherirse_a_su_propio_reclamo(self):
        with self.assertRaises(AutoAdhesionError):
            self.reclamo.agregar_adherente(self.creador)

    def test_otro_usuario_puede_adherirse(self):
        self.reclamo.agregar_adherente(self.otro)
        self.assertEqual(len(self.reclamo.adherentes), 1)
        self.assertIn(self.otro, self.reclamo.adherentes)

    def test_quitar_adherente(self):
        self.reclamo.agregar_adherente(self.otro)
        self.reclamo.quitar_adherente(self.otro.id_bd)
        self.assertEqual(self.reclamo.adherentes, [])


class TestReclamoCambiarEstado(unittest.TestCase):
    def setUp(self):
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.depto = Departamento("maestranza", id=1)
        self.reclamo = Reclamo(self.creador, "El proyector no enciende", self.depto, id_reclamo=100)

    def test_en_proceso_sin_dias_lanza_excepcion(self):
        with self.assertRaises(TransicionEstadoInvalidaError):
            self.reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO)

    def test_en_proceso_con_dias_en_cero_lanza_excepcion(self):
        with self.assertRaises(TransicionEstadoInvalidaError):
            self.reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=0)

    def test_en_proceso_con_dias_mayor_a_15_lanza_excepcion(self):
        with self.assertRaises(TransicionEstadoInvalidaError):
            self.reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=16)

    def test_en_proceso_con_dias_en_el_limite_inferior_es_valido(self):
        self.reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=1)
        self.assertEqual(self.reclamo.tiempo_resolucion_asignado, 1)

    def test_en_proceso_con_dias_en_el_limite_superior_es_valido(self):
        self.reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=15)
        self.assertEqual(self.reclamo.tiempo_resolucion_asignado, 15)

    def test_en_proceso_con_dias_valido_actualiza_estado_y_tiempo(self):
        self.reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=7)
        self.assertEqual(self.reclamo.estado, EstadoReclamo.EN_PROCESO)
        self.assertEqual(self.reclamo.tiempo_resolucion_asignado, 7)

    def test_excepcion_expone_los_dias_recibidos(self):
        try:
            self.reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=50)
            self.fail("debería haber lanzado TransicionEstadoInvalidaError")
        except TransicionEstadoInvalidaError as e:
            self.assertEqual(e.dias_resolucion, 50)


if __name__ == "__main__":
    unittest.main()
