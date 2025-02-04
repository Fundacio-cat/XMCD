from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium_stealth import stealth
from fake_useragent import UserAgent  # Necessitaràs instal·lar: pip install fake-useragent
import undetected_chromedriver as uc  # Necessitaràs instal·lar: pip install undetected-chromedriver
from stem import Signal
from stem.control import Controller

import time
import random

CERCA = "la vanguardia avui"

# Defineix si un títol h3 està dins d'un mòdul de "Més preguntes"
def h3_modul_preguntes(h3):

    try:
        div_preguntes = h3.find_element(By.XPATH, './parent::span/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div')
        div_mes_preguntes = div_preguntes.find_element(By.XPATH, './div/div[1]/div/div')
        mes_preguntes = div_mes_preguntes.find_element(By.XPATH, './/span')
        if "preguntes" in mes_preguntes.text.lower():
            es_pregunta = True
        else:
            es_pregunta = False

    # No està dins un contenidor de Més preguntes
    except:
        mes_preguntes = None
        es_pregunta = False

    return mes_preguntes, es_pregunta

def cerca_dades(element_cercar):

    link = None
    titol = None
    description = None

    mes_preguntes, es_pregunta = h3_modul_preguntes(element_cercar)

    if not es_pregunta:

        # Guardem les URL
        link = element_cercar.get_attribute('href')

        # Guardem els titols
        contingut_html = element_cercar.get_attribute("innerHTML")
        soup = BeautifulSoup(contingut_html, 'html.parser')
        titol = soup.find('h3').text

        # Obtenim la descripció
        try:

            # Accedeix a l'element pare 3 vegades
            div_pare = element_cercar.find_element(By.XPATH, './parent::span/parent::div/parent::div/parent::div/parent::div/parent::div')

            # L'enllaç no té imatge. La descripció està al 2n div
            try:
                div_descripcio = div_pare.find_element(By.XPATH, './div/div[2]')
                spans = div_descripcio.find_elements(By.XPATH, './/span')
                description = spans[len(spans)-1].text

            # L'enllaç té una imatge. La descripció està al 3r div
            except:
                div_descripcio = div_pare.find_element(By.XPATH, './div/div[3]')
                spans = div_descripcio.find_elements(By.XPATH, './/span')
                description = spans[len(spans)-1].text

        except:
            try:
                # Altre accés de les descripcions
                div_pare = element_cercar.find_element(By.XPATH, './parent::span/parent::div/parent::div/parent::div/parent::div')
                div_descripcio = div_pare.find_element(By.XPATH, './div[3]')
                description = div_descripcio.text

                if description == '':
                    div_descripcio = div_pare.find_element(By.XPATH, './div[2]')
                    description = div_descripcio.text

            except:
                if mes_preguntes is not None:
                    description = mes_preguntes.text
                else:
                    description = None


    return [link, titol, description]

# Configurar el driver de Firefox
options = Options()
ua = UserAgent()

# Configuració del proxy Tor
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9050
options.set_preference('network.proxy.type', 1)
options.set_preference('network.proxy.socks', PROXY_HOST)
options.set_preference('network.proxy.socks_port', PROXY_PORT)
options.set_preference('network.proxy.socks_version', 5)
def canvia_ip_tor():
    try:
        # Per generar la password de Tor:
        # 1. Obre el fitxer torrc (normalment a /etc/tor/torrc)
        # 2. Afegeix la línia: HashedControlPassword $(tor --hash-password "la_teva_password")
        # 3. Reinicia el servei Tor
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="prova123")  # Posa aquí la mateixa password que has fet servir abans
            controller.signal(Signal.NEWNYM)
            time.sleep(5)  # Espera per assegurar que la nova identitat s'ha establert
            return True
    except Exception as e:
        print(f"Error canviant la IP de Tor: {str(e)}")
        return False

# Intenta canviar la IP de Tor abans d'iniciar el navegador
if not canvia_ip_tor():
    print("No s'ha pogut canviar la IP de Tor. Continuant amb la IP actual...")

# Executa el driver
driver = webdriver.Firefox(options=options)

# Obrir Google
driver.get("https://www.google.com")

# Acceptar cookies si cal
buttons = driver.find_elements(By.XPATH, '//button')
for button in buttons:
    try:
        if button.find_element(By.XPATH, './/div[contains(text(), "Accepta-ho tot")]'):
            button.click()
            acceptat = True
            break  # Afegeix un break aquí per sortir del bucle un cop acceptat
    except NoSuchElementException:
        pass

try:
    textarea = driver.find_element(By.TAG_NAME, value='textarea')
    textarea.send_keys(Keys.CONTROL, 'a')
    textarea.send_keys(Keys.DELETE)
    # Envia la nova cerca
    time.sleep(random.uniform(1, 3))  # Espera aleatòria
    textarea.send_keys(CERCA + Keys.ENTER)
except:
    raise ValueError("No s'ha pogut fer la cerca")

time.sleep(30)


resultats = {}
resultats_desats = 1
intents = 0

time.sleep(3)

while resultats_desats <= 10 and intents < 3:

    intents += 1

    resultats_cerca = driver.find_elements(By.XPATH, '//a[h3]')

    for resultat in resultats_cerca:
        if resultats_desats < 11:
            link, titol, description = cerca_dades(resultat)

            if titol == "Més resultats":
                driver.get(link)
                time.sleep(3)
                a_elements_with_h3 = driver.find_elements(By.XPATH, '//a[h3]')

                for a in a_elements_with_h3:
                    if resultats_desats < 11:
                        link, titol, description = cerca_dades(a)

                        if link is not None:
                            resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                            resultats_desats += 1

                    else:
                        driver.execute_script("window.history.go(-1)")
                        break

            else:
                if link is not None:
                    resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                    resultats_desats += 1

    if resultats_desats < 11:
        try:
            driver.find_elements(By.XPATH, '//a[@aria-label=\'Page 2\']')[0].click()
            time.sleep(3)
            a_elements_with_h3 = driver.find_elements(By.XPATH, '//a[h3]')

            for a in a_elements_with_h3:
                if resultats_desats < 11:
                    link, titol, description = cerca_dades(a)

                    if link is not None:
                        resultats[resultats_desats] = {'titol': titol, 'url': link, 'description': description}
                        resultats_desats += 1
                else:
                    driver.execute_script("window.history.go(-1)")
                    time.sleep(3)
                    break
        except:
            time.sleep(3)

    if resultats_desats < 11:
        if intents < 3:
            resultats_desats = 1
            resultats = {}
            driver.get('https://google.com')
            time.sleep(3)
            textarea = driver.find_element(By.TAG_NAME, value='textarea')
            textarea.send_keys(CERCA + Keys.ENTER)
            time.sleep(3)
        else:
            raise ValueError(f"No s'han pogut obtenir resultats després de 3 intents per la cerca: {CERCA}")

    else:
        break

for resultat in resultats:
    print(f"{resultat}: {resultats[resultat]['titol']}, {resultats[resultat]['url']}, {resultats[resultat]['description']}")
