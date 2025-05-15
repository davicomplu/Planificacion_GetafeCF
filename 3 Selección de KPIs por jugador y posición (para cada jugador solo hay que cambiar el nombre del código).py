#Selección de KPIs por jugador y posición.

import pandas as pd

# Definir rutas de los archivos CSV
ruta_base = 'C:/Users/david/LIGAS/Getafe 18-19/Escalado_Getafe 18-19/'
archivos = {
    'Estadística estándar': 'Estadística estándar.csv',
    'Marcadores y partidos': 'Marcadores y partidos.csv',
    'Porteros': 'Porteros.csv',
    'Portería avanzada': 'Portería avanzada.csv',
    'Tiros': 'Tiros.csv',
    'Pases': 'Pases.csv',
    'Tipos de pases': 'Tipos de pases.csv',
    'Creación de goles y tiros': 'Creación de goles y tiros.csv',
    'Acciones defensivas': 'Acciones defensivas.csv',
    'Posesión del balón': 'Posesión del balón.csv',
    'Tiempo jugado': 'Tiempo jugado.csv',
    'Estadísticas diversas': 'Estadísticas diversas.csv'
}

# Crear un dataframe vacío para almacenar todos los datos
all_data_df = pd.DataFrame()

# Función para extraer datos de un archivo CSV
def extraer_datos(archivo, columnas):
    df = pd.read_csv(ruta_base + archivo)
    if 'Jugador' in df.columns and 'Jorge Molina' in df['Jugador'].values:
        return df[df['Jugador'] == 'Jorge Molina'][['Jugador'] + columnas]
    else:
        # Crear un dataframe con un mensaje cuando Damián Suárez no aparece
        return pd.DataFrame({'Jugador': ['No aparece Jorge Molina'], **{columna: ['N/A'] for columna in columnas}})

# Extraer datos de todas las tablas y combinarlos
for tabla, archivo in archivos.items():
    if tabla == 'Estadística estándar':
        columnas = ['Mín', 'TA', 'TR', 'G-TP.1', 'Ast']
    elif tabla == 'Marcadores y partidos':
        columnas = []  # No se especificaron columnas para esta tabla
    elif tabla == 'Porteros':
        columnas = []  # No se especificaron columnas para esta tabla
    elif tabla == 'Portería avanzada':
        columnas = []  # No se especificaron columnas para esta tabla
    elif tabla == 'Tiros':
        columnas = ['TalArc/90', 'G/TalArc', 'npxG']  # No se especificaron columnas para esta tabla
    elif tabla == 'Pases':
        columnas = ['% Cmp.1', '% Cmp.2', '% Cmp.3']  # No se especificaron columnas para esta tabla
    elif tabla == 'Tipos de pases':
        columnas = []  # No se especificaron columnas para esta tabla
    elif tabla == 'Creación de goles y tiros':
        columnas = ['SCA90', 'GCA90']  # No se especificaron columnas para esta tabla
    elif tabla == 'Acciones defensivas':
        columnas = ['Tkl%', 'Tkl+Int']
    elif tabla == 'Posesión del balón':
        columnas = ['Exitosa%']  # No se especificaron columnas para esta tabla
    elif tabla == 'Tiempo jugado':
        columnas = []  # No se especificaron columnas para esta tabla
    elif tabla == 'Estadísticas diversas':
        columnas = ['% de ganados']
    
    if columnas:  # Solo procesar tablas con columnas especificadas
        datos = extraer_datos(archivo, columnas)
        all_data_df = pd.concat([all_data_df, datos], ignore_index=True)

# Guardar el dataframe en un archivo CSV
ruta_guardar = 'C:/Users/david/LIGAS/Getafe 18-19/Escalado_Getafe 18-19/Jugadores/DC. Jorge Molina/Jorge Molina.csv'
all_data_df.to_csv(ruta_guardar, index=False)

# Confirmación
print(f"El dataframe ha sido guardado en: {ruta_guardar}")
