# -*- coding: utf-8 -*-

################# Imports #################

from credencials import obtenir_credentials

host, port, database, user, password = obtenir_credentials()

print (host, port, database, user, password)