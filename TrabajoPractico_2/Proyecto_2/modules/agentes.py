import numpy as np
from abc import ABC

class Alimentos(ABC):
    def __init__(self,peso):
        self.__masa = peso  
    
    def getmasa(self):
        return self.__masa

class Fruta(Alimentos,ABC):#ABC
    def __init__(self, peso):
        super().__init__(peso)

class Verdura(Alimentos,ABC):
    def __init__(self, peso):
        super().__init__(peso)

class Kiwi(Fruta): #Iniciacion con super
    
    def __init__(self, peso):
        super().__init__(peso)
        
    def calcularaw(self):
        e = np.e
        a = (-18)*self.getmasa()
        aw = 0.96 * ((1-e**a)/(1+e**a))
        aw = round(aw, 2)
        return aw
    
class Manzana(Fruta):
    
    def __init__(self, peso):
        super().__init__(peso)

    def calcularaw(self):
        peso = float(self.getmasa())
        a = (15*peso)**2
        aa = a/(1+a)
        aw = 0.97 * aa
        aw = round(aw, 2)
        return aw

class Papa(Verdura):
    
    def __init__(self, peso):
        super().__init__(peso)
        
    def calcularaw(self):
        peso = float(self.getmasa())
        a = (18)*peso
        arctan = np.arctan(a)
        aw = 0.66 * arctan
        aw = round(aw, 2)
        return aw
    
class Zanahoria(Verdura):
    
    def __init__(self, peso):
        super().__init__(peso)

    def calcularaw(self):
        e = np.e
        peso = float(self.getmasa())
        a = (-10)*peso
        aw = 0.96 * (1-e**a)
        aw = round(aw, 2)
        return aw
