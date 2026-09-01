from sqlalchemy.orm import Session

from modules.repositorio_abstracto import IRepositorio as RepositorioAbstracto
# Importamos nuestras clases
from modules.usuarios import Usuario, UsuarioFinal, JefeDepartamento, SecretarioTecnico, Departamento
from modules.reclamo import Reclamo
# Importamos nuestros modelos de BD específicos y la Base
from modules.modelos_db import ModeloUsuario, ModeloReclamo, Base
from typing import Optional, List  # Usamos Optional/List para claridad en los retornos


# Repositorio para usuarios

class RepositorioUsuariosSQLAlchemy(RepositorioAbstracto):
    """Implementación concreta para manejar la persistencia de Usuarios."""

    def __init__(self, session: Session):
        self.__session = session
        # Asegura que la tabla de usuarios exista
        Base.metadata.create_all(bind=self.__session.bind)

    # Métodos de Mapeo (usuario)

    def __map_modelo_a_entidad(self, modelo: ModeloUsuario) -> Usuario:
        """Convierte un ModeloUsuario (tabla) a un objeto Usuario/Jefe/Secretario (dominio)."""
        if modelo.rol == "jefe_departamento":
            departamento = Departamento(nombre=modelo.departamento_asignado)
            entidad = JefeDepartamento(
                nombre=modelo.nombre,
                apellido=modelo.apellido,
                email=modelo.email,
                nombre_usuario=modelo.nombre_usuario,
                contrasena="temporal",  # se sobreescribe abajo con el hash ya guardado
                departamento_asignado=departamento,
                id_bd=modelo.id
            )
        elif modelo.rol == "secretario_tecnico":
            entidad = SecretarioTecnico(
                nombre=modelo.nombre,
                apellido=modelo.apellido,
                email=modelo.email,
                nombre_usuario=modelo.nombre_usuario,
                contrasena="temporal",
                id_bd=modelo.id
            )
        else:  
            entidad = UsuarioFinal(
                nombre=modelo.nombre,
                apellido=modelo.apellido,
                email=modelo.email,
                nombre_usuario=modelo.nombre_usuario,
                claustro=modelo.claustro,
                contrasena="temporal",
                id_bd=modelo.id
            )
        # La contraseña ya está hasheada en la BD: la restauramos tal cual está guardada, sin volver a hashearla (si no, el login rompería)
        Usuario._reconstruir_contrasena(entidad, modelo.contrasena)
        return entidad

    def __map_entidad_a_modelo(self, entidad: Usuario) -> ModeloUsuario:
        """Convierte un objeto usuario/jefe/secretario (dominio) a un ModeloUsuario (tabla)."""
        modelo = ModeloUsuario(
            nombre=entidad.nombre,
            apellido=entidad.apellido,
            email=entidad.email,
            nombre_usuario=entidad.nombre_usuario,
            contrasena=entidad.contrasena,  # ya viene hasheada desde la entidad
            claustro=entidad.claustro if isinstance(entidad, UsuarioFinal) else None,
            rol=entidad.rol,
        )
        # Atributos específicos si es Jefe
        if isinstance(entidad, JefeDepartamento):
            modelo.departamento_asignado = entidad.departamento_asignado.nombre

        return modelo

    # Implementación de repositorio (usuario)

    def guardar(self, entidad: Usuario):
        # Validación específica para usuario antes de mapear
        existente_email = self.obtener_por_filtro(email=entidad.email)
        existente_nom_usr = self.obtener_por_filtro(nombre_usuario=entidad.nombre_usuario)
        if existente_email or existente_nom_usr:
            raise ValueError("El email o nombre de usuario ya está registrado.")

        modelo = self.__map_entidad_a_modelo(entidad)
        self.__session.add(modelo)
        self.__session.commit()
        self.__session.refresh(modelo)
        entidad.id_bd = modelo.id

    def obtener_por_id(self, id: int) -> Optional[Usuario]:
        modelo = self.__session.get(ModeloUsuario, id)
        return self.__map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos(self) -> List[Usuario]:
        modelos = self.__session.query(ModeloUsuario).all()
        return [self.__map_modelo_a_entidad(m) for m in modelos]

    def actualizar(self, entidad: Usuario):
        # Buscamos por nombre_usuario que es único y asumimos que la entidad lo tiene bien
        modelo_actualizar = self.__session.query(ModeloUsuario).filter_by(nombre_usuario=entidad.nombre_usuario).first()
        if not modelo_actualizar:
            raise ValueError("Usuario no encontrado para actualizar.")

        # Actualizamos los campos desde la entidad mapeada (ID y contraseña no)
        modelo_mapeado = self.__map_entidad_a_modelo(entidad)
        modelo_actualizar.nombre = modelo_mapeado.nombre
        modelo_actualizar.apellido = modelo_mapeado.apellido
        modelo_actualizar.email = modelo_mapeado.email
        modelo_actualizar.claustro = modelo_mapeado.claustro
        modelo_actualizar.rol = modelo_mapeado.rol
        modelo_actualizar.departamento_asignado = modelo_mapeado.departamento_asignado

        self.__session.commit()

    def eliminar(self, id: int):
        modelo_eliminar = self.__session.get(ModeloUsuario, id)
        if not modelo_eliminar:
            raise ValueError("Usuario no encontrado para eliminar.")
        self.__session.delete(modelo_eliminar)
        self.__session.commit()

    def obtener_por_filtro(self, **kwargs) -> Optional[Usuario]:
        modelo = self.__session.query(ModeloUsuario).filter_by(**kwargs).first()
        return self.__map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos_por_filtro(self, **kwargs) -> List[Usuario]:
        modelos = self.__session.query(ModeloUsuario).filter_by(**kwargs).all()
        return [self.__map_modelo_a_entidad(m) for m in modelos]

    def asociar_reclamos_a_usuario(self, id_usuario: int, id_reclamo: int):
        # Encontrar el modelo del usuario
        usuario_modelo = self.__session.get(ModeloUsuario, id_usuario)
        if not usuario_modelo:
            raise ValueError("El usuario no existe.")

        # Encontrar el modelo del reclamo
        reclamo_modelo = self.__session.get(ModeloReclamo, id_reclamo)
        if not reclamo_modelo:
            raise ValueError("El reclamo no existe.")

        # Añadir la relación
        if reclamo_modelo not in usuario_modelo.reclamos_adheridos:
            usuario_modelo.reclamos_adheridos.append(reclamo_modelo)

        # Guardar los cambios
        self.__session.commit()

    def quitar_reclamos_a_usuario(self, id_usuario: int, id_reclamo: int):
        usuario_modelo = self.__session.get(ModeloUsuario, id_usuario)
        reclamo_modelo = self.__session.get(ModeloReclamo, id_reclamo)
        if not usuario_modelo or not reclamo_modelo:
            raise ValueError("El usuario o el reclamo no existen.")
        if reclamo_modelo in usuario_modelo.reclamos_adheridos:
            usuario_modelo.reclamos_adheridos.remove(reclamo_modelo)
        self.__session.commit()


