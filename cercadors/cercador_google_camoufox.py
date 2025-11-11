import os
import logging
import random
from cercadors.cercador_base import CercadorBase
from datetime import datetime
from utils.utils import assegura_directori_existeix
from time import sleep
from os.path import sep
from os import remove
from urllib.parse import quote_plus
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class GoogleCercadorCamoufox(CercadorBase):

    def inicia_cercador(self):
        # Configura el valor de self.cercador com a 1 (Google)
        id_cercador_db = 1
        try:
            acceptat = False
            page = self.navegador.page
            
            # Simula comportament humà abans d'anar a Google
            # Va primer a una pàgina neutral per semblar més natural
            page.goto('https://www.wikipedia.org')
            page.wait_for_load_state('domcontentloaded')
            sleep(2)  # Espera curta per semblar natural
            
            # Ara va a Google
            page.goto('https://www.google.com')
            page.wait_for_load_state('domcontentloaded')
            sleep(self.config.temps_espera_cerques)
            
            # Simula moviment del ratolí per semblar més humà
            page.mouse.move(100, 100)
            sleep(0.5)
            page.mouse.move(200, 150)
            sleep(0.5)
            
            # Intenta acceptar les cookies
            buttons = page.query_selector_all('button')
            for button in buttons:
                try:
                    text_content = button.inner_text()
                    if "Accepta-ho tot" in text_content or "Accept all" in text_content or "Aceptar" in text_content:
                        button.click()
                        acceptat = True
                        break
                except:
                    pass
            
            if not acceptat:
                textarea = page.query_selector('textarea')
                if not textarea:
                    self.config.write_log("No s'ha pogut acceptar les cookies de Google. No es pot seguir", level=logging.ERROR)
                    raise ValueError("No s'han pogut acceptar les cookies de Google")
                else:
                    self.config.write_log("No s'ha pogut acceptar les cookies de Google. Continuant...", level=logging.WARNING)

        except Exception as e:
            error_message = f"Error iniciant el cercador Google amb Camoufox: {e}"
            self.config.write_log(error_message, level=logging.ERROR)
            raise ValueError(error_message) from e

        return id_cercador_db

    def composa_nom_captura(self, cerca, navegador_text, suffix=None):
        # Obtenim el directori actual del fitxer de configuració
        current_directory = self.config.current_directory
        # Eliminem els espais del nom de cerca i obtenim el format de data-hora
        cerca_sense_espais = cerca.replace(' ', '_')
        data_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Composem el nom del fitxer
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
        page = self.navegador.page

        resultats = {}
        resultats_desats = 1
        intents = 0

        sleep(self.config.temps_espera_processos)
        try:
            self._executa_cerca(page, cerca)
        except Exception as error:
            raise ValueError("No s'ha pogut fer la cerca") from error

        sleep(self.config.temps_espera_cerques)

        if self.detecta_captcha(page):
            self.supera_captcha(page)
            sleep(300)

        sleep(self.config.temps_espera_cerques + 20)

        while resultats_desats <= 10 and intents < 3:
            sleep(self.config.temps_espera_processos)
            nom_captura_1 = self.composa_nom_captura(cerca, navegador_text)
            nom_captura_2 = self.composa_nom_captura(cerca, navegador_text, suffix="2a")

            logging.info(f"Fent la captura de {nom_captura_1}...")
            navegador.captura_pantalla(nom_captura_1)

            resultats_desats = self._processa_resultats_pagina(
                page, resultats, resultats_desats, navegador, nom_captura_2
            )

            logging.info(f"Valorant els resultats de {cerca}...")

            if resultats_desats < 11:
                logging.info(
                    f"No s'han obtingut els 10 resultats de {cerca}. "
                    f"S'han obtingut {resultats_desats - 1} resultats."
                )

                try:
                    if os.path.exists(nom_captura_2):
                        remove(nom_captura_2)
                except Exception:
                    pass

                intents += 1
                if intents < 3:
                    resultats_desats = 1
                    resultats = {}
                    self._executa_cerca(page, cerca)
                    sleep(self.config.temps_espera_cerques)
                    sleep(self.config.temps_espera_processos)
                    logging.info(f"Torna a realitzar la cerca. Intent {intents + 1} de 3")
                else:
                    logging.error(
                        f"No s'han pogut obtenir resultats després de 3 intents per la cerca: {cerca}"
                    )
                    raise ValueError(
                        f"No s'han pogut obtenir resultats després de 3 intents per la cerca: {cerca}"
                    )
            else:
                return resultats

    def _executa_cerca(self, page, cerca: str) -> None:
        """Executa la cerca amb escriptura humana; recorre a URL directa si falla."""
        url = self._genera_url_cerca(cerca)
        locator = page.locator('textarea')

        if locator.count() == 0:
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')
            return

        try:
            textarea = locator.first
            textarea.click()
            page.wait_for_timeout(200)
            textarea.fill('')
            page.wait_for_timeout(200)

            for char in cerca:
                delay = random.randint(40, 120)
                textarea.type(char, delay=delay)
                page.wait_for_timeout(random.randint(30, 90))

            page.wait_for_timeout(300)
            textarea.press('Enter')
        except PlaywrightTimeoutError:
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')
        except Exception as e:
            self.config.write_log(
                f"No s'ha pogut escriure la cerca '{cerca}' a Camoufox: {e}",
                level=logging.WARNING
            )
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')

    def _processa_resultats_pagina(self, page, resultats, resultats_desats, navegador, nom_captura_2):
        """Extreu els resultats de la pàgina actual i, si cal, de la segona pàgina."""
        resultats_cerca = page.query_selector_all('a:has(h3)')

        for resultat in resultats_cerca:
            if resultats_desats >= 11:
                break

            titol, link, description = self._extreu_dades_resultat(resultat)
            if not titol or not link:
                continue

            titol_normalitzat = titol.strip().lower()
            if titol_normalitzat in {"més resultats", "más resultados", "more results"}:
                resultats_desats = self._processa_segona_pagina(
                    page, navegador, nom_captura_2, resultats, resultats_desats, link
                )
            else:
                resultats[resultats_desats] = {
                    'titol': titol,
                    'url': link,
                    'description': description
                }
                resultats_desats += 1

        return resultats_desats

    def _processa_segona_pagina(self, page, navegador, nom_captura_2, resultats, resultats_desats, link):
        """Carrega la segona pàgina de resultats i extreu fins a completar 10 entrades."""
        if not link:
            return resultats_desats

        try:
            page.goto(link)
            page.wait_for_load_state('domcontentloaded')
            sleep(self.config.temps_espera_processos)
            navegador.captura_pantalla(nom_captura_2)

            a_elements = page.query_selector_all('a:has(h3)')
            for element in a_elements:
                if resultats_desats >= 11:
                    break

                titol, url, description = self._extreu_dades_resultat(element)
                if url and titol:
                    resultats[resultats_desats] = {
                        'titol': titol,
                        'url': url,
                        'description': description
                    }
                    resultats_desats += 1
        except Exception as e:
            self.config.write_log(
                f"Error obtenint la segona pàgina de resultats: {e}",
                level=logging.WARNING
            )
        finally:
            try:
                page.go_back()
                page.wait_for_load_state('domcontentloaded')
                sleep(self.config.temps_espera_processos)
            except Exception:
                pass

        return resultats_desats

    def _extreu_dades_resultat(self, resultat):
        """Obté títol, enllaç i descripció d'un resultat."""
        try:
            link = resultat.get_attribute('href')
            h3_element = resultat.query_selector('h3')
            titol = h3_element.inner_text().strip() if h3_element else ""

            description = resultat.evaluate(
                """(node) => {
                    try {
                        const container = node.closest('div.g') || node.parentElement;
                        if (!container) {
                            return '';
                        }
                        const desc = container.querySelector('.VwiC3b, .MUxGbd, .BNeawe');
                        return desc ? desc.innerText : '';
                    } catch (error) {
                        return '';
                    }
                }"""
            )

            return titol, link, description or ""
        except Exception:
            return "", None, ""

    def detecta_captcha(self, page) -> bool:
        """Detecta la presència d'un reCAPTCHA a la pàgina."""
        try:
            element = page.locator('div.rc-anchor-logo-text')
            if element.count() and any(
                text.strip().lower() == 'recaptcha'
                for text in element.all_inner_texts()
            ):
                logging.warning("Captcha de Google detectat mitjançant rc-anchor-logo-text")
                return True

            for frame in page.frames:
                try:
                    frame_element = frame.query_selector('div.rc-anchor-logo-text')
                    if frame_element and frame_element.inner_text().strip().lower() == 'recaptcha':
                        logging.warning("Captcha de Google detectat dins d'un iframe")
                        return True
                except Exception:
                    continue

            page_source = page.content().lower()
            if 'recaptcha' in page_source or 'i\'m not a robot' in page_source:
                logging.warning("Captcha de Google detectat mitjançant text a la pàgina")
                return True
        except Exception as e:
            self.config.write_log(
                f"Error detectant el captcha de Google a Camoufox: {e}",
                level=logging.WARNING
            )

        return False

    def supera_captcha(self, page):
        logging.info("Intenta superar el captcha de Google amb Camoufox!")

        try:
            page_source = page.content()
            with open('page_source.html', 'w') as f:
                f.write(page_source)
        except Exception:
            pass

        try:
            frame_locator = page.frame_locator('iframe[src*="recaptcha"]')
            checkbox = frame_locator.locator('div.recaptcha-checkbox-border')
            checkbox.wait_for(state='visible', timeout=self.config.temps_espera_processos * 1000)
            page.wait_for_timeout(random.randint(250, 500))
            checkbox.click()
            logging.info("Checkbox del reCAPTCHA clicat correctament (Camoufox).")
        except PlaywrightTimeoutError:
            logging.warning("No s'ha pogut trobar o clicar el checkbox del reCAPTCHA abans del temps límit (Camoufox).")
        except Exception as e:
            self.config.write_log(
                f"Error intentant superar el captcha de Google amb Camoufox: {e}",
                level=logging.WARNING
            )

    def _genera_url_cerca(self, cerca: str) -> str:
        return f"https://www.google.com/search?q={quote_plus(cerca)}&hl=ca"

