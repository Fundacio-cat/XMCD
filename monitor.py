# -*- coding: utf-8 -*-

import logging
import sys
import argparse
from utils.config import Config
from utils.utils import nom_sensor
from navegadors.navegador_chrome import ChromeNavegador
from navegadors.navegador_firefox import FirefoxNavegador
from cercadors.cercador_google import GoogleCercador
from cercadors.cercador_bing import BingCercador
from repository.repository import Repository

def parseja_arguments():
    parser = argparse.ArgumentParser(description='Agafa els paràmetres del fitxer json')
    parser.add_argument('-c', '--config', default='config.json', help='Ruta al fitxer de configuració. Per defecte és "config.json".')
    return parser.parse_args()

def inicia_base_dades(config: Config) -> Repository:
    try:
        repo = Repository(config)
        repo.connecta_bd()
        return repo
    except Exception as e:
        config.write_log(
            f"Error en la connexió a PostgreSQL: {e}", level=logging.ERROR)
        sys.exit(503)

def obtenir_sensor() -> str:
    sensor = nom_sensor()
    if not sensor:
        config.write_log(
            "No s'ha pogut obtenir el nom del sensor", level=logging.ERROR)
        sys.exit(1)
    return sensor

def crea_navegador(navegador: int, navegador_text: str, config: Config):

    # Retorna el navegador Chrome si 1
    if navegador == 1:
        return ChromeNavegador(config)

    # Retorna el navegador Firefox si 2
    elif navegador == 2:
        return FirefoxNavegador(config)

    # Si no està plantejat retorna un error
    else:
        config.write_log(f"Error: No existeix el navegador {navegador_text}", level=logging.ERROR)
        sys.exit(1)

def crea_cercador(cercador: int, cercador_text: str, config: Config):

    # Retorna Google si 1
    if cercador == 1:
        return GoogleCercador(config)

    # Retorna Bing si 2
    elif cercador == 2:
        return BingCercador(config)

    # Si no està plantejat retorna un error
    else:
        config.write_log(f"Error: No existeix el cercador {cercador_text}", level=logging.ERROR)
        sys.exit(1)

def executa_crawler(config: Config, cerca: str, id_cerca: int):
    try:
        resultats = config.cercador.guarda_resultats(cerca)
        logging.info(
            f"Guardant a la base de dades els resultats per la cerca {cerca}")
        for posicio, dades in resultats.items():
            logging.info(
                f"Guardant a la base de dades la posició {posicio}, amb el sensor {config.sensor}")
            repo.guarda_bd(
                id_cerca,
                posicio,
                dades.get('titol', ''),
                dades.get('url', ''),
                dades.get('description', ''),
                False
            )
    except Exception as e:
        config.write_log(
            f"Error en l'execució del crawler per la cerca {cerca}: {e}", level=logging.ERROR)


if __name__ == "__main__":
    args = parseja_arguments()
    # Carrega la configuració utilitzant el fitxer especificat o el fitxer per defecte
    config = Config.carrega_config(args.config)
    repo = inicia_base_dades(config)
    try:

        # Inici del sensor
        sensor = obtenir_sensor()
        config.set_repository(repo) # BD
        config.set_sensor(sensor)
        config.write_log(f"Sensor {sensor} iniciat correctament", level=logging.INFO)

        # Selecciona el navegador
        int_navegador = repo.selecciona_navegador()
        navegador_text = "Chrome" if int_navegador == 1 else "Firefox" if int_navegador == 2 else "Navegador desconegut"
        # Crea'l
        config.write_log(f"Creant el navegador {navegador_text} ...", level=logging.INFO)
        navegador = crea_navegador(int_navegador, navegador_text, config)
        config.set_navegador(navegador)
        config.write_log(f"Navegador {navegador_text} creat correctament", level=logging.INFO)

        # Selecciona el cercador
        int_cercador = repo.selecciona_cercador()
        cercador_text = "Google" if int_cercador == 1 else "Bing" if int_cercador == 2 else "Navegador desconegut"
        # Crea'l
        config.write_log(f"Creant el cercador {cercador_text} ...", level=logging.INFO)
        cercador = crea_cercador(int_cercador, cercador_text, config)
        config.set_cercador(cercador)
        config.write_log(f"Cercador {cercador_text} creat correctament", level=logging.INFO)

        # Selecciona el dispositiu? --> S'hauria de seleccionar abans del navegador per a definir les mides
        #int_cercador = repo.selecciona_cercador()
        #cercador_text = "Google" if int_cercador == 1 else "Bing" if int_cercador == 2 else "Navegador desconegut"
        # Crea'l
        #config.write_log(f"Creant el cercador {cercador_text} ...", level=logging.INFO)
        #cercador = crea_cercador(int_cercador, cercador_text, config)
        #config.set_cercador(cercador)
        #config.write_log(f"Cercador {cercador_text} creat correctament", level=logging.INFO)

        # Selecciona el accept_lang? --> S'hauria de seleccionar abans del cercador segur, potser abans del navegador? 
        #int_cercador = repo.selecciona_cercador()
        #cercador_text = "Google" if int_cercador == 1 else "Bing" if int_cercador == 2 else "Navegador desconegut"
        # Crea'l
        #config.write_log(f"Creant el cercador {cercador_text} ...", level=logging.INFO)
        #cercador = crea_cercador(int_cercador, cercador_text, config)
        #config.set_cercador(cercador)
        #config.write_log(f"Cercador {cercador_text} creat correctament", level=logging.INFO)

        id_cerca, cerca = repo.seguent_cerca(sensor)
        if cerca:
            config.write_log(f"Cerca a executar: {cerca}", level=logging.INFO)
            executa_crawler(config, cerca, id_cerca)
        else:
            config.write_log("No s'ha obtingut cap cerca",level=logging.WARNING)

    except Exception as e:
        config.write_log(f"Error durant l'execució: {e}", level=logging.ERROR)
        sys.exit(1)

    finally:
        # Intenta tancar el navegador i la connexió amb la base de dades, independentment de si hi ha hagut errors o no.
        try:
            navegador.tanca_navegador()
        except Exception as e:
            config.write_log(
                f"Error tancant el navegador: {e}", level=logging.ERROR)

        try:
            repo.close_connection()
        except Exception as e:
            config.write_log(
                f"Error tancant la connexió amb la BD: {e}", level=logging.ERROR)

        config.write_log("Crawler finalitzat", level=logging.INFO)
        sys.exit(0)
