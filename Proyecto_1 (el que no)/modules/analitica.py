"""
analitica.py

Agrupa todo lo necesario para calcular estadísticas de reclamos y
generar los 3 gráficos que pide el enunciado, usando matplotlib.
"""

from __future__ import annotations

import base64
import io
import re
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

import matplotlib
matplotlib.use("Agg")  # backend sin interfaz gráfica: obligatorio en un server Flask
import matplotlib.pyplot as plt

from .reclamos import Reclamo, EstadoReclamo
from .calculadora_mediana import MonticuloMediana
from .excepciones import TipoInformeNoSoportadoError

if TYPE_CHECKING:
    from .informes import Informe

# Stopwords: lista estática
STOPWORDS_ES: frozenset[str] = frozenset({
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
    "tenidas", "tenido", "tenidos", "teniendo", "tenéis", "tendrás",
    "ti", "tiene", "tienen", "tienes", "todo", "todos", "tu", "tus",
    "tuve", "tuviera", "tuvierais", "tuvieran", "tuvieras", "tuvieron",
    "tuviese", "tuvieseis", "tuviesen", "tuvieses", "tuvimos", "tuviste",
    "tuvisteis", "tuviéramos", "tuviésemos", "tuvo", "tuya", "tuyas",
    "tuyo", "tuyos", "tú", "un", "una", "uno", "unos", "vosotras",
    "vosotros", "vuestra", "vuestras", "vuestro", "vuestros", "y", "ya",
    "yo",
})


# Resultado de calculardatos()
@dataclass(frozen=True)
class Datos:
    total: int
    pct_pendiente: float
    pct_en_proceso: float
    pct_resuelto: float
    pct_invalido: float
    mediana_tiempo_en_proceso: float | None
    mediana_tiempo_resuelto: float | None
    palabras_frecuentes: list[tuple[str, int]]  # top 15 ya ordenadas desc


# Figura de matplotlib -> data URI

def _figura_a_data_uri(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)  # Evita fugas de memoria
    buffer.seek(0)
    codificado = base64.b64encode(buffer.read()).decode("ascii")
    return f"data:image/png;base64,{codificado}"


# Graficas
class Graficas(ABC):
    @abstractmethod
    def generar_grafica(self, datos: Datos) -> str:
        """Devuelve la imagen como data URI PNG"""
        raise NotImplementedError

class Graf_torta(Graficas):
    """Diagrama circular con el porcentaje de reclamos por estado."""

    def generar_grafica(self, datos: Datos) -> str:
        fig, ax = plt.subplots(figsize=(5.5, 5.5))

        if datos.total == 0:
            ax.text(0.5, 0.5, "Sin reclamos para mostrar", ha="center", va="center")
            ax.axis("off")
            return _figura_a_data_uri(fig)

        secciones = [
            ("Pendiente", datos.pct_pendiente),
            ("En proceso", datos.pct_en_proceso),
            ("Resuelto", datos.pct_resuelto),
            ("Inválido", datos.pct_invalido),
        ]
        secciones = [(etiqueta, pct) for etiqueta, pct in secciones if pct > 0]

        etiquetas = [f"{etiqueta}" for etiqueta, _ in secciones]
        valores = [pct for _, pct in secciones]

        ax.pie(valores, labels=etiquetas, autopct="%1.1f%%", startangle=90)
        ax.set_title(f"Distribución de reclamos (total: {datos.total})")
        ax.axis("equal")
        return _figura_a_data_uri(fig)


class Graf_tiempo(Graficas):
    """Gráfico de barras comparando la mediana de días de resolución entre reclamos en proceso y reclamos resueltos."""

    def generar_grafica(self, datos: Datos) -> str:
        fig, ax = plt.subplots(figsize=(5.5, 4))

        categorias = ["En proceso", "Resuelto"]
        crudos = [datos.mediana_tiempo_en_proceso, datos.mediana_tiempo_resuelto]
        valores = [v if v is not None else 0 for v in crudos]

        barras = ax.bar(categorias, valores, color=["#4C72B0", "#55A868"])
        ax.set_ylabel("Mediana (días)")
        ax.set_title("Tiempo de resolución de reclamos")

        for barra, valor_original in zip(barras, crudos):
            etiqueta = f"{valor_original:.1f}" if valor_original is not None else "Sin datos"
            ax.text(
                barra.get_x() + barra.get_width() / 2, barra.get_height(),
                etiqueta, ha="center", va="bottom",
            )
        return _figura_a_data_uri(fig)


