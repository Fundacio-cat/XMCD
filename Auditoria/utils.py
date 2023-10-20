# -*- coding: utf-8 -*-

### IMPORTS ###






### FUNCIONS ###

def nom_sensor():
    try:
        # Obre l'arxiu /etc/hostname en mode de lectura
        with open('/etc/hostname', 'r') as arxiu:
            # Llegeix el contingut de l'arxiu
            contingut = arxiu.read()
            # Agafa els primers 5 caràcters
            sensor = contingut[:5]
            return sensor
    except:
        # Si l'arxiu no es troba
        return None