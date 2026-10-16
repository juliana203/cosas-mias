class Facultad:
    def __init__(self, nombre):
        self.__nombre_F = nombre
        self.__profesores = []
        self.__departamentos = []
        self.__alumnos = []

    def inscribir_alumno(self, alumno):
        self.__alumnos.append(alumno)

    def contratar_prof(self, profesor):
        self.__profesores.append(profesor)
    
    # Metodo para listar los departamentos. Devuelve una lista que se recorre en main.
    def listar_departamentos(self):
        return [dep for dep in self.__departamentos]
    
    # Método para listar los alumnos. Devuelve una lista que se recorre en main.
    def listar_alumnos(self):
        return [alum for alum in self.__alumnos]
    
    # Método para listar los profesores que no son directores. Devuelve una lista que se recorre en main.
    def listar_prof_no_dir(self):
        return [prof for prof in self.__profesores if not prof.get_director_de()]
    
    # Método para listar los profesores. Devuelve una lista que se recorre en main.
    def listar_prof(self):
        return [prof for prof in self.__profesores]

    # Método para cambiar el atributo director de un profesor y crear el departamento
    def buscardirector(self,ind,nombre_departamento):
        if 1 <= ind <= len(self.__profesores):
            self.__asignar_dir_y_crear_dep(ind, nombre_departamento)
            return 2
        else:
            return 1
          
    def __asignar_dir_y_crear_dep(self, ind, nombre_departamento):
        profe = self.__profesores[ind - 1]
        profe.set_director_de(nombre_departamento)
        departamento = Departamento(nombre_departamento, profe)
        self.__departamentos.append(departamento)
    
    
    def crear_curso(self, indice_departamento, nombre_curso, director_c): #Quitar print e inputs, agregar metodos de control 
        self.__departamentos[indice_departamento - 1].crear_cursos(nombre_curso, director_c)
    
    def buscardep(self,indice_departamento, nombre_curso, ind_director_c):
        if 1 <= indice_departamento <= len(self.__departamentos):
            if 1 <= ind_director_c <= len(self.__profesores):
                director_c = self.__profesores[ind_director_c - 1]
                self.__departamentos[indice_departamento - 1].crear_cursos(nombre_curso, director_c)
                return 1
            else:
                return 2
        else:
            return 0 


    def buscar_cursos_de_dep(self, indice_departamento):
        if 1 <= indice_departamento <= len(self.__departamentos):
            departamento = self.__departamentos[indice_departamento - 1]
            return departamento.listar_cursos_dep()
        else:
            return 1
    
    def inscribir_estudiante_en_curso(self, indice_alumno, curso):
        if 1 <= indice_alumno <= len(self.__alumnos):
            alumno = self.__alumnos[indice_alumno - 1]
            curso.inscribir_estudiante(alumno)
            alumno.set_cursos_inscriptos(curso)
            return 4
        else:
            return 3
    def buscar_curso(self, indice_curso, x):
        if 1 <= indice_curso <= len(x):
            curso = x[indice_curso - 1 ]
            return curso
        else:
            return 2

class Departamento:
    def __init__(self, nombre, director):
        self.__nombre_dep = nombre
        self.__director = director
        self.__profesores_dep = []
        self.__cursos = []
        if director:
            self.__profesores_dep.append(director)
    
    def agregar_profesores_al_departamento(self, prof_dep):
        self.__profesores_dep.append(prof_dep)
    
    def crear_cursos(self, nombre_curso, director_c):
        curso = Curso(nombre_curso, director_c)
        self.__cursos.append(curso)

    def listar_cursos_dep(self):
        return [cur for cur in self.__cursos]
    
    def incribir_alumno(self, indice, estudiante):
        self.__cursos[indice - 1].agregar_est(estudiante)

    def get_cursos(self):
        return self.__cursos

    def __str__(self):
        lista_profesores = [str(profesor) for profesor in self.__profesores_dep]
        cursos = [str(curso) for curso in self.__cursos]
        return f"Departamento: {self.__nombre_dep}\nDirector: {self.__director}\nProfesores: {', '.join(lista_profesores)}\nCursos: {', '.join(cursos)}"

class Curso:
    def __init__(self, nombre, profesor):
        self.__nombre_del_curso = nombre
        self.__prof_a_cargo = profesor
        self.__lista_estudiantes = []
    
    def inscribir_estudiante(self, estudiante):
        self.__lista_estudiantes.append(estudiante)

    def lista_estudiantes(self):
        lista_est =[]
        for est in self.__lista_estudiantes:
            nom_estudiante = est.get_nombre_completo()
            lista_est.append(nom_estudiante)
        return lista_est
    
    def __str__(self):
        return f"Curso: {self.__nombre_del_curso}, Profesor a cargo: {self.__prof_a_cargo}, Alumnos: {self.lista_estudiantes()}"