from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email, Length, Optional, NumberRange

# Formulario para el registro de usuarios finales
class FormRegistro(FlaskForm):
    nombre = StringField(label="Nombre", validators=[DataRequired()])
    apellido = StringField(label="Apellido", validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    nombre_usuario = StringField(label="Nombre de Usuario", validators=[DataRequired()])

    # Opciones para el campo 'claustro'
    claustro_opciones = [('estudiante', 'Estudiante'), ('docente', 'Docente'), ('PAyS', 'PAyS')]
    claustro = SelectField(label='Claustro', choices=claustro_opciones, validators=[DataRequired()])

    password = PasswordField(label='Contraseña', validators=[DataRequired(), Length(min=4)])
    confirmacion = PasswordField(label='Repetir Contraseña', 
                                 validators=[DataRequired(), 
                                             EqualTo('password', message='Las contraseñas deben coincidir')])
    submit = SubmitField(label='Registrarse')

# Formulario para el Login (común a todos los usuarios)
class FormLogin(FlaskForm):
    nombre_usuario = StringField(label='Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField(label='Contraseña', validators=[DataRequired()])
    submit = SubmitField(label='Ingresar')

class FormCrearReclamo(FlaskForm):
    """
    Formulario para que el usuario final cree un nuevo reclamo
    """
    contenido = TextAreaField(
        label='Detalle su reclamo', 
        validators=[DataRequired(), Length(min=10, max=1000)], # Pedimos al menos 10 caracteres
        render_kw={"rows": 5} 
    )
    submit = SubmitField(label='Buscar reclamos similares')

class FormEditarEstado(FlaskForm):
    """
    Formulario para que el admin cambie el estado de un reclamo.
    """
    opciones_estado = [
        ('pendiente', 'Pendiente'),
        ('en proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('inválido', 'Inválido')
    ]
    estado = SelectField(label='Nuevo Estado', 
                         choices=opciones_estado, 
                         validators=[DataRequired()])

    # Campo para el tiempo de resolución. Es opcional porque solo se usa si el estado es 'en proceso'.
    tiempo_resolucion = IntegerField(
        label='Tiempo de Resolución (en días, 1-15)',
        validators=[
            Optional(),
            NumberRange(min=1, max=15, message="Debe estar entre 1 y 15 días")
        ],
        render_kw={"placeholder": "Solo si está 'En Proceso'"}
    )

    submit = SubmitField(label='Actualizar Estado')

class FormDerivarReclamo(FlaskForm):
    """
    Formulario para que Secretaría Técnica derive un reclamo.
    """
    opciones_depto = [
        ('soporte informático', 'Soporte Informático'),
        ('maestranza', 'Maestranza'),
        ('secretaría técnica', 'Secretaría Técnica')
    ]
    departamento = SelectField(label='Nuevo Departamento', 
                               choices=opciones_depto, 
                               validators=[DataRequired()])

    submit = SubmitField(label='Derivar Reclamo')

    