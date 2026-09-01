import unittest
from modules.repositorio_abstracto import IRepositorio


class RepoIncompleto(IRepositorio):
    """Implementa todos los métodos delegando al padre, para forzar el NotImplementedError."""
    def guardar(self, entidad):
        return super().guardar(entidad)

    def obtener_por_id(self, id: int):
        return super().obtener_por_id(id)

    def obtener_todos(self) -> list:
        return super().obtener_todos()

    def actualizar(self, entidad):
        return super().actualizar(entidad)

    def eliminar(self, id: int):
        return super().eliminar(id)

    def obtener_por_filtro(self, **kwargs):
        return super().obtener_por_filtro(**kwargs)

    def obtener_todos_por_filtro(self, **kwargs) -> list:
        return super().obtener_todos_por_filtro(**kwargs)


class TestIRepositorio(unittest.TestCase):
    def setUp(self):
        self.repo = RepoIncompleto()

    def test_guardar_no_implementado(self):
        with self.assertRaises(NotImplementedError):
            self.repo.guardar(None)

    def test_obtener_por_id_no_implementado(self):
        with self.assertRaises(NotImplementedError):
            self.repo.obtener_por_id(1)

    def test_obtener_todos_no_implementado(self):
        with self.assertRaises(NotImplementedError):
            self.repo.obtener_todos()

    def test_actualizar_no_implementado(self):
        with self.assertRaises(NotImplementedError):
            self.repo.actualizar(None)

    def test_eliminar_no_implementado(self):
        with self.assertRaises(NotImplementedError):
            self.repo.eliminar(1)

    def test_obtener_por_filtro_no_implementado(self):
        with self.assertRaises(NotImplementedError):
            self.repo.obtener_por_filtro(nombre="test")

    def test_obtener_todos_por_filtro_no_implementado(self):
        with self.assertRaises(NotImplementedError):
            self.repo.obtener_todos_por_filtro(nombre="test")


if __name__ == "__main__":
    unittest.main()
