# Aplicación principal
from modules.edificios import Facultad
from modules.agentes import Alumno, Profesor

facultad = Facultad("Facultad de Ciencias")

profesores = []
with open('data/profesor.txt', 'r') as file:
    for line in file:
        prof = line.strip().split(',')
        nomb =  prof[0]
        dni = prof[1]
        profesor = Profesor(nomb, dni, director_de = "Nada")
        facultad.contratar_prof(profesor)

alumnos = []
with open('data/Alumnos.txt', 'r') as file:
    for line in file:
        alumno = line.strip().split(',')
        nomb =  alumno[0]
        dni = alumno[1]
        alumno = Alumno(nomb,dni)  
        facultad.inscribir_alumno(alumno)

def main():
    while True:
        print("##########################################")
        print("#  Sistema de Información Universitaria  #")
        print("##########################################")
        print("Elige una opción:")
        print("1) Inscribir alumno")
        print("2) Contratar profesor")
        print("3) Crear departamento nuevo")
        print("4) Crear curso nuevo")
        print("5) Inscribir estudiante a un curso")
        print("6) Salir")

        opcion = input("Opción: ")

        if opcion == "1":
            nom = input("Ingrese el nombre del nuevo alumno: ")
            dni = input("Ingrese el dni del alumno: ")
            alum = Alumno(nom, dni)
            facultad.inscribir_alumno(alum)
            print(f"Alumno {nom} inscripto correctamente en la facultad! \n¿Desea inscribir a ",nom, " a algun curso?\n 1)Si \n 2)No")
            x = int(input("Su respuesta: "))
            while True:
                if x == 1:
                    print("Departamentos disponibles:")
                    deps = facultad.listar_departamentos()
                    for i, dep in enumerate(deps):
                        print(f"{i + 1}. {dep}")
                    ind_departamento = int(input("Seleccione el número del departamento: "))
                    x = facultad.buscar_cursos_de_dep(ind_departamento)
                    while x == 1:
                        print("Departamento no encontrado, ingrese nuevamente: ")
                        ind_departamento = int(input("Ingrese el número del departamento nuevamente: "))
                        x = facultad.buscar_cursos_de_dep(ind_departamento)
                        print("Cursos en el departamento:")
                    for i, curso in enumerate(x):
                        print(f"{i + 1}. {curso}")
                    indice_curso = int(input("Seleccione el número del curso: "))
                    c = facultad.buscar_curso(indice_curso,x)
                    while c == 2:
                        print("Curso no encontrado, ingrese nuevamente: ")
                        indice_curso = int(input("Ingrese el número del curso nuevamente: "))
                        c = facultad.buscar_curso(indice_curso, x)
                    alum = facultad.listar_alumnos()
                    ind_alumno = len(alum)
                    z = facultad.inscribir_estudiante_en_curso(ind_alumno,c)
                    print("Se inscribio con exito")
                    break

                elif x==2:

                    break
                print("\n\nNumero invalido\n¿Desea inscribir a ",nom, " a algun curso?\n 1)Si \n 2)No")
                x = int(input("Su respuesta: "))
            
        elif opcion == "2":
            nom = input("Ingrese el nombre del nuevo profesor: ")
            dni = input("Ingrese el dni del profesor: ")
            prof = Profesor(nom, dni, director_de = "Nada")
            facultad.contratar_prof(prof)
            print(f"Profesor {nom} contratado correctamente!")
            
        elif opcion == "3":
            nom_dep = input("Ingrese el nombre del departamento: ")
            print("Elija un director para el departamento:")
            print("Profesores disponibles:")
            # Obtener una lista de profesores disponibles para ser directores
            prof_no_dire = facultad.listar_prof_no_dir()
            for i, profesor in enumerate(prof_no_dire):
                print(f"{i + 1}. {profesor}")
            dir_index = int(input("Ingrese el número del profesor como director: "))
            x =facultad.buscardirector(dir_index,nom_dep)
            while x !=2:
                print("Profesor no encontrado. Intente nuevamente.")
                dir_index = int(input("Ingrese el número del profesor como director: "))
                x =facultad.buscardirector(dir_index,nom_dep)
            deps = facultad.listar_departamentos()
            for i, dep in enumerate(deps):
                print(f"{i + 1}. {dep}")
            
        elif opcion == "4":
            nom = input("Ingrese el nombre del nuevo curso: ")
            print("Profesores (elija quien estara a cargo del curso):")
            pro = facultad.listar_prof()
            for x, prof in enumerate(pro):
                print(f"{x + 1}. {prof}")
            prof_index = int(input("Ingrese el número del profesor a cargo: "))
            print("Departamentos:")
            deptos = facultad.listar_departamentos()
            for i, prof in enumerate(deptos):
                print(f"{i + 1}. {prof}")
            dpto_index = int(input("Ingrese el número del departamento donde estara el curso: "))
            x = facultad.buscardep(dpto_index, nom, prof_index)
            while(x!= 1):
                if(x == 2):
                    print("Profesor no encontrado, ingrese nuevamente: ")
                    prof_index = int(input("Ingrese el número del profesor a cargo: "))
                elif(x==0):
                    print("Departamento no encontrado, ingrese nuevamente: ")
                    dpto_index = int(input("Ingrese el número del departamento donde estara el curso: "))
                x = facultad.buscardep(dpto_index, nom, prof_index)
                
                    
            
        elif opcion == "5":
            print("Departamentos disponibles:")
            deps = facultad.listar_departamentos()
            for i, dep in enumerate(deps):
                print(f"{i + 1}. {dep}")
            ind_departamento = int(input("Seleccione el número del departamento: "))
            x = facultad.buscar_cursos_de_dep(ind_departamento)
            while x == 1:
                print("Departamento no encontrado, ingrese nuevamente: ")
                ind_departamento = int(input("Ingrese el número del departamento nuevamente: "))
                x = facultad.buscar_cursos_de_dep(ind_departamento)
            print("Cursos en el departamento:")
            for i, curso in enumerate(x):
                print(f"{i + 1}. {curso}")
            indice_curso = int(input("Seleccione el número del curso: "))
            c = facultad.buscar_curso(indice_curso,x)
            while c == 2:
                print("Curso no encontrado, ingrese nuevamente: ")
                indice_curso = int(input("Ingrese el número del curso nuevamente: "))
                c = facultad.buscar_curso(indice_curso, x)
            print("Alumnos inscriptos:")
            alum = facultad.listar_alumnos()
            for i, alumno in enumerate(alum):
                print(f"{i + 1}. {alumno}")
            ind_alumno = int(input("Seleccione el número del alumno: "))
            z = facultad.inscribir_estudiante_en_curso(ind_alumno,c)
            while z != 4:
                print("Alumno no encontrado, ingrese nuevamente: ")
                ind_alumno = int(input("Ingrese el número del alumno nuevamente: "))
                z = facultad.inscribir_estudiante_en_curso(ind_alumno, c)
        elif opcion == "6":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()