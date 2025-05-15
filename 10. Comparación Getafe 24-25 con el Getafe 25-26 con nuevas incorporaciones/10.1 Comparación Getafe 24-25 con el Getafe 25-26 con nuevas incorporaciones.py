#Comparación Getafe 24-25 con el Getafe 25-26 con nuevas incorporaciones
pip install pandas openpyxl matplotlib numpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- Configuración de Archivos y Leyendas ---
file_path_1 = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\RESULTADOS COMPARACIÓN\Comp. Getafe 24-25 vs nuevos fichajes\Getafe 24-25.xlsx"
legend_1 = "Getafe 24-25"
file_path_2 = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\RESULTADOS COMPARACIÓN\Comp. Getafe 24-25 vs nuevos fichajes\Getafe nuevos fichajes.xlsx"
legend_2 = "Getafe 25-26 con nuevas incorporaciones"

output_dir = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\RESULTADOS COMPARACIÓN\Comp. Getafe 24-25 vs nuevos fichajes"
# Nombre del archivo de imagen de salida
output_filename = "comparacion_radar_equipos.jpg" 
output_path = os.path.join(output_dir, output_filename)

# --- Headers de las columnas a sumar y graficar ---
# Asegúrate de que estos nombres coincidan EXACTAMENTE con los de tu Excel.
# La columna 'Jugador' se asume que es de texto y no se sumará.
stats_headers = [
    "% de ganados", "G-TP.1", "Ast", "SCA90", "GCA90",
    "% Cmp.1", "% Cmp.2", "% Cmp.3", "Exitosa%", "TalArc/90",
    "G/TalArc", "npxG", "Tkl+Int", "Tkl%", "Err", "GC90",
    "% Salvadas", "PaC%", "% Salvadas.1", "PSxG+/-", "Long. prom..1"
]

# --- Función para procesar los archivos Excel ---
def process_excel_file(filepath, columns_to_sum):
    """
    Lee un archivo Excel y suma los valores de las columnas especificadas.
    Maneja columnas que puedan ser no numéricas o estén faltantes, tratándolas como 0.
    """
    try:
        df = pd.read_excel(filepath)
        
        # Inicializar una Serie de pandas para almacenar las sumas.
        # Todas las 'stats_headers' estarán presentes, con 0.0 como valor por defecto.
        sums = pd.Series(0.0, index=columns_to_sum, dtype=float)

        for col in columns_to_sum:
            if col in df.columns:
                # Intentar convertir la columna a numérico. Los errores se convertirán a NaN.
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                # Sumar los valores numéricos, tratando los NaNs como 0 en la suma.
                sums[col] = numeric_col.sum(skipna=True)
            else:
                print(f"Advertencia: La columna '{col}' no se encontró en el archivo '{os.path.basename(filepath)}'. Se considerará como 0 para esta columna.")
        
        return sums
    except FileNotFoundError:
        print(f"Error CRÍTICO: Archivo no encontrado en la ruta '{filepath}'. Verifica la ruta.")
        # Devuelve una Serie de ceros si el archivo no se encuentra.
        return pd.Series(0.0, index=columns_to_sum, dtype=float)
    except Exception as e:
        print(f"Error CRÍTICO: Ocurrió un error al procesar el archivo '{filepath}': {e}")
        # Devuelve una Serie de ceros en caso de otros errores.
        return pd.Series(0.0, index=columns_to_sum, dtype=float)

# --- Carga y procesamiento de datos ---
print("Procesando archivos Excel...")
sums_data1 = process_excel_file(file_path_1, stats_headers)
sums_data2 = process_excel_file(file_path_2, stats_headers)

# Si después de procesar, ambas sumas son completamente cero, podría indicar un problema mayor.
# (ej. nombres de columnas incorrectos en `stats_headers` para AMBOS archivos)
if sums_data1.sum() == 0 and sums_data2.sum() == 0 and not sums_data1.empty and not sums_data2.empty:
    print("Advertencia: La suma total de todas las estadísticas es cero para ambos archivos. \n"
          "Esto podría indicar que los nombres de las columnas en 'stats_headers' no coinciden \n"
          "con los de tus archivos Excel, o que todos los datos son genuinamente cero.")

# --- Preparación de datos para el gráfico de radar ---
num_vars = len(stats_headers)

