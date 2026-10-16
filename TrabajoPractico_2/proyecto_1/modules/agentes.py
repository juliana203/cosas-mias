from abc import ABC
class Persona(ABC): # Abstracto
    def __init__(self, nombre_completo, dni, cursos = None):
        self.__nombre_completo = nombre_completo
        self.__dni = dni
        self.__cursos = [] if cursos is not None else []

    # Getters
    def get_nombre_completo(self):
        return self.__nombre_completo

    def get_dni(self):
        return self.__dni

    # Setters
    def set_nombre_completo(self, nombre_completo):
        self.__nombre_completo = nombre_completo

    def set_dni(self, dni):
        self.__dni = dni

class Alumno(Persona):
    def __init__(self, nombre_completo, dni, cursos = None):
        super().__init__(nombre_completo, dni, cursos = None) 
        self.__cursos_inscriptos = [] if cursos is not None else []
    # Getter y setter para cursos_inscriptos
    def get_cursos_inscriptos(self):
        return self.__cursos_inscriptos

    def set_cursos_inscriptos(self, cursos_inscriptos):
        self.__cursos_inscriptos = cursos_inscriptos

    def inscribir_a_curso(self, curso):
        self.__cursos_inscriptos.append(curso)

    def __str__(self):
        return f"Nombre: {self.get_nombre_completo()}, DNI: {self.get_dni()}"
        

class Profesor(Persona):#Probar otra relacion
    def __init__(self, nombre_completo, dni,director_de,cursos = None):
        super().__init__(nombre_completo, dni)
        self.__cursos = [] if cursos is not None else []
        self.__director_de = ""
    # Getters y setters para curso_a_cargo y director_de

    def get_cursos(self):
        return self.__cursos

    def set_cursos(self,curso):
        self.__cursos.append(curso)

    def get_director_de(self):
        return self.__director_de

    def set_director_de(self, director_de):
        self.__director_de = director_de
   
    def __str__(self):
        return f"Nombre: {self.get_nombre_completo()}, DNI: {self.get_dni()}"
    