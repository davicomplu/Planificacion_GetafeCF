#David Soria vs nuevos fichajes

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re # Importado para usar expresiones regulares en la limpieza de nombres
import traceback # Para imprimir detalles de errores

# --- 1. Configuración Inicial ---
# !!! AJUSTA ESTAS RUTAS SEGÚN TU ARCHIVO Y CARPETA !!!
file_path = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\RESULTADOS COMPARACIÓN\PO. David Soria\APTOS. PO. David Soria.xlsx"
save_folder_path = r"C:\Users\david\OneDrive\Escritorio\MÁSTER\TFM\RESULTADOS COMPARACIÓN\PO. David Soria"

# --- Crear Carpeta y Verificar Archivo ---
try:
    os.makedirs(save_folder_path, exist_ok=True)
    print(f"Carpeta de guardado asegurada/creada en: {save_folder_path}")
except OSError as e:
    print(f"Error al crear la carpeta de guardado '{save_folder_path}': {e}")
    raise
if not os.path.exists(file_path):
    print(f"Error: No se encontró el archivo Excel en la ruta: {file_path}")
    raise FileNotFoundError(f"Archivo Excel no encontrado: {file_path}")
else:
    print(f"Archivo Excel encontrado en: {file_path}")

# --- Función sanitize_filename ---
def sanitize_filename(name):
    """Limpia un string para usarlo como nombre de archivo."""
    name = str(name) # Asegurarse de que es un string
    name = name.replace(' ', '_')
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = name.strip('.')
    # Evitar nombres vacíos después de la limpieza
    if not name:
        name = "nombre_invalido"
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
    if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip().lower() == 'final':
        final_row_index = index
        print(f"Encontrada fila 'Final' en el índice: {final_row_index} (basado en 0)")
        break
if final_row_index == -1:
    print("Error: No se encontró la fila que comienza con 'Final'. Revisa la primera columna del Excel.")
    raise ValueError("Fila 'Final' no encontrada.")

header_row_index = final_row_index + 1
print(f"Se usará la fila en el índice {header_row_index} como encabezado.")

try:
    df = pd.read_excel(file_path, header=header_row_index, sheet_name=0)
    print(f"\nLectura con encabezado (fila {header_row_index}) completada.")
    # print(f"Primeras filas leídas:\n{df.head()}")
    # print(f"Columnas detectadas: {df.columns.tolist()}")
except Exception as e:
    print(f"Error al leer el archivo Excel con el encabezado correcto (fila {header_row_index}): {e}")
    raise

original_columns = df.columns.tolist()
df.columns = [str(col).strip() for col in df.columns]
cleaned_columns = df.columns.tolist()
if original_columns != cleaned_columns:
    print("\n--- Nombres de columnas limpiados (quitando espacios) ---")
else:
    print("\n--- Nombres de columnas no necesitaron limpieza de espacios ---")

if 'Jugador' not in df.columns:
    print("\n¡ERROR CRÍTICO! La columna 'Jugador' NO existe después de la limpieza.")
    print(f"Columnas disponibles: {df.columns.tolist()}")
    raise KeyError("Columna 'Jugador' no encontrada.")
else:
    print("Columna 'Jugador' encontrada.")

initial_rows = len(df)
df = df.dropna(subset=['Jugador'])
df = df[df['Jugador'].astype(str).str.strip() != '']
rows_after_dropna_jugador = len(df)
print(f"Filtradas {initial_rows - rows_after_dropna_jugador} filas con 'Jugador' vacío o NaN.")
print(f"Número de filas con datos de jugador: {rows_after_dropna_jugador}")
if rows_after_dropna_jugador == 0:
      print("\nAdvertencia: No quedan filas válidas después de filtrar por 'Jugador'. El script no puede continuar.")
      raise ValueError("No hay datos de jugadores válidos para procesar.")


