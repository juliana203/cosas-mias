import random
import matplotlib.pyplot as plt
import numpy as np
from modules.agentes import Fruta,Verdura,Kiwi,Manzana,Papa,Zanahoria


class Calculadora:
    def __init__(self, cajon):#definir de forma correcta relaciones
        self.__cajon = cajon

    def calcularprom(self):
        aw_kiwi=aw_manzana=aw_papa=aw_zanahoria=aw_frutas=aw_verduras=0
        num_kiwi=num_manzana=num_papa=num_zanahoria=num_frutas=num_verduras=0
        dic = {"awprom":0,"awkiwiprom":0,"awmanzanaprom": 0, "awpapaprom":0, "awzanahoriaprom":0, "awfrutasprom":0, "awverdurasprom":0 }
        for alimento in self.__cajon:
            if isinstance(alimento, Kiwi):
                num_kiwi += 1
                aw_kiwi += alimento.calcularaw()
                
            if isinstance(alimento, Manzana):
                num_manzana += 1
                aw_manzana += alimento.calcularaw()

            if isinstance(alimento, Papa):
                num_papa += 1
                aw_papa += alimento.calcularaw()

            if isinstance(alimento, Zanahoria):
                num_zanahoria += 1
                aw_zanahoria += alimento.calcularaw()
            
            if isinstance(alimento, Fruta):
                aw_frutas+=alimento.calcularaw()
                num_frutas += 1
            
            if isinstance(alimento, Verdura):
                aw_verduras+=alimento.calcularaw()
                num_verduras += 1

        dic["awfrutasprom"]=self.__dividir(aw_frutas,num_frutas)
        dic["awverdurasprom"]=self.__dividir(aw_verduras,num_verduras)
        dic["awprom"] = self.__dividir(aw_frutas +aw_verduras,num_verduras+num_frutas)
        dic["awkiwiprom"] = self.__dividir(aw_kiwi,num_kiwi)
        dic["awmanzanaprom"] = self.__dividir(aw_manzana,num_manzana)
        dic["awpapaprom"] = self.__dividir(aw_papa,num_papa)
        dic["awzanahoriaprom"] = self.__dividir(aw_zanahoria,num_zanahoria)
        return dic
    
    def __dividir(self,numerador,denominador):
        try:
            return round(numerador/denominador,2)
        except ZeroDivisionError:
            return 0

class Cajon:
    def __init__(self):
        self.__peso = 0
        self.__Alimentos=[]
    
    def cargaralimento(self,alimento):
        self.__Alimentos.append(alimento)
        self.__peso += alimento.getmasa()
       
    def __iter__(self):
        return(x for x in self.__Alimentos)
    
    def getpeso(self):
        return self.__peso
    

class Cinta:
    def __init__(self, sensor): #Error de relaciones
        self.__sensor = sensor
        self.__ali_desconocidos = 0
    
    def transportar(self):
        return self.__sensor.detectar_alimento()
    
    def getali_desconocidos(self):
        return self.__ali_desconocidos

    def cargaralimento(self,n,cajon):#Error de relacion
        x=1
        while x <= n:
            ali = self.transportar()
            tipo = ali["alimento"]
            peso = ali["peso"]
            if tipo == "undefined":
                self.__ali_desconocidos += 1
            else:
                if tipo == "kiwi":
                    alimento = Kiwi(peso)

                if tipo == "manzana":
                    alimento = Manzana(peso)
                
                if tipo == "papa":
                    alimento = Papa(peso)
    
                if tipo == "zanahoria":
                    alimento = Zanahoria(peso) 

                cajon.cargaralimento(alimento)
                x+=1

class DetectorAlimento:
    """clase que representa un conjunto de sensores de la cinta transportadora
    para detectar el tipo de alimento y su peso.
    """
    def __init__(self):
        self.alimentos = ["kiwi", "manzana", "papa", "zanahoria", "undefined"]
        self.peso_alimentos = np.round(np.linspace(0.05, 0.6, 12),2)
        self.prob_pesos = np.round(self.__softmax(self.peso_alimentos)[::-1], 2)

    def __softmax(self, x):
        """función softmax para crear vector de probabilidades 
        que sumen 1 en total
        """
        return (np.exp(x - np.max(x)) / np.exp(x - np.max(x)).sum())

    def detectar_alimento(self):
        """método que simula la detección del alimento y devuelve un diccionario
        con la información del tipo y el peso del alimento.
        """
        n_alimentos = len(self.alimentos)
        alimento_detectado = self.alimentos[random.randint(0, n_alimentos-1)]
        peso_detectado = random.choices(self.peso_alimentos, self.prob_pesos)[0]
        return {"alimento": alimento_detectado, "peso": peso_detectado}
    

if __name__ == "__main__":
    
    pass