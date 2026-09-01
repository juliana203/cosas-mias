from modules.reclamo import Reclamo, EstadoReclamo
from collections import Counter  # modulo para evitar usar diccionarios
from modules.calculadora_mediana import MonticuloMediana
import re

STOPWORDS: frozenset[str] = frozenset({
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con",
    "contra", "cual", "cuando", "de", "del", "desde", "donde", "durante",
    "e", "el", "ella", "ellas", "ellos", "en", "entre", "era", "erais",
    "eran", "eras", "eres", "es", "esa", "esas", "ese", "eso", "esos",
    "esta", "estaba", "estabais", "estaban", "estabas", "estad", "estada",
    "estadas", "estado", "estados", "estamos", "estando", "estar",
    "estaremos", "estará", "estarán", "estarás", "estaré", "estaréis",
    "estaría", "estaríais", "estaríamos", "estarían", "estarías", "estas",
    "este", "estemos", "esto", "estos", "estoy", "estuve", "estuviera",
    "estuvierais", "estuvieran", "estuvieras", "estuvieron", "estuviese",
    "estuvieseis", "estuviesen", "estuvieses", "estuvimos", "estuviste",
    "estuvisteis", "estuviéramos", "estuviésemos", "estuvo", "está",
    "estábamos", "estáis", "están", "estás", "esté", "estéis", "estén",
    "estés", "fue", "fuera", "fuerais", "fueran", "fueras", "fueron",
    "fuese", "fueseis", "fuesen", "fueses", "fui", "fuimos", "fuiste",
    "fuisteis", "fuéramos", "fuésemos", "ha", "habida", "habidas",
    "habido", "habidos", "habiendo", "habremos", "habrá", "habrán",
    "habrás", "habré", "habréis", "habría", "habríais", "habríamos",
    "habrían", "habrías", "han", "has", "hasta", "hay", "haya", "hayamos",
    "hayan", "hayas", "hayáis", "he", "hemos", "hube", "hubiera",
    "hubierais", "hubieran", "hubieras", "hubieron", "hubiese",
    "hubieseis", "hubiesen", "hubieses", "hubimos", "hubiste",
    "hubisteis", "hubiéramos", "hubiésemos", "hubo", "la", "las", "le",
    "les", "lo", "los", "me", "mi", "mis", "misma", "mismas", "mismo",
    "mismos", "mucho", "muchos", "muy", "más", "mí", "mía", "mías", "mío",
    "míos", "nada", "ni", "no", "nos", "nosotras", "nosotros", "nuestra",
    "nuestras", "nuestro", "nuestros", "o", "os", "otra", "otras", "otro",
    "otros", "para", "pero", "poco", "por", "porque", "que", "quien",
    "quienes", "qué", "se", "sea", "seamos", "sean", "seas", "seremos",
    "será", "serán", "serás", "seré", "seréis", "sería", "seríais",
    "seríamos", "serían", "serías", "seáis", "sido", "siendo", "sin",
    "sobre", "sois", "somos", "son", "soy", "su", "sus", "suya", "suyas",
    "suyo", "suyos", "también", "tanto", "te", "tendremos", "tendrá",
    "tendrán", "tendrás", "tendré", "tendréis", "tendría", "tendríais",
    "tendríamos", "tendrían", "tendrías", "tened", "tenemos", "tenga",
    "tengamos", "tengan", "tengas", "tengo", "tengáis", "tenida",
    "tenidas", "tenido", "tenidos", "teniendo", "tenéis", "ti", "tiene",
    "tienen", "tienes", "todo", "todos", "tu", "tus", "tuve", "tuviera",
    "tuvierais", "tuvieran", "tuvieras", "tuvieron", "tuviese",
    "tuvieseis", "tuviesen", "tuvieses", "tuvimos", "tuviste",
    "tuvisteis", "tuviéramos", "tuviésemos", "tuvo", "tuya", "tuyas",
    "tuyo", "tuyos", "tú", "un", "una", "uno", "unos", "vosotras",
    "vosotros", "vuestra", "vuestras", "vuestro", "vuestros", "y", "ya",
    "yo",
})


class Analitica:
    def __init__(self, reclamos: list[Reclamo]):
        self.__reclamos = reclamos

    def calcular_porcentaje_estado(self) -> dict[str, float]:
        """
        Calcula el número total de reclamos y los porcentajes por estado.
        """
        total_reclamos = len(self.__reclamos)
        if total_reclamos == 0:
            return {"total": 0, "pendientes": 0, "en_proceso": 0, "resueltos": 0, "invalidos": 0}

        conteo_estados = Counter(r.estado for r in self.__reclamos)  # cuenta cuántas veces aparece cada elemento único.

        reporte = {
            "total": total_reclamos,
            "pendientes": (conteo_estados.get(EstadoReclamo.PENDIENTE.value, 0) / total_reclamos) * 100,
            "en_proceso": (conteo_estados.get(EstadoReclamo.EN_PROCESO.value, 0) / total_reclamos) * 100,
            "resueltos": (conteo_estados.get(EstadoReclamo.RESUELTO.value, 0) / total_reclamos) * 100,
            "invalidos": (conteo_estados.get(EstadoReclamo.INVALIDO.value, 0) / total_reclamos) * 100,
        }
        return reporte

    def calcular_palabras_frecuentes(self, cantidad: int = 15) -> list[tuple[str, int]]:
        # Unimos el contenido de todos los reclamos en un solo texto.
        texto_completo = " ".join(r.contenido for r in self.__reclamos).lower()

        # Extraemos únicamente secuencias de letras
        tokens = re.findall(r"[a-záéíóúñ]+", texto_completo)

        # Filtramos stopwords y palabras muy cortas
        palabras = [palabra for palabra in tokens if palabra not in STOPWORDS and len(palabra) > 2]

        # Contamos las frecuencias y devolvemos las más comunes (si hay empate: orden alfabético)
        contador = Counter(palabras)
        return sorted(contador.items(), key=lambda par: (-par[1], par[0]))[:cantidad]

    def calcular_mediana_tiempos_resolucion(self) -> float:
        calculadora = MonticuloMediana()
        reclamos_validos_contados = 0

        for reclamo in self.__reclamos:
            # Filtramos solo los estados que pide la consigna
            if reclamo.estado in (EstadoReclamo.EN_PROCESO.value, EstadoReclamo.RESUELTO.value):
                tiempo_asignado = reclamo.tiempo_resolucion_asignado

                # Nos aseguramos que el reclamo tenga un tiempo asignado
                if tiempo_asignado is not None:
                    calculadora.agregar_numero(tiempo_asignado)
                    reclamos_validos_contados += 1

        if reclamos_validos_contados == 0:
            return 0.0  # Evitamos errores si no hay reclamos con tiempo

        return calculadora.obtener_mediana()
