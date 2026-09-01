from modules.usuarios import Usuario, UsuarioFinal, JefeDepartamento, SecretarioTecnico
from modules.reclamo import Reclamo, EstadoReclamo
from modules.excepciones import (
    EmailYaRegistradoError, NombreUsuarioYaExisteError, UsuarioNoEncontradoError,
    ReclamoNoEncontradoError, DepartamentoNoEncontradoError,
)
from modules.repositorio_abstracto import IRepositorio as RepositorioAbstracto
from typing import Optional, List
from modules.clasificador_reclamos import ClasificadorReclamo

DEPARTAMENTOS_VALIDOS = ["secretaría técnica", "soporte informático", "maestranza"]

class SubSubsistemaGestionReclamos:
    def __init__(self, repo_usuarios: RepositorioAbstracto, repo_reclamos: RepositorioAbstracto):
        """
        Constructor que recibe los repositorios para usuarios y reclamos.
        """
        self.__repo_usuarios = repo_usuarios
        self.__repo_reclamos = repo_reclamos
        self.__clasificador = ClasificadorReclamo()

    # Gestión de usuarios

    def registrar_usuario(self, nombre: str, apellido: str, email: str, nombre_usuario: str, claustro: str, contrasena: str) -> UsuarioFinal:
        """
        Registra un nuevo usuario final usando el repositorio. Lanza EmailYaRegistradoError o NombreUsuarioYaExisteError 
        si ya existen (validado antes de tocar el repo).
        """
        if self.__repo_usuarios.obtener_por_filtro(email=email):
            raise EmailYaRegistradoError(email)
        if self.__repo_usuarios.obtener_por_filtro(nombre_usuario=nombre_usuario):
            raise NombreUsuarioYaExisteError(nombre_usuario)

        nuevo_usuario = UsuarioFinal(nombre, apellido, email, nombre_usuario, claustro, contrasena)
        self.__repo_usuarios.guardar(nuevo_usuario)
        return nuevo_usuario

    def buscar_usuario(self, nombre_usuario: str) -> Usuario:
        """
        Busca un usuario por su nombre de usuario usando el repositorio. Lanza UsuarioNoEncontradoError si no existe.
        """
        usuario_encontrado = self.__repo_usuarios.obtener_por_filtro(nombre_usuario=nombre_usuario)
        if not usuario_encontrado:
            raise UsuarioNoEncontradoError(nombre_usuario)
        return usuario_encontrado

    # Gestión de reclamos

    def crear_reclamo(self, usuario_creador: Usuario, contenido: str) -> Reclamo:
        """
        Crea un nuevo reclamo. El departamento se asigna automáticamente usando el clasificador.
        """
        usuario_existente = self.__repo_usuarios.obtener_por_filtro(nombre_usuario=usuario_creador.nombre_usuario)
        if not usuario_existente:
            raise UsuarioNoEncontradoError(usuario_creador.nombre_usuario)

        # Clasificar el contenido
        departamento_asignado = self.__clasificador.clasificar(contenido)

        # Crear la entidad Reclamo con el departamento clasificado
        nuevo_reclamo = Reclamo(usuario_existente, contenido, departamento_asignado)

        # Guardar el reclamo usando el repositorio
        self.__repo_reclamos.guardar(nuevo_reclamo)

        return nuevo_reclamo

    def buscar_reclamo_por_id(self, id_reclamo: int) -> Reclamo:
        """Busca un reclamo por su ID usando el repositorio."""
        reclamo_encontrado = self.__repo_reclamos.obtener_por_id(id_reclamo)
        if not reclamo_encontrado:
            raise ReclamoNoEncontradoError(id_reclamo)
        return reclamo_encontrado

    def adherir_a_reclamo(self, usuario: Usuario, id_reclamo: int):
        """
        Permite a un usuario adherirse a un reclamo existente (persistente).
        """
        if not usuario.id_bd:
            usuario_existente = self.__repo_usuarios.obtener_por_filtro(nombre_usuario=usuario.nombre_usuario)
            if not usuario_existente or not usuario_existente.id_bd:
                raise UsuarioNoEncontradoError(usuario.nombre_usuario)
            usuario_a_adherir = usuario_existente
        else:
            usuario_a_adherir = usuario

        reclamo_a_adherir = self.buscar_reclamo_por_id(id_reclamo)

        # Validar que el usuario no esté ya adherido
        for adherente in reclamo_a_adherir.adherentes:
            if adherente.id_bd == usuario_a_adherir.id_bd:
                return  # Ya está adherido, no devuelve nada

        self.__repo_usuarios.asociar_reclamos_a_usuario(
            id_usuario=usuario_a_adherir.id_bd,
            id_reclamo=reclamo_a_adherir.id_reclamo
        )
        reclamo_a_adherir.agregar_adherentes(usuario_a_adherir)

    def quitar_adhesion_reclamo(self, usuario: Usuario, id_reclamo: int):
        reclamo = self.buscar_reclamo_por_id(id_reclamo)
        self.__repo_usuarios.quitar_reclamos_a_usuario(
            id_usuario=usuario.id_bd,
            id_reclamo=reclamo.id_reclamo,
        )
        reclamo.quitar_adherentes(usuario)

    def cambiar_estado_reclamo(self, usuario: Usuario, id_reclamo: int, nuevo_estado: str, dias_resolucion: Optional[int] = None):
        """
        Permite a un jefe de departamento o a Secretaría Técnica cambiar el estado de un
        reclamo, y actualiza en la BD (jefe de departamento -> solo reclamos de su departamento; 
        secretario tecnico -> cualquier reclamo)
        """
        reclamo_a_modificar = self.buscar_reclamo_por_id(id_reclamo)

        # Verificación de permisos
        if isinstance(usuario, JefeDepartamento) and reclamo_a_modificar.departamento != usuario.departamento_asignado.nombre:
            raise Exception("Permiso denegado: no puede modificar reclamos de otro departamento.")
        elif not isinstance(usuario, (JefeDepartamento, SecretarioTecnico)):
            raise Exception("Permiso denegado: no tiene autorización para cambiar el estado de un reclamo.")

        # Cambiamos el estado en el objeto
        reclamo_a_modificar.cambiar_estado(nuevo_estado, dias_resolucion)

        # Actualizamos el reclamo en la base de datos usando el repositorio
        self.__repo_reclamos.actualizar(reclamo_a_modificar)

    def listar_reclamos_usuario(self, usuario: Usuario) -> List[Reclamo]:
        """
        Devuelve una lista con todos los reclamos creados por un usuario específico.
        """
        usuario_existente = self.__repo_usuarios.obtener_por_filtro(nombre_usuario=usuario.nombre_usuario)
        if not usuario_existente:
            raise UsuarioNoEncontradoError(usuario.nombre_usuario)

        reclamos_del_usuario = self.__repo_reclamos.obtener_todos_por_filtro(id_usuario_creador=usuario_existente.id_bd)
        return reclamos_del_usuario

    def buscar_reclamos_pendientes_todos(self) -> List[Reclamo]:
        """
        Busca en la BD todos los reclamos que están en estado 'pendiente'
        """
        return self.__repo_reclamos.obtener_todos_por_filtro(estado=EstadoReclamo.PENDIENTE.value)

    def buscar_reclamos_pendientes_por_departamento(self, departamento: str) -> List[Reclamo]:
        """
        Busca en la BD todos los reclamos pendientes de un departamento específico
        """
        return self.__repo_reclamos.obtener_todos_por_filtro(
            estado=EstadoReclamo.PENDIENTE.value,
            departamento=departamento
        )

    def derivar_reclamo(self, usuario_secretario: Usuario, id_reclamo: int, nuevo_departamento: str):
        """
        Permite a Secretario Técnico derivar un reclamo
        """
        if not isinstance(usuario_secretario, SecretarioTecnico):
            raise Exception("Permiso denegado: Solo el Secretario Técnico puede derivar reclamos.")

        if nuevo_departamento not in DEPARTAMENTOS_VALIDOS:
            raise DepartamentoNoEncontradoError(nuevo_departamento)

        reclamo_a_derivar = self.buscar_reclamo_por_id(id_reclamo)
        reclamo_a_derivar.departamento = nuevo_departamento
        self.__repo_reclamos.actualizar(reclamo_a_derivar)

    def buscar_reclamos_similares(self, contenido_reclamo: str) -> List[Reclamo]:
        # Clasificar el texto para saber qué buscar
        clasificacion = self.__clasificador.clasificar(contenido_reclamo)

        if clasificacion == "indefinido":
            print("Advertencia: El clasificador no pudo determinar una categoría.")
            return [] 

        # Buscar en la BD reclamos pendientes con esa clasificación
        return self.__repo_reclamos.obtener_todos_por_filtro(
            estado=EstadoReclamo.PENDIENTE.value,
            departamento=clasificacion
        )