# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


# Defineix si un títol h3 està dins d'un mòdul de "Més preguntes"
def h3_modul_preguntes(h3):

    try:
        div_preguntes = h3.find_element(By.XPATH, './parent::span/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div/parent::div')
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

def num_links_anteriors_noticies(browser):
    # Busquem tots els elements <a> que contenen un <h3>
    resultats_cerca = browser.find_elements(By.XPATH, '//a[h3[@class]]')

    preguntes = 0
    # Agafem els resultats
    for resultat in resultats_cerca:
        descripcio, pregunta_google = h3_modul_preguntes(resultat)

        if pregunta_google == True:
            preguntes +=1

    # Obté el codi de la pàgina fins a "<g-section-with-header"
    body = browser.find_element(By.XPATH, '//body')
    page_source = body.get_attribute("innerHTML")

    # Cerca on estan les noticies
    index = page_source.find('Notícies destacades')
    # Agafa el codi de la pàgina anterior a les notícies
    if index != -1:
        page_source = page_source[:index]

    soup = BeautifulSoup(page_source, 'html.parser')
    # Troba tots els elements h3
    elements_h3 = soup.find_all('h3')
    # Compta el nombre d'elements h3
    nombre_elements_h3 = len(elements_h3)

    if nombre_elements_h3 > preguntes:
        titols_anteriors = nombre_elements_h3 - preguntes
    else:
        titols_anteriors = nombre_elements_h3

    return titols_anteriors

