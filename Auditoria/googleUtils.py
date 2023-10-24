# -*- coding: utf-8 -*-

### IMPORTS ###

################# IMPORTS #################

# Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Utilitats
from datetime import datetime
from time import sleep
from os import remove

# Mòduls
from selenium_helpers import cerca_dades

# Globals
import logging

# Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime


import json
with open('/home/catalanet/XMCD/Auditoria/config.json', 'r') as file:
    globals = json.load(file)

### GLOBALS ###

directori_Imatges = globals['directori_Imatges']
temps_espera_processos = globals['temps_espera_processos']
temps_espera_cerques = globals['temps_espera_cerques']
fitxer_logs = globals['fitxer_logs']


def inicia_cercador(browser):

    try:
        # El 1 està definit a la BD com a Google. Taula: cercadors
        cercador = 1

        # Calen acceptar les cookies amb Google
        acceptat = False

        # Fa la petició a Google per anar-hi des d'allà
        browser.get('https://www.google.com')

        # Cerca tots els botons a la pàgina
        buttons = browser.find_elements(By.XPATH, '//button')

        # Itera sobre els botons i si contenen el div amb el text Accepta-ho tot el prem
        for button in buttons:
            try:
                if button.find_element(By.XPATH, './/div[contains(text(), "Accepta-ho tot")]'):
                    button.click()
                    acceptat = True
            except:
                pass
        
        if not acceptat:
            cercador = 21

    except:
        # Error de petició del cercador
        cercador = 20
    
    finally:
        return cercador
    

def executa_cerca(browser, cerca):
    # Busca el quadre de text per fer la cerca. Neteja el contingut i cerca
    try:
        textarea = browser.find_element(By.TAG_NAME, value='textarea')
        textarea.send_keys(cerca + Keys.ENTER)
        cercador = 1

    except:
        cercador = 22
    
    return cercador

def guarda_resultats(browser, directori_Imatges, navegador, sensor, cerca):

    if navegador == 1: 
        from chromeUtils import captura_pantalla
    elif navegador == 2:
        from firefoxUtils import captura_pantalla

    resultats = {}

    # Nº de resultats guardats
    resultats_desats = 1

    # Cal desar 10 resultats sempre
    while resultats_desats <= 10:

        sleep(temps_espera_processos)

        # Defineix les variables de les imatges
        nom_captura_1 = directori_Imatges + sensor + '_Google_' + cerca.replace(' ', '_') + str(datetime.now()).replace(' ', '_')+'.png'
        nom_captura_2 = directori_Imatges + sensor + '_Google_' + cerca.replace(' ', '_') + str(datetime.now()).replace(' ', '_')+'_2a.png'

        # Guarda la captura de la pantalla principal
        captura_pantalla(browser, nom_captura_1)

        # A Google els resultats son tots els títols <h3>
        # Busquem tots els elements <a> que contenen un <h3>
        resultats_cerca = browser.find_elements(By.XPATH, '//a[h3]')

        # Agafem els resultats
        for resultat in resultats_cerca:

            # Mentre hi hagin menys de 10
            if resultats_desats < 11:

                link, titol, description = cerca_dades(resultat)

                # Si una de les respostes és un més resultats, se'n va a la 2a pàgina de Google
                if titol == "Més resultats":

                    logging.info(f"Obtenint la segona pàgina de {cerca}...")

                    browser.get(link)

                    sleep(temps_espera_processos)

                    # Guarda la captura de la segona pantalla
                    captura_pantalla(browser, nom_captura_2)

                    # Busca a la segona pàgina de Google
                    a_elements_with_h3 = browser.find_elements(By.XPATH, '//a[h3]')
                    for a in a_elements_with_h3:
                        if resultats_desats < 11:
                            
                            ############### Això podria ser la funció cerca dades que crida a la (guarda_resultat). Valorar

                            link, titol, description = cerca_dades(a)

                            if link is not None:
                                resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                                resultats_desats += 1

                        # Un cop tenim 10 resultats.
                        else:
                            logging.info(f"S'han agafat els 10 resultats a la segona pàgina de {cerca}...")
                            browser.execute_script("window.history.go(-1)")
                            sleep(temps_espera_processos)
                            break

                # Guarda la pàgina. No és un enllaç de més resultats.
                else:
                    ############### Això podria ser una funció individual (guarda_resultat)
                    if link is not None:
                        resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                        resultats_desats += 1

        # Si no hi han 10 respostes cerca el botó de següent pàgina
        if resultats_desats < 11:
            # Si no troba el botó de la segona pàgina peta. 
            try:
                # Prem al botó de la segona pàgina
                browser.find_elements(By.XPATH, '//a[@aria-label=\'Page 2\']')[0].click()

                # Esperem a que carreguin els elements
                sleep(temps_espera_processos)

                # Guarda la captura de la segona pantalla
                captura_pantalla(browser, nom_captura_2)

                # Busquem tots els elements <a> que contenen un <h3>
                a_elements_with_h3 = browser.find_elements(By.XPATH, '//a[h3]')

                for a in a_elements_with_h3:
                    # Mentre hi hagin menys de 10
                    if resultats_desats < 11:
                        # Cerca les dades
                        link, titol, description = cerca_dades(a)

                        if link is not None:
                            resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                            resultats_desats += 1
                    else:
                        browser.execute_script("window.history.go(-1)")
                        sleep(temps_espera_processos)
                        break
            except:
                # Si peta no podem fer res. Esperar i tornar a reiniciar la cerca.
                sleep(temps_espera_cerques)
                logging.error(f"No s'ha pogut fer la petició de la segona pàgina de {cerca}")

        logging.info(f"Valorant els resultats de {cerca}...")

        # Si al final de tot no ha trobat 10 resultats torna a fer la cerca:
        if resultats_desats < 11:

            logging.info(f"No s'han obtingut els 10 resultats de {cerca}...")

            # Esborra les captures
            remove(nom_captura_1)
            try:
                remove(nom_captura_2)

            except:
                pass

            finally:

                # Torna a definir els paràmetres de la cerca actual
                logging.debug(f"Esborrades les captures de pantalla")
                resultats_desats = 1
                resultats = {}
                browser.get('https://google.com')
                sleep(temps_espera_cerques)
                textarea = browser.find_element(By.TAG_NAME, value='textarea')    
                textarea.send_keys(cerca + Keys.ENTER)
                sleep(temps_espera_processos)
                logging.info(f"Torna a realitzar la cerca")


        #Desa les dades
        else:
            return resultats