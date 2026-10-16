import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
# Ajustá este valor al tiempo real de tu simulación.
# En tu imagen llega hasta 15 ns. Si la tuya duró 20, cambialo a 20.
TIEMPO_TOTAL_NS = 15 

# Nombres exactos de tus archivos CSV
file_rmsd = 'rmsd_ca.csv'
file_rmsf = 'rmsf_ca.csv'
file_radgyr = 'radius_gyration.csv'

# Configuración global de fuentes para que se vea como en Colab
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

# ==========================================
# 2. GRÁFICO 1: RMSD (Estabilidad Global)
# ==========================================
if os.path.exists(file_rmsd):
    # Leemos el CSV y sacamos la última columna (los datos reales)
    df_rmsd = pd.read_csv(file_rmsd)
    y_rmsd = df_rmsd.iloc[:, -1].values
    
    # Recreamos el eje del tiempo (de 0 a 15 ns, repartido en la cantidad de frames)
    x_time = np.linspace(0, TIEMPO_TOTAL_NS, len(y_rmsd))
    
    plt.figure(figsize=(6, 4))
    plt.plot(x_time, y_rmsd, alpha=0.6, color='blue', linewidth=1.0)
    
    plt.xlim(0, TIEMPO_TOTAL_NS)
    plt.xlabel("Time (ns)")
    plt.ylabel("RMSD [Å]")
    
    plt.tight_layout()
    plt.savefig('Plot_1_RMSD.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✅ Gráfico de RMSD generado con éxito.")
else:
    print(f"❌ No se encontró {file_rmsd}")

# ==========================================
# 3. GRÁFICO 2: RMSF (Flexibilidad por Residuo)
# ==========================================
if os.path.exists(file_rmsf):
    df_rmsf = pd.read_csv(file_rmsf)
    y_rmsf = df_rmsf.iloc[:, -1].values
    
    # El eje X acá no es tiempo, es el número de aminoácido (residuo)
    x_res = np.arange(1, len(y_rmsf) + 1)
    
    plt.figure(figsize=(6, 4))
    plt.plot(x_res, y_rmsf, alpha=0.6, color='red', linewidth=1.0)
    
    plt.xlim(0, len(y_rmsf))
    plt.xlabel("Residue")
    plt.ylabel("RMSF (Å)")
    
    plt.tight_layout()
    plt.savefig('Plot_2_RMSF.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✅ Gráfico de RMSF generado con éxito.")
else:
    print(f"❌ No se encontró {file_rmsf}")

# ==========================================
# 4. GRÁFICO 3: RADIO DE GIRO (Empaquetamiento)
# ==========================================
if os.path.exists(file_radgyr):
    df_radgyr = pd.read_csv(file_radgyr)
    y_radgyr = df_radgyr.iloc[:, -1].values
    
    # Reusamos la misma lógica de tiempo que en el RMSD
    x_time_rg = np.linspace(0, TIEMPO_TOTAL_NS, len(y_radgyr))
    
    plt.figure(figsize=(6, 4))
    plt.plot(x_time_rg, y_radgyr, alpha=0.6, color='green', linewidth=1.0)
    
    plt.xlim(0, TIEMPO_TOTAL_NS)
    plt.xlabel("Time (ns)")
    plt.ylabel("Radius of gyration (Å)")
    
    plt.tight_layout()
    plt.savefig('Plot_3_RadGyr.png', dpi=600, bbox_inches='tight')
    plt.show()
    print("✅ Gráfico de Radio de Giro generado con éxito.")
else:
    print(f"❌ No se encontró {file_radgyr}")
