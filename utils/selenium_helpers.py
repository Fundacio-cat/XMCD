# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
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

# Retorna el número de titols que hi han anteriors a que apareguin les noticies. 
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

# Agafa totes les notícies de la pàgina i les retorna amb format diccionari
def hi_ha_noticies(browser):

    # Obté el codi de la pàgina fins a "<g-section-with-header"
    body = browser.find_element(By.XPATH, '//body')
    page_source = body.get_attribute("innerHTML")
    soup = BeautifulSoup(page_source, 'html.parser')

    # Troba tots els elements amb la classe 'g-section-with-header'
    elements_g_section = soup.find_all('g-section-with-header')

    # Imprimeix o processa els elements trobats
    for element in elements_g_section:

        div_pare = element.find_parent('div').find_parent('div')

        # Cerca el div on ha d'estar el text descriptiu del bloc
        try:
            # Div on ha d'estar el títol de les noticies. En aquest nivell o inferior
            div_text_noticies = div_pare.find('div').find('div').find('div')
        except:
            div_text_noticies = None

        if "Notícies destacades" in str(div_text_noticies):

            return True
        
    return False

# Agafa totes les notícies de la pàgina. Entra un diccionari i un index de nº de noticies i afegeix les noticies a aquest diccionari.
def agafa_noticies(browser, resultats_desats, resultats):

    # Obté el codi de la pàgina fins a "<g-section-with-header"
    body = browser.find_element(By.XPATH, '//body')
    page_source = body.get_attribute("innerHTML")
    soup = BeautifulSoup(page_source, 'html.parser')

    # Troba tots els elements amb la classe 'g-section-with-header'
    elements_g_section = soup.find_all('g-section-with-header')

    # Imprimeix o processa els elements trobats
    for element in elements_g_section:

        div_pare = element.find_parent('div').find_parent('div')

        # Cerca el div on ha d'estar el text descriptiu del bloc
        try:
            # Div on ha d'estar el títol de les noticies. En aquest nivell o inferior
            div_text_noticies = div_pare.find('div').find('div').find('div')
        except:
            div_text_noticies = None

        if "Notícies destacades" in str(div_text_noticies):

            with open('./divs.html', 'w', encoding='utf-8') as file:
                file.write(str(div_text_noticies))

            # El aria-level 2 és el text de notícies. Les notícies estan per sota del 2 sempre. El més avall que he vist és lvl 4.
            for i in range(3,5):

                list_noticies = div_pare.find_all('div', {'aria-level': f'{i}'})

                for noticia in list_noticies:

                    # De tot l'element ens basem en el títol
                    titol = noticia.text.replace('\n', '')

                    # Descripció
                    div_descripcio = noticia.find_parent('div').find_all('div')
                    descripcio = div_descripcio[2].find('span').text.replace('\n', '')

                    # Enllaç
                    link = noticia.find_parent('div').find_parent('div').find_parent('div').find('a').get('href')

                    if titol != '' and descripcio != '' and link != '':
                        resultats[resultats_desats] = {"titol":titol, "descripcio:":descripcio, "link":link}
                        resultats_desats += 1

    return (resultats, resultats_desats)

def neteja_descripcio_bing(descripcio_bruta):

    descripcio_neta = descripcio_bruta.replace("fa ", "").replace("LLOC WEB", "").replace("LLOC WEBfa","").replace("Lloc web", "").replace("lloc web", "").replace("Lloc webfa", "").replace("lloc webfa", "").replace("Anunci", "").replace("Resultat del web", "").replace("Mostra'n més", "")
    return (descripcio_neta)

def cerca_dades_bing(resultat):

    # Element pare del <h2> del resultat
    element_pare = resultat.find_element(By.XPATH, '..')

    # Agafa el títol si en té
    titol = None
    try:
        titol = resultat.find_element(By.XPATH, './a').text

        if titol.startswith("Notícies sobre") or titol.startswith("Imatges de:"):
            raise Exception
    except:
        return (False, None, None, None)

    # Agafa l'enllaç si en té
    link = None
    try:
        link = element_pare.find_element(By.XPATH, './/cite').text
        if not link.startswith('http') and not link.startswith('www'):
            link = 'www.' + link
    except NoSuchElementException:
        return (False, None, None, None)

    descripcio_anuncis = None
    descripcio_wikipedia = None
    # Agafa la descripció si en té
    try:
        descripcio_anuncis_brut = element_pare.find_element(By.XPATH, './/div[@class="b_caption"]/div')
        if descripcio_anuncis_brut.text == '':
            descripcio_anuncis_brut = element_pare.find_element(By.XPATH, './/div/p')
        descripcio_anuncis = neteja_descripcio_bing(descripcio_anuncis_brut.text)
    except NoSuchElementException:
        try:
            descripcio_wikipedia_bruta = element_pare.find_element(By.XPATH, './/div/p')
            descripcio_wikipedia = neteja_descripcio_bing(descripcio_wikipedia_bruta.text)
        except NoSuchElementException:
            pass

    if descripcio_anuncis:
        descripcio = descripcio_anuncis
    elif descripcio_wikipedia:
        descripcio = descripcio_wikipedia
    else:
        descripcio = None

    return (True, link, titol, descripcio)

