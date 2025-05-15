#Radar Uche vs Jaime Mata

import pandas as pd
import os
from mplsoccer import Radar, grid
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

# Leer el archivo CSV del primer jugador
file_path_1 = 'C:/Users/david/LIGAS/La Liga/Getafe/Escalado_Getafe/Jugadores/DC. Chrisantus Uche/Chrisantus Uche.csv'
data_1 = pd.read_csv(file_path_1)

# Leer el archivo CSV del segundo jugador
file_path_2 = 'C:/Users/david/LIGAS/Getafe 18-19/Escalado_Getafe 18-19/Jugadores/DC. Jaime Mata/Jaime Mata.csv'
data_2 = pd.read_csv(file_path_2)

# Extraer los nombres de los jugadores
player_name_1 = data_1['Jugador'].unique()[0]
player_name_2 = data_2['Jugador'].unique()[0]

# Filtrar solo las columnas numéricas y descartar las no numéricas
player_data_1 = data_1.drop(columns=['Jugador']).select_dtypes(include=[np.number])
player_data_2 = data_2.drop(columns=['Jugador']).select_dtypes(include=[np.number])

# Agregar los valores de cada métrica (sumar filas si es necesario)
player_data_aggregated_1 = player_data_1.sum()
player_data_aggregated_2 = player_data_2.sum()

# Parámetros (headers del archivo CSV)
params = list(player_data_aggregated_1.keys())
low = [0] * len(params)  # Límite inferior (mínimo posible) para cada métrica
high = [1] * len(params)  # Límite superior (máximo posible) para cada métrica

# Normalizar los valores al rango [0, 1]
def normalize_value(value, min_val, max_val):
    """Normaliza un valor al rango [0, 1]."""
    if max_val - min_val == 0:  # Evitar divisiones por cero
        return 0
    return (value - min_val) / (max_val - min_val)

# Ajustar cada valor al rango [0, 1]
player_values_1 = [
    normalize_value(value, low[i], high[i])
    for i, value in enumerate(player_data_aggregated_1.values)
]

player_values_2 = [
    normalize_value(value, low[i], high[i])
    for i, value in enumerate(player_data_aggregated_2.values)
]

# Crear el radar
radar = Radar(params, low, high, round_int=[False] * len(params), num_rings=10, ring_width=0.1, center_circle_radius=0.0)

# Crear la figura usando la función grid de mplsoccer con ajustes en grid_width y left
fig, axs = grid(figheight=14, grid_width=0.8, left=0.1,
                title_height=0.08, title_space=0,
                endnote_height=0.025, endnote_space=0,
                grid_key='radar', axis=False)

# Graficar el radar
radar.setup_axis(ax=axs['radar'])

# Dibujar manualmente las franjas con un único color (por ejemplo: gris claro)
for i in range(1, 11):  # Dibujar 10 anillos (ajustados para llegar a 1.00)
    axs['radar'].add_patch(plt.Circle((0, 0), i / 10,
                                      transform=axs['radar'].transData,
                                      facecolor='#E0E0E0', edgecolor='#BDBDBD', lw=1))

# Ajustar el rango del eje para que abarque completamente el radar y los valores
axs['radar'].set_xlim(-1.05, 1.05)  # Extender ligeramente para evitar recortes
axs['radar'].set_ylim(-1.05, 1.05)

# Ajustar los indicadores de rango después de dibujar el radar
range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=16)

# Dibujar las etiquetas de los parámetros (headers) alrededor del radar y acercarlas más al centro
param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=22, fontweight='bold')

# Acercar las etiquetas al radar ajustando su posición manualmente (ajuste intermedio)
for label in param_labels:
    x, y = label.get_position()  # Obtener la posición actual de la etiqueta
    label.set_position((x * 0.55, y * 0.55))  # Acercarlas multiplicando por un factor menor a 1

# Coordenadas del área poligonal para ambos jugadores (convertimos valores a coordenadas polares)
angles = np.linspace(0, 2 * np.pi, len(player_values_1), endpoint=False).tolist()
angles += angles[:1]  # Cerrar el polígono

values_1 = player_values_1 + player_values_1[:1]  # Cerrar el polígono para el primer jugador
values_2 = player_values_2 + player_values_2[:1]  # Cerrar el polígono para el segundo jugador

