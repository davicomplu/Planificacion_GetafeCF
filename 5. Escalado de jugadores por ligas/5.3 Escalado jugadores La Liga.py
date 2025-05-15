#Escalado jugadores La Liga (para cada equipo solo cambio el nombre del equipo en el código)


import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Ruta de la carpeta que contiene los archivos CSV
carpeta = 'C:\\Users\\david\\LIGAS\\La Liga\\Alavés'
carpeta_salida = os.path.join(carpeta, 'Escalado_Alavés')

# Crear la carpeta de salida si no existe
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Diccionario de archivos y sus columnas a escalar
archivos_y_columnas = {
    "Estadística estándar.csv": ["PJ", "Titular", "Mín", "90 s", "Gls.", "Ass", "G+A", "G-TP", "TP", "TPint", "TA", "TR", "xG", "npxG", "xAG", "npxG+xAG", "PrgC", "PrgP", "PrgR", "Gls.", "Ast", "G+A", "G-TP", "G+A-TP", "xG", "xAG", "xG+xAG", "npxG", "npxG+xAG"],
    "Porteros.csv": ["PJ", "Titular", "Mín", "90 s", "GC", "GC90", "DaPC", "Salvadas", "% Salvadas", "PG", "PE", "PP", "PaC", "PaC%", "TPint", "PD", "PD", "PC", "% Salvadas"],
    "Portería avanzada.csv": ["90 s", "GC", "PD", "TL", "TE", "GC", "PSxG", "PSxG/SoT", "PSxG+/-", "/90", "Cmp", "Int.", "% Cmp", "Att (GK)", "TI", "%deLanzamientos", "Long. prom.", "Int.", "%deLanzamientos", "Long. prom.", "Opp", "Stp", "% de Stp", "Núm. de OPA", "Núm. de OPA/90", "DistProm."],
    "Tiros.csv": ["90 s", "Gls.", "Dis", "DaP", "% de TT", "T/90", "TalArc/90", "G/T", "G/TalArc", "Dist", "FK", "TP", "TPint", "xG", "npxG", "npxG/Sh", "G-xG", "np:G-xG"],
    "Pases.csv": ["90 s", "Cmp", "Int.", "% Cmp", "Dist. tot.", "Dist. prg.", "Cmp.1", "Int..1", "% Cmp.1", "Cmp.2", "Int..2", "% Cmp.2", "Cmp.3", "Int..3", "% Cmp.3", "Ass", "xAG", "xA", "A-xAG", "PC", "1/3", "PPA", "CrAP", "PrgP"],
    "Tipos de pases.csv": ["90 s", "Int.", "Balón vivo", "Balón muerto", "FK", "PL", "Camb.", "Pcz", "Lanz.", "SE", "Dentro", "Fuera", "Rect.", "Cmp", "PA", "Bloqueos"],
    "Creación de goles y tiros.csv": ["90 s", "ACT", "SCA90", "PassLive", "PassDead", "HASTA", "Dis", "FR", "Def", "ACG", "GCA90", "PassLive", "PassDead", "HASTA", "Dis", "FR", "Def"],
    "Acciones defensivas.csv": ["90 s", "Tkl", "TklG", "3.º def.", "3.º cent.", "3.º ataq.", "Tkl", "Att", "Tkl%", "Pérdida", "Bloqueos", "Dis", "Pases", "Int", "Tkl+Int", "Desp.", "Err"],
    "Posesión del balón.csv": ["90 s", "Toques", "Def. pen.", "3.º def.", "3.º cent.", "3.º ataq.", "Ataq. pen.", "Balón vivo", "Att", "Succ", "Exitosa%", "Tkld", "Tkld%", "Transportes", "Dist. tot.", "Dist. prg.", "PrgC", "1/3", "TAP", "Errores de control", "Des", "Rec", "PrgR"],
    "Tiempo jugado.csv": ["PJ", "Mín", "Mn/PJ", "% min", "90 s", "Titular", "Mn/arranque", "Compl", "Sup", "Mn/Sust", "Partidos como sustituto", "PPP", "onG", "onGA", "+/-", "+/-90", "Dentro-Fuera", "onxG", "onxGA", "xG+/-", "xG+/-90", "Dentro-Fuera"],
    "Estadísticas diversas.csv": ["90 s", "TA", "TR", "2a amarilla", "Fls", "FR", "PA", "Pcz", "Int", "TklG", "Penal ejecutado", "Penal concedido", "GC", "Recup.", "Ganados", "Perdidos", "% de ganados"]
}

# Verificar los archivos en la carpeta
archivos_encontrados = os.listdir(carpeta)
print(f"Archivos encontrados en la carpeta '{carpeta}': {archivos_encontrados}")

# Función para escalar un DataFrame usando Min-Max Scaler
def escalar_dataframe(df, columnas_numericas):
    scaler = MinMaxScaler()
    df_escalado = df.copy()
    for columna in columnas_numericas:
        if df[columna].dtype == 'object':
            # Convertir a numérico y llenar NaN temporalmente
            df_escalado[columna] = pd.to_numeric(df[columna].str.replace(',', '').str.replace('+', '').str.replace('-', ''), errors='coerce')
        else:
            df_escalado[columna] = pd.to_numeric(df[columna], errors='coerce')
        
        mask_nan = df_escalado[columna].isna()
        df_escalado[columna] = df_escalado[columna].fillna(-1)  # Valor temporal para NaN

        # Escalar los datos y restaurar NaN
        df_escalado[columna] = scaler.fit_transform(df_escalado[[columna]])
        df_escalado.loc[mask_nan, columna] = None  # Restaurar NaN
        df_escalado[columna] = df_escalado[columna].round(2)  # Redondear a las centésimas
    
    return df_escalado

# Procesar cada archivo en la carpeta
for archivo, columnas_numericas in archivos_y_columnas.items():
    ruta_archivo = os.path.join(carpeta, archivo)
    
    # Verificar si el archivo existe antes de procesarlo
    if not os.path.exists(ruta_archivo):
        print(f"Archivo no encontrado: {ruta_archivo}")
        continue
    
    df = pd.read_csv(ruta_archivo)

    # Excluir las últimas dos filas del DataFrame
    df_sin_ultimas = df.iloc[:-2].copy()

    # Aplicar el escalado min-max a las columnas numéricas
    df_escalado = escalar_dataframe(df_sin_ultimas, columnas_numericas)

    # Añadir las últimas dos filas sin modificar al DataFrame escalado
    df_ultimas = df.iloc[-2:].copy()

    # Eliminar columnas vacías o todas nulas antes de la concatenación
    df_escalado = df_escalado.dropna(how='all', axis=1)
    df_ultimas = df_ultimas.dropna(how='all', axis=1)

    df_final = pd.concat([df_escalado, df_ultimas])

    # Generar la ruta para el archivo de salida
    ruta_salida = os.path.join(carpeta_salida, archivo)
    
    # Guardar el DataFrame final en la carpeta de salida
    df_final.to_csv(ruta_salida, index=False)

    print(f"Archivo procesado y guardado exitosamente en '{ruta_salida}'")

print("Todos los archivos han sido procesados y guardados correctamente.")