# --- 3. Identificar Columnas y Jugadores ---
# !!! ASEGÚRATE QUE ESTA LISTA ES CORRECTA Y COMPLETA !!!
excluded_cols = [
    'Jugador', 'Mín', 'TA', 'TR',
    'Liga', 'Equipo',
    'Valor de mercado', # Versión correcta
    'Valo de mercado',  # Errata común 1
    'Valor de marcado', # Errata común 2
    'Demarcación', 'Edad',
    'KPI Verde', 'KPI Clave Verde',
    'KPI Amarillo', # Versión correcta
    'KPI Amarrillo', # Errata común
    'Tipo', 'Evidencia',
    # Incluir explícitamente TODAS las Unnamed que no sean métricas
    'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21',
    'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24',  'Unnamed: 25', 'Unnamed: 26'
]
print(f"\nColumnas a excluir del radar (definidas en el script): {excluded_cols}")

all_cols = df.columns.tolist()
metric_cols = []
for col in all_cols:
    is_excluded = col in excluded_cols
    # Tratar cualquier columna que empiece con 'Unnamed:' como excluida, incluso si no está listada explícitamente
    is_unnamed = str(col).startswith('Unnamed:')
    is_jugador = col == 'Jugador'
    if not is_excluded and not is_unnamed and not is_jugador:
        metric_cols.append(col)

metric_cols = [m for m in metric_cols if m != 'Jugador' and not str(m).startswith('Unnamed:')] # Doble check

print(f"\nMétricas FINALES seleccionadas para el radar: {metric_cols}")
if not metric_cols:
     print("\nError CRÍTICO: No quedan métricas para el radar después de excluir columnas.")
     raise ValueError("No hay métricas válidas seleccionadas para graficar.")

# Crear df_radar solo con las columnas necesarias
valid_metric_cols = [col for col in metric_cols if col in df.columns]
if len(valid_metric_cols) != len(metric_cols):
    missing_cols = list(set(metric_cols) - set(valid_metric_cols))
    print(f"\nAdvertencia: Las siguientes métricas seleccionadas no se encontraron en el DataFrame: {missing_cols}")
    metric_cols = valid_metric_cols
if not metric_cols:
     print("\nError CRÍTICO: No quedan métricas válidas después de comprobar su existencia en el DataFrame.")
     raise ValueError("No hay métricas válidas finales para graficar.")

# Mantener todas las filas que pasaron el filtro de Jugador NaN
df_radar = df[['Jugador'] + metric_cols].copy()
# *** Importante: Resetear el índice aquí para tener índices únicos (0, 1, 2...)
# *** Esto será útil para diferenciar filas con el mismo nombre de jugador.
df_radar.reset_index(drop=True, inplace=True)
print(f"\nDataFrame 'df_radar' creado con {len(df_radar)} filas.")
print(f"Índice reseteado. Columnas: {df_radar.columns.tolist()}")


