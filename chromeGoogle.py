# -*- coding: utf-8 -*-

################# Imports #################

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 

# Description
from bs4 import BeautifulSoup

# Utilitats
from datetime import datetime
from time import sleep
from os import remove

# Postgres
import psycopg2

# Mòduls
from credencials import obtenir_credentials_oficina

################# GLOBALS #################

directori_Imatges = './Chrome/Captures/' # Directori on desar les captures de pantalla
temps_espera_processos = 1 # Temps d'espera a cada un dels passos
temps_espera_cerques = 5 # Temps d'espera entre cada una de les cerques

#cerques = ['augmentar brillantor apple', 'barcelona', 'biografia Gerard Romero', 'calendari escolar 2023', 'calendari laboral barcelona', 'canvi climàtic']
cerques = ['calendari laboral barcelona', 'canvi climàtic']

################# FUNCIONS #################

def guarda(conn, cursor, sensor, navegador, cercador, cerca, posicio, titol, url, descripcio, llengua):

    # conn -> Objecte de la connexió amb Postgres
    # cursor -> Objecte del cursor
    # sensor -> charvar 6
    # hora -> timestamp with time zone
    # navegador -> smallint
    # cercador -> smallint
    # cerca -> charvar 50
    # posicio -> smallint
    # titol -> charvar 128
    # url -> charvar 1024
    # descripcio -> text
    # llengua -> charvar 2

    now = datetime.now()

    # Neteja de les cometes per a que no peti al fer l'Insert
    if cerca is not None:
        cerca = cerca.replace("'", "''")

    if titol is not None:
        titol = titol.replace("'", "''")

    if descripcio is not None:
        descripcio = descripcio.replace("'", "''")

    # Executar la instrucció SQL per inserir dades a la base de dades
    insert_query = "INSERT INTO cerques (sensor, hora, navegador, cercador, cerca, posicio, titol, url, descripcio, llengua) VALUES ('{}', '{}', {}, {}, '{}', {}, '{}', '{}', '{}', '{}');".format(
        sensor, now, navegador, cercador, cerca, posicio, titol, url, descripcio, llengua)

    # Executar la consulta amb els valors
    cursor.execute(insert_query)

    # Fer commit per desar els canvis a la base de dades
    conn.commit()

def cerca_dades(element_cercar):

    link = None
    titol = None
    description = None

    # Si està dins d'un contenidor que conté la cadena "preguntes" ho descarta.
    # Més preguntes // Preguntes relacionades amb la teva cerca
    try:
        div_preguntes = element_cercar.find_element(By.XPATH, './parent::span/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div')
        div_mes_preguntes = div_preguntes.find_element(By.XPATH, './div/div[1]/div/div')
        mes_preguntes = div_mes_preguntes.find_element(By.XPATH, './/span')
        if "preguntes" in mes_preguntes.text.lower():
            afegit_google = True
        else:
            afegit_google = False

    # No està dins un contenidor de Més preguntes
    except:
        mes_preguntes = None
        afegit_google = False

    if not afegit_google:

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
            if mes_preguntes is not None:
                description = mes_preguntes.text
            else:
                description = None

    return [link, titol, description]

################# POSTGRESQL #################

# Agafa les credencials per al sensor de la oficina
sensor, host, port, database, user, password = obtenir_credentials_oficina()

configuracio = {
    'host': host,
    'port': port,
    'database': database,
    'user': user,
    'password': password,
}

################# CONNEXIÓ BD #################

# Connecta a la BD
try:
    conn = psycopg2.connect(**configuracio)
    cursor = conn.cursor()

except psycopg2.Error as e:
    print("Error en la connexió a PostgreSQL:", e)
    conn = None

except:
    print ("Error desconegut en la connexió")
    conn = None

# Si no s'ha pogut connectar a la BD surt del programa amb codi d'error
if conn is None:
    exit(1)
else: 
    print ("Connectat a la BD")

################# PROGRAMA #################

# Seleccionem un User Agent
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'

# Definim les variables globals
navegador = 1 # Firefox
cercador = 1 # Google

# Inicia el navegador

# Mides
width = 1024
height = 4212

'''
service = Service('./chromedriver')
options = Options()
options.add_argument(f"--window-size={width},{height}")
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument(f"user-agent={user_agent}")

browser = webdriver.Chrome(service=service, options=options)
'''

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

