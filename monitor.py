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

NAVEGADORS_PERMESOS = ["Chrome", "Firefox"]
CERCADORS_PERMESOS = ["Google", "Bing"]

navegador_firefox = None
navegador_chrome = None


def parseja_arguments():
    parser = argparse.ArgumentParser(
        description='Rebutja quin navegador i cercador utilitzarà per paràmetre')
    #parser.add_argument('navegador', choices=NAVEGADORS_PERMESOS, help='Quin navegador? Chrome / Firefox')
    parser.add_argument('cercador', choices=CERCADORS_PERMESOS,
                        help='Quin cercador? Google / Bing')
    parser.add_argument('-c', '--config', default='config.json',
                        help='Ruta al fitxer de configuració. Per defecte és "config.json".')
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

def crea_navegador(navegador_id: int, config: Config):
    if navegador_id == 1:
        config.write_log(f"Creant el navegador Chrome", level=logging.INFO)
        return ChromeNavegador(config) 
    else:
        config.write_log(f"Creant el navegador Firefox", level=logging.INFO)
        return FirefoxNavegador(config)
    
def crea_cercador(tipus: str, config: Config):
    if tipus not in CERCADORS_PERMESOS:
        config.write_log(
            f"El cercador {tipus} no està suportat", level=logging.ERROR)
        sys.exit(1)
    return GoogleCercador(config) if tipus == "Google" else BingCercador(config)


def executa_crawler(config: Config, cerca: str, id_cerca: int):
    try:
        resultats = config.cercador.guarda_resultats(cerca)
        logging.info(
            f"Guardant a la base de dades els resultats per la cerca {cerca}")
        for posicio, dades in resultats.items():
            logging.info(f"Guardant a la base de dades la posició {posicio}, amb el sensor {config.sensor}")
            repo.guarda_bd(
                id_cerca,
                posicio,
                dades.get('titol', ''),
                dades.get('url', ''),
                dades.get('description', ''),
                False
            )
    except Exception as e:
        config.write_log(f"Error en l'execució del crawler per la cerca {cerca}: {e}", level=logging.ERROR)


if __name__ == "__main__":
    args = parseja_arguments()
    # inicialitza configuració, base de dades, sensor, cercador i navegador
    # es posa tot a la configuració
    # Carrega la configuració utilitzant el fitxer especificat o el fitxer per defecte
    config = Config.carrega_config(args.config)
    repo = inicia_base_dades(config)
    try:

        ### Sensor ###
        sensor = obtenir_sensor()
        config.set_repository(repo)
        config.set_sensor(sensor)
        config.write_log(f"Sensor {sensor} iniciat correctament", level=logging.INFO)

        # Pregunta a quina navegador ha de realitzar la consulta
        config.write_log(f"Obtenint la cerca i el navegador", level=logging.INFO)
        id_cerca, cerca, navegador_id = repo.seguent_cerca_v2(sensor)

        ### Navegador ###
        navegador = crea_navegador(navegador_id, config)
        config.set_navegador(navegador)
        config.write_log(f"Navegador {navegador_id} creat correctament", level=logging.INFO)

        ### Cercador ###
        config.write_log(f"Creant el cercador {args.cercador} ...", level=logging.INFO)
        cercador = crea_cercador(args.cercador, config)
        config.set_cercador(cercador)
        config.write_log(f"Cercador {args.cercador} creat correctament", level=logging.INFO)

        ### Cerca ###
        if cerca:
            executa_crawler(config, cerca, id_cerca)
        else:
            config.write_log("No s'ha obtingut cap cerca", level=logging.WARNING)


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