# Obtener los valores sumados como arrays de NumPy
values1 = sums_data1.values
values2 = sums_data2.values

# Normalización: El valor máximo entre los dos archivos para CADA estadística será el 100%
# max_per_stat contendrá el valor máximo para cada estadística individualmente.
max_per_stat = np.maximum(values1, values2)

# Evitar división por cero si max_per_stat es 0 para alguna estadística.
# Si max_per_stat[i] es 0, significa que values1[i] y values2[i] son ambos 0.
# En tal caso, el valor normalizado también será 0.
normalized_values1 = np.zeros_like(values1, dtype=float)
np.divide(values1, max_per_stat, out=normalized_values1, where=max_per_stat != 0)

normalized_values2 = np.zeros_like(values2, dtype=float)
np.divide(values2, max_per_stat, out=normalized_values2, where=max_per_stat != 0)

# --- Creación del gráfico de radar ---
print("Creando gráfico de radar...")
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# Para que el gráfico de radar sea un polígono cerrado, repetimos el primer valor y ángulo al final.
values1_plot = np.concatenate((normalized_values1, [normalized_values1[0]]))
values2_plot = np.concatenate((normalized_values2, [normalized_values2[0]]))
angles_plot = np.concatenate((angles, [angles[0]]))

# Configuración de la figura y el eje polar
# Aumenta figsize si las etiquetas de las estadísticas son largas o numerosas
fig, ax = plt.subplots(figsize=(15, 15), subplot_kw=dict(polar=True))

# Graficar datos del Archivo 1
ax.plot(angles_plot, values1_plot, linewidth=2, linestyle='solid', label=legend_1, color='dodgerblue', zorder=3)
ax.fill(angles_plot, values1_plot, 'dodgerblue', alpha=0.3, zorder=2)

# Graficar datos del Archivo 2
ax.plot(angles_plot, values2_plot, linewidth=2, linestyle='solid', label=legend_2, color='tomato', zorder=3)
ax.fill(angles_plot, values2_plot, 'tomato', alpha=0.3, zorder=2)

# Etiquetas de las variables (estadísticas) en cada eje del radar
ax.set_xticks(angles)
# Ajusta el tamaño de fuente si es necesario para que no se superpongan
ax.set_xticklabels(stats_headers, fontsize=10) 

# Ajustar alineación de etiquetas de los ejes para mejor visualización
for label, angle_deg in zip(ax.get_xticklabels(), np.degrees(angles)):
    if angle_deg == 0:
        label.set_horizontalalignment('center')
    elif angle_deg == 180:
        label.set_horizontalalignment('center')
    elif 0 < angle_deg < 180:
        label.set_horizontalalignment('left')
    else: # 180 < angle_deg < 360
        label.set_horizontalalignment('right')
    # Mover un poco las etiquetas para que no colisionen con el gráfico
    label.set_y(label.get_position()[1] - 0.05) # Ajusta este valor si es necesario


# Etiquetas del eje Y (radial) - representando el porcentaje del máximo (0% a 100%)
ax.set_yticks(np.linspace(0, 1, 5)) # Crea 5 ticks: 0, 0.25, 0.5, 0.75, 1.0
ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=9, color="grey")
ax.set_ylim(0, 1) # Asegurar que el eje Y (radial) va de 0 a 1

# Título del gráfico y leyenda
plt.title('Comparación de Estadísticas Agregadas de Equipos', size=20, y=1.12, weight='bold')
# Colocar la leyenda fuera del área de trazado para no obstruir el gráfico
ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), fontsize=12)

# Ajustar el layout para evitar que los elementos se superpongan tanto como sea posible
# plt.tight_layout() # A veces causa problemas con bbox_to_anchor, usar con precaución o ajustar bbox.

# --- Guardar el gráfico ---
try:
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    # Guardar la figura. `bbox_inches='tight'` ayuda a incluir todos los elementos en la imagen guardada.
    plt.savefig(output_path, format='jpg', dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado exitosamente en: {output_path}")
except Exception as e:
    print(f"Error CRÍTICO: No se pudo guardar el gráfico en '{output_path}': {e}")

# Mostrar el gráfico en Jupyter Lab (si no se guarda, esto es esencial para verlo)
plt.show()

print("Proceso completado.")