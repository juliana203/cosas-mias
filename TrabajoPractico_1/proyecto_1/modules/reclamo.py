from modules.usuarios import Usuario
from modules.excepciones import TransicionEstadoInvalidaError
from enum import Enum
import datetime


class EstadoReclamo(Enum):
    """Estados posibles de un Reclamo"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en proceso"
    RESUELTO = "resuelto"
    INVALIDO = "inválido"


class Reclamo:
    """Modela un Reclamo realizado por un Usuario."""

    def __init__(self, usuario_creador: Usuario, contenido: str, departamento: str):
        self.__id_reclamo: int | None = None  # El ID se asignará después de guardarlo
        self.__usuario_creador: Usuario = usuario_creador
        self.__contenido: str = contenido
        self.__departamento: str = departamento
        self.__timestamp: datetime.datetime = datetime.datetime.now()
        self.__estado: str = EstadoReclamo.PENDIENTE.value
        self.__adherentes: list[Usuario] = []
        self.__tiempo_resolucion_asignado: int | None = None

    @property
    def id_reclamo(self) -> int:
        return self.__id_reclamo

    @id_reclamo.setter
    def id_reclamo(self, valor: int):
        self.__id_reclamo = valor

    @property
    def usuario_creador(self) -> Usuario:
        return self.__usuario_creador

    @property
    def contenido(self) -> str:
        return self.__contenido

    @property
    def departamento(self) -> str:
        return self.__departamento

    @departamento.setter
    def departamento(self, nuevo_depto: str):
        """Setter para cambiar el departamento (para secretario técnico)"""
        self.__departamento = nuevo_depto

    @property
    def timestamp(self) -> datetime.datetime:
        return self.__timestamp

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def numero_adherentes(self) -> int:
        return len(self.__adherentes)

    @property
    def tiempo_resolucion_asignado(self) -> int | None:
        return self.__tiempo_resolucion_asignado

    @property
    def adherentes(self) -> list[Usuario]:
        return self.__adherentes

    def agregar_adherentes(self, usuario: Usuario):
        if usuario not in self.__adherentes:
            self.__adherentes.append(usuario)

    def quitar_adherentes(self, usuario: Usuario):
        if usuario in self.__adherentes:
            self.__adherentes.remove(usuario)

    def cambiar_estado(self, nuevo_estado: str, dias_resolucion: int | None = None):
        estados_validos = [e.value for e in EstadoReclamo]
        if nuevo_estado not in estados_validos:
            raise ValueError(f"El estado '{nuevo_estado}' no es un estado válido")

        if nuevo_estado == EstadoReclamo.EN_PROCESO.value:
            if dias_resolucion is not None and 1 <= dias_resolucion <= 15:
                self.__tiempo_resolucion_asignado = dias_resolucion
            else:
                # Lanza un error si el estado es 'en proceso' pero los días no son válidos.
                raise TransicionEstadoInvalidaError(dias_resolucion)

        self.__estado = nuevo_estado