class Palabras_frecuentes(Graficas):
    """ Gráfico de barras horizontales con las palabras clave más frecuentes"""

    def generar_grafica(self, datos: Datos) -> str:
        palabras = datos.palabras_frecuentes

        fig, ax = plt.subplots(figsize=(6.5, 5))

        if not palabras:
            ax.text(0.5, 0.5, "Sin datos suficientes", ha="center", va="center")
            ax.axis("off")
            return _figura_a_data_uri(fig)

        # reversed: para que la palabra más frecuente quede arriba
        ordenadas = list(reversed(palabras))
        etiquetas = [palabra for palabra, _ in ordenadas]
        frecuencias = [frecuencia for _, frecuencia in ordenadas]

        ax.barh(etiquetas, frecuencias, color="#8172B2")
        ax.set_xlabel("Frecuencia")
        ax.set_title("Palabras más frecuentes en los reclamos")

        max_frec, min_frec = max(frecuencias), min(frecuencias)
        for etiqueta_tick, frecuencia in zip(ax.get_yticklabels(), frecuencias):
            proporcion = (frecuencia - min_frec) / (max_frec - min_frec) if max_frec > min_frec else 1.0
            etiqueta_tick.set_fontsize(9 + proporcion * 10)  # entre 9 y 19 pt
            etiqueta_tick.set_fontweight("bold" if proporcion > 0.66 else "normal")

        return _figura_a_data_uri(fig)


# Lo que usa GestorReclamos.generar_reporte
class Analitica:
    def __init__(self,
                 graf_torta: Graficas | None = None,
                 graf_tiempo: Graficas | None = None,
                 palabras_frecuentes: Graficas | None = None,
                 stopwords: frozenset[str] | None = None):
        self._graf_torta = graf_torta or Graf_torta()
        self._graf_tiempo = graf_tiempo or Graf_tiempo()
        self._palabras_frecuentes = palabras_frecuentes or Palabras_frecuentes()
        self._stopwords = stopwords if stopwords is not None else STOPWORDS_ES

    def _extraer_palabras(self, contenido: str) -> list[str]:
        tokens = re.findall(r"[a-záéíóúñ]+", contenido.lower())
        return [t for t in tokens if t not in self._stopwords and len(t) > 2]

    def calculardatos(self, lista_de_reclamos: list[Reclamo],
                       monticulo_mediana_cls: type[MonticuloMediana] = MonticuloMediana) -> Datos:
        total = len(lista_de_reclamos)
        conteo = {estado: 0 for estado in EstadoReclamo}
        mediana_en_proceso = monticulo_mediana_cls()
        mediana_resuelto = monticulo_mediana_cls()
        contador_palabras: Counter[str] = Counter()

        for reclamo in lista_de_reclamos:
            conteo[reclamo.estado] += 1

            if reclamo.tiempo_resolucion_asignado is not None:
                if reclamo.estado == EstadoReclamo.EN_PROCESO:
                    mediana_en_proceso.agregar_numero(reclamo.tiempo_resolucion_asignado)
                elif reclamo.estado == EstadoReclamo.RESUELTO:
                    mediana_resuelto.agregar_numero(reclamo.tiempo_resolucion_asignado)

            contador_palabras.update(self._extraer_palabras(reclamo.contenido))

        def pct(n: int) -> float:
            return (n / total * 100.0) if total > 0 else 0.0

        # top 15 por frecuencia desc; empate se rompe alfabéticamente
        top_palabras = sorted(contador_palabras.items(), key=lambda par: (-par[1], par[0]))[:15]

        return Datos(
            total=total,
            pct_pendiente=pct(conteo[EstadoReclamo.PENDIENTE]),
            pct_en_proceso=pct(conteo[EstadoReclamo.EN_PROCESO]),
            pct_resuelto=pct(conteo[EstadoReclamo.RESUELTO]),
            pct_invalido=pct(conteo[EstadoReclamo.INVALIDO]),
            mediana_tiempo_en_proceso=mediana_en_proceso.obtener_mediana(),
            mediana_tiempo_resuelto=mediana_resuelto.obtener_mediana(),
            palabras_frecuentes=top_palabras,
        )

    def generar_grafica_tor(self, datos: Datos) -> str:
        return self._graf_torta.generar_grafica(datos)

    def generar_grafica_tie(self, datos: Datos) -> str:
        return self._graf_tiempo.generar_grafica(datos)

    def generar_grafica_pa(self, datos: Datos) -> str:
        return self._palabras_frecuentes.generar_grafica(datos)

    def generar_reporte(self, datos: Datos, grafico_tor: str, grafico_tie: str,
                         grafico_pa: str, tipo: str) -> "Informe":
        # Import local para evitar import circular: informes.py no necesita conocer analitica.py, sólo al revés.
        from .informes import INFORMES_DISPONIBLES

        clase_informe = INFORMES_DISPONIBLES.get(tipo)
        if clase_informe is None:
            raise TipoInformeNoSoportadoError(tipo, INFORMES_DISPONIBLES.keys())
        return clase_informe(datos, grafico_tor, grafico_tie, grafico_pa)