# --- 4. Conversión a Numérico y Manejo de NaNs ---
print("\n--- Convirtiendo métricas seleccionadas a tipo numérico ---")
# (El código de conversión es el mismo)
potential_numeric_errors = {}
try:
    for col in metric_cols:
        if pd.api.types.is_object_dtype(df_radar[col].dtype):
            df_radar[col] = df_radar[col].astype(str).str.replace(',', '.', regex=False)
            df_radar[col] = pd.to_numeric(df_radar[col], errors='coerce')
            if df_radar[col].isnull().any():
                 potential_numeric_errors[col] = "Valores no numéricos encontrados y convertidos a NaN."
        elif pd.api.types.is_numeric_dtype(df_radar[col].dtype):
             df_radar[col] = df_radar[col].astype(float)
        else:
             try:
                 df_radar[col] = pd.to_numeric(df_radar[col], errors='coerce')
                 if df_radar[col].isnull().any():
                     potential_numeric_errors[col] = "Valores no numéricos encontrados y convertidos a NaN."
             except Exception as conv_err:
                 potential_numeric_errors[col] = f"Error inesperado en conversión forzada: {conv_err}"

    print("Conversión inicial a numérico completada.")
    if potential_numeric_errors:
        print("\nDetalles de conversión a numérico (columnas con posibles problemas):")
        for col, msg in potential_numeric_errors.items():
            print(f"  - Columna '{col}': {msg}")

    print("\n--- Comprobando NaNs después de la conversión ---")
    nan_report = df_radar[metric_cols].isnull().sum()
    nan_columns = nan_report[nan_report > 0]
    nan_in_metrics = not nan_columns.empty

    if nan_in_metrics:
        print("\n¡Advertencia! Se encontraron valores NaN en las siguientes columnas de métricas:")
        print(nan_columns)
        rows_with_nan = df_radar[df_radar[metric_cols].isnull().any(axis=1)]
        print(f"\nFilas que contienen NaNs en columnas métricas (serán eliminadas):\n{rows_with_nan[['Jugador'] + nan_columns.index.tolist()]}") # Mostrar solo jugador y columnas con NaN

        print("\nSe eliminarán las filas que tengan NaN en CUALQUIERA de las columnas métricas seleccionadas.")
        rows_before_dropna_metrics = len(df_radar)
        df_radar = df_radar.dropna(subset=metric_cols)
        rows_after_dropna_metrics = len(df_radar)
        # *** Resetear índice de nuevo DESPUÉS de eliminar filas por NaN ***
        df_radar.reset_index(drop=True, inplace=True)
        print(f"\nSe eliminaron {rows_before_dropna_metrics - rows_after_dropna_metrics} filas debido a NaNs en métricas.")
        print(f"Quedan {len(df_radar)} filas válidas para normalizar y graficar.")
        if len(df_radar) == 0:
             print("\n¡Advertencia CRÍTICA! No quedan filas después de limpiar NaNs en métricas. No se pueden generar gráficos.")
             exit()
    else:
        print("\nNo se encontraron NaNs en las columnas métricas después de la conversión.")
        print(f"Se usarán las {len(df_radar)} filas para normalización y gráficos.")

except Exception as e:
    print(f"\nError CRÍTICO durante la conversión a numérico o limpieza de NaNs: {e}")
    traceback.print_exc()
    raise

# --- 5. Normalización Dinámica (Min-Max por columna) ---
df_normalized = pd.DataFrame()
data_ranges = {}

# *** Usar df_radar directamente que ahora contiene solo filas válidas ***
if not df_radar.empty and metric_cols:
    print("\n--- Normalizando datos (Min-Max por métrica para el grupo actual) ---")
    # Copiar Jugador e índice (opcional, pero puede ser útil) al nuevo DataFrame
    df_normalized = df_radar[['Jugador']].copy()

    print(f"Normalizando datos para {len(df_radar)} filas.")

    for col in metric_cols:
        min_val = df_radar[col].min()
        max_val = df_radar[col].max()
        data_ranges[col] = {'min': min_val, 'max': max_val}

        if max_val == min_val:
             df_normalized[col] = 0.0
             # print(f"  - Columna '{col}': Normalizado a 0.0 (Min=Max={min_val:.2f})") # Menos verboso
        else:
             df_normalized[col] = (df_radar[col] - min_val) / (max_val - min_val)
             # print(f"  - Columna '{col}': Normalizada (Min={min_val:.2f}, Max={max_val:.2f})") # Menos verboso

    print("\nNormalización completada.")
    # print(f"Datos DESPUÉS de normalizar (df_normalized):\n{df_normalized.head()}")

else:
    print("\n--- No se realizará normalización (No hay filas/métricas válidas) ---")
    exit() # Salir si no hay nada que normalizar


