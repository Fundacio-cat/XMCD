import os
import logging
import random
from cercadors.cercador_base import CercadorBase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from utils.selenium_helpers import cerca_dades
from utils.utils import assegura_directori_existeix
from time import sleep
from urllib.parse import quote_plus

from os.path import sep
from datetime import datetime
from os import remove


class GoogleCercador(CercadorBase):

    def inicia_cercador(self):
        # Configura el valor de self.navegador com a 1 (Chrome)
        id_cercador_db = 1
        try:
            if getattr(self.config.navegador, "id_navegador_db", None) == 2:
                logging.info("Firefox detectat: s'omet la càrrega inicial de google.com")
                return id_cercador_db

            acceptat = False
            self.browser.get('https://www.google.com')
            sleep(self.config.temps_espera_cerques)
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
                textarea = self.browser.find_element(By.TAG_NAME, value='textarea')
                if not textarea:
                    self.config.write_log("No s'ha pogut acceptar les cookies de Google. No es pot seguir", level=logging.ERROR)
                    raise ValueError("No s'han pogut acceptar les cookies de Google")
                else:
                    self.config.write_log("No s'ha pogut acceptar les cookies de Google. Continuant...", level=logging.ERROR)

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

    def composa_nom_captura(self, cerca, navegador_text, suffix=None):
        # Obtenim el directori actual del fitxer de configuració
        current_directory = self.config.current_directory
        # Eliminem els espais del nom de cerca i obtenim el format de data-hora
        cerca_sense_espais = cerca.replace(' ', '_')
        data_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Composem el nom del fitxer amb os.path.join
        nom_base = f"{current_directory}{sep}{self.config.directori_Imatges}{sep}{self.config.sensor}_{navegador_text}_Google_{cerca_sense_espais}_{data_hora_actual}"
        # Comprovem si hi ha un sufix i l'afegim si existeix
        if suffix:
            nom_captura = f"{nom_base}_{suffix}.png"
        else:
            nom_captura = f"{nom_base}.png"

        assegura_directori_existeix(os.path.dirname(nom_captura))

        return nom_captura

    def guarda_resultats(self, cerca, navegador_text):
        navegador = self.config.navegador
        browser = self.browser

        resultats = {}
        resultats_desats = 1
        intents = 0

        sleep(self.config.temps_espera_processos)
        try:
            if getattr(self.config.navegador, "id_navegador_db", None) == 2:
                self._executa_cerca_firefox(browser, cerca)
            else:
                textarea = self.browser.find_element(By.TAG_NAME, value='textarea')
                textarea.send_keys(Keys.CONTROL, 'a')
                textarea.send_keys(Keys.DELETE)
                # Envia la nova cerca
                textarea.send_keys(cerca + Keys.ENTER)
        except Exception as error:
            raise ValueError("No s'ha pogut fer la cerca") from error

        sleep(self.config.temps_espera_cerques)

        # Si hi ha un captcha de Cloudflare, espera a que es resolgui.
        if self.detecta_captcha(browser):
            self.supera_captcha(browser)

            sleep(300)

        sleep(self.config.temps_espera_cerques + 20)
        
        while resultats_desats <= 10 and intents < 3:
            sleep(self.config.temps_espera_processos)
            nom_captura_1 = self.composa_nom_captura("error", navegador_text)
            nom_captura_2 = self.composa_nom_captura(cerca, navegador_text, suffix="2a")

            logging.info(f"Fent la captura de {nom_captura_1}...")

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
                    browser.find_elements(By.XPATH, '//a[@aria-label=\'Page 2\']')[0].click()
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
                    logging.error(f"No s'ha pogut fer la petició de la segona pàgina de {cerca}")

            logging.info(f"Valorant els resultats de {cerca}...")

            if resultats_desats < 11:
                logging.info(f"No s'han obtingut els 10 resultats de {cerca}...")
                #remove(nom_captura_1)

                try:
                    remove(nom_captura_2)
                except:
                    pass

                finally:
                    if intents < 3:
                        resultats_desats = 1
                        resultats = {}
                        intents += 1
                        if getattr(self.config.navegador, "id_navegador_db", None) == 2:
                            self._executa_cerca_firefox(browser, cerca)
                        else:
                            browser.get('https://google.com')
                            sleep(self.config.temps_espera_cerques)
                            textarea = browser.find_element(By.TAG_NAME, value='textarea')
                            textarea.send_keys(cerca + Keys.ENTER)
                        sleep(self.config.temps_espera_cerques)
                        sleep(self.config.temps_espera_processos)
                        logging.info(f"Torna a realitzar la cerca. Intent {intents + 1} de 3")
                    else:
                        logging.error(f"No s'han pogut obtenir resultats després de 3 intents per la cerca: {cerca}")
                        raise ValueError(f"No s'han pogut obtenir resultats després de 3 intents per la cerca: {cerca}")

            else:
                return resultats

    def _executa_cerca_firefox(self, browser, cerca: str) -> None:
        """
        Realitza la cerca utilitzant la barra de navegació de Firefox,
        escrivint caràcter a caràcter per imitar un usuari.
        """
        url = f"https://www.google.com/search?q={quote_plus(cerca)}&hl=ca"
        logging.info(f"Executant la cerca a Firefox mitjançant la barra d'adreces: {url}")

        if not self._focus_barra_adreces(browser):
            logging.warning("No s'ha pogut enfocar la barra d'adreces. Obrint la URL directament.")
            browser.get(url)
            return

        try:
            # El text existent queda seleccionat després del focus; assegurem que s'esborra.
            ActionChains(browser).send_keys(Keys.DELETE).perform()

            for caracter in url:
                ActionChains(browser).send_keys(caracter).perform()
                sleep(random.uniform(0.05, 0.18))

            ActionChains(browser).send_keys(Keys.ENTER).perform()
        except Exception as e:
            self.config.write_log(
                f"No s'ha pogut escriure la cerca a la barra d'adreces de Firefox: {e}",
                level=logging.WARNING
            )
            browser.get(url)

    def _focus_barra_adreces(self, browser) -> bool:
        """Intenta enfocar la barra d'adreces utilitzant combinacions de teclat habituals."""
        combinacions = [Keys.CONTROL, Keys.COMMAND]

        enfocat = False
        for tecla in combinacions:
            try:
                accions = ActionChains(browser)
                accions.key_down(tecla).send_keys('l').key_up(tecla).perform()
                sleep(0.2)
                enfocat = True
            except Exception:
                continue

        return enfocat

    def detecta_captcha(self, browser):
        try:
            elements = browser.find_elements(By.CSS_SELECTOR, 'div.rc-anchor-logo-text')
            if any(element.text.strip().lower() == 'recaptcha' for element in elements):
                logging.warning("Captcha de Google detectat mitjançant l'element rc-anchor-logo-text")
                return True

        except Exception as e:
            self.config.write_log(
                f"Error detectant el captcha de Google: {e}", level=logging.WARNING)

        return False

    def supera_captcha(self, browser):
        logging.info("Intenta superarel captcha de Google!")

        # Guardar el codi de la pàgina per a valorar-lo
        page_source = browser.page_source
        with open('page_source.html', 'w') as f:
            f.write(page_source)

        iframe = None
        try:
            iframe = WebDriverWait(
                browser,
                self.config.temps_espera_processos
            ).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')
                )
            )
            browser.switch_to.frame(iframe)

            checkbox = WebDriverWait(
                browser,
                self.config.temps_espera_processos
            ).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'div.recaptcha-checkbox-border')
                )
            )
            checkbox.click()
            logging.info("Checkbox del reCAPTCHA clicat correctament.")
        except TimeoutException:
            logging.warning(
                "No s'ha pogut trobar o clicar el checkbox del reCAPTCHA abans del temps límit."
            )
        except Exception as e:
            self.config.write_log(
                f"Error intentant superar el captcha de Google: {e}",
                level=logging.WARNING
            )
        finally:
            if iframe:
                try:
                    browser.switch_to.default_content()
                except Exception:
                    pass