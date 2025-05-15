#Extracción de datos de los jugadores de los equipos de la Ligue 1 (para cada equipo solo cambio el nombre del equipo en el código) (FBREF)


import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Configuración del navegador
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

# Lista de ligas con URLs, nombres y códigos
ligas = [
    ('https://fbref.com/es/equipos/69236f98/Estadisticas-de-Angers', 'Ligue 1', '13'),
]

# Información de las tablas a extraer
tablas_info = {
    'Estadística estándar': {
        'xpath': '//*[@id="stats_standard_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', 'PJ', 'Titular', 'Mín', '90 s', 'Gls.', 'Ass', 'G+A', 'G-TP', 'TP', 'TPint', 'TA', 'TR', 'xG', 'npxG', 'xAG', 'npxG+xAG', 'PrgC', 'PrgP', 'PrgR', 'Gls.', 'Ast', 'G+A', 'G-TP', 'G+A-TP', 'xG', 'xAG', 'xG+xAG', 'npxG', 'npxG+xAG', 'Partidos', 'Enlace'
        ],
    },
    'Marcadores y partidos': {
        'xpath': '//*[@id="matchlogs_for"]',
        'headers': [
            'Fecha', 'Hora', 'Comp', 'Ronda', 'Día', 'Sedes', 'Resultado', 'GF', 'GC', 'Adversario', 'xG', 'xGA', 'Pos.', 'Asistencia', 'Capitán', 'Formación', 'Formación del oponente', 'Árbitro', 'Informe del partido', 'Notas'
        ],
    },
    'Porteros': {
        'xpath': '//*[@id="stats_keeper_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', 'PJ', 'Titular', 'Mín', '90 s', 'GC', 'GC90', 'DaPC', 'Salvadas', '% Salvadas', 'PG', 'PE', 'PP', 'PaC', 'PaC%', 'TPint', 'PD', 'PD', 'PC', '% Salvadas', 'Partidos'
        ],
    },
    'Portería avanzada': {
        'xpath': '//*[@id="stats_keeper_adv_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'GC', 'PD', 'TL', 'TE', 'GC', 'PSxG', 'PSxG/SoT', 'PSxG+/-', '/90', 'Cmp', 'Int.', '% Cmp', 'Att (GK)', 'TI', '%deLanzamientos', 'Long. prom.', 'Int.', '%deLanzamientos', 'Long. prom.', 'Opp', 'Stp', '% de Stp', 'Núm. de OPA', 'Núm. de OPA/90', 'DistProm.', 'Partidos'
        ],
    },
    'Tiros': {
        'xpath': '//*[@id="stats_shooting_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Gls.', 'Dis', 'DaP', '% de TT', 'T/90', 'TalArc/90', 'G/T', 'G/TalArc', 'Dist', 'FK', 'TP', 'TPint', 'xG', 'npxG', 'npxG/Sh', 'G-xG', 'np:G-xG', 'Partidos'
        ],
    },
    'Pases': {
        'xpath': '//*[@id="stats_passing_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Cmp', 'Int.', '% Cmp', 'Dist. tot.', 'Dist. prg.', 'Cmp', 'Int.', '% Cmp', 'Cmp', 'Int.', '% Cmp', 'Cmp', 'Int.', '% Cmp', 'Ass', 'xAG', 'xA', 'A-xAG', 'PC', '1/3', 'PPA', 'CrAP', 'PrgP', 'Partidos'
        ],
    },
    'Tipos de pases': {
        'xpath': '//*[@id="stats_passing_types_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Int.', 'Balón vivo', 'Balón muerto', 'FK', 'PL', 'Camb.', 'Pcz', 'Lanz.', 'SE', 'Dentro', 'Fuera', 'Rect.', 'Cmp', 'PA', 'Bloqueos', 'Partidos'
        ],
    },
    'Creación de goles y tiros': {
        'xpath': '//*[@id="stats_gca_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'ACT', 'SCA90', 'PassLive', 'PassDead', 'HASTA', 'Dis', 'FR', 'Def', 'ACG', 'GCA90', 'PassLive', 'PassDead', 'HASTA', 'Dis', 'FR', 'Def', 'Partidos'
        ],
    },
    'Acciones defensivas': {
        'xpath': '//*[@id="stats_defense_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Tkl', 'TklG', '3.º def.', '3.º cent.', '3.º ataq.', 'Tkl', 'Att', 'Tkl%', 'Pérdida', 'Bloqueos', 'Dis', 'Pases', 'Int', 'Tkl+Int', 'Desp.', 'Err', 'Partidos'
        ],
    },
    'Posesión del balón': {
        'xpath': '//*[@id="stats_possession_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Toques', 'Def. pen.', '3.º def.', '3.º cent.', '3.º ataq.', 'Ataq. pen.', 'Balón vivo', 'Att', 'Succ', 'Exitosa%', 'Tkld', 'Tkld%', 'Transportes', 'Dist. tot.', 'Dist. prg.', 'PrgC', '1/3', 'TAP', 'Errores de control', 'Des', 'Rec', 'PrgR', 'Partidos'
        ],
    },
    'Tiempo jugado': {
        'xpath': '//*[@id="stats_playing_time_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', 'PJ', 'Mín', 'Mn/PJ', '% min', '90 s', 'Titular', 'Mn/arranque', 'Compl', 'Sup', 'Mn/Sust', 'Partidos como sustituto', 'PPP', 'onG', 'onGA', '+/-', '+/-90', 'Dentro-Fuera', 'onxG', 'onxGA', 'xG+/-', 'xG+/-90', 'Dentro-Fuera', 'Partidos'
        ],
    },
    'Estadísticas diversas': {
        'xpath': '//*[@id="stats_misc_13"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'TA', 'TR', '2a amarilla', 'Fls', 'FR', 'PA', 'Pcz', 'Int', 'TklG', 'Penal ejecutado', 'Penal concedido', 'GC', 'Recup.', 'Ganados', 'Perdidos', '% de ganados', 'Partidos'
        ],
    },
    'La Liga': {
        'xpath': '//*[@id="results2024-2025131_overall"]',
        'headers': [
            'RL', 'Equipo', 'PJ', 'PG', 'PE', 'PP', 'GF', 'GC', 'DG', 'Pts', 'Pts/PJ', 'xG', 'xGA', 'xGD', 'xGD/90', 'Últimos 5', 'Asistencia', 'Máximo Goleador del Equipo', 'Portero', 'Notas'
        ],
    }
}

