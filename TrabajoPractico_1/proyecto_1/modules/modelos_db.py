from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship # relationship para definir relaciones

# 1: Crear una base declarativa. Todas nuestras tablas heredarán de ella.
Base = declarative_base()

asociacion_reclamos_adherentes = Table('reclamos_adherentes', Base.metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id'), primary_key=True),
    Column('reclamo_id', Integer, ForeignKey('reclamos.id'), primary_key=True)
)

# 2: Definir el modelo para la tabla de Usuarios.
class ModeloUsuario(Base):
    __tablename__ = 'usuarios' 

    # Columnas de la tabla. primary_key=True: Identificador único de cada usuario. SQLAlchemy lo hará autoincremental
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False) # nullable=False significa que no puede estar vacío
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True) # unique=True asegura que no haya emails repetidos
    nombre_usuario = Column(String(50), nullable=False, unique=True) # unique=True asegura que no haya nombres de usuario repetidos
    claustro = Column(String(20), nullable=True)  # sólo aplica a usuario_final; jefe/secretario no tienen claustro
    contrasena = Column(String(255), nullable=False) # Guardaremos la contraseña hasheada (más adelante)
    
    # Para la relación uno-a-muchos (usuario crea muchos reclamos)
    reclamos_creados = relationship("ModeloReclamo", back_populates="creador")

    # Definimos el tipo de usuario
    rol = Column(String(20), nullable=False, default="final")
    # Para jefes de departamento guardamos el departamento asignado
    departamento_asignado = Column(String(100), nullable=True) # nullable=True porque no todos los usuarios son jefes
    reclamos_adheridos = relationship(
        "ModeloReclamo",
        secondary=asociacion_reclamos_adherentes,
        back_populates="adherentes"
    )

# 3: Definir el modelo para la tabla de reclamos.
class ModeloReclamo(Base):
    __tablename__ = 'reclamos' # Nombre de la tabla en la BD

    id = Column(Integer, primary_key=True)
    contenido = Column(String(1000), nullable=False)
    departamento = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False) # Guardará fecha y hora
    estado = Column(String(20), nullable=False)
    tiempo_resolucion_asignado = Column(Integer, nullable=True) # Puede ser nulo al principio

    # Clave Foránea: Conecta el reclamo con el usuario que lo creó.
    id_usuario_creador = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    
    # Define la relación inversa (reclamo pertenece a un creador)
    creador = relationship("ModeloUsuario", back_populates="reclamos_creados")
    adherentes = relationship(
        "ModeloUsuario",
        secondary=asociacion_reclamos_adherentes,
        back_populates="reclamos_adheridos"
    )