resultats = {}

# Realitza la cerca
for cerca in cerques: 

    # Camp de cerca a afegir a la BD
    consulta = cerca

    # Calen fer temps d'espera per a que es carreguin els elements
    sleep(temps_espera_cerques)
    
    # Definim el diccionari on es guardaran les dades
    resultats[cerca] = {}

    # Busca el quadre de text per fer la cerca. Neteja el contingut i cerca
    textarea = browser.find_element(By.TAG_NAME, value='textarea')
    textarea.send_keys(cerca + Keys.ENTER)

    # Esperem a que carreguin els elements
    sleep(temps_espera_processos)

    resultats_desats = 1

    # Cal desar 10 resultats sempre
    while resultats_desats <= 10:

        # Defineix les variables de les imatges
        data_i_hora_actuals = datetime.now()
        nom_captura_1 = directori_Imatges + cerca.replace(' ', '_') + str(data_i_hora_actuals).replace(' ', '_')+'.png'
        nom_captura_2 = directori_Imatges + cerca.replace(' ', '_') + str(data_i_hora_actuals).replace(' ', '_')+'_2a.png'

        # Guarda la captura de la pantalla principal
        browser.save_screenshot(nom_captura_1)

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
                    browser.get(link)

                    sleep(temps_espera_processos)

                    # Guarda la captura de la segona pantalla
                    browser.save_screenshot(nom_captura_2)

                    # Busca a la segona pàgina de Google
                    a_elements_with_h3 = browser.find_elements(By.XPATH, '//a[h3]')
                    for a in a_elements_with_h3:
                        if resultats_desats < 11:
                            
                            link, titol, description = cerca_dades(a)

                            if link is not None:
                                resultats[cerca].update({resultats_desats: {'titol': titol, 'url': link, 'description': description}})
                                resultats_desats += 1

                        # Un cop tenim 10 resultats.
                        else:
                            browser.execute_script("window.history.go(-1)")
                            sleep(temps_espera_processos)
                            break

                # Guarda la pàgina. No és un enllaç de més resultats.
                else:
                    if link is not None:
                        resultats[cerca].update({resultats_desats: {'titol': titol, 'url': link, 'description': description}})
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
                browser.save_screenshot(nom_captura_2)

                # Busquem tots els elements <a> que contenen un <h3>
                a_elements_with_h3 = browser.find_elements(By.XPATH, '//a[h3]')

                for a in a_elements_with_h3:
                    # Mentre hi hagin menys de 10
                    if resultats_desats < 11:
                        # Cerca les dades
                        link, titol, description = cerca_dades(a)

                        if link is not None:
                            #guarda_dades(conn, cursor, sensor, consulta, navegador, cercador, resultats_desats, titol, link, description, llengua)
                            resultats[cerca].update({resultats_desats: {'titol': titol, 'url': link, 'description': description}})
                            resultats_desats += 1
                    else:
                        browser.execute_script("window.history.go(-1)")
                        sleep(temps_espera_processos)
                        break
            except:
                # Si peta no podem fer res. Esperar i tornar a reiniciar la cerca.
                sleep(temps_espera_cerques)
                print ("Error en la petició de la segona pàgina")

        # Si al final de tot no ha trobat 10 resultats torna a fer la cerca:
        if resultats_desats < 11:
            # Esborra les captures
            remove(nom_captura_1)
            try:
                remove(nom_captura_2)
            except:
                pass

            # Torna a definir els paràmetres de la cerca actual
            resultats_desats = 1
            resultats[cerca] = {}
            browser.get('https://google.com')
            sleep(temps_espera_cerques)
            textarea = browser.find_element(By.TAG_NAME, value='textarea')    
            textarea.send_keys(cerca + Keys.ENTER)
            sleep(temps_espera_processos)

        #Desa les dades
        else:
            for posicio, dades in resultats[cerca].items():
                titol = dades['titol']
                url = dades['url']
                descripcio = dades['description']
                llengua = "--"

                guarda(conn, cursor, sensor, navegador, cercador, cerca, posicio, titol, url, descripcio, llengua)
                

    # Torna a Google per a fer-hi la següent cerca
    browser.get('https://google.com')

browser.quit()