import unittest
from modules.calculadora_mediana import MonticuloMediana

class TestMonticuloMediana(unittest.TestCase):

    def test_mediana_estado_inicial_none(self):
        """La mediana debe ser None antes de agregar cualquier número"""
        calc = MonticuloMediana()
        self.assertIsNone(calc.obtener_mediana()) #Se prueba si realmente es None
        
    def test_mediana_con_un_solo_elemento_impar_max_heap(self):
        """Cubre mediana impar donde tam_inf > tam_sup"""
        calc = MonticuloMediana()
        calc.agregar_numero(100)
        self.assertEqual(calc.obtener_mediana(), 100.0) #Se prueba que la mediana es correcta
        
    def test_mediana_con_cantidad_par_promedio(self):
        """Cubre el caso de la mediana par"""
        calc = MonticuloMediana()
        # 1, 7 -> Mediana: (1+7)/2 = 4.0
        calc.agregar_numero(1)
        calc.agregar_numero(7)
        self.assertEqual(calc.obtener_mediana(), 4.0) #Se prueba si la mediana es correcta
        
    def test_mediana_con_cantidad_impar_min_heap_raiz(self):
        """Fuerza el caso de mediana impar donde tam_sup > tam_inf"""
        calc = MonticuloMediana()
        calc.agregar_numero(10)
        calc.agregar_numero(20)
        calc.agregar_numero(30)
        calc.agregar_numero(40)
        calc.agregar_numero(50) 
        calc.agregar_numero(60)
        calc.agregar_numero(70)
        self.assertEqual(calc.obtener_mediana(), 40.0) #Se prueba que la mediana es correcta.
        
    def test_balanceo_mueve_de_max_a_min(self):
        """Cubre la rama 'if tam_inf > tam_sup:' del balanceo."""
        calc = MonticuloMediana()
        calc.agregar_numero(10) 
        calc.agregar_numero(20)
        calc.agregar_numero(5)  
        self.assertEqual(calc.obtener_mediana(), 10.0) #Se prueba que la mediana es correcta

    def test_balanceo_mueve_de_min_a_max(self):
        """Cubre la rama 'else' del balanceo."""
        calc = MonticuloMediana()
        calc.agregar_numero(100) 
        calc.agregar_numero(10)  
        calc.agregar_numero(200) 
        calc.agregar_numero(300) 
        calc.agregar_numero(400)
        self.assertEqual(calc.obtener_mediana(), 200.0) #Se prueba que la mediana es correcta.

        