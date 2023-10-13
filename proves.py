# Postgres
import psycopg2
from credencials import obtenir_credentials_oficina


# Agafa les credencials per al sensor de la oficina
host, port, database, user, password = obtenir_credentials_oficina()

configuracio = {
    'host': host,
    'port': port,
    'database': database,
    'user': user,
    'password': password,
}

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

    return cerca

cerca = cerca_cerca(conn, cursor, 'kakkz')

print ([cerca])