"""
graficas.py
Clase 'Graficas'que genera los 3 gráficos pedidos usando matplotlib, devolviendo cada
uno como una imagen PNG codificada en base64 (data URI) lista para insertar en un <img src="..."> del HTML.
"""

import base64
import io

import matplotlib
matplotlib.use("Agg")  # backend sin interfaz gráfica: obligatorio en un server Flask
import matplotlib.pyplot as plt

class Graficas:

    def __figura_a_data_uri(self, fig) -> str:
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight", dpi=110)
        plt.close(fig)  # Evita fugas de memoria
        buffer.seek(0)
        codificado = base64.b64encode(buffer.read()).decode("ascii")
        return f"data:image/png;base64,{codificado}"

    def generar_grafica_tor(self, estadisticas: dict) -> str:
        """Torta con el porcentaje de reclamos por estado."""
        fig, ax = plt.subplots(figsize=(5.5, 5.5))
        total = estadisticas.get("total", 0)

        if total == 0:
            ax.text(0.5, 0.5, "Sin reclamos para mostrar", ha="center", va="center")
            ax.axis("off")
            return self.__figura_a_data_uri(fig)

        secciones = [
            ("Pendiente", estadisticas.get("pendientes", 0)),
            ("En proceso", estadisticas.get("en_proceso", 0)),
            ("Resuelto", estadisticas.get("resueltos", 0)),
            ("Inválido", estadisticas.get("invalidos", 0)),
        ]
        secciones = [(etiqueta, pct) for etiqueta, pct in secciones if pct > 0]
        etiquetas = [etiqueta for etiqueta, _ in secciones]
        valores = [pct for _, pct in secciones]

        ax.pie(valores, labels=etiquetas, autopct="%1.1f%%", startangle=90)
        ax.set_title(f"Distribución de reclamos (total: {total})")
        ax.axis("equal")
        return self.__figura_a_data_uri(fig)

    def generar_grafica_tiem(self, mediana_tiempos: float) -> str:
        """Barra con la mediana de días de resolución de los reclamos"""
        fig, ax = plt.subplots(figsize=(4.5, 4))

        barra = ax.bar(["Mediana"], [mediana_tiempos], color="#4C72B0", width=0.4)
        ax.set_ylabel("Días")
        ax.set_title("Mediana del tiempo de resolución")
        ax.text(
            barra[0].get_x() + barra[0].get_width() / 2, barra[0].get_height(),
            f"{mediana_tiempos:.1f}", ha="center", va="bottom",
        )
        return self.__figura_a_data_uri(fig)

    def generar_grafica_pf(self, palabras_frecuentes: list[tuple[str, int]]) -> str:
        """Barras horizontales con las palabras clave más frecuentes."""
        fig, ax = plt.subplots(figsize=(6.5, 5))

        if not palabras_frecuentes:
            ax.text(0.5, 0.5, "Sin datos suficientes", ha="center", va="center")
            ax.axis("off")
            return self.__figura_a_data_uri(fig)

        # reversed: para que la palabra más frecuente quede arriba
        ordenadas = list(reversed(palabras_frecuentes))
        etiquetas = [palabra for palabra, _ in ordenadas]
        frecuencias = [frecuencia for _, frecuencia in ordenadas]

        ax.barh(etiquetas, frecuencias, color="#8172B2")
        ax.set_xlabel("Frecuencia")
        ax.set_title("Palabras más frecuentes en los reclamos")
        return self.__figura_a_data_uri(fig)
