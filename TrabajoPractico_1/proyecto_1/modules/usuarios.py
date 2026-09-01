"""
usuarios.py
Agrupa a Departamento y toda la jerarquía de Usuario:
    Usuario (abstract)
        |-- UsuarioFinal
        |-- JefeDepartamento
        |-- SecretarioTecnico
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from werkzeug.security import generate_password_hash, check_password_hash

from .excepciones import ClaustroInvalidoError


# Departamento

class Departamento:
    def __init__(self, nombre: str, id: int | None = None):
        self._id = id
        self._nombre = nombre

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def nombre(self) -> str:
        return self._nombre

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Departamento):
            return NotImplemented
        if self._id is not None and other._id is not None:
            return self._id == other._id
        return self._nombre == other._nombre

    def __hash__(self) -> int:
        return hash((self._id, self._nombre))

    def __repr__(self) -> str:
        return f"Departamento(id={self._id}, nombre='{self._nombre}')"


# Usuario (abstracta)

class Usuario(ABC):
    def __init__(self, nombre: str, apellido: str, email: str,
                 nombre_usuario: str, contrasena: str,
                 id_bd: int | None = None):
        self._id_bd = id_bd
        self._nombre = nombre
        self._apellido = apellido
        self._email = email
        self._nombre_usuario = nombre_usuario
        # La contraseña se hashea apenas se construye el objeto.
        self._contrasena = generate_password_hash(contrasena)

    # Propiedades
    @property
    def id_bd(self) -> int | None:
        return self._id_bd

    @id_bd.setter
    def id_bd(self, value: int) -> None:
        self._id_bd = value

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def apellido(self) -> str:
        return self._apellido

    @property
    def email(self) -> str:
        return self._email

    @property
    def nombre_usuario(self) -> str:
        return self._nombre_usuario

    @property
    def contrasena(self) -> str:
        # Devuelve el hash de la contraseña, nunca la original.
        return self._contrasena

    @property
    @abstractmethod
    def rol(self) -> str:
        """
        Cada subclase concreta declara su propio rol (usuario_final, jefe_departamento, secretario_tecnico). 
        """
        raise NotImplementedError

    # Acciones
    def verificar_contrasena(self, raw_pwd: str) -> bool:
        return check_password_hash(self._contrasena, raw_pwd)

    def get_id(self) -> str:
        """
        Es lo que login_user() guarda en la sesión, y lo que se le pasa al user_loader para recargar al usuario en cada request.
        """
        return str(self._id_bd)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    @classmethod
    def _reconstruir_contrasena(cls, instancia: "Usuario", hash_contrasena: str) -> "Usuario":
        """
        Como en la db la contraseña ya se guarda hasheada, si pasara por el __init__ normal se volvería a hashear un hash 
        (rompiendo el login). Este método restaura el hash original sin duplicar la lógica de contraseña en cada repo.
        """
        instancia._contrasena = hash_contrasena
        return instancia

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Usuario):
            return NotImplemented
        return self.id_bd is not None and self.id_bd == other.id_bd

    def __hash__(self) -> int:
        return hash(self.id_bd)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id_bd={self._id_bd}, nombre_usuario='{self._nombre_usuario}')"

# UsuarioFinal
CLAUSTROS_VALIDOS = {"estudiante", "docente", "PAyS"}

class UsuarioFinal(Usuario):
    # Persona que registra reclamos. Es el único rol que se da de alta mediante un formulario público de registro.

    def __init__(self, nombre: str, apellido: str, email: str,
                 nombre_usuario: str, claustro: str, contrasena: str,
                 id_bd: int | None = None):
        if claustro not in CLAUSTROS_VALIDOS:
            raise ClaustroInvalidoError(claustro, CLAUSTROS_VALIDOS)
        super().__init__(nombre, apellido, email, nombre_usuario, contrasena, id_bd)
        self._claustro = claustro

    @property
    def claustro(self) -> str:
        return self._claustro

    @property
    def rol(self) -> str:
        return "usuario_final"


# JefeDepartamento

class JefeDepartamento(Usuario):
    """
    Se da de alta a nivel de sistema. departamento_asignado es una departamento real (no str) para que incorporar un jefe de un 
    departamento nuevo sea crear el Departamento y luego este objeto.
    """

    def __init__(self, nombre: str, apellido: str, email: str,
                 nombre_usuario: str, contrasena: str,
                 departamento_asignado: Departamento,
                 id_bd: int | None = None):
        super().__init__(nombre, apellido, email, nombre_usuario, contrasena, id_bd)
        self._departamento_asignado = departamento_asignado

    @property
    def departamento_asignado(self) -> Departamento:
        return self._departamento_asignado

    @property
    def rol(self) -> str:
        return "jefe_departamento"


# SecretarioTecnico

class SecretarioTecnico(Usuario):
    """
    Puede ver todos los reclamos (no los de un departamento) y derivar un reclamo de un departamento a otro. 
    Se da de alta a nivel de sistema.
    """

    def __init__(self, nombre: str, apellido: str, email: str,
                 nombre_usuario: str, contrasena: str,
                 id_bd: int | None = None):
        super().__init__(nombre, apellido, email, nombre_usuario, contrasena, id_bd)

    @property
    def rol(self) -> str:
        return "secretario_tecnico"
