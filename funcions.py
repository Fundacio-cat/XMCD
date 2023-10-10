# -*- coding: utf-8 -*-

# Guarda BD
from datetime import datetime

# Cerca
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

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
    insert_query = "INSERT INTO resultats (sensor, hora, navegador, cercador, cerca, posicio, titol, url, descripcio, llengua) VALUES ('{}', '{}', {}, {}, '{}', {}, '{}', '{}', '{}', '{}');".format(
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
