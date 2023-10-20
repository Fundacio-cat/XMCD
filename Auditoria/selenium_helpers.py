# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

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

def cerca_cerca(conn, cursor, sensor):

    # Executar la instrucció SQL per inserir dades a la base de dades
    select_integral = "SELECT seguent_cerca('{}');".format(sensor)

    # Executar la consulta amb els valors
    cursor.execute(select_integral)

    int_cerca = cursor.fetchone()[0]

    # Executar la instrucció SQL per inserir dades a la base de dades
    select_cerca = "SELECT consulta FROM cerques WHERE cerqId = {};".format(int_cerca)

    # Executar la consulta amb els valors
    cursor.execute(select_cerca)

    cerca = cursor.fetchone()[0]

    return int_cerca, cerca