x_coords_1 = [v * np.sin(a) for v, a in zip(values_1, angles)]
y_coords_1 = [v * np.cos(a) for v, a in zip(values_1, angles)]

x_coords_2 = [v * np.sin(a) for v, a in zip(values_2, angles)]
y_coords_2 = [v * np.cos(a) for v, a in zip(values_2, angles)]

# Dibujar manualmente las áreas poligonales para ambos jugadores
polygon_red = Polygon(xy=list(zip(x_coords_1, y_coords_1)), closed=True,
                      facecolor='red', edgecolor='red', alpha=0.6)
polygon_blue = Polygon(xy=list(zip(x_coords_2, y_coords_2)), closed=True,
                       facecolor='blue', edgecolor='blue', alpha=0.6)

axs['radar'].add_patch(polygon_red)
axs['radar'].add_patch(polygon_blue)

# Ruta de los escudos
escudo_getafe_path = 'C:/Users/david/OneDrive/Escritorio/MÁSTER/ESCUDOS/GETAFE.jpg'
escudo_liverpool_path = 'C:/Users/david/OneDrive/Escritorio/MÁSTER/ESCUDOS/GETAFE.jpg'

# Cargar las imágenes de los escudos
escudo_getafe_img = mpimg.imread(escudo_getafe_path)
escudo_liverpool_img = mpimg.imread(escudo_liverpool_path)

# Crear OffsetImages para los escudos
escudo_getafe_offset_img = OffsetImage(escudo_getafe_img, zoom=0.15)
escudo_liverpool_offset_img = OffsetImage(escudo_liverpool_img, zoom=0.15)

# Añadir el nombre y escudo del primer jugador (Getafe)
axs['title'].text(0.15, 0.5, player_name_1,
                  fontsize=24, fontweight='bold',
                  color='red', ha='center', va='center')

escudo_ab_player1 = AnnotationBbox(escudo_getafe_offset_img,
                                   (0.35, 0.5), frameon=False,
                                   xycoords="axes fraction")
axs['title'].add_artist(escudo_ab_player1)

# Añadir el nombre y escudo del segundo jugador (Liverpool)
axs['title'].text(0.75, 0.5, f"{player_name_2} (18/19)",
                  fontsize=24, fontweight='bold',
                  color='blue', ha='center', va='center')

escudo_ab_player2 = AnnotationBbox(escudo_liverpool_offset_img,
                                   (1.05, 0.5), frameon=False,
                                   xycoords="axes fraction")
axs['title'].add_artist(escudo_ab_player2)

# Añadir la segunda leyenda más arriba y hacia la izquierda al lado derecho del radar
legend_text_second = """
Min: minutos jugados en la temporada
TA: Tarjetas amarillas
TR: Tarjetas rojas
G-TP.1: Goles anotados cada 90 minutos (sin penales)
Ast: asistencias cada 90 minutos
SCA90: Acciones de creación de tiro cada 90 minutos
GCA90: Acciones de creación de goles cada 90 minutos
Tkl%: Tacklings realizados con éxito (regateadores tacleados dividido entre el número de intentos)
Tkl+Int: Tacklings+intercepciones
% de ganados: Porcentaje de duelos aéreos ganados
% Cmp.1: Pases cortos (de entre 5 y 15 yardas) completados
% Cmp.2: Pases de distancia media (de entre 15 y 30 yardas) completados
% Cmp.3: Pases largos (de más de 30 yardas) completados
Exitosa%: Porcentaje de regates realizados con éxito
TalArc/90: Disparos a puerta por 90 minutos
G/TalArc: Goles anotados por tiros a puerta
npxG: Goles esperados sin contar penales"""

axs['radar'].text(1.15, 0.5, legend_text_second,
                  fontsize=14,
                  ha='left', va='center',
                  transform=axs['radar'].transAxes)

plt.show()

# Ruta donde se guardará la imagen
output_path = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\DEFENSA TFM\Imágenes radares comparación getafe"

# Nombre del archivo de salida
output_file = os.path.join(output_path, "radar_comparacion_getafe.jpg")

# Guardar la figura como imagen JPG
fig.savefig(output_file, format='jpg', dpi=300, bbox_inches='tight')

print(f"Radar guardado exitosamente en: {output_file}")
