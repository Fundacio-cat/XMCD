import os
import logging
from cercadors.cercador_base import CercadorBase
from datetime import datetime
from utils.utils import assegura_directori_existeix
from time import sleep
from os.path import sep
from os import remove


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
            sleep(2)  # Espera curta per semblar natural
            
            # Ara va a Google
            page.goto('https://www.google.com')
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
            textarea = page.query_selector('textarea')
            if not textarea:
                raise ValueError("No s'ha trobat el camp de cerca")
            
            # Simula comportament humà més realista
            # Mou el ratolí al camp de cerca
            textarea.hover()
            sleep(0.3)
            
            # Neteja i envia la cerca amb comportament més humà
            textarea.click()
            sleep(0.2)
            textarea.fill('')  # Neteja el camp
            sleep(0.3)
            
            # Escriu la cerca caràcter per caràcter per semblar més humà
            for char in cerca:
                textarea.type(char)
                sleep(0.05)  # Petita pausa entre caràcters
            
            sleep(0.5)  # Pausa abans d'enviar
            textarea.press('Enter')

            sleep(self.config.temps_espera_cerques)
            
        except Exception as e:
            raise ValueError(f"No s'ha pogut fer la cerca: {e}")

        while resultats_desats <= 10 and intents < 3:
            intents += 1
            sleep(self.config.temps_espera_processos)
            nom_captura_1 = self.composa_nom_captura(cerca, navegador_text)
            nom_captura_2 = self.composa_nom_captura(cerca, navegador_text, suffix="2a")

            logging.info(f"Fent la captura de {nom_captura_1}...")

            navegador.captura_pantalla(nom_captura_1)
            
            # Busca els resultats de la cerca (elements <a> que contenen <h3>)
            resultats_cerca = page.query_selector_all('a:has(h3)')

            for resultat in resultats_cerca:
                if resultats_desats < 11:
                    try:
                        link = resultat.get_attribute('href')
                        h3_element = resultat.query_selector('h3')
                        titol = h3_element.inner_text() if h3_element else ""
                        
                        # Intenta obtenir la descripció (simplificat)
                        description = ""
                        
                    except:
                        continue

                    if titol and link:
                        if titol == "Més resultats":
                            logging.info(f"Obtenint la segona pàgina de {cerca}...")
                            # Simula comportament humà abans de clicar
                            page.mouse.move(400, 300)
                            sleep(0.3)
                            page.goto(link)
                            sleep(self.config.temps_espera_processos)
                            navegador.captura_pantalla(nom_captura_2)
                            a_elements_with_h3 = page.query_selector_all('a:has(h3)')

                            for a in a_elements_with_h3:
                                if resultats_desats < 11:
                                    try:
                                        link = a.get_attribute('href')
                                        h3_element = a.query_selector('h3')
                                        titol = h3_element.inner_text() if h3_element else ""
                                        description = ""
                                        
                                        if link and titol:
                                            resultats[resultats_desats] = {
                                                'titol': titol, 'url': link, 'description': description}
                                            resultats_desats += 1
                                    except:
                                        continue
                                else:
                                    logging.info(f"S'han agafat els 10 resultats a la segona pàgina de {cerca}...")
                                    page.go_back()
                                    sleep(self.config.temps_espera_processos)
                                    break
                        else:
                            resultats[resultats_desats] = {
                                'titol': titol, 'url': link, 'description': description}
                            resultats_desats += 1

            # Intenta anar a la pàgina 2 si no tenim prou resultats
            if resultats_desats < 11:
                try:
                    # Busca el botó de pàgina 2
                    page_2_link = page.query_selector('a[aria-label*="2"]')
                    if page_2_link:
                        # Simula comportament humà abans de clicar
                        page_2_link.hover()
                        sleep(0.5)
                        page_2_link.click()
                        sleep(self.config.temps_espera_processos)
                        navegador.captura_pantalla(nom_captura_2)
                        a_elements_with_h3 = page.query_selector_all('a:has(h3)')

                        for a in a_elements_with_h3:
                            if resultats_desats < 11:
                                try:
                                    link = a.get_attribute('href')
                                    h3_element = a.query_selector('h3')
                                    titol = h3_element.inner_text() if h3_element else ""
                                    description = ""

                                    if link and titol:
                                        resultats[resultats_desats] = {
                                            'titol': titol, 'url': link, 'description': description}
                                        resultats_desats += 1
                                except:
                                    continue
                            else:
                                page.go_back()
                                sleep(self.config.temps_espera_processos)
                                break
                except Exception as e:
                    sleep(self.config.temps_espera_cerques)
                    logging.error(f"No s'ha pogut fer la petició de la segona pàgina de {cerca}: {e}")

            logging.info(f"Valorant els resultats de {cerca}...")

            if resultats_desats < 11:
                logging.info(f"No s'han obtingut els 10 resultats de {cerca}. S'han obtingut {resultats_desats - 1} resultats.")
                
                try:
                    if os.path.exists(nom_captura_2):
                        remove(nom_captura_2)
                except:
                    pass

                if intents < 3:
                    resultats_desats = 1
                    resultats = {}
                    page.goto('https://google.com')
                    sleep(self.config.temps_espera_cerques)
                    textarea = page.query_selector('textarea')
                    if textarea:
                        textarea.fill('')
                        textarea.type(cerca)
                        page.keyboard.press('Enter')
                        sleep(self.config.temps_espera_processos)
                        logging.info(f"Torna a realitzar la cerca. Intent {intents + 1} de 3")
                else:
                    logging.error(f"No s'han pogut obtenir resultats després de 3 intents per la cerca: {cerca}")
                    raise ValueError(f"No s'han pogut obtenir resultats després de 3 intents per la cerca: {cerca}")
            else:
                return resultats

