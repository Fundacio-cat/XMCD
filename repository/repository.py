# -*- coding: utf-8 -*-

import psycopg2
import logging
from datetime import datetime
from utils.config import Config


class Repository:
    def __init__(self, config: Config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connecta_bd(self):
        try:
            # Obtenir les credencials de la configuració
            host = self.config.host
            port = self.config.port
            database = self.config.database
            user = self.config.user
            password = self.config.password

            configuracio = {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password,
            }

            # Connectar a la BD
            self.conn = psycopg2.connect(**configuracio)
            self.cursor = self.conn.cursor()

        except Exception as e:
            self.config.write_log(f"Error en la connexió a PostgreSQL: {e}",
                                  level=logging.ERROR)
            raise ValueError(f"Error en la connexió a PostgreSQL: {e}")

    def registra_error(self, error):
        try:
            # Registrar l'error a la taula de registre (log)
            sql = "INSERT INTO registre_errors (data, descripcio) VALUES (CURRENT_TIMESTAMP, %s)"
            self.cursor.execute(sql, (str(error),))
            self.conn.commit()
        except psycopg2.Error as db_error:
            self.config.write_log(f"Error en la connexió a PostgreSQL: {db_error}",
                                  level=logging.ERROR)

    def guarda_bd(self, int_cerca, posicio, titol, url, descripcio, noticia):
        try:
            now = datetime.now()
            if titol is not None:
                titol = titol.replace("'", "''")

            if descripcio is not None:
                descripcio = descripcio.replace("'", "''")

            insert_query = "INSERT INTO resultats (sensor, hora, navegador, cercador, cerca, posicio, titol, url, descripcio, noticia) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (self.config.sensor, now, self.config.navegador.id_navegador_db,
                      self.config.cercador.id_cercador_db,
                      int_cerca, posicio, titol, url, descripcio, noticia)

            self.cursor.execute(insert_query, values)
            self.conn.commit()
        except psycopg2.Error as db_error:
            self.config.write_log(f"Error en la connexió a PostgreSQL: {db_error}",
                                  level=logging.ERROR)

    def mock_guarda_bd(self, int_cerca, posicio, titol, url, descripcio, noticia):
        try:
            now = datetime.now()
            if titol is not None:
                titol = titol.replace("'", "''")

            if descripcio is not None:
                descripcio = descripcio.replace("'", "''")

            insert_query = "INSERT INTO resultats (sensor, hora, navegador, cercador, cerca, posicio, titol, url, descripcio, noticia) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (self.config.sensor, now,
                      self.config.navegador.id_navegador_db,
                      self.config.cercador.id_cercador_db,
                      int_cerca, posicio, titol, url, descripcio, noticia)

            # self.cursor.execute(insert_query, values)
            # self.conn.commit()
            # scriu la query per pantalla
            print(insert_query % values)
        except psycopg2.Error as db_error:
            self.config.write_log(f"Error en la connexió a PostgreSQL: {db_error}",
                                  level=logging.ERROR)

    def cerca_userAgent(self, navegador):
        try:
            select_query = f"SELECT useragent FROM navegadors WHERE navId = {navegador};"
            self.cursor.execute(select_query)
            resultat = self.cursor.fetchone()
            if resultat:
                useragent = str(resultat[0])
                return useragent
            else:
                return None
        except psycopg2.Error as db_error:
            self.config.write_log(
                f"Error en la connexió a PostgreSQL: {db_error}", level=logging.ERROR)
            return None

    def seguent_cerca(self, sensor):
        try:
            # Executar la instrucció SQL per obtenir l'ID de la següent cerca
            select_integral = "SELECT seguent_cerca_filtrada('{}');".format(sensor)
            self.cursor.execute(select_integral)
            int_cerca = self.cursor.fetchone()[0]

            # Executar la instrucció SQL per obtenir la consulta str de la cerca
            select_cerca = "SELECT consulta FROM cerques WHERE cerqId = {};".format(int_cerca)
            self.cursor.execute(select_cerca)
            cerca = self.cursor.fetchone()[0]
            return int_cerca, cerca
        except psycopg2.Error as db_error:
            self.config.write_log(
                f"Error en la connexió a PostgreSQL: {db_error}", level=logging.ERROR)
            return None, None
        

    def selecciona_navegador(self):
        try:
            # Executar la instrucció SQL per obtenir l'ID de la següent cerca
            select_navegador = "SELECT selecciona_navegador();"
            self.cursor.execute(select_navegador)
            int_navegador = self.cursor.fetchone()[0]

            return int_navegador

        except psycopg2.Error as db_error:
            self.config.write_log(
                f"Error en la connexió a PostgreSQL: {db_error}", level=logging.ERROR)
            return None, None
        
    def selecciona_cercador(self):
        try:
            # Executar la instrucció SQL per obtenir l'ID de la següent cerca
            select_navegador = "SELECT selecciona_cercador();"
            self.cursor.execute(select_navegador)
            int_cercador = self.cursor.fetchone()[0]

            return int_cercador

        except psycopg2.Error as db_error:
            self.config.write_log(
                f"Error en la connexió a PostgreSQL: {db_error}", level=logging.ERROR)
            return None, None

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
