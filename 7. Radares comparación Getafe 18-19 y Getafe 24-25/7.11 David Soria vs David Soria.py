#David Soria vs David Soria

import pandas as pd
from mplsoccer import Radar, FontManager, grid
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import os

# Rutas de los archivos CSV
file_path_1 = r"C:/Users/david/LIGAS/Getafe 18-19/Escalado_Getafe 18-19/Jugadores/PO. David Soria/David Soria.csv"
file_path_2 = r"C:/Users/david/LIGAS/La Liga/Getafe/Escalado_Getafe/Jugadores/PO. David Soria/David Soria.csv"

# Leer los archivos CSV y extraer los nombres de los jugadores
data_1 = pd.read_csv(file_path_1)
data_2 = pd.read_csv(file_path_2)

player1_name = f"{data_1['Jugador'].iloc[0]} (18/19)"  # Nombre del jugador 1 con "(18/19)"
player2_name = data_2['Jugador'].iloc[0]  # Nombre del jugador 2

# Valores de los jugadores (puedes ajustar estos valores según las métricas que quieras representar)
player1_values = [3330, 0.92, 77.4, 35.1, 20, 7.5, 59.2, 90.9, 94.1, 38.9, 6]
player2_values = [1890, 0.81, 77.8, 28.6, 25, 4.1, 59.8, 100, 97.8, 41.7, 2]

# Parámetros del radar
params = ["Mín", "GC90", "% Salvadas", "PaC%", "% Salvadas.1", "PSxG+/-", 
          "Long. prom..1", "% Cmp.1", "% Cmp.2", "% Cmp.3", "Err"]

# Límites mínimos y máximos para cada parámetro (ajustando PSxG+/- de 1 a 10)
min_range = [0, 0, 0, 0, 0, -2, 0, 50, 50, 30, 0]   # Cambiado -5 a +1 para PSxG+/-
max_range = [3330, 1, 100, 100, 100, 8, 100, 100, 100, 100, 20]   # Cambiado +5 a +10 para PSxG+/-

# Configuración de colores y equipos
player1_team = "Getafe"
player2_team = "Getafe"
player1_color = "#29B6F6"
player2_color = "#FF5722"

# Configuración de fuentes (Google Fonts)
URL4 = 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf'
robotto_thin = FontManager(URL4)

URL5 = ('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/' 'RobotoSlab%5Bwght%5D.ttf')
robotto_bold = FontManager(URL5)

# Crear radar con división en franjas según los parámetros
radar = Radar(params=params,
              min_range=min_range,
              max_range=max_range,
              round_int=[False] * len(params), # No redondear etiquetas a enteros por defecto
              num_rings=10,
              ring_width=1,
              center_circle_radius=1)

# Configurar que PSxG+/- tenga divisiones enteras manualmente (ajustando round_int)
radar.round_int[params.index("PSxG+/-")] = True

# Crear figura y ejes con grid de mplsoccer
fig, axs = grid(figheight=14,
                grid_width=0.95,
                grid_height=0.915,
                title_height=0.06,
                endnote_height=0.025,
                title_space=0,
                endnote_space=0,
                grid_key='radar',
                axis=False)

# Configurar el radar en el eje correspondiente
radar.setup_axis(ax=axs['radar'])

# Dibujar círculos del radar con las divisiones especificadas
radar.draw_circles(ax=axs['radar'], facecolor='#E0E0E0', edgecolor='#BDBDBD')

# Dibujar las áreas poligonales de ambos jugadores en el radar
radar.draw_radar(player1_values,
                 ax=axs['radar'],
                 kwargs_radar={'facecolor': player1_color, 'alpha': 0.6})
radar.draw_radar(player2_values,
                 ax=axs['radar'],
                 kwargs_radar={'facecolor': player2_color, 'alpha': 0.6})

# Ajustar las etiquetas de rango (división proporcional en cada franja)
radar.draw_range_labels(ax=axs['radar'], fontsize=16,
                        fontproperties=robotto_thin.prop)

# Dibujar etiquetas de parámetros
radar.draw_param_labels(ax=axs['radar'], fontsize=22)

