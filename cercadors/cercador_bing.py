import os
import logging
from cercadors.cercador_base import CercadorBase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from datetime import datetime
import logging
from utils.selenium_helpers import cerca_dades_bing
from utils.utils import assegura_directori_existeix
from time import sleep

from os.path import sep
from datetime import datetime
from os import remove

class BingCercador(CercadorBase):
    def __init__(self, config):
        super().__init__(config)

    def inicia_cercador(self):

        id_cercador_db = 2

        try:
            # Aqui arriba
            acceptat = False
            self.browser.get("https://www.bing.com/?setlang=ca")
            sleep(5)
            boto_cookies = self.browser.find_element(By.ID, "bnp_btn_accept")
            if boto_cookies:
                boto_cookies.click()
                acceptat=True

            if not acceptat:
                self.config.write_log("No s'ha pogut acceptar les cookies de Bing", level=logging.ERROR)
                raise ValueError("No s'han pogut acceptar les cookies de Google")
        except Exception as e:
            try:
                # Intenta obtenir la informació de la versió del navegador i del driver
                browser_version = self.browser.capabilities['browserVersion']
                driver_version = self.browser.capabilities['chrome']['chromedriverVersion'].split(' ')[
                    0]
                error_message = f"Error iniciant el cercador: " \
                                f"Versió del navegador Chrome: {browser_version}\n" \
                                f"Versió del ChromeDriver: {driver_version}"
            except WebDriverException:
                # Si no es pot obtenir la informació de la versió, utilitza un missatge genèric
                error_message = f"Error iniciant el cercador: {e}\n" \
                                "No s'ha pogut obtenir la informació de la versió del navegador o del driver."

            self.config.write_log(error_message, level=logging.ERROR)
            raise ValueError(error_message) from e

        return id_cercador_db

    def composa_nom_captura(self, cerca, suffix=None):
        # Obtenim el directori actual del fitxer de configuració
        current_directory = self.config.current_directory
        # Eliminem els espais del nom de cerca i obtenim el format de data-hora
        cerca_sense_espais = cerca.replace(' ', '_')
        data_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Composem el nom del fitxer amb os.path.join
        nom_base = f"{current_directory}{sep}{self.config.directori_Imatges}{sep}{self.config.sensor}_Google_{cerca_sense_espais}_{data_hora_actual}"
        # Comprovem si hi ha un sufix i l'afegim si existeix
        if suffix:
            nom_captura = f"{nom_base}_{suffix}.png"
        else:
            nom_captura = f"{nom_base}.png"

        assegura_directori_existeix(os.path.dirname(nom_captura))

        return nom_captura

    def guarda_resultats(self, cerca):
        navegador = self.config.navegador
        browser = self.browser

        resultats = {}
        resultats_desats = 1

        sleep(self.config.temps_espera_cerques)

        # Fem la cerca
        try:
            textarea = browser.find_element(By.ID, "sb_form_q")
            textarea.send_keys(Keys.CONTROL, 'a')
            textarea.send_keys(Keys.DELETE)
            textarea.send_keys(cerca + Keys.ENTER)
        except:
            raise ValueError("No s'ha pogut fer la cerca")


        while resultats_desats <= 10:
            sleep(self.config.temps_espera_cerques)
            nom_captura_1 = self.composa_nom_captura(cerca)
            nom_captura_2 = self.composa_nom_captura(cerca, suffix="2a")

            navegador.captura_pantalla(nom_captura_1)
            taula_resultats = browser.find_element(By.ID, "b_results")
            resultats_cerca = taula_resultats.find_elements(By.XPATH, '//h2[a]')

            for resultat in resultats_cerca:
                if resultats_desats < 11:
                    guardar, link, titol, description = cerca_dades_bing(resultat)

                    if guardar: 
                        resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                        resultats_desats += 1

            # Valora la 2a pàgina
            if resultats_desats < 11:
                sleep(self.config.temps_espera_cerques)
                pagina_2 = browser.find_element(By.XPATH, '//a[@aria-label="Pàgina 2"]')
                pagina_2.click()
                sleep(self.config.temps_espera_cerques)
                navegador.captura_pantalla(nom_captura_2)

                taula_resultats = browser.find_element(By.ID, "b_results")
                resultats_cerca = taula_resultats.find_elements(By.XPATH, '//h2[a]')

                for resultat in resultats_cerca:
                    if resultats_desats < 11:
                        guardar, link, titol, description = cerca_dades_bing(resultat)

                        if guardar: 
                            resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                            resultats_desats += 1

            logging.info(f"Valorant els resultats de {cerca}...")

            if resultats_desats < 11:
                logging.info(f"No s'han obtingut els 10 resultats de {cerca}...")
                remove(nom_captura_1)

                try:
                    remove(nom_captura_2)
                except:
                    pass

                finally:
                    resultats_desats = 1
                    resultats = {}
                    browser.get("https://www.bing.com/?setlang=ca")
                    sleep(self.config.temps_espera_cerques)
                    textarea = browser.find_element(By.TAG_NAME, value='textarea')
                    textarea.send_keys(cerca + Keys.ENTER)
                    sleep(self.config.temps_espera_processos)
                    logging.info(f"Torna a realitzar la cerca")

            else:
                return resultats
