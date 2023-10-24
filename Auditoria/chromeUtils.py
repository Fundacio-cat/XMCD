# -*- coding: utf-8 -*-

### IMPORTS ###

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 

# BD
from postgres import cerca_userAgent

### FUNCIONS ###
def inicia_navegador(cursor):

    # El 1 està definit a la BD com a Chrome. Taula: navegadors
    navegador = 1

    # Seleccionem un User Agent
    user_agent = cerca_userAgent(cursor, navegador)

    if user_agent:
        # Inicia el navegador
        service = Service('/home/catalanet/XMCD/Auditoria/Controladors/chromedriver')
        options = Options()
        options.add_argument(f"user-agent={user_agent}")
        try:
            browser = webdriver.Chrome(service=service, options=options)
        except:
            browser = 10
    else:
        # No hi ha user agent
        browser = 3

    return navegador, browser   

def captura_pantalla(browser, nom):
    # Guarda la captura de la pantalla principal
    browser.save_screenshot(nom)