# --- 6. Preparación Ángulos para Gráficos ---
angles = []
if not df_radar.empty and metric_cols: # Basado en si tenemos datos y métricas
    print("\n--- Preparando ángulos para gráficos ---")
    num_vars = len(metric_cols)
    if num_vars > 0:
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1] # Cerrar el círculo
        print(f"Número de variables/métricas en el radar: {num_vars}")
    else:
        print("Error: No hay métricas para calcular ángulos.")
else:
    print("\n--- No se prepararán ángulos (faltan datos o métricas) ---")


# --- 7. Crear y Guardar Gráficos de Radar Individuales (Iterando por FILAS) ---
# *** CAMBIO CLAVE: Iterar por filas de df_normalized usando iterrows() ***
if not df_normalized.empty and angles:
    print(f"\n--- Generando y Guardando Gráficos Individuales ({len(df_normalized)} en total) ---")
    # Iterar por cada fila (índice y contenido de la fila)
    for index, row in df_normalized.iterrows():
        # Extraer el nombre del jugador de la fila actual
        player_name = row['Jugador']
        print(f"Procesando fila índice {index}, Jugador: {player_name}")

        try:
            # Extraer los datos normalizados de la fila actual para las columnas métricas
            player_data_normalized = row[metric_cols].tolist()

            # Comprobar NaN residual (poco probable, pero seguro)
            if pd.isna(player_data_normalized).any():
                 print(f"   - ¡Advertencia! Datos NaN residuales en fila índice {index} ({player_name}). Saltando gráfico.")
                 continue

            # Cerrar los datos para el gráfico
            player_data_closed = player_data_normalized + player_data_normalized[:1]

            # Crear figura y eje polar
            fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
            # Usar player_name para la etiqueta de la leyenda (aunque solo hay una línea aquí)
            ax.plot(angles, player_data_closed, linewidth=2, linestyle='solid', label=str(player_name))
            ax.fill(angles, player_data_closed, alpha=0.35)

            # Configurar ejes
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metric_cols, fontsize=9)
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

            # Eje Y (radial): Marcas SIN etiquetas numéricas
            ax.set_yticks(np.linspace(0, 1, 5))
            ax.set_yticklabels([])
            ax.set_ylim(0, 1.05)

            # Título
            plt.title(f'Radar de {player_name} (Fila {index})\n(Escala relativa al máximo del grupo por métrica)', size=15, y=1.15)
            plt.tight_layout()

            # Guardar el gráfico individual
            # *** CAMBIO CLAVE: Añadir índice al nombre de archivo para evitar sobrescrituras ***
            sanitized_player_name = sanitize_filename(player_name)
            filename = f"{sanitized_player_name}_idx{index}_Radar.jpg" # Añadir _idx{index}
            save_filepath = os.path.join(save_folder_path, filename)
            try:
                plt.savefig(save_filepath, format='jpg', dpi=300, bbox_inches='tight')
                print(f"   - Guardado: {save_filepath}")
            except Exception as save_e:
                print(f"   - Error al guardar el gráfico para fila {index} ({player_name}): {save_e}")

            plt.show()
            plt.close(fig)

        except Exception as e:
            print(f"   - Error general al procesar/graficar fila {index} ({player_name}): {e}")
            traceback.print_exc()
            if 'fig' in locals() and plt.fignum_exists(fig.number):
                 plt.close(fig)
            continue # Continuar con la siguiente fila
else:
     print("\n--- No se generarán gráficos individuales (faltan datos normalizados o ángulos) ---")


