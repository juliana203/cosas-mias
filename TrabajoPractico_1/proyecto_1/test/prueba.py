# pruebas de codigo
import csv
import matplotlib.pyplot as plt
from datetime import datetime
import mpld3

historial = []
historial2 = []
with open("C:\\tp\\proyecto_5\\data\\historial.csv", 'r', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        historial.append({'nombre': row[0], 'tiempo': row[1], 'aciertos': f"{row[2]}/{row[4]}", "desaciertos": f"{row[3]}/{row[4]}"})
        historial2.append(row)

fechas = []
aciertos = []
desaciertos = []
total_aciertos = 0
total_desaciertos = 0

for registro in historial2:
    fecha_str = registro[1].split(".")[0]  # Eliminar decimales de los segundos
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S").date()
    fechas.append(fecha.strftime('%Y-%m-%d'))  # Convertir a cadena en formato 'YYYY-MM-DD'
    aciertos.append(int(registro[2]))
    desaciertos.append(int(registro[3]))
    total_aciertos += int(registro[2])
    total_desaciertos += int(registro[3])
print(fechas)

# Graficar
plt.figure(figsize=(10, 6))
plt.plot(fechas, aciertos, marker='o', label='Aciertos')
plt.plot(fechas, desaciertos, marker='x', label='Desaciertos')
plt.title('Aciertos y desaciertos a lo largo del tiempo')
plt.xlabel('Fecha')
plt.ylabel('Cantidad')
plt.xticks(rotation=45)  # Rotar fechas para mejor visualización
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

# Crear el gráfico circular
labels = ['Aciertos', 'Desaciertos']
sizes = [total_aciertos, total_desaciertos]
colors = ['lightgreen', 'lightcoral']
explode = (0.1, 0)  # Resaltar la primera sección (aciertos)

plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
plt.title('Porcentaje de Aciertos y Desaciertos acumulados')
plt.axis('equal')  # Para asegurar que el gráfico sea circular

plt.show()

#grafica por promedios.

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
    promedio_aciertos.append(sum(totales['aciertos']) / len(totales['aciertos']))
    promedio_desaciertos.append(sum(totales['desaciertos']) / len(totales['desaciertos']))

# Graficar
plt.figure(figsize=(10, 6))
plt.plot(fechas2, promedio_aciertos, marker='o', label='Promedio Aciertos')
plt.plot(fechas2, promedio_desaciertos, marker='x', label='Promedio Desaciertos')
plt.title('Promedio de Aciertos y Desaciertos por Fecha')
plt.xlabel('Fecha')
plt.ylabel('Promedio')
plt.xticks(rotation=45)  # Rotar fechas para mejor visualización
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Convertir la gráfica a HTML
html_fig = mpld3.fig_to_html(plt.gcf())

# Guardar el HTML en un archivo existente
with open("./templates/resultados.html", "a") as file:
    file.write(html_fig)