# Repositorio para reclamos

class RepositorioReclamosSQLAlchemy(RepositorioAbstracto):
    """Implementación concreta para manejar la persistencia de Reclamos."""

    def __init__(self, session: Session):
        self.__session = session
        Base.metadata.create_all(bind=self.__session.bind)
        # Guardamos una referencia al repo de usuarios para buscar creadores
        self.__repo_usuarios = RepositorioUsuariosSQLAlchemy(session)

    # Métodos de mapeo (reclamo)

    def __map_modelo_a_entidad(self, modelo: ModeloReclamo) -> Reclamo:
        """Convierte un ModeloReclamo (tabla) a un objeto Reclamo (dominio)."""
        creador_entidad = self.__repo_usuarios.obtener_por_id(modelo.id_usuario_creador)
        if not creador_entidad:
            raise Exception(f"Inconsistencia: No se encontró el usuario creador ID {modelo.id_usuario_creador}")

        entidad = Reclamo(
            usuario_creador=creador_entidad,
            contenido=modelo.contenido,
            departamento=modelo.departamento
        )
        entidad._Reclamo__id_reclamo = modelo.id
        entidad._Reclamo__timestamp = modelo.timestamp
        entidad._Reclamo__estado = modelo.estado
        entidad._Reclamo__tiempo_resolucion_asignado = modelo.tiempo_resolucion_asignado

        if modelo.adherentes:
            for adherente_modelo in modelo.adherentes:
                adherente_entidad = self.__repo_usuarios._RepositorioUsuariosSQLAlchemy__map_modelo_a_entidad(adherente_modelo)
                entidad.agregar_adherentes(adherente_entidad)

        return entidad

    def __map_entidad_a_modelo(self, entidad: Reclamo) -> ModeloReclamo:
        """Convierte un objeto Reclamo (dominio) a un ModeloReclamo (tabla)."""
        modelo_creador = self.__session.query(ModeloUsuario).filter_by(
            nombre_usuario=entidad.usuario_creador.nombre_usuario
        ).first()
        if not modelo_creador:
            raise ValueError("El usuario creador del reclamo no existe en la base de datos.")

        id_reclamo_bd = entidad.id_reclamo if entidad.id_reclamo is not None else None

        return ModeloReclamo(
            id=id_reclamo_bd,
            contenido=entidad.contenido,
            departamento=entidad.departamento,
            timestamp=entidad.timestamp,
            estado=entidad.estado,
            tiempo_resolucion_asignado=entidad.tiempo_resolucion_asignado,
            id_usuario_creador=modelo_creador.id
        )

    # Implementación métodos repositorio (reclamo)

    def guardar(self, entidad: Reclamo):
        try:
            modelo = self.__map_entidad_a_modelo(entidad)
            self.__session.add(modelo)
            self.__session.commit()
            self.__session.refresh(modelo)
            entidad.id_reclamo = modelo.id
        except Exception as e:
            self.__session.rollback()
            print(f"Error al guardar reclamo: {e}")
            raise e

    def obtener_por_id(self, id: int) -> Optional[Reclamo]:
        modelo = self.__session.get(ModeloReclamo, id)
        return self.__map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos(self) -> List[Reclamo]:
        modelos = self.__session.query(ModeloReclamo).all()
        return [self.__map_modelo_a_entidad(m) for m in modelos]

    def actualizar(self, entidad: Reclamo):
        if not entidad.id_reclamo:
            raise ValueError("El Reclamo debe tener un ID para ser actualizado.")

        modelo_actualizar = self.__session.get(ModeloReclamo, entidad.id_reclamo)
        if not modelo_actualizar:
            raise ValueError("Reclamo no encontrado para actualizar.")

        modelo_mapeado = self.__map_entidad_a_modelo(entidad)
        modelo_actualizar.contenido = modelo_mapeado.contenido
        modelo_actualizar.departamento = modelo_mapeado.departamento
        modelo_actualizar.estado = modelo_mapeado.estado
        modelo_actualizar.tiempo_resolucion_asignado = modelo_mapeado.tiempo_resolucion_asignado

        self.__session.commit()

    def eliminar(self, id: int):
        modelo_eliminar = self.__session.get(ModeloReclamo, id)
        if not modelo_eliminar:
            raise ValueError("Reclamo no encontrado para eliminar.")
        self.__session.delete(modelo_eliminar)
        self.__session.commit()

    def obtener_por_filtro(self, **kwargs) -> Optional[Reclamo]:
        modelo = self.__session.query(ModeloReclamo).filter_by(**kwargs).first()
        return self.__map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos_por_filtro(self, **kwargs) -> List[Reclamo]:
        modelos = self.__session.query(ModeloReclamo).filter_by(**kwargs).all()
        return [self.__map_modelo_a_entidad(m) for m in modelos]