# --- 8. Crear y Guardar Gráfico de Radar Combinado (Iterando por FILAS) ---
# *** CAMBIO CLAVE: Condición basada en número de FILAS y iteración por filas ***
# Generar combinado si hay más de una FILA válida
if not df_normalized.empty and angles and len(df_normalized) > 1:
    print(f"\n--- Generando y Guardando Gráfico Combinado para {len(df_normalized)} entradas ---")
    try:
        fig_combined, ax_combined = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        cmap = plt.colormaps.get_cmap('tab10') # Usar 'tab20' o 'viridis' si hay muchos jugadores
        # Ajustar número de colores si es necesario
        num_entries = len(df_normalized)
        colors = [cmap(i % cmap.N) for i in range(num_entries)] # Colores basados en el número de filas
        plotted_entries_count = 0

        # Iterar por cada fila para añadirla al gráfico combinado
        for index, row in df_normalized.iterrows():
            player_name = row['Jugador'] # Nombre para la leyenda
            # Crear una etiqueta única para la leyenda si los nombres se repiten mucho
            # legend_label = f"{player_name} (Idx {index})" # Opción A: incluir índice
            legend_label = str(player_name) # Opción B: usar solo el nombre (puede haber duplicados en leyenda)

            try:
                player_data_normalized = row[metric_cols].tolist()

                if pd.isna(player_data_normalized).any():
                    print(f"   - Adv: Datos NaN en normalizados para fila {index} ({player_name}) en combinado. Saltando.")
                    continue

                player_data_closed = player_data_normalized + player_data_normalized[:1]
                # Usar el índice para seleccionar el color de forma consistente
                ax_combined.plot(angles, player_data_closed, linewidth=1.5, linestyle='solid', label=legend_label, color=colors[index])
                plotted_entries_count += 1
            except Exception as loop_e:
                 print(f"   - Error procesando fila {index} ({player_name}) en bucle combinado: {loop_e}")
                 continue

        if plotted_entries_count > 0:
            # Configurar ejes del combinado
            ax_combined.set_xticks(angles[:-1])
            ax_combined.set_xticklabels(metric_cols, fontsize=10)
            plt.setp(ax_combined.get_xticklabels(), rotation=30, ha="right")

            # Eje Y (radial): Marcas SIN etiquetas numéricas
            ax_combined.set_yticks(np.linspace(0, 1, 5))
            ax_combined.set_yticklabels([])
            ax_combined.set_ylim(0, 1.05)

            # Título y Leyenda
            plt.title('Comparativa Radar\n(Escala relativa al máximo del grupo por métrica)', size=18, y=1.15)
            # Ajustar tamaño de fuente y posición de leyenda si hay muchas entradas
            legend_fontsize = 9 if num_entries < 15 else 7 # Reducir fuente si hay muchas leyendas
            ax_combined.legend(loc='upper right', bbox_to_anchor=(1.40, 1.15), fontsize=legend_fontsize) # Ajustar posición si es necesario
            plt.tight_layout(rect=[0, 0, 0.78, 1]) # Ajustar layout para dar más espacio a la leyenda

            # Guardar el gráfico combinado
            combined_filename = "Comparacion_Radar_Normalizado_Todas_Filas.jpg"
            save_filepath_combined = os.path.join(save_folder_path, combined_filename)
            try:
                plt.savefig(save_filepath_combined, format='jpg', dpi=300, bbox_inches='tight')
                print(f"   - Guardado Gráfico Combinado: {save_filepath_combined}")
            except Exception as save_e:
                print(f"   - Error al guardar el gráfico combinado: {save_e}")

            plt.show()

        else:
             print("\nNo se dibujó ninguna entrada válida en el gráfico combinado.")

        if 'fig_combined' in locals() and plt.fignum_exists(fig_combined.number):
             plt.close(fig_combined)

    except Exception as e:
        print(f"\nError CRÍTICO general al generar/guardar el gráfico combinado: {e}")
        traceback.print_exc()
        if 'fig_combined' in locals() and plt.fignum_exists(fig_combined.number):
             plt.close(fig_combined)

elif len(df_normalized) == 1:
     print("\n--- No se generará gráfico combinado (Solo queda 1 fila válida) ---")
else: # Si no hay datos normalizados o ángulos
    print("\n--- No se generará gráfico combinado (faltan datos válidos o ángulos) ---")


print("\n--- Proceso Completado ---")