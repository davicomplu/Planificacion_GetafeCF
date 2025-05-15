#Mapas de acciones (pases J2 y J4)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import numpy as np

# --- Configuración ---
# Lista de rutas a los archivos Excel que quieres combinar
excel_file_paths = [
    r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\Eventing\Getafe 18-19\Excel\eventing-Jornada 2-2025-02-28.xlsx",
    r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\Eventing\Getafe 18-19\Excel\eventing-Jornada 4-2025-02-28.xlsx"
    # Puedes añadir más rutas aquí si es necesario
]

output_image_directory = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\Eventing\Getafe 18-19\Excel\Pases_J2_J4_Combinados"
team_of_interest = "Getafe CF"
players_of_interest = [
    "Antunes", "D. Suarez", "D. Dakonam", "David Soria",
    "M. Dmitrovic", "M. Arambarri", "L. Cabrera",  "N. Maksimovic"
]

# --- Dimensiones del Campo (Se determinarán dinámicamente después de cargar todos los datos) ---
FIELD_LENGTH_X = 100 # Valor inicial, se actualizará
FIELD_WIDTH_Y = 68   # Valor inicial, se actualizará

# --- Parámetros de Visualización ---
INVERT_Y_AXIS = True
LENGTH_INCLUDES_HEAD = False
COLOR_SUCCESSFUL = "blue"
COLOR_UNSUCCESSFUL = "red"
COLOR_OTHER = "grey"
FIELD_VIEW_MARGIN_X = 1.5
FIELD_VIEW_MARGIN_Y = 1.5
EDGE_THRESHOLD = 1.0

os.makedirs(output_image_directory, exist_ok=True)

# --- Cargar y Combinar Datos de Múltiples Archivos ---
all_data_frames = []
required_cols_check = ["teamName", "type", "name", "x", "y", "endX", "endY", "outcomeType"] # Columnas mínimas

for file_path in excel_file_paths:
    try:
        df_single_file = pd.read_excel(file_path)
        print(f"Archivo cargado: {file_path}, {len(df_single_file)} filas.")

        # Verificar columnas en este archivo individual
        if not all(col in df_single_file.columns for col in required_cols_check):
            missing_in_file = [col for col in required_cols_check if col not in df_single_file.columns]
            print(f"ADVERTENCIA: Faltan columnas {missing_in_file} en {file_path}. Omitiendo este archivo.")
            continue # Saltar al siguiente archivo

        all_data_frames.append(df_single_file)
    except Exception as e:
        print(f"Error al leer el archivo {file_path}: {e}")

if not all_data_frames:
    print("No se cargaron datos de ningún archivo. Terminando.")
    exit()

# Concatenar todos los DataFrames
df_full_combined = pd.concat(all_data_frames, ignore_index=True)
print(f"Total de filas combinadas de {len(all_data_frames)} archivos: {len(df_full_combined)}")

# --- Análisis de Rango Global sobre DATOS COMBINADOS ---
print("\n--- Análisis Global de Coordenadas (Todos los Archivos Combinados) ---")
coord_cols_analysis = ['x', 'y', 'endX', 'endY']
df_analysis = df_full_combined.copy()
for col in coord_cols_analysis:
    df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')

all_x_coords = pd.concat([df_analysis['x'], df_analysis['endX']]).dropna()
all_y_coords = pd.concat([df_analysis['y'], df_analysis['endY']]).dropna()

min_x_data_global, max_x_data_global = (0, 100)
min_y_data_global, max_y_data_global = (0, 68)

if not all_x_coords.empty:
    min_x_data_global = all_x_coords.min()
    max_x_data_global = all_x_coords.max()
    print(f"Rango X en datos combinados: Mín={min_x_data_global:.2f}, Máx={max_x_data_global:.2f}")
else: print("No se encontraron datos X válidos en los archivos combinados.")

if not all_y_coords.empty:
    min_y_data_global = all_y_coords.min()
    max_y_data_global = all_y_coords.max()
    print(f"Rango Y en datos combinados: Mín={min_y_data_global:.2f}, Máx={max_y_data_global:.2f}")
else: print("No se encontraron datos Y válidos en los archivos combinados.")

# Actualizar las dimensiones del campo con los máximos globales
# (Asumiendo que el origen del campo es (0,0) o que los mínimos son >= 0)
# Si los mínimos son negativos, la lógica del origen del campo se vuelve más compleja
FIELD_LENGTH_X = np.ceil(max_x_data_global) if not all_x_coords.empty else 100
FIELD_WIDTH_Y = np.ceil(max_y_data_global) if not all_y_coords.empty else 68
print(f"Dimensiones del campo ajustadas a: Largo={FIELD_LENGTH_X}, Ancho={FIELD_WIDTH_Y}")
if min_x_data_global < -EDGE_THRESHOLD or min_y_data_global < -EDGE_THRESHOLD : # Un pequeño umbral para mínimos negativos
    print(f"ADVERTENCIA: Se detectaron coordenadas mínimas negativas significativas (X:{min_x_data_global:.2f}, Y:{min_y_data_global:.2f}).")
    print("El campo se dibuja desde (0,0). Si el origen visual debe ser diferente, se requieren más ajustes.")
