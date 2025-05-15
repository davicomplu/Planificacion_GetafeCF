#Extracción de datos de los jugadores de los equipos de la 2ª división inglesa (Championship PL) (para cada equipo solo cambio el nombre del equipo en el código) (FBREF)


import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Configuración del navegador
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-infobars')
options.add_argument('--disable-notifications')
driver = webdriver.Chrome(options=options)

# Lista de ligas con URLs, nombres y códigos
ligas = [
    ('https://fbref.com/es/equipos/5bfb9659/Estadisticas-de-Leeds-United', "Championship", "10"),
    ('https://fbref.com/es/equipos/1df6b87e/Estadisticas-de-Sheffield-United', "Championship", "10"),
    ('https://fbref.com/es/equipos/943e8050/Estadisticas-de-Burnley', "Championship", "10"),
    ('https://fbref.com/es/equipos/8ef52968/Estadisticas-de-Sunderland', "Championship", "10"),
    ('https://fbref.com/es/equipos/60c6b05f/Estadisticas-de-West-Bromwich-Albion', "Championship", "10"),
    ('https://fbref.com/es/equipos/e090f40b/Estadisticas-de-Blackburn-Rovers', "Championship", "10"),
    ('https://fbref.com/es/equipos/f7e3dfe9/Estadisticas-de-Coventry-City', "Championship", "10"),
    ('https://fbref.com/es/equipos/93493607/Estadisticas-de-Bristol-City', "Championship", "10"),
    ('https://fbref.com/es/equipos/2abfe087/Estadisticas-de-Watford', "Championship", "10"),
    ('https://fbref.com/es/equipos/1c781004/Estadisticas-de-Norwich-City', "Championship", "10"),
    ('https://fbref.com/es/equipos/7f59c601/Estadisticas-de-Middlesbrough', "Championship", "10"),
    ('https://fbref.com/es/equipos/e3c537a1/Estadisticas-de-Millwall', "Championship", "10"),
    ('https://fbref.com/es/equipos/bba7d733/Estadisticas-de-Sheffield-Wednesday', "Championship", "10"),
    ('https://fbref.com/es/equipos/a757999c/Estadisticas-de-Queens-Park-Rangers', "Championship", "10"),
    ('https://fbref.com/es/equipos/22df8478/Estadisticas-de-Preston-North-End', "Championship", "10"),
    ('https://fbref.com/es/equipos/fb10988f/Estadisticas-de-Swansea-City', "Championship", "10"),
    ('https://fbref.com/es/equipos/76ffc013/Estadisticas-de-Portsmouth', 'Championship', '24'),
    ('https://fbref.com/es/equipos/604617a2/Estadisticas-de-Oxford-United', 'Championship', '24'),
    ('https://fbref.com/es/equipos/75fae011/Estadisticas-de-Cardiff-City', "Championship", "10"),
    ('https://fbref.com/es/equipos/17892952/Estadisticas-de-Stoke-City', "Championship", "10"),
    ('https://fbref.com/es/equipos/bd8769d1/Estadisticas-de-Hull-City', "Championship", "10"),
    ('https://fbref.com/es/equipos/32a1480e/Estadisticas-de-Plymouth-Argyle', "Championship", "10"),
    ('https://fbref.com/es/equipos/26ab47ee/Estadisticas-de-Derby-County', 'Championship', '24'),
    ('https://fbref.com/es/equipos/e297cd13/Estadisticas-de-Luton-Town', 'Championship', '24'),
]

