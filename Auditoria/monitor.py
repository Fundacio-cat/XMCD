# -*- coding: utf-8 -*-

################# IMPORTS #################

# Mòduls
from selenium_helpers import cerca_cerca
from postgres import connecta_bd, guarda_bd
from utils import nom_sensor

# Globals
import logging
import sys
import argparse

import json
with open('/home/catalanet/XMCD/Auditoria/config.json', 'r') as file:
    globals = json.load(file)

### GLOBALS ###

directori_Imatges = globals['directori_Imatges']
fitxer_logs = globals['fitxer_logs']

# Fitxer de logs
logging.basicConfig(filename=fitxer_logs, level=logging.DEBUG)

### ARGUMENTS ###
parser = argparse.ArgumentParser(description='Rep quin navegador i cercador utilitzarà per paràmetre')
parser.add_argument('navegador', type=str, help='Quin navegador? Chrome / Firefox')
parser.add_argument('cercador',  type=str, help='Quin cercador? Google / Bing')
args = parser.parse_args()

### BASE DE DADES ###

if not connecta_bd():
    logging.error(f"El dispositiu no té connexió a internet")
    sys.exit(503)
else:
    conn, cursor = connecta_bd()

### SENSOR ###

# Cerca el nom de la màquina
if nom_sensor() is not None:
    sensor = nom_sensor()
else:
    logging.error(f"No s'ha agafat el nom de sensor")
    sys.exit(1)

### FUNCIONS ###

# Navegador
if args.navegador == 'Chrome':
    # Fem l'import de les funcions de Chrome
    from chromeUtils import inicia_navegador
elif args.navegador == 'Firefox':
    from firefoxUtils import inicia_navegador
else:
    logging.error(f"El navegador {args.navegador} no està acceptat")
    sys.exit(2)

# Cercador
if args.cercador == 'Google':
    # Fem l'import de les funcions de Chrome
    from googleUtils import inicia_cercador, guarda_resultats, executa_cerca
else:
    logging.error(f"El navegador {args.navegador} no està acceptat")
    sys.exit(2)

### NAVEGADOR ###

# Iniciem el navegador
navegador, browser = inicia_navegador(cursor)

# Control errors del navegador
if browser == 3:
    logging.error(f"No s'ha pogut agafar correctament el User Agent amb {args.navegador}")
    sys.exit(3)
elif browser == 10:
    logging.error(f"No s'ha pogut iniciar correctament el driver del navegador {args.navegador}")
    sys.exit(10)

### CERCADOR ###

# Iniciem el cercador
cercador = inicia_cercador(browser)

# Control errors del cercador
if browser == 20:
    logging.error(f"No s'ha pogut iniciar correctament el cercador {args.cercador}")
    sys.exit(20)
elif browser == 21:
    logging.error(f"No s'han pogut acceptar les cookies del cercador {args.cercador}")
    sys.exit(21)

### CERCA ###

# Obté la cadena a buscar al cercador
int_cerca, cerca = cerca_cerca(cursor, sensor)

# Executem la cerca
browser = executa_cerca(browser, cerca)
if browser == 22:
    logging.error(f"No s'ha pogut realitzar la cerca {cerca} del cercador {args.cercador}")
    sys.exit(22)

### RESULTATS ###

# Obté els resultats
logging.info(f"Cercant els resultats de {cerca}...")

resultats = guarda_resultats(browser, directori_Imatges, navegador, sensor, cerca)

# Guarda els resultats
logging.info(f"Guardant a la base de dades els resultats")
for posicio, dades in resultats.items():
    titol = dades['titol']
    url = dades['url']
    descripcio = dades['description']
    llengua = "--"

    guarda_bd(conn, cursor, sensor, navegador, cercador, int_cerca, posicio, titol, url, descripcio, llengua)

conn.close()

logging.info(f"Crawler finalitzat correctament")
sys.exit(0)