# Función genérica para extraer tablas
def extraer_tabla(xpath, headers):
    table = driver.find_element(By.XPATH, xpath)
    outerHTML = table.get_attribute("outerHTML")
    soup = BeautifulSoup(outerHTML, 'html.parser')

    # Extraer filas y datos de cada equipo
    rows = []
    for row in soup.find_all('tr', attrs={"data-row": True}):
        cells = row.find_all(['th', 'td'])
        row_data = []
        link = None
        for cell in cells:
            anchor = cell.find('a')
            if anchor and 'href' in anchor.attrs:
                link = anchor['href']
            row_data.append(cell.get_text())
        if link:
            row_data.append(link)
        rows.append(row_data)

    df = pd.DataFrame(rows, columns=headers)
    return df
    







#PARA OBTENER PERMISOS DE CHROME DEL LA WEB A LA QUE ESTAMOS ENTRANDO

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-infobars')
options.add_argument('--disable-notifications')
driver = webdriver.Chrome(options=options)








#MÁS PERMISOS

for url, league_name, table_code in ligas:
    driver.get(url)
    time.sleep(5)  # Espera a que la página cargue completamente (puedes ajustar el tiempo según sea necesario)
    
    for table_name, table_info in tablas_info.items():
        xpath = table_info['xpath']
        headers = table_info['headers']
        try:
            df = extraer_tabla(xpath, headers)
            # Guardar el DataFrame en un archivo CSV o procesar los datos como desees
            df.to_csv(f'{league_name}_{table_name}.csv', index=False)
            print(f'Tabla {table_name} extraída y guardada.')
        except Exception as e:
            print(f'Error al extraer la tabla {table_name}: {str(e)}')







