from flask import Flask, render_template, request, redirect, send_file
import random
from PyPDF4 import PdfFileMerger
from modules.config import app
from modules.funciones import lector, diccionario_trivia, mostrar_historial, verificar_resultados, grafica_curvas,grafica_prom, guardar

ruta = "./data/"
archivo1 = ruta + "frases_de_peliculas.txt"
archivo2= ruta + "historial.csv"
respuestas = []

historial, historial2 = mostrar_historial(archivo2)

frase_de_peli, peliculas = lector(archivo1) 
# Con la funcion lector obtenemos una lista con todas las peliculas que despues vamos a listar (peliculas), 
# y otra lista que dentro tiene diccionarios de la siguiete forma: {frase:peli} (frase_de_peli)

peliculas = sorted(peliculas)   # Ordenamos alfabeticamente las peliculas a listar

# Como tanto frase_de_peli como peliculas son utilizados luego en varias partes del programa se escogio darles un valor 
# como variables globales.

# Lista final de frases peliculas y opciones aleatorias utilizando las listas anteriores (frase_de_peli para 
# obtener la frase y su respuesta correcta, y peliculas para obtener las demas opciones aleatorias)
frases_de_peliculas= diccionario_trivia(frase_de_peli, peliculas)

# inicio de la pagina, donde se ingresa nombre, cantidad de frases, y se puede acceder al 
# historial y listado de peliculas disponibles.
@app.route('/')
def inicio():
    global indice, respuestas
    respuestas = []
    indice = -1
    return render_template('inicio.html')

# Inicio de la trivia, se cargan las frases con sus opciones aleatorias, una vez respondida la frase
# se lo dirije a verificacion.
@app.route('/trivia', methods=['GET', 'POST'])
def trivia():
    global frases_aleatorias, num_frases, indice, nombre_jugador, respuestas, frase_actual
    indice += 1
    mensaje = None
    if indice == 0:
            nombre_jugador = request.form['nombre']
            num_frases = int(request.form['num_frases'])
            frases_aleatorias = random.sample(frases_de_peliculas, num_frases)
    if indice < num_frases:
        frase_actual = frases_aleatorias[indice]
        return render_template('trivia.html', frase=frase_actual, nombre_jugador = nombre_jugador,indice = indice,num=num_frases, mensaje= mensaje)
    else:
        return redirect('/verificar_respuestas')

# Se verifica que la respuesta del usuario sea la correcta o no y se informa el rsultado, luego se lo vuelve a 
# dirigir a trivia
@app.route('/verificacion', methods= ('POST', 'GET'))
def verificacion():
    resp_correcta = frase_actual['peli']
    resp = request.form.getlist('respuesta')
    respuestas.extend(resp)
    if resp:
        if resp[0] == resp_correcta:
            print(resp_correcta)
            mensaje = "Felicidades, respuesta correcta!"
        else:
            mensaje = (f"Incorrecto, la respuesta correcta es: {frase_actual['peli']}")
    return render_template('verificacion.html', mensaje = mensaje)

# Verificacion de repuestas correctas e incorrectas (para guardar en el historial) que se guardan en listas, 
# agregar jugador al historial (junto con el tiempo de inicio de la partida), luego con las listas de
# respuestas correctas o incorrectas se lo redirige a resultados (resultados finales de la partida, incluyendo
# graficas y las correcciones de ser necesarias).

@app.route('/verificar_respuestas', methods=['get'])
def verificar_respuestas():
    global resp_correctas_usu, resp_incorrectas_usu
    resp_correctas, resp_incorrectas_usu, resp_correctas_usu = verificar_resultados(respuestas,frases_aleatorias, frases_de_peliculas)
    return render_template('resultados.html', resp_correctas_usu = resp_correctas_usu, 
                           resp_incorrectas_usu = resp_incorrectas_usu, resp_correctas= resp_correctas)

@app.route('/graficas', methods=['get'])
def mostrar_graficas():
    global grafica3, grafica2
    grafica2= grafica_curvas(historial2)
    grafica3= grafica_prom(historial2)
    return render_template('graficas.html', graf2 = grafica2, graf3 = grafica3)

@app.route('/guardar', methods=['get'])
def guardar_historial():
    guardar(frases_aleatorias, resp_correctas_usu, resp_incorrectas_usu, nombre_jugador, archivo2)
    return render_template('graficas.html')

@app.route('/descargar', methods=['get'])
def descargar():
    merger=PdfFileMerger()
    merger.append('.\statics\Grafico1.pdf')
    merger.append('.\statics\Graficocircular.pdf')
    merger.write('.\statics\Graficas.pdf')

    return send_file('.\statics\Graficas.pdf', as_attachment=True)

#Listado en modo de tabla donde se muesta el historial de juego de todos los jugadores que han 
# jugado una partida

@app.route('/ver_historial')
def ver_historial():
    global historial2
    historial, historial2 = mostrar_historial(archivo2)
    return render_template('historial.html', historial=historial)

# Listado de todas las peliculas disponibles.
@app.route('/ver_peliculas')
def ver_peliculas():
    return render_template('peliculas.html', peliculas=peliculas)



if __name__ == '__main__':
    app.run(debug=True)