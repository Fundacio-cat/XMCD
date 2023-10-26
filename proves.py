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
# Guarda el contingut HTML en un fitxer
with open('./divs.html', 'w', encoding='utf-8') as file:
    file.write(page_source)

soup = BeautifulSoup(page_source, 'html.parser')

# Troba tots els elements amb la classe 'g-section-with-header'
elements_g_section = soup.find_all('g-section-with-header')

# Imprimeix o processa els elements trobats
for element in elements_g_section:

    with open('./divs.html', 'w', encoding='utf-8') as file:
        file.write(str(element))

    try:
        # Div on ha d'estar el títol de les noticies. En aquest nivell o inferior
        text_noticies = element.find('div').find('div').find('div').find('div')
    except:
        text_noticies = None

    if "Notícies destacades" in str(text_noticies):

        # Agafem tots els div de les noticies
        divs = element.find_all('div', recursive=False)

        # Es salta el primer div, és el del text de notícies        
        for noticia in divs[1:]:

            with open('./news.html', 'a', encoding='utf-8') as file:
                file.write(str(noticia))
                file.write('\nNext\n')
                
            # Enllaç de les notícies
            link_noticia = noticia.find('a')['href']

            print (link_noticia)



                

'''
# A Google els resultats son tots els títols <h3>
# Busquem tots els elements <a> que contenen un <h3>
resultats_cerca = browser.find_elements(By.XPATH, '//div[@aria-level="2"]/span')

# Agafem els resultats
for resultat in resultats_cerca:

    print (resultat.get_attribute("innerHTML"))

    if "Notícies destacades" in resultat.get_attribute("innerHTML"):

        print ("Estic dins de les notícies!")

        div_noticies = resultat.find_element(By.XPATH, './parent::div/parent::div/parent::div/parent::div/parent::g-section-with-header')
        #div_noticies = resultat.find_element(By.XPATH, './parent::div/parent::div/parent::div/parent::g-section-with-header')

        print (div_noticies.get_attribute("innerHTML"))
'''