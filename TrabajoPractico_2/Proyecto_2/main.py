# Aplicación principal
from modules.Alimentos import Kiwi,Manzana,Zanahoria,Papa
from modules.Maquinaria import Cajon, Cinta, DetectorAlimento, Calculadora
from modules.config import app
from flask import Flask, render_template, request



@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/resultados', methods=['GET', 'POST'])
def resultados():
    cinta = Cinta()
    cajon = Cajon()
    calculadora = Calculadora(cajon)
    n = int(request.form['n'])
    cinta.cargaralimento(n,cajon)
    ali_desconocido = cinta.getali_desconocidos()
    pesocajon = round(cajon.getpeso(),3)
    diccionario = calculadora.calcularprom()
    
    return render_template('resultados.html', peso_cajon=pesocajon,  
                           aw_kiwi_p=diccionario["awkiwiprom"], 
                           aw_manzana_p=diccionario["awmanzanaprom"], 
                           aw_papa_p=diccionario["awpapaprom"], 
                           aw_zanahoria_p=diccionario["awzanahoriaprom"], 
                           aw_fru_p=diccionario["awfrutasprom"], 
                           aw_verd_p=diccionario["awverdurasprom"],
                           ali_desconocido =ali_desconocido ,
                           aw_total_p = diccionario["awprom"])

if __name__ == "__main__":
    app.run(debug=True)