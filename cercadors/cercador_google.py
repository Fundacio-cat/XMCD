import os
import logging
from cercadors.cercador_base import CercadorBase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from datetime import datetime
import logging
from utils.selenium_helpers import cerca_dades
from utils.utils import assegura_directori_existeix
from time import sleep

from os.path import sep
from datetime import datetime
from os import remove


class GoogleCercador(CercadorBase):

    def inicia_cercador(self):
        # Configura el valor de self.navegador com a 1 (Chrome)
        id_cercador_db = 1
        try:
            acceptat = False
            self.browser.get('https://www.google.com')
            buttons = self.browser.find_elements(By.XPATH, '//button')
            for button in buttons:
                try:
                    if button.find_element(By.XPATH, './/div[contains(text(), "Accepta-ho tot")]'):
                        button.click()
                        acceptat = True
                        break  # Afegeix un break aquí per sortir del bucle un cop acceptat
                except NoSuchElementException:
                    pass
            if not acceptat:
                self.config.write_log(
                    "No s'ha pogut acceptar les cookies de Google", level=logging.ERROR)
                raise ValueError(
                    "No s'han pogut acceptar les cookies de Google")
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

        sleep(self.config.temps_espera_processos)
        try:
            textarea = self.browser.find_element(By.TAG_NAME, value='textarea')
            # Selecciona tot el text del textarea
            # En Mac, usa Keys.COMMAND en comptes de Keys.CONTROL
            textarea.send_keys(Keys.CONTROL, 'a')
            # Esborra el text seleccionat
            textarea.send_keys(Keys.DELETE)
            # Envia la nova cerca
            textarea.send_keys(cerca + Keys.ENTER)
        except:
            raise ValueError("No s'ha pogut fer la cerca")

        while resultats_desats <= 10:
            sleep(self.config.temps_espera_processos)
            nom_captura_1 = self.composa_nom_captura(cerca)
            nom_captura_2 = self.composa_nom_captura(cerca, suffix="2a")

            navegador.captura_pantalla(nom_captura_1)
            resultats_cerca = browser.find_elements(By.XPATH, '//a[h3]')

            for resultat in resultats_cerca:
                if resultats_desats < 11:
                    link, titol, description = cerca_dades(resultat)

                    if titol == "Més resultats":
                        logging.info(
                            f"Obtenint la segona pàgina de {cerca}...")
                        browser.get(link)
                        sleep(self.config.temps_espera_processos)
                        navegador.captura_pantalla(nom_captura_2)
                        a_elements_with_h3 = browser.find_elements(
                            By.XPATH, '//a[h3]')

                        for a in a_elements_with_h3:
                            if resultats_desats < 11:
                                link, titol, description = cerca_dades(a)

                                if link is not None:
                                    resultats[resultats_desats] = {
                                        'titol': titol, 'url': link, 'description': description}
                                    resultats_desats += 1

                            else:
                                logging.info(
                                    f"S'han agafat els 10 resultats a la segona pàgina de {cerca}...")
                                browser.execute_script("window.history.go(-1)")
                                sleep(self.config.temps_espera_processos)
                                break

                    else:
                        if link is not None:
                            resultats[resultats_desats] = {
                                'titol': titol, 'url': link, 'description': description}
                            resultats_desats += 1

            if resultats_desats < 11:
                try:
                    browser.find_elements(
                        By.XPATH, '//a[@aria-label=\'Page 2\']')[0].click()
                    sleep(self.config.temps_espera_processos)
                    navegador.captura_pantalla(nom_captura_2)
                    a_elements_with_h3 = browser.find_elements(
                        By.XPATH, '//a[h3]')

                    for a in a_elements_with_h3:
                        if resultats_desats < 11:
                            link, titol, description = cerca_dades(a)

                            if link is not None:
                                resultats[resultats_desats] = {
                                    'titol': titol, 'url': link, 'description': description}
                                resultats_desats += 1
                        else:
                            browser.execute_script("window.history.go(-1)")
                            sleep(self.config.temps_espera_processos)
                            break
                except:
                    sleep(self.config.temps_espera_cerques)
                    logging.error(
                        f"No s'ha pogut fer la petició de la segona pàgina de {cerca}")

            logging.info(f"Valorant els resultats de {cerca}...")

            if resultats_desats < 11:
                logging.info(
                    f"No s'han obtingut els 10 resultats de {cerca}...")
                remove(nom_captura_1)

                try:
                    remove(nom_captura_2)
                except:
                    pass

                finally:
                    resultats_desats = 1
                    resultats = {}
                    browser.get('https://google.com')
                    sleep(self.config.temps_espera_cerques)
                    textarea = browser.find_element(
                        By.TAG_NAME, value='textarea')
                    textarea.send_keys(cerca + Keys.ENTER)
                    sleep(self.config.temps_espera_processos)
                    logging.info(f"Torna a realitzar la cerca")

            else:
                return resultats