# Añadir títulos al gráfico
axs['title'].text(0.01, 0.65,
                  player1_name,
                  fontsize=25,
                  color=player1_color,
                  fontproperties=robotto_bold.prop,
                  ha='left', va='center')

axs['title'].text(0.01, 0.25,
                  player1_team,
                  fontsize=20,
                  fontproperties=robotto_thin.prop,
                  ha='left', va='center',
                  color=player1_color)

axs['title'].text(0.99, 0.65,
                  player2_name,
                  fontsize=25,
                  color=player2_color,
                  fontproperties=robotto_bold.prop,
                  ha='right', va='center')

axs['title'].text(0.99, 0.25,
                  player2_team,
                  fontsize=20,
                  fontproperties=robotto_thin.prop,
                  ha='right', va='center',
                  color=player2_color)

endnote_text = axs['endnote'].text(0.99, 0.5,
                                   'www.futbolcondatos.com',
                                   fontsize=15,
                                   fontproperties=robotto_thin.prop,
                                   ha='right', va='center')

# Añadir escudos junto a los nombres de los jugadores
escudo_path_1 = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\ESCUDOS\GETAFE.jpg" # Ruta al escudo del equipo del jugador 1
escudo_path_2 = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\ESCUDOS\GETAFE.jpg" # Ruta al escudo del equipo del jugador 2

# Verificar si las imágenes existen antes de cargarlas
if os.path.exists(escudo_path_1):
    escudo_img_1 = mpimg.imread(escudo_path_1) # Cargar la imagen del escudo del jugador 1
    imagebox_1 = OffsetImage(escudo_img_1, zoom=0.15)
    ab_1 = AnnotationBbox(imagebox_1,
                          (0.30, 0.4),
                          frameon=False,
                          xycoords='axes fraction',
                          box_alignment=(0.5, 0))
    axs['title'].add_artist(ab_1)
else:
    print(f"Advertencia: No se encontró el archivo {escudo_path_1}")

if os.path.exists(escudo_path_2):
    escudo_img_2 = mpimg.imread(escudo_path_2) # Cargar la imagen del escudo del jugador 2
    imagebox_2 = OffsetImage(escudo_img_2, zoom=0.15)
    ab_2 = AnnotationBbox(imagebox_2,
                          (1.15, 0.4),
                          frameon=False,
                          xycoords='axes fraction',
                          box_alignment=(0.5, 0))
    axs['title'].add_artist(ab_2)
else:
    print(f"Advertencia: No se encontró el archivo {escudo_path_2}")

# Modificar la segunda leyenda a la derecha del radar con letra más grande
second_legend_text = (
    "Min: minutos jugados en la temporada\n"
    "Err: Errores que desembocan en un tiro del oponente\n"
    "% Cmp.1: Pases cortos (de entre 5 y 15 yardas) completados\n"
    "% Cmp.2: Pases de distancia media (de entre 15 y 30 yardas) completados\n"
    "% Cmp.3: Pases largos (de más de 30 yardas) completados\n"
    "GC90: Goles en contra cada 90 minutos\n"
    "% Salvadas: Porcentaje de paradas\n"
    "PaC%: Porcentaje de porterías a cero\n"
    "% Salvadas.1: Porcentaje de penales parados\n"
    "PSxG+/-: Goles esperados menos los goles permitidos (los números positivos indican una mejor suerte o capacidad del portero para detener los disparos)\n"
    "Long. prom..1: Longitud media de los pases (en yardas)"
)

axs['radar'].text(
    x=1.15, y=0.5,
    s=second_legend_text,
    fontsize=14,
    fontproperties=robotto_thin.prop,
    ha='left',
    va='center',
    transform=axs['radar'].transAxes
)

# Mostrar el gráfico final con radar combinado
plt.show()

# Ruta donde se guardará la imagen
output_path = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\DEFENSA TFM\Imágenes radares comparación getafe"

# Guardar la figura como imagen JPG
output_file = os.path.join(output_path, "radar_comparacion_getafe.jpg")
fig.savefig(output_file, format='jpg', dpi=300, bbox_inches='tight')

print(f"Radar guardado exitosamente en: {output_file}")