# Información de las tablas a extraer
tablas_info = {
    'Estadística estándar': {
        'xpath': '//*[@id="stats_standard_10"]',
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
        'xpath': '//*[@id="stats_keeper_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', 'PJ', 'Titular', 'Mín', '90 s', 'GC', 'GC90', 'DaPC', 'Salvadas', '% Salvadas', 'PG', 'PE', 'PP', 'PaC', 'PaC%', 'TPint', 'PD', 'PD', 'PC', '% Salvadas', 'Partidos'
        ],
    },
    'Portería avanzada': {
        'xpath': '//*[@id="stats_keeper_adv_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'GC', 'PD', 'TL', 'TE', 'GC', 'PSxG', 'PSxG/SoT', 'PSxG+/-', '/90', 'Cmp', 'Int.', '% Cmp', 'Att (GK)', 'TI', '%deLanzamientos', 'Long. prom.', 'Int.', '%deLanzamientos', 'Long. prom.', 'Opp', 'Stp', '% de Stp', 'Núm. de OPA', 'Núm. de OPA/90', 'DistProm.', 'Partidos'
        ],
    },
    'Tiros': {
        'xpath': '//*[@id="stats_shooting_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Gls.', 'Dis', 'DaP', '% de TT', 'T/90', 'TalArc/90', 'G/T', 'G/TalArc', 'Dist', 'FK', 'TP', 'TPint', 'xG', 'npxG', 'npxG/Sh', 'G-xG', 'np:G-xG', 'Partidos'
        ],
    },
    'Pases': {
        'xpath': '//*[@id="stats_passing_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Cmp', 'Int.', '% Cmp', 'Dist. tot.', 'Dist. prg.', 'Cmp', 'Int.', '% Cmp', 'Cmp', 'Int.', '% Cmp', 'Cmp', 'Int.', '% Cmp', 'Ass', 'xAG', 'xA', 'A-xAG', 'PC', '1/3', 'PPA', 'CrAP', 'PrgP', 'Partidos'
        ],
    },
    'Tipos de pases': {
        'xpath': '//*[@id="stats_passing_types_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Int.', 'Balón vivo', 'Balón muerto', 'FK', 'PL', 'Camb.', 'Pcz', 'Lanz.', 'SE', 'Dentro', 'Fuera', 'Rect.', 'Cmp', 'PA', 'Bloqueos', 'Partidos'
        ],
    },
    'Creación de goles y tiros': {
        'xpath': '//*[@id="stats_gca_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'ACT', 'SCA90', 'PassLive', 'PassDead', 'HASTA', 'Dis', 'FR', 'Def', 'ACG', 'GCA90', 'PassLive', 'PassDead', 'HASTA', 'Dis', 'FR', 'Def', 'Partidos'
        ],
    },
    'Acciones defensivas': {
        'xpath': '//*[@id="stats_defense_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Tkl', 'TklG', '3.º def.', '3.º cent.', '3.º ataq.', 'Tkl', 'Att', 'Tkl%', 'Pérdida', 'Bloqueos', 'Dis', 'Pases', 'Int', 'Tkl+Int', 'Desp.', 'Err', 'Partidos'
        ],
    },
    'Posesión del balón': {
        'xpath': '//*[@id="stats_possession_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'Toques', 'Def. pen.', '3.º def.', '3.º cent.', '3.º ataq.', 'Ataq. pen.', 'Balón vivo', 'Att', 'Succ', 'Exitosa%', 'Tkld', 'Tkld%', 'Transportes', 'Dist. tot.', 'Dist. prg.', 'PrgC', '1/3', 'TAP', 'Errores de control', 'Des', 'Rec', 'PrgR', 'Partidos'
        ],
    },
    'Tiempo jugado': {
        'xpath': '//*[@id="stats_playing_time_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', 'PJ', 'Mín', 'Mn/PJ', '% min', '90 s', 'Titular', 'Mn/arranque', 'Compl', 'Sup', 'Mn/Sust', 'Partidos como sustituto', 'PPP', 'onG', 'onGA', '+/-', '+/-90', 'Dentro-Fuera', 'onxG', 'onxGA', 'xG+/-', 'xG+/-90', 'Dentro-Fuera', 'Partidos'
        ],
    },
    'Estadísticas diversas': {
        'xpath': '//*[@id="stats_misc_10"]',
        'headers': [
            'Jugador', 'País', 'Posc', 'Edad', '90 s', 'TA', 'TR', '2a amarilla', 'Fls', 'FR', 'PA', 'Pcz', 'Int', 'TklG', 'Penal ejecutado', 'Penal concedido', 'GC', 'Recup.', 'Ganados', 'Perdidos', '% de ganados', 'Partidos'
        ],
    },
    'Série A, Série A': {
        'xpath': '//*[@id="results2024-2025101_overall"]',
        'headers': [
            'RL', 'Equipo', 'PJ', 'PG', 'PE', 'PP', 'GF', 'GC', 'DG', 'Pts', 'Pts/PJ', 'xG', 'xGA', 'xGD', 'xGD/90', 'Últimos 5', 'Asistencia', 'Máximo Goleador del Equipo', 'Portero', 'Notas'
        ],
    }
}

# Función para extraer el nombre del equipo de la URL
def get_team_name(url):
    return url.split('Estadisticas-de-')[-1].replace('-', ' ')

# Crear los directorios si no existen
for url, _, _ in ligas:
    team_name = get_team_name(url)
    team_dir = os.path.join('Equipos', team_name)
    if not os.path.exists(team_dir):
        os.makedirs(team_dir)

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

# Iterar sobre todas las ligas y tablas
for url, league_name, table_code in ligas:
    driver.get(url)
    time.sleep(5)  # Espera a que la página cargue completamente

    team_name = get_team_name(url)
    team_dir = os.path.join('Equipos', team_name)

    for nombre_tabla, info in tablas_info.items():
        try:
            df = extraer_tabla(info['xpath'], info['headers'])
            print(f'Tabla "{nombre_tabla}" extraída para {team_name}:')
            print(df.head())  # Mostrar las primeras filas para verificar

            # Guardar el DataFrame como archivo CSV en el directorio del equipo
            output_path = os.path.join(team_dir, f'{nombre_tabla}.csv')
            df.to_csv(output_path, index=False)
            print(f'Tabla "{nombre_tabla}" guardada en {output_path}')
        except Exception as e:
            print(f'Error al extraer la tabla "{nombre_tabla}" para {team_name}: {e}')

driver.quit()