#PARA EXTRAER BIEN LOS DATOS

def extraer_tabla(xpath, headers):
    table = driver.find_element(By.XPATH, xpath)
    outerHTML = table.get_attribute("outerHTML")
    soup = BeautifulSoup(outerHTML, 'html.parser')

    # Extraer filas y datos de cada equipo
    rows = []
    for row in soup.find_all('tr', attrs={"data-row": True}):
        cells = row.find_all(['th', 'td'])
        row_data = []
        link = None
        for cell in cells:
            anchor = cell.find('a')
            if anchor and 'href' in anchor.attrs:
                link = anchor['href']
            row_data.append(cell.get_text())
        if link:
            row_data.append(link)
        rows.append(row_data)

    # Alinear automáticamente las columnas de los datos extraídos con los headers
    max_columns = len(headers)
    aligned_rows = []
    for row in rows:
        if len(row) > max_columns:
            row = row[:max_columns]
        while len(row) < max_columns:
            row.append('')
        aligned_rows.append(row)

    df = pd.DataFrame(aligned_rows, columns=headers)
    return df

# Iterar sobre todas las tablas
for nombre_tabla, info in tablas_info.items():
    try:
        df = extraer_tabla(info['xpath'], info['headers'])
        print(f'Tabla "{nombre_tabla}" extraída y guardada:')
        print(df.head())  # Mostrar las primeras filas para verificar
    except Exception as e:
        print(f'Error al extraer la tabla "{nombre_tabla}": {e}')











#PARA GUARDAR TODAS LAS TABLAS EN ARCHIVOS CSV

import os

# Crear los directorios si no existen
base_dir = 'Ligue 1/Angers'
if not os.path.exists(base_dir):
    os.makedirs(base_dir)

def extraer_tabla(xpath, headers):
    table = driver.find_element(By.XPATH, xpath)
    outerHTML = table.get_attribute("outerHTML")
    soup = BeautifulSoup(outerHTML, 'html.parser')

    # Extraer filas y datos de cada equipo
    rows = []
    for row in soup.find_all('tr', attrs={"data-row": True}):
        cells = row.find_all(['th', 'td'])
        row_data = []
        link = None
        for cell in cells:
            anchor = cell.find('a')
            if anchor and 'href' in anchor.attrs:
                link = anchor['href']
            row_data.append(cell.get_text())
        if link:
            row_data.append(link)
        rows.append(row_data)

    # Alinear automáticamente las columnas de los datos extraídos con los headers
    max_columns = len(headers)
    aligned_rows = []
    for row in rows:
        if len(row) > max_columns:
            row = row[:max_columns]
        while len(row) < max_columns:
            row.append('')
        aligned_rows.append(row)

    df = pd.DataFrame(aligned_rows, columns=headers)
    return df

# Iterar sobre todas las tablas y guardarlas como archivos CSV en el directorio correcto
for nombre_tabla, info in tablas_info.items():
    try:
        df = extraer_tabla(info['xpath'], info['headers'])
        print(f'Tabla "{nombre_tabla}" extraída y guardada:')
        print(df.head())  # Mostrar las primeras filas para verificar

        # Guardar el DataFrame como archivo CSV en el directorio especificado
        output_path = os.path.join(base_dir, f'{nombre_tabla}.csv')
        df.to_csv(output_path, index=False)
        print(f'Tabla "{nombre_tabla}" guardada en {output_path}')
    except Exception as e:
        print(f'Error al extraer la tabla "{nombre_tabla}": {e}')