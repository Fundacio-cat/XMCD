# -*- coding: utf-8 -*-

################# Imports #################

from credencials import obtenir_credentials_oficina

sensor, host, port, database, user, password = obtenir_credentials_oficina()

print (sensor, host, port, database, user, password)