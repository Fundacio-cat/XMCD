# -*- coding: utf-8 -*-

### IMPORTS ###

# Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def inicia_cercador(browser, cerca):

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

        else:
            # Busca el quadre de text per fer la cerca. Neteja el contingut i cerca
            try:
                textarea = browser.find_element(By.TAG_NAME, value='textarea')
                textarea.send_keys(cerca + Keys.ENTER)
            except:
                cercador = 22

    except:
        # Error de petició del cercador
        cercador = 20
    
    finally:
        return cercador