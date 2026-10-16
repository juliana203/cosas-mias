import random
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from datetime import datetime


#Lee el archivotxt, cada linea les borra el "\n" las transforma en minuscula y separa en 2 
#Uno toma el valor de frase y el otro de peli, crea un diccionario de forma {clave = frase : valor = pelicula}
#Tambien crea una lista con todas las peliculas existentes
def lector(archivo):
    fraseypeli = {}
    pelicula = []
    with open(archivo, "r",encoding='utf-8') as archi:
        for x in archi:
            frase, peli = x.rstrip().lower().split(";")
            fraseypeli.update({frase:peli})
            pelicula.append(peli)
        peliculas = list(set(pelicula))        
        return(fraseypeli,peliculas)

#A partir de las frases y la lista de peliculas, crea 3 opciones aleatorias sin repetir 
#Las guarda en una lista y las retorna.
def diccionario_trivia(fraseypeli, peliculas):
    frases_de_peliculas = []
    for key, clave in fraseypeli.items():
        frase_peliculas = {
            'frase' : key,
            'peli' : clave
            }
        num1 = 0
        num2 = 0
        while peliculas[num1] == peliculas[num2] or peliculas[num2] == clave or peliculas[num1] == clave:
            num1 = random.randint(0, len(peliculas)-1)
            num2 = random.randint(0, len(peliculas)-1)
            frase_peliculas['opciones'] = [clave , peliculas[num1], peliculas[num2]]
            random.shuffle(frase_peliculas['opciones'])
        frases_de_peliculas.append(frase_peliculas)
    return(frases_de_peliculas)

#Guarda los datos de forma [nombre, tiempo_juego, aciertos, desaciertos, total_frases]
#En el archivos csv con el historial
def guardar_resultados_historial(archivo2, nombre, tiempo_juego, aciertos, desaciertos, total_frases):
    with open(archivo2, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([nombre, tiempo_juego, aciertos, desaciertos, total_frases])



#Muestra todos los resultados cargados en el archivo csv de historial
def mostrar_historial(archivo2):
    historial = []
    historial2= []
    with open(archivo2, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            historial.append({'nombre': row[0], 'tiempo': row[1], 'aciertos': f"{row[2]}/{row[4]}", "desaciertos": f"{row[3]}/{row[4]}"})
            historial2.append(row)
    return(historial, historial2)


def verificar_resultados(respuestas, frases_aleatorias, frases_de_peliculas):
    resp_correctas_usu = {}
    resp_incorrectas_usu = {}
    resp_correctas = {}
    for i, frase_usu in enumerate(respuestas): #Recorre las respuestas transformando, el indice y la respuesta en pares clave: valor
        respuesta_correcta = next(item['peli'] for item in frases_de_peliculas if item['frase'] == frases_aleatorias[i]['frase'])
        if frase_usu == respuesta_correcta:
            resp_correctas_usu.update({frases_aleatorias[i]['frase']: frase_usu})
        else:
            resp_incorrectas_usu.update({frases_aleatorias[i]['frase']: frase_usu})
            resp_correctas.update({frases_aleatorias[i]['frase']: respuesta_correcta})
    return (resp_correctas, resp_incorrectas_usu, resp_correctas_usu)


def guardar(frases_aleatorias, resp_correctas_usu, resp_incorrectas_usu, nombre_jugador,archivo2):
    tiempo_inicio = datetime.now()  
    cantidad_aciertos = len(resp_correctas_usu)
    cantidad_desaciertos = len(resp_incorrectas_usu)
    total_frases = len(frases_aleatorias)
    guardar_resultados_historial(archivo2, nombre_jugador, tiempo_inicio, cantidad_aciertos, cantidad_desaciertos, total_frases)


# GRAFICAS


def grafica_curvas(historial2):
    fechas = []
    total_aciertos = 0
    total_desaciertos = 0
    for registro in historial2:
        fecha_str = registro[1].split(".")[0]  # Eliminar decimales de los segundos
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S").date()
        fechas.append(fecha.strftime('%Y-%m-%d'))  # Convertir a cadena en formato 'YYYY-MM-DD')
        total_aciertos += int(registro[2])
        total_desaciertos += int(registro[3])
    # Crear el gráfico circular
    labels = ['Aciertos', 'Desaciertos']
    sizes = [total_aciertos, total_desaciertos]
    colors = ['lightgreen', 'lightcoral']
    explode = (0.1, 0)  # Resaltar la primera sección (aciertos)
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Porcentaje de Aciertos y Desaciertos acumulados')
    plt.axis('equal')  # Para asegurar que el gráfico sea circular
    
    plt.savefig(".\statics\Graficocircular.pdf")
    # Convertir la gráfica a HTML
    grafica2 = plt.savefig(".\statics\Graficocircular.png")
    return(grafica2)


def grafica_prom(historial2):
    #grafica por promedios
    totales_por_fecha = {}
    for registro in historial2:
        fecha_str = registro[1].split()[0]  # Extraer solo la parte de la fecha
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        aciertos2 = int(registro[2])
        desaciertos2 = int(registro[3])
        # Si la fecha ya está en el diccionario, actualiza los totales, de lo contrario, crea una nueva entrada
        if fecha in totales_por_fecha:
            totales_por_fecha[fecha]['aciertos'].append(aciertos2)
            totales_por_fecha[fecha]['desaciertos'].append(desaciertos2)
        else:
            totales_por_fecha[fecha] = {'aciertos': [aciertos2], 'desaciertos': [desaciertos2]}
    # Calcular el promedio de aciertos y desaciertos para cada fecha
    fechas2 = []
    promedio_aciertos = []
    promedio_desaciertos = []
    for fecha, totales in totales_por_fecha.items():
        fechas2.append(fecha.strftime('%Y-%m-%d')) 
        promedio_aciertos.append(sum(totales['aciertos']))
        promedio_desaciertos.append(sum(totales['desaciertos']))
    # Graficar
    plt.figure(figsize=(8, 6))
    plt.plot(fechas2, promedio_aciertos, marker='o', label='Aciertos')
    plt.plot(fechas2, promedio_desaciertos, marker='x', label='Desaciertos')
    plt.title('Aciertos y Desaciertos por Fecha')
    plt.xlabel('Fecha')
    plt.ylabel('Promedio')
    plt.xticks(rotation=45)  # Rotar fechas para mejor visualización
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    plt.savefig(".\statics\Grafico1.pdf")
    
    # Convertir la gráfica a HTML
    grafica3 = plt.savefig(".\statics\Grafico1.png")
    return(grafica3)