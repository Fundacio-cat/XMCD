# -*- coding: utf-8 -*-

# Connecta BD
import psycopg2

# Guarda BD
from datetime import datetime
from credentials import obtenir_credentials

# Funció per a connectar-se a la BD. Agafa les credencials del fitxer credencials.py
def connecta_bd():

    # Agafa les credencials per al sensor de la oficina
    host, port, database, user, password = obtenir_credentials()

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
    # Si falla la connexió retorna fals 
    except:    
        return False
    finally:
        return conn, cursor 

# Funció per registrar errors a la base de dades 
def registra_error(conn, cursor, error): 
    
    try: 
        # Registra l'error a la taula de registre (log) 
        sql = "INSERT INTO registre_errors (data, descripcio) VALUES (CURRENT_TIMESTAMP, %s)" 
        cursor.execute(sql, (str(error),)) 
        conn.commit() 

    except psycopg2.Error as db_error: 
        # Gestió d'errors relacionats amb la base de dades 
        print("Error en la connexió a PostgreSQL:", db_error) 

    finally: 
        if conn is not None: 
            conn.close() 

# Guarda a la base de dades els resultats de la cerca
def guarda_bd(conn, cursor, sensor, navegador, cercador, cerca, posicio, titol, url, descripcio):

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

    if titol is not None:
        titol = titol.replace("'", "''")

    if descripcio is not None:
        descripcio = descripcio.replace("'", "''")

    # Executar la instrucció SQL per inserir dades a la base de dades
    insert_query = "INSERT INTO resultats (sensor, hora, navegador, cercador, cerca, posicio, titol, url, descripcio) VALUES ('{}', '{}', {}, {}, '{}', {}, '{}', '{}', '{}', '{}');".format(
        sensor, now, navegador, cercador, cerca, posicio, titol, url, descripcio)

    # Executar la consulta amb els valors
    cursor.execute(insert_query)

    # Fer commit per desar els canvis a la base de dades
    conn.commit()

def cerca_userAgent(cursor, navegador):

    select_query = f"SELECT useragent FROM navegadors WHERE navId = {navegador};"
    cursor.execute(select_query)
    resultat = cursor.fetchone()

    if resultat:
        useragent = str(resultat[0])
        return useragent
    else:
        return None