# -*- coding: utf-8 -*-

################# Imports #################

# Selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Seleccionem un User Agent
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0'

# Definim valors per a la BD
navegador = 2 # Firefox
cercador = 1 # Google

### NAVEGADOR ###

#firefox_path = '/home/catalanet/firefox-115.3.1esr/firefox/firefox'
geckodriver_path = './Firefox/geckodriver'

# Inicia el navegador Firefox
options = Options()
options.headless = True
options.set_preference("general.useragent.override", user_agent)
#options.binary_location = firefox_path

servei = Service(geckodriver_path)
browser = webdriver.Firefox(service=servei, options=options)

# Fa la petició a Google per anar-hi des d'allà
browser.get('https://google.com')

# Cerca tots els botons a la pàgina
buttons = browser.find_elements(By.XPATH, '//button')

# Itera sobre els botons i si contenen el div amb el text Accepta-ho tot el prem
for button in buttons:
    try:
        if button.find_element(By.XPATH, './/div[contains(text(), "Accepta-ho tot")]'):
            button.click()
    except:
         pass

browser.quit()
