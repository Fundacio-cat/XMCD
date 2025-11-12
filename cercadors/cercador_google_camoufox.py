import logging
import random
from cercadors.cercador_base import CercadorBase
from datetime import datetime
from utils.utils import assegura_directori_existeix
from os.path import sep, dirname
from urllib.parse import quote_plus
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class GoogleCercadorCamoufox(CercadorBase):

    def inicia_cercador(self):
        return 1

    def composa_nom_captura(self, cerca, navegador_text, suffix=None):
        current_directory = self.config.current_directory
        cerca_sense_espais = cerca.replace(' ', '_')
        data_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nom_base = (
            f"{current_directory}{sep}{self.config.directori_Imatges}"
            f"{sep}{self.config.sensor}_{navegador_text}_Google_{cerca_sense_espais}_{data_hora_actual}"
        )
        nom_captura = f"{nom_base}_{suffix}.png" if suffix else f"{nom_base}.png"
        assegura_directori_existeix(dirname(nom_captura))
        return nom_captura

    def guarda_resultats(self, cerca, navegador_text):
        navegador = self.config.navegador
        page = self.navegador.page
        timeout_ms = max(60000, self.config.temps_espera_cerques * 1000)
        url = f"https://www.google.com/search?q={quote_plus(cerca)}&hl=ca"

        ha_navegat = False

        for combinacio in ['Control+L', 'Meta+L']:
            try:
                page.keyboard.press(combinacio)
                page.wait_for_timeout(150)
                for caracter in url:
                    page.keyboard.type(caracter, delay=random.randint(40, 120))
                page.keyboard.press('Enter')
                ha_navegat = True
                break
            except Exception:
                continue

        if ha_navegat:
            try:
                page.wait_for_load_state('domcontentloaded', timeout=timeout_ms)
            except PlaywrightTimeoutError:
                logging.warning(f"Timeout carregant '{cerca}' després d'escriure la URL.")
                page.wait_for_load_state('load')
            except Exception:
                pass
        else:
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=timeout_ms)
            except PlaywrightTimeoutError:
                logging.warning(f"Timeout carregant '{cerca}'. Intentant sense esperar DOM complet.")
                page.goto(url, wait_until='load')
            except Exception as error:
                raise ValueError("No s'ha pogut fer la cerca") from error

        try:
            page.wait_for_load_state('networkidle', timeout=timeout_ms)
        except Exception:
            pass

        # Accepta cookies si apareix el banner
        buttons = page.query_selector_all('button')
        for button in buttons:
            try:
                text = (button.inner_text() or "").strip().lower()
                if any(keyword in text for keyword in ["accepta-ho tot", "accept all", "aceptar todo"]):
                    button.click()
                    page.wait_for_timeout(300)
                    break
            except Exception:
                continue

        page.wait_for_timeout(400)

        resultats = {}
        intents = 0

        while intents < 3 and len(resultats) < 10:
            navegador.captura_pantalla(
                self.composa_nom_captura(cerca, navegador_text, suffix=f"intent{intents+1}")
            )

            links = page.query_selector_all('a:has(h3)')
            for element in links:
                if len(resultats) >= 10:
                    break

                link = element.get_attribute('href')
                h3 = element.query_selector('h3')
                titol = h3.inner_text().strip() if h3 else ""
                if not link or not titol:
                    continue

                descripcio = ""
                container = element.evaluate_handle("(node) => node.closest('div.g') || node.parentElement")
                if container:
                    desc = container.query_selector('.VwiC3b, .MUxGbd, .BNeawe')
                    if desc:
                        descripcio = desc.inner_text()

                resultats[len(resultats) + 1] = {
                    'titol': titol,
                    'url': link,
                    'description': descripcio
                }

            if len(resultats) >= 10:
                break

            intents += 1
            segona_pagina = page.query_selector("a[aria-label*='2']")
            if not segona_pagina:
                break

            segona_pagina.click()
            page.wait_for_load_state('domcontentloaded')

        if not resultats:
            raise ValueError(f"No s'han pogut obtenir resultats per la cerca: {cerca}")

        if len(resultats) < 10:
            logging.warning(f"S'han obtingut {len(resultats)} resultats per '{cerca}'.")

        return resultats