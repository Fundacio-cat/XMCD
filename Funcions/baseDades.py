
def guarda(conn, cursor, sensor, consulta, navegador, cercador, posicio, titol, url, descripcio, llengua):

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

    # Executar la instrucció SQL per inserir dades a la base de dades
    insert_query = "INSERT INTO cerques (sensor, hora, navegador, cercador, posicio, titol, url, descripcio, llengua) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {});".format(sensor, consulta, navegador, cercador, posicio, titol, url, descripcio, llengua)

    # Executar la consulta amb els valors
    cursor.execute(insert_query)

    # Fer commit per desar els canvis a la base de dades
    conn.commit()