print("----------------------------------------------------------------------\n")


# --- Filtrado y Preparación sobre el DataFrame Combinado ---
df_team = df_full_combined[df_full_combined["teamName"] == team_of_interest].copy()
if df_team.empty: print(f"No se encontraron datos para el equipo '{team_of_interest}' en los datos combinados."); exit()

df_passes_team_combined = df_team[df_team["type"] == "Pass"].copy()
if df_passes_team_combined.empty: print(f"No se encontraron pases para el equipo '{team_of_interest}' en los datos combinados."); exit()

# Aplicar transformaciones al DataFrame combinado de pases
for col in coord_cols_analysis:
    df_passes_team_combined[col] = pd.to_numeric(df_passes_team_combined[col], errors='coerce')
df_passes_team_combined['name'] = df_passes_team_combined['name'].astype(str)
df_passes_team_combined['outcomeType'] = df_passes_team_combined['outcomeType'].astype(str)
df_passes_team_combined['outcomeType_cleaned'] = df_passes_team_combined['outcomeType'].str.strip().str.lower()


# --- Función para Dibujar Campo (sin cambios respecto a la versión anterior) ---
def draw_pitch_final(ax, field_len, field_w, margin_x, margin_y,
                     pitch_color="#2E7D32", line_color="white"):
    ax.add_patch(patches.Rectangle((0, 0), field_len, field_w, facecolor=pitch_color, zorder=0))
    ax.plot([0, field_len], [0, 0], color=line_color, zorder=1)
    ax.plot([0, field_len], [field_w, field_w], color=line_color, zorder=1)
    ax.plot([0, 0], [0, field_w], color=line_color, zorder=1)
    ax.plot([field_len, field_len], [0, field_w], color=line_color, zorder=1)
    ax.plot([field_len/2, field_len/2], [0, field_w], color=line_color, zorder=1)
    pa_l = 16.5*(field_len/100.0); pa_w = 40.3*(field_w/68.0)
    sa_l = 5.5*(field_len/100.0); sa_w = 18.3*(field_w/68.0)
    ax.add_patch(patches.Rectangle((0,(field_w-pa_w)/2),pa_l,pa_w,fill=False,edgecolor=line_color,zorder=1))
    ax.add_patch(patches.Rectangle((0,(field_w-sa_w)/2),sa_l,sa_w,fill=False,edgecolor=line_color,zorder=1))
    ax.add_patch(patches.Rectangle((field_len-pa_l,(field_w-pa_w)/2),pa_l,pa_w,fill=False,edgecolor=line_color,zorder=1))
    ax.add_patch(patches.Rectangle((field_len-sa_l,(field_w-sa_w)/2),sa_l,sa_w,fill=False,edgecolor=line_color,zorder=1))
    cc_r = 9.15*(field_len/100.0)
    ax.add_patch(patches.Circle((field_len/2,field_w/2),cc_r,edgecolor=line_color,facecolor="none",lw=1,zorder=1))
    ax.add_patch(patches.Circle((field_len/2,field_w/2),0.3*(field_len/100.0),color=line_color,zorder=1))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0 - margin_x, field_len + margin_x)
    ax.set_ylim(0 - margin_y, field_w + margin_y)
    ax.set_aspect('equal', adjustable='box')

# --- Iterar por Jugador y Generar Gráficos (usando df_passes_team_combined) ---
active_players_in_combined_data = df_passes_team_combined['name'].str.strip().unique()
print(f"Jugadores con pases para {team_of_interest} en datos combinados: {sorted(list(active_players_in_combined_data))}")

