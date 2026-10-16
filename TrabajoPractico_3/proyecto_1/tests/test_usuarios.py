import unittest

from modules.usuarios import Usuario, UsuarioFinal, JefeDepartamento, SecretarioTecnico, Departamento
from modules.excepciones import ClaustroInvalidoError


class TestDepartamento(unittest.TestCase):
    def test_igualdad_por_nombre_cuando_no_hay_id(self):
        d1 = Departamento("maestranza")
        d2 = Departamento("maestranza")
        self.assertEqual(d1, d2)

    def test_desigualdad(self):
        d1 = Departamento("maestranza", id=1)
        d2 = Departamento("soporte informático", id=2)
        self.assertNotEqual(d1, d2)

    def test_id_setter(self):
        d = Departamento("maestranza")
        self.assertIsNone(d.id)
        d.id = 5
        self.assertEqual(d.id, 5)

class TestUsuarioAbstracto(unittest.TestCase):
    def test_no_se_puede_instanciar_directamente(self):
        with self.assertRaises(TypeError):
            Usuario("a", "b", "c", "d", "e")

    def test_igualdad_por_id_bd(self):
        u1 = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass", id_bd=10)
        u2 = UsuarioFinal("X", "Y", "x@y.com", "xy", "docente", "otra", id_bd=10)
        self.assertEqual(u1, u2)

    def test_desigualdad_por_id_bd_distinto(self):
        u1 = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass", id_bd=1)
        u2 = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass", id_bd=2)
        self.assertNotEqual(u1, u2)


class TestUsuarioFinal(unittest.TestCase):
    def setUp(self):
        self.usuario = UsuarioFinal(
            "Juliana", "Perez", "juliana@fiuner.edu.ar", "jperez",
            "estudiante", "Clave123!", id_bd=1,
        )

    def test_rol_fijo(self):
        self.assertEqual(self.usuario.rol, "usuario_final")

    def test_claustro_valido_se_guarda(self):
        self.assertEqual(self.usuario.claustro, "estudiante")

    def test_claustro_invalido_lanza_excepcion(self):
        with self.assertRaises(ClaustroInvalidoError):
            UsuarioFinal("A", "B", "a@b.com", "ab", "claustro_invalido", "pass")

    def test_claustro_invalido_expone_atributos_utiles(self):
        try:
            UsuarioFinal("A", "B", "a@b.com", "ab", "claustro_invalido", "pass")
            self.fail("debería haber lanzado ClaustroInvalidoError")
        except ClaustroInvalidoError as e:
            self.assertEqual(e.claustro, "claustro_invalido")
            self.assertIn("estudiante", e.claustros_validos)

    def test_contrasena_no_se_guarda_en_texto_plano(self):
        self.assertNotEqual(self.usuario.contrasena, "Clave123!")

    def test_verificar_contrasena_correcta(self):
        self.assertTrue(self.usuario.verificar_contrasena("Clave123!"))

    def test_verificar_contrasena_incorrecta(self):
        self.assertFalse(self.usuario.verificar_contrasena("otra_clave"))

    def test_get_id_devuelve_string_del_id_bd(self):
        self.assertEqual(self.usuario.get_id(), "1")


class TestJefeDepartamento(unittest.TestCase):
    def test_departamento_asignado_y_rol(self):
        depto = Departamento("maestranza", id=1)
        jefe = JefeDepartamento(
            "Ana", "Gomez", "ana.gomez@fi.uner.edu.ar", "agomez",
            "Clave123!", depto, id_bd=2,
        )
        self.assertEqual(jefe.departamento_asignado, depto)
        self.assertEqual(jefe.rol, "jefe_departamento")

    def test_hereda_verificacion_de_contrasena(self):
        depto = Departamento("maestranza", id=1)
        jefe = JefeDepartamento("Ana", "Gomez", "ana@fi.uner.edu.ar", "agomez",
                                 "Clave123!", depto)
        self.assertTrue(jefe.verificar_contrasena("Clave123!"))
        self.assertFalse(jefe.verificar_contrasena("otra"))


class TestSecretarioTecnico(unittest.TestCase):
    def test_rol_fijo(self):
        secretario = SecretarioTecnico(
            "Laura", "Fernandez", "laura.fernandez@fi.uner.edu.ar",
            "lfernandez", "Clave123!", id_bd=3,
        )
        self.assertEqual(secretario.rol, "secretario_tecnico")

    def test_id_bd_por_defecto_es_none(self):
        secretario = SecretarioTecnico("A", "B", "a@b.com", "ab", "pass")
        self.assertIsNone(secretario.id_bd)


if __name__ == "__main__":
    unittest.main()