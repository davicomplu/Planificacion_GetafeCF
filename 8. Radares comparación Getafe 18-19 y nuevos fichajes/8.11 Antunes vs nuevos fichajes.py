#Antunes vs nuevos fichajes

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re # Importado para usar expresiones regulares en la limpieza de nombres

# --- 1. Configuración Inicial ---
# Ruta al archivo Excel
file_path = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\RESULTADOS COMPARACIÓN\LI. Vitorino Antunes\APTOS. LI. Vitorino Antunes.xlsx"
# Ruta donde se guardarán las imágenes JPG
save_folder_path = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\RESULTADOS COMPARACIÓN\LI. Vitorino Antunes"

# Crear la carpeta de destino si no existe
try:
    os.makedirs(save_folder_path, exist_ok=True)
    print(f"Carpeta de guardado asegurada/creada en: {save_folder_path}")
except OSError as e:
    print(f"Error al crear la carpeta de guardado '{save_folder_path}': {e}")
    # Podrías decidir detener el script si no se puede crear la carpeta
    raise

# Verificar si el archivo Excel existe
if not os.path.exists(file_path):
    print(f"Error: No se encontró el archivo Excel en la ruta: {file_path}")
    raise FileNotFoundError(f"Archivo Excel no encontrado: {file_path}")
else:
    print(f"Archivo Excel encontrado en: {file_path}")

# --- Función para limpiar nombres de archivo ---
def sanitize_filename(name):
    """Limpia un string para usarlo como nombre de archivo."""
    # Reemplazar espacios con guiones bajos
    name = name.replace(' ', '_')
    # Eliminar caracteres no válidos (manteniendo letras, números, _, -)
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    # Eliminar puntos al principio o final si los hubiera
    name = name.strip('.')
    # Truncar si es demasiado largo (opcional, pero bueno para algunos sistemas)
    # max_len = 100
    # if len(name) > max_len:
    #     name = name[:max_len]
    return name

# --- 2. Cargar y Preparar los Datos ---
print("\n--- Iniciando lectura del archivo Excel ---")
try:
    df_full = pd.read_excel(file_path, header=None, sheet_name=0)
    print("Lectura inicial (sin header) completada.")
except Exception as e:
    print(f"Error al leer el archivo Excel inicialmente: {e}")
    raise

final_row_index = -1
for index, row in df_full.iterrows():
    if pd.notna(row[0]) and str(row[0]).strip().lower() == 'final':
        final_row_index = index
        print(f"Encontrada fila 'Final' en el índice: {final_row_index} (basado en 0)")
        break

if final_row_index == -1:
    print("Error: No se encontró la fila que comienza con 'Final'.")
    raise ValueError("Fila 'Final' no encontrada.")

header_row_index = final_row_index + 1
print(f"Se usará la fila en el índice {header_row_index} como encabezado.")

try:
    df = pd.read_excel(file_path, header=header_row_index, sheet_name=0)
    print(f"\nLectura con encabezado (fila {header_row_index}) completada.")
    # print(f"Columnas leídas inicialmente: {df.columns.tolist()}") # Descomentar para debug
except Exception as e:
    print(f"Error al leer el archivo Excel con el encabezado correcto: {e}")
    raise

original_columns = df.columns.tolist()
df.columns = [str(col).strip() for col in df.columns]
cleaned_columns = df.columns.tolist()
if original_columns != cleaned_columns:
    print("\n--- Nombres de columnas limpiados (quitando espacios) ---")
    # print(f"Originales: {original_columns}") # Descomentar para debug
    # print(f"Limpiadas : {cleaned_columns}") # Descomentar para debug
else:
    print("\n--- Nombres de columnas no necesitaron limpieza de espacios ---")

if 'Jugador' not in df.columns:
    print("\n¡ERROR CRÍTICO! La columna 'Jugador' NO existe.")
    print(f"Columnas detectadas: {df.columns.tolist()}")
    raise KeyError("Columna 'Jugador' no encontrada.")
else:
    print("Columna 'Jugador' encontrada.")

