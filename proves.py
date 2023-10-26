# -*- coding: utf-8 -*-

################# Imports #################

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 

from time import sleep
from bs4 import BeautifulSoup

# Seleccionem un User Agent
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'

service = Service('/usr/bin/chromedriver')
options = Options()
options.add_argument(f"user-agent={user_agent}")
browser = webdriver.Chrome(service=service, options=options)

# Fa la petició a Google per anar-hi des d'allà
browser.get('https://www.google.com')

# Cerca tots els botons a la pàgina
buttons = browser.find_elements(By.XPATH, '//button')

# Itera sobre els botons i si contenen el div amb el text Accepta-ho tot el prem
for button in buttons:
    try:
        if button.find_element(By.XPATH, './/div[contains(text(), "Accepta-ho tot")]'):
            button.click()
    except:
         pass

cerca = 'que es la kings league'

# Busca el quadre de text per fer la cerca. Neteja el contingut i cerca
textarea = browser.find_element(By.TAG_NAME, value='textarea')

sleep(2)

textarea.send_keys(cerca + Keys.ENTER)

sleep(2)

# Obté el codi de la pàgina fins a "<g-section-with-header"
body = browser.find_element(By.XPATH, '//body')
page_source = body.get_attribute("innerHTML")


# A Google els resultats son tots els títols <h3>
# Busquem tots els elements <a> que contenen un <h3>
resultats_cerca = browser.find_elements(By.XPATH, '//g-section-with-header')

# Agafem els resultats
for resultat in resultats_cerca:

    print (resultat)

    print (resultat.get_attribute("innerHTML"))