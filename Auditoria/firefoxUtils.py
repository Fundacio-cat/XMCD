# -*- coding: utf-8 -*-

### IMPORTS ###

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
# Selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# BD
from postgres import cerca_userAgent

### FUNCIONS ###
def inicia_navegador(cursor):

    # El 2 està definit a la BD com a Firefox. Taula: navegadors
    navegador = 2

    # Seleccionem un User Agent
    user_agent = cerca_userAgent(cursor, navegador)

    if user_agent:
        # Inicia el navegador Firefox
        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        options.set_preference('intl.accept_languages', 'ca')
        servei = Service('./Controladors/geckodriver')

        try:
            browser = webdriver.Firefox(service=servei, options=options)
        except:
            browser = 10
    else:
        # No hi ha user agent
        browser = 3


    return navegador, browser

def captura_pantalla(browser, nom):
    # Guarda la captura de la pantalla principal
    browser.save_full_page_screenshot(nom)
