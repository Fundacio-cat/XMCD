# -*- coding: utf-8 -*-

import logging
import sys
import argparse
from utils.config import Config
from utils.utils import nom_sensor
from navegadors.navegador_camoufox import CamoufoxNavegador
from cercadors.cercador_google_camoufox import GoogleCercadorCamoufox
from repository.repository import Repository

# Aquest monitor utilitza exclusivament Camoufox

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
        config.write_log("No s'ha pogut obtenir el nom del sensor", level=logging.ERROR)
        sys.exit(1)
    return sensor

def crea_navegador(navegador_text: str, amplada: int, altura: int, config: Config):
    
    try:
        return CamoufoxNavegador(config, amplada, altura)

    # Si no està plantejat retorna un error
    except Exception as e:
        config.write_log(f"Error en la creació del navegador {navegador_text}: {e}", level=logging.ERROR)
        sys.exit(1)

def crea_cercador(cercador: int, cercador_text: str, config: Config):
    try:
        if cercador == 1:
            return GoogleCercadorCamoufox(config)
        else:
            config.write_log(f"Cercador {cercador_text} no suportat amb Camoufox", level=logging.ERROR)
            sys.exit(1)
    except Exception as e:
        config.write_log(f"Error en la creació del cercador {cercador_text}: {e}", level=logging.ERROR)
        sys.exit(1)

def executa_crawler(config: Config, cerca: str, id_cerca: int, navegador_text: str, int_mida: int):
    try:
        resultats = config.cercador.guarda_resultats(cerca, navegador_text)
        logging.info(f"Guardant a la base de dades els resultats per la cerca {cerca}")
        for posicio, dades in resultats.items():
            logging.info(f"Guardant a la base de dades la posició {posicio}, amb el sensor {config.sensor}")
            repo.guarda_bd(
                id_cerca,
                posicio,
                dades.get('titol', ''),
                dades.get('url', ''),
                dades.get('description', ''),
                False,
                int_mida
            )
    except Exception as e:
        config.write_log(f"Error en l'execució del crawler per la cerca {cerca}: {e}", level=logging.ERROR)

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

        # Agafa les mides del dispositiu
        int_mida, amplada, altura = repo.selecciona_mides()
        mida_text = "mida de mòbil" if int_mida == 1 else "mida de sobretaula" if int_mida == 2 else "mida desconeguda"
        config.write_log(f"S'utilitzarà la {mida_text} ...", level=logging.INFO)

        # Selecciona el navegador
        navegador_text = "Camoufox"
        # Crea'l
        config.write_log(f"Creant el navegador {navegador_text} ...", level=logging.INFO)
        navegador = crea_navegador(navegador_text, amplada, altura, config)
        config.set_navegador(navegador)
        config.write_log(f"Navegador {navegador_text} creat correctament", level=logging.INFO)

        # Selecciona el cercador
        int_cercador = repo.selecciona_cercador()
        cercador_text = "Google" if int_cercador == 1 else "Cercador desconegut"

        # Crea'l
        config.write_log(f"Creant el cercador {cercador_text} ...", level=logging.INFO)
        cercador = crea_cercador(int_cercador, cercador_text, config)
        config.set_cercador(cercador)
        config.write_log(f"Cercador {cercador_text} creat correctament", level=logging.INFO)

        id_cerca, cerca = repo.seguent_cerca(sensor)
        if cerca:
            config.write_log(f"Cerca a executar: {cerca}", level=logging.INFO)
            executa_crawler(config, cerca, id_cerca, navegador_text, int_mida)
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
            config.write_log(f"Error tancant el navegador: {e}", level=logging.ERROR)

        try:
            repo.close_connection()
        except Exception as e:
            config.write_log(
                f"Error tancant la connexió amb la BD: {e}", level=logging.ERROR)

        config.write_log("Crawler finalitzat", level=logging.INFO)
        sys.exit(0)