for player_name_raw in players_of_interest:
    player_name = player_name_raw.strip()
    if player_name not in active_players_in_combined_data:
        # print(f"Jugador '{player_name}' no encontrado en datos combinados. Omitiendo.")
        continue

    # Filtrar del DataFrame combinado de pases
    df_player_passes = df_passes_team_combined[
        (df_passes_team_combined["name"].str.strip() == player_name) &
        df_passes_team_combined[coord_cols_analysis].notna().all(axis=1) &
        (df_passes_team_combined['outcomeType_cleaned'].notna()) &
        (df_passes_team_combined['outcomeType_cleaned'] != '') &
        (df_passes_team_combined['outcomeType_cleaned'] != 'nan')
    ].copy()

    if df_player_passes.empty:
        # print(f"No pases válidos para {player_name} en datos combinados (después de filtros).")
        continue
    print(f"Procesando {len(df_player_passes)} pases para: {player_name} (de datos combinados)")

    fig_width_inches = 11
    fig_height_inches = fig_width_inches * ((FIELD_WIDTH_Y + 2*FIELD_VIEW_MARGIN_Y) / (FIELD_LENGTH_X + 2*FIELD_VIEW_MARGIN_X))
    fig, ax = plt.subplots(figsize=(fig_width_inches, fig_height_inches))
    
    # Usar las dimensiones del campo determinadas dinámicamente
    draw_pitch_final(ax, FIELD_LENGTH_X, FIELD_WIDTH_Y, FIELD_VIEW_MARGIN_X, FIELD_VIEW_MARGIN_Y)

    for i, (index, row) in enumerate(df_player_passes.iterrows()):
        x_start_data, y_start_data = row["x"], row["y"]
        x_end_data, y_end_data = row["endX"], row["endY"]
        outcome_cleaned = row["outcomeType_cleaned"]

        x_start_plot = x_start_data
        x_end_plot = x_end_data

        if INVERT_Y_AXIS:
            y_start_plot = FIELD_WIDTH_Y - y_start_data
            y_end_plot = FIELD_WIDTH_Y - y_end_data
        else:
            y_start_plot = y_start_data
            y_end_plot = y_end_data

        color = COLOR_OTHER
        if outcome_cleaned == "successful": color = COLOR_SUCCESSFUL
        elif outcome_cleaned == "unsuccessful": color = COLOR_UNSUCCESSFUL

        dx = x_end_plot - x_start_plot
        dy = y_end_plot - y_start_plot
        pass_length_plot = np.sqrt(dx**2 + dy**2)

        if pass_length_plot < 0.1: continue

        scale_ref = FIELD_LENGTH_X / 100.0
        base_head_width = 1.5 * scale_ref
        base_head_length = 2.0 * scale_ref
        base_arrow_width = 0.3 * scale_ref
        current_head_width = base_head_width
        current_head_length = base_head_length
        current_arrow_width = base_arrow_width
        if pass_length_plot < (5 * scale_ref):
            reduction_factor = pass_length_plot / (5 * scale_ref)
            current_head_width = max(0.2 * scale_ref, base_head_width * reduction_factor)
            current_head_length = max(0.3 * scale_ref, base_head_length * reduction_factor)
            current_arrow_width = max(0.1 * scale_ref, base_arrow_width * reduction_factor)
        
        is_on_bottom_edge_y = (y_end_data <= EDGE_THRESHOLD)
        is_on_top_edge_y = (y_end_data >= FIELD_WIDTH_Y - EDGE_THRESHOLD)
        is_on_left_edge_x = (x_end_plot <= EDGE_THRESHOLD)
        is_on_right_edge_x = (x_end_plot >= FIELD_LENGTH_X - EDGE_THRESHOLD)
        is_on_any_edge = is_on_bottom_edge_y or is_on_top_edge_y or is_on_left_edge_x or is_on_right_edge_x
        
        draw_head = True
        if is_on_any_edge:
            current_head_width *= 0.3
            current_head_length *= 0.3
        
        current_head_width = max(0.01, current_head_width) if draw_head else 0
        current_head_length = max(0.01, current_head_length) if draw_head else 0
        current_arrow_width = max(0.05, current_arrow_width)

        if draw_head:
            ax.arrow(x_start_plot, y_start_plot, dx, dy,
                     head_width=current_head_width, head_length=current_head_length,
                     fc=color, ec=color, length_includes_head=LENGTH_INCLUDES_HEAD,
                     width=current_arrow_width, zorder=2)
        else:
             ax.plot([x_start_plot, x_end_plot], [y_start_plot, y_end_plot], 
                     color=color, linewidth=current_arrow_width * 2, 
                     zorder=2, solid_capstyle='round')

    ax.set_title(f"Pases de {player_name} ({team_of_interest}) - Campo {FIELD_LENGTH_X:.0f}x{FIELD_WIDTH_Y:.0f}", fontsize=12)
    safe_player_name = "".join(c if c.isalnum() else "_" for c in player_name)
    output_filename = f"Pases_{safe_player_name}_Campo{int(FIELD_LENGTH_X)}x{int(FIELD_WIDTH_Y)}.png"
    output_filepath = os.path.join(output_image_directory, output_filename)

    try:
        plt.savefig(output_filepath, bbox_inches='tight', dpi=200)
        print(f"Gráfico guardado: {output_filepath}")
    except Exception as e_save:
        print(f"Error al guardar el gráfico para {player_name}: {e_save}")
    plt.close(fig)

print("\nProceso completado.")