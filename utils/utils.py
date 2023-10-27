import socket


def nom_sensor():
    """
    Retorna el nom del host del sistema operatiu. 
    Aquesta funció ha estat modificada per ser compatible tant amb Linux com amb Windows.

    Returns:
    - string: Els primers 5 caràcters del nom del host. Si hi ha un error, retorna None.
    """
    try:
        # Obté el nom complet del host utilitzant la biblioteca socket.
        # Aquest mètode és multiplataforma i funciona tant en Linux com en Windows.
        hostname = socket.gethostname()

        # Agafa els primers 5 caràcters del nom del host.
        sensor = hostname[:5]
        return sensor
    except Exception as e:
        # Registra l'error si es produeix algun problema obtenint el nom del host.
        print(f"Error obtenint el nom del sensor: {e}")
        return None