initial_rows = len(df)
df = df.dropna(subset=['Jugador'])
df = df[df['Jugador'].astype(str).str.strip() != ''] # Asegurar que no sean strings vacíos
rows_after_dropna_jugador = len(df)
print(f"Filtradas {initial_rows - rows_after_dropna_jugador} filas con 'Jugador' vacío o NaN.")
print(f"Número de filas con datos de jugador: {rows_after_dropna_jugador}")

if rows_after_dropna_jugador == 0:
      print("\nAdvertencia: No quedan filas válidas después de filtrar por 'Jugador'.")
      # raise ValueError("No hay datos de jugadores válidos para procesar.") # Descomentar para detener

# --- 3. Identificar Columnas y Jugadores ---
excluded_cols = [
    'Jugador', 'Mín', 'TA', 'TR',
    'Liga', 'Equipo', 'Valor de mercado',
    'Demarcación', 'Edad',
    'KPI Verde', 'KPI Clave Verde', 'KPI Amarillo', 'Tipo',
    'Evidencia', 'Unnamed: 24',
    'Unnamed: 26' # Ajusta o añade más 'Unnamed: XX' si es necesario
]
print(f"\nColumnas a excluir del radar: {excluded_cols}")

all_cols = df.columns.tolist()
jugador_col_index = all_cols.index('Jugador')
metric_cols = [col for i, col in enumerate(all_cols)
               if i > jugador_col_index and col not in excluded_cols]

print(f"\nMétricas FINALES seleccionadas para el radar: {metric_cols}")

if not metric_cols:
     print("\nError: No quedan métricas para el radar después de excluir columnas.")
     raise ValueError("No hay métricas válidas seleccionadas para graficar.")

players = df['Jugador'].unique().tolist()
print(f"Jugadores únicos encontrados ({len(players)}): {players}")

df_radar = df[['Jugador'] + metric_cols].copy()

# --- Conversión a Numérico y Manejo de NaNs ---
print("\n--- Convirtiendo métricas seleccionadas a tipo numérico ---")
try:
    for col in metric_cols:
        if df_radar[col].dtype == 'object':
             df_radar[col] = df_radar[col].astype(str).str.replace(',', '.', regex=False)
        df_radar[col] = pd.to_numeric(df_radar[col], errors='coerce')
    print("Conversión inicial a numérico completada.")

    nan_in_metrics = df_radar[metric_cols].isnull().any().any()
    if nan_in_metrics:
        print("\nAdvertencia: Se encontraron valores NaN en las columnas de métricas.")
        print("Se eliminarán las filas que tengan NaN en CUALQUIERA de las columnas métricas.")
        rows_before_dropna_metrics = len(df_radar)
        df_radar = df_radar.dropna(subset=metric_cols)
        rows_after_dropna_metrics = len(df_radar)
        print(f"Se eliminaron {rows_before_dropna_metrics - rows_after_dropna_metrics} filas debido a NaNs en métricas.")
        players = df_radar['Jugador'].unique().tolist()
        print(f"Jugadores restantes después de limpiar NaNs en métricas ({len(players)}): {players}")
        if not players:
             print("\nAdvertencia CRÍTICA: No quedan jugadores después de limpiar NaNs en métricas.")
    else:
        print("No se encontraron NaNs en las columnas métricas después de la conversión.")

except Exception as e:
    print(f"Error durante la conversión a numérico o limpieza de NaNs: {e}")
    raise

# --- 4. Preparación para Gráficos de Radar ---
angles = []
if players and metric_cols:
    print("\n--- Preparando datos para gráficos ---")
    num_vars = len(metric_cols)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    print(f"Número de variables/métricas en el radar: {num_vars}")
else:
    print("\n--- No hay suficientes datos para preparar gráficos ---")

