"""
test_dao.py
Usa una base de datos SQLite EN MEMORIA, nueva y vacía en cada test
"""

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.persistencia import Base, ModeloUsuario, ModeloDepartamento
from modules.dao import DaoUsuarioSQLAlchemy, DaoReclamosSQLAlchemy
from modules.usuarios import UsuarioFinal, JefeDepartamento, SecretarioTecnico, Departamento
from modules.reclamos import Reclamo, EstadoReclamo
from modules.excepciones import UsuarioNoEncontradoError, ReclamoNoEncontradoError, RolUsuarioDesconocidoError


def _crear_sesion_en_memoria():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    return SessionFactory()


class TestDaoUsuarioSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.session = _crear_sesion_en_memoria()
        self.dao_usuarios = DaoUsuarioSQLAlchemy(self.session)

    def tearDown(self):
        self.session.close()

    def _crear_departamento_directo(self, nombre):
        modelo = ModeloDepartamento(nombre=nombre)
        self.session.add(modelo)
        self.session.commit()
        return Departamento(nombre=modelo.nombre, id=modelo.id)

    def test_guardar_y_obtener_usuario_final(self):
        uf = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar", "jperez",
                           "estudiante", "Clave123!")
        self.dao_usuarios.guardar(uf)
        self.assertIsNotNone(uf.id_bd)

        recuperado = self.dao_usuarios.obtener_por_id(uf.id_bd)
        self.assertIsInstance(recuperado, UsuarioFinal)
        self.assertEqual(recuperado.nombre_usuario, "jperez")
        self.assertEqual(recuperado.claustro, "estudiante")
        # la contraseña recuperada debe seguir verificando contra la original
        self.assertTrue(recuperado.verificar_contrasena("Clave123!"))

    def test_guardar_y_obtener_jefe_departamento(self):
        depto = self._crear_departamento_directo("maestranza")
        jefe = JefeDepartamento("Ana", "Gomez", "ana.gomez@fi.uner.edu.ar", "agomez",
                                 "Clave123!", depto)
        self.dao_usuarios.guardar(jefe)

        recuperado = self.dao_usuarios.obtener_por_id(jefe.id_bd)
        self.assertIsInstance(recuperado, JefeDepartamento)
        self.assertEqual(recuperado.departamento_asignado.nombre, "maestranza")
        self.assertEqual(recuperado.rol, "jefe_departamento")

    def test_guardar_y_obtener_secretario_tecnico(self):
        secretario = SecretarioTecnico("Laura", "Fernandez", "laura.fernandez@fi.uner.edu.ar",
                                        "lfernandez", "Clave123!")
        self.dao_usuarios.guardar(secretario)

        recuperado = self.dao_usuarios.obtener_por_id(secretario.id_bd)
        self.assertIsInstance(recuperado, SecretarioTecnico)
        self.assertEqual(recuperado.rol, "secretario_tecnico")

    def test_obtener_por_id_inexistente_devuelve_none(self):
        self.assertIsNone(self.dao_usuarios.obtener_por_id(9999))

    def test_obtener_todos(self):
        self.dao_usuarios.guardar(UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass"))
        self.dao_usuarios.guardar(UsuarioFinal("C", "D", "c@d.com", "cd", "docente", "pass"))
        self.assertEqual(len(self.dao_usuarios.obtener_todos()), 2)

    def test_actualizar_usuario_persiste_cambios(self):
        uf = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar", "jperez",
                           "estudiante", "Clave123!")
        self.dao_usuarios.guardar(uf)

        uf_modificado = UsuarioFinal("Juliana", "Perez Cambiado", "nuevo@fi.uner.edu.ar",
                                      "jperez", "docente", "OtraClave!")
        uf_modificado.id_bd = uf.id_bd
        self.dao_usuarios.actualizar(uf_modificado)

        recuperado = self.dao_usuarios.obtener_por_id(uf.id_bd)
        self.assertEqual(recuperado.apellido, "Perez Cambiado")
        self.assertEqual(recuperado.email, "nuevo@fi.uner.edu.ar")
        self.assertEqual(recuperado.claustro, "docente")

    def test_eliminar_usuario(self):
        uf = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass")
        self.dao_usuarios.guardar(uf)
        self.dao_usuarios.eliminar(uf.id_bd)
        self.assertIsNone(self.dao_usuarios.obtener_por_id(uf.id_bd))

    def test_filtrarporemail(self):
        self.dao_usuarios.guardar(UsuarioFinal("A", "B", "unico@b.com", "ab", "estudiante", "pass"))
        encontrado = self.dao_usuarios.filtrarporemail("unico@b.com")
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.nombre_usuario, "ab")
        self.assertIsNone(self.dao_usuarios.filtrarporemail("no_existe@b.com"))

    def test_filtrarpornombreusuario(self):
        self.dao_usuarios.guardar(UsuarioFinal("A", "B", "a@b.com", "usuario_unico", "estudiante", "pass"))
        encontrado = self.dao_usuarios.filtrarpornombreusuario("usuario_unico")
        self.assertIsNotNone(encontrado)
        self.assertIsNone(self.dao_usuarios.filtrarpornombreusuario("no_existe"))

    def test_rol_desconocido_en_bd_lanza_excepcion(self):
        """Si la BD tiene un rol inválido (ej. editada a mano), el DAO
        debe fallar de forma clara al reconstruir la entidad."""
        modelo = ModeloUsuario(nombre="X", apellido="Y", email="x@y.com",
                                nombreUsuario="xy", contrasena="hash_falso", rol="rol_invalido")
        self.session.add(modelo)
        self.session.commit()
        with self.assertRaises(RolUsuarioDesconocidoError):
            self.dao_usuarios.obtener_por_id(modelo.id)


class TestDaoReclamosSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.session = _crear_sesion_en_memoria()
        self.dao_usuarios = DaoUsuarioSQLAlchemy(self.session)
        self.dao_reclamos = DaoReclamosSQLAlchemy(self.session, self.dao_usuarios)

    def tearDown(self):
        self.session.close()

    def _crear_usuario_final(self, nombre_usuario):
        uf = UsuarioFinal("Juliana", "Perez", f"{nombre_usuario}@fi.uner.edu.ar",
                           nombre_usuario, "estudiante", "Clave123!")
        self.dao_usuarios.guardar(uf)
        return uf

    def test_crear_departamento_es_idempotente(self):
        d1 = self.dao_reclamos.crear_departamento("maestranza")
        d2 = self.dao_reclamos.crear_departamento("maestranza")
        self.assertEqual(d1.id, d2.id)
        self.assertEqual(len(self.dao_reclamos.obtener_todos_los_departamentos()), 1)

    def test_obtener_departamento_por_nombre(self):
        creado = self.dao_reclamos.crear_departamento("soporte informático")
        encontrado = self.dao_reclamos.obtener_departamento_por_nombre("soporte informático")
        self.assertEqual(encontrado.id, creado.id)

    def test_obtener_departamento_por_nombre_inexistente_devuelve_none(self):
        self.assertIsNone(self.dao_reclamos.obtener_departamento_por_nombre("no existe"))

    def test_obtener_todos_los_departamentos(self):
        self.dao_reclamos.crear_departamento("maestranza")
        self.dao_reclamos.crear_departamento("soporte informático")
        self.assertEqual(len(self.dao_reclamos.obtener_todos_los_departamentos()), 2)

    def test_guardar_y_obtener_reclamo(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("jperez1")
        reclamo = Reclamo(creador, "El proyector no enciende", depto)
        self.dao_reclamos.guardar_reclamo(reclamo)
        self.assertIsNotNone(reclamo.id_reclamo)

        recuperado = self.dao_reclamos.obtener_por_id(reclamo.id_reclamo)
        self.assertEqual(recuperado.contenido, "El proyector no enciende")
        self.assertEqual(recuperado.departamento.nombre, "maestranza")
        self.assertEqual(recuperado.usuario_creador.id_bd, creador.id_bd)
        self.assertEqual(recuperado.estado, EstadoReclamo.PENDIENTE)

    def test_guardar_reclamo_en_proceso_persiste_tiempo_resolucion(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("jperez2")
        reclamo = Reclamo(creador, "El aire acondicionado no enfria", depto)
        reclamo.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=5)
        self.dao_reclamos.guardar_reclamo(reclamo)

        recuperado = self.dao_reclamos.obtener_por_id(reclamo.id_reclamo)
        self.assertEqual(recuperado.estado, EstadoReclamo.EN_PROCESO)
        self.assertEqual(recuperado.tiempo_resolucion_asignado, 5)

    def test_guardar_reclamo_con_imagen_persiste_la_ruta(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("jperez2b")
        reclamo = Reclamo(creador, "El proyector no enciende", depto,
                           ruta_imagen="uploads/abc123_foto.jpg")
        self.dao_reclamos.guardar_reclamo(reclamo)

        recuperado = self.dao_reclamos.obtener_por_id(reclamo.id_reclamo)
        self.assertEqual(recuperado.ruta_imagen, "uploads/abc123_foto.jpg")

    def test_adherirse_persiste_la_relacion(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador1")
        otro = self._crear_usuario_final("otro1")
        reclamo = Reclamo(creador, "Reclamo de prueba", depto)
        self.dao_reclamos.guardar_reclamo(reclamo)

        self.dao_reclamos.adherirse(reclamo.id_reclamo, otro.id_bd)

        recuperado = self.dao_reclamos.obtener_por_id(reclamo.id_reclamo)
        self.assertEqual(len(recuperado.adherentes), 1)
        self.assertEqual(recuperado.adherentes[0].id_bd, otro.id_bd)

    def test_adherirse_a_reclamo_inexistente_lanza_excepcion(self):
        otro = self._crear_usuario_final("otro2")
        with self.assertRaises(ReclamoNoEncontradoError):
            self.dao_reclamos.adherirse(9999, otro.id_bd)

    def test_adherirse_con_usuario_inexistente_lanza_excepcion(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador2")
        reclamo = Reclamo(creador, "x", depto)
        self.dao_reclamos.guardar_reclamo(reclamo)
        with self.assertRaises(UsuarioNoEncontradoError):
            self.dao_reclamos.adherirse(reclamo.id_reclamo, 9999)

    def test_desadherirse_quita_la_relacion(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador3")
        otro = self._crear_usuario_final("otro3")
        reclamo = Reclamo(creador, "Reclamo de prueba", depto)
        self.dao_reclamos.guardar_reclamo(reclamo)
        self.dao_reclamos.adherirse(reclamo.id_reclamo, otro.id_bd)

        self.dao_reclamos.desadherirse(reclamo.id_reclamo, otro.id_bd)

        recuperado = self.dao_reclamos.obtener_por_id(reclamo.id_reclamo)
        self.assertEqual(len(recuperado.adherentes), 0)

    def test_actualizar_reclamo_persiste_nuevo_estado(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador4")
        reclamo = Reclamo(creador, "Reclamo de prueba", depto)
        self.dao_reclamos.guardar_reclamo(reclamo)

        reclamo.cambiar_estado(EstadoReclamo.RESUELTO)
        self.dao_reclamos.actualizar(reclamo)

        recuperado = self.dao_reclamos.obtener_por_id(reclamo.id_reclamo)
        self.assertEqual(recuperado.estado, EstadoReclamo.RESUELTO)

    def test_actualizar_reclamo_inexistente_lanza_excepcion(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador5")
        reclamo = Reclamo(creador, "x", depto, id_reclamo=9999)
        with self.assertRaises(ReclamoNoEncontradoError):
            self.dao_reclamos.actualizar(reclamo)

    def test_eliminar_reclamo(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador6")
        reclamo = Reclamo(creador, "x", depto)
        self.dao_reclamos.guardar_reclamo(reclamo)
        self.dao_reclamos.eliminar(reclamo.id_reclamo)
        self.assertIsNone(self.dao_reclamos.obtener_por_id(reclamo.id_reclamo))

    def test_get_reclamo_porautor(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador7")
        otro = self._crear_usuario_final("otro7")
        self.dao_reclamos.guardar_reclamo(Reclamo(creador, "reclamo 1", depto))
        self.dao_reclamos.guardar_reclamo(Reclamo(otro, "reclamo 2", depto))

        resultado = self.dao_reclamos.get_reclamo_porautor(creador.id_bd)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].contenido, "reclamo 1")

    def test_get_reclamo_pordepto(self):
        depto1 = self.dao_reclamos.crear_departamento("maestranza")
        depto2 = self.dao_reclamos.crear_departamento("soporte informático")
        creador = self._crear_usuario_final("creador8")
        self.dao_reclamos.guardar_reclamo(Reclamo(creador, "reclamo maestranza", depto1))
        self.dao_reclamos.guardar_reclamo(Reclamo(creador, "reclamo soporte", depto2))

        resultado = self.dao_reclamos.get_reclamo_pordepto("maestranza")
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].contenido, "reclamo maestranza")

    def test_obtener_por_filtro(self):
        depto = self.dao_reclamos.crear_departamento("maestranza")
        creador = self._crear_usuario_final("creador9")
        reclamo = Reclamo(creador, "único", depto)
        self.dao_reclamos.guardar_reclamo(reclamo)

        encontrado = self.dao_reclamos.obtener_por_filtro({"contenido": "único"})
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.id_reclamo, reclamo.id_reclamo)

if __name__ == "__main__":
    unittest.main()