# --- 5. Crear y Guardar Gráficos de Radar Individuales ---
if players and angles:
    print("\n--- Generando y Guardando Gráficos Individuales ---")
    for player in players:
        print(f"Procesando jugador: {player}")
        try:
            player_data_series = df_radar.loc[df_radar['Jugador'] == player, metric_cols].iloc[0]
            player_data = player_data_series.tolist()

            if pd.isna(player_data).any():
                 print(f"   - Advertencia: Datos NaN residuales. Saltando gráfico y guardado.")
                 continue

            player_data_closed = player_data + player_data[:1]

            fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
            ax.plot(angles, player_data_closed, linewidth=2, linestyle='solid', label=player)
            ax.fill(angles, player_data_closed, alpha=0.35)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metric_cols, fontsize=9)
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
            ax.set_yticks(np.linspace(0, 1, 5))
            ax.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"], fontsize=9)
            ax.set_ylim(0, 1.05)
            plt.title(f'Radar de {player}', size=15, y=1.12)
            plt.tight_layout()

            # --- Guardar el gráfico individual ---
            sanitized_player_name = sanitize_filename(player)
            filename = f"{sanitized_player_name}_Radar.jpg"
            save_filepath = os.path.join(save_folder_path, filename)
            try:
                plt.savefig(save_filepath, format='jpg', dpi=300, bbox_inches='tight')
                print(f"   - Guardado: {save_filepath}")
            except Exception as save_e:
                print(f"   - Error al guardar el gráfico para {player}: {save_e}")
            # --- Fin Guardar ---

            plt.show() # Mostrar después de guardar
            plt.close(fig) # Cerrar la figura para liberar memoria

        except Exception as e:
            print(f"   - Error general al procesar/graficar para {player}: {e}")
            # Asegurarse de cerrar la figura si se creó pero hubo error antes de guardar/mostrar
            if 'fig' in locals() and plt.fignum_exists(fig.number):
                 plt.close(fig)
            continue
else:
     print("\n--- No se generarán gráficos individuales (faltan jugadores o métricas) ---")


# --- 6. Crear y Guardar Gráfico de Radar Combinado ---
if players and angles and len(players) > 0:
    print("\n--- Generando y Guardando Gráfico Combinado ---")
    try:
        fig_combined, ax_combined = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        cmap = plt.colormaps.get_cmap('tab10')
        colors = [cmap(i % cmap.N) for i in range(len(players))]
        plotted_players_count = 0

        for i, player in enumerate(players):
            player_data_series = df_radar.loc[df_radar['Jugador'] == player, metric_cols].iloc[0]
            player_data = player_data_series.tolist()
            if pd.isna(player_data).any():
                 # Ya se advirtió antes, no es necesario repetir aquí
                 continue
            player_data_closed = player_data + player_data[:1]
            ax_combined.plot(angles, player_data_closed, linewidth=1.5, linestyle='solid', label=player, color=colors[i])
            plotted_players_count += 1

        if plotted_players_count > 0:
            ax_combined.set_xticks(angles[:-1])
            ax_combined.set_xticklabels(metric_cols, fontsize=10)
            plt.setp(ax_combined.get_xticklabels(), rotation=30, ha="right")
            ax_combined.set_yticks(np.linspace(0, 1, 5))
            ax_combined.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"], fontsize=9)
            ax_combined.set_ylim(0, 1.05)
            plt.title('Comparativa Radar de Jugadores', size=18, y=1.12)
            ax_combined.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=9)
            plt.tight_layout(rect=[0, 0, 0.8, 1]) # Ajustar para leyenda

            # --- Guardar el gráfico combinado ---
            combined_filename = "Comparacion_Radar.jpg"
            save_filepath_combined = os.path.join(save_folder_path, combined_filename)
            try:
                plt.savefig(save_filepath_combined, format='jpg', dpi=300, bbox_inches='tight')
                print(f"   - Guardado: {save_filepath_combined}")
            except Exception as save_e:
                print(f"   - Error al guardar el gráfico combinado: {save_e}")
            # --- Fin Guardar ---

            plt.show() # Mostrar después de guardar

        else:
             print("No se dibujó ningún jugador válido en el gráfico combinado.")
             # No es necesario cerrar la figura si nunca se dibujó nada relevante o si no se creó

        # Cerrar la figura combinada después de guardar/mostrar
        if 'fig_combined' in locals() and plt.fignum_exists(fig_combined.number):
             plt.close(fig_combined)

    except Exception as e:
        print(f"Error general al generar/guardar el gráfico combinado: {e}")
        if 'fig_combined' in locals() and plt.fignum_exists(fig_combined.number):
             plt.close(fig_combined)

else:
    print("\n--- No se generará gráfico combinado (faltan jugadores válidos o métricas) ---")


print("\n--- Proceso Completado ---")