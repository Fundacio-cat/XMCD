# Xarxa de monitoratge del català digital

### 1. Què fa la Xarxa de Monitoratge del Català Digital (XMCD)?

La Xarxa de Monitoratge del Català Digital (XMCD) té com a objectiu monitoritzar el posicionament del català en l'entorn digital mitjançant una xarxa de sensors. Aquests sensors estan desplegats en diverses localitzacions dels territoris de parla catalana i altres regions, i realitzen cerques automatitzades diàries als principals motors de cerques per recollir les dades dels resultats obtinguts.

Els sensors recullen informació de les cerques realitzades, com ara el títol del resultat, la seva descripció, la URL i, el més important, la posició del resultat en els 10 primers resultats de Google. Aquests resultats aleshores es guarden a una base de dades centralitzada per a ser analitzats posteriorment.

---

### 2. Per què existeix la XMCD?

La presència del català en el món digital és crucial per a la seva supervivència i promoció. Sovint, però, no es disposa de dades sobre com apareixen els continguts en català en motors de cerca com Google. La XMCD existeix per monitoritzar aquesta informació de forma automatitzada, proporcionant dades valuoses per analitzar la visibilitat del català en l'entorn digital.

Amb aquest sistema de monitorització es poden identificar tendències i possibles problemàtiques en el posicionament del català a internet, així com ajudar en futures iniciatives per millorar-ne la presència.

### 2. Per què existeix la XMCD?

En els darrers mesos, s'ha detectat una disminució significativa de la presència de pàgines web en català en els resultats dels cercadors, fins i tot quan l'usuari té configurat el seu entorn de navegació per donar preferència al català. Aquesta situació, observada des del 2022, afecta negativament la visibilitat del català en l'entorn digital, i no se'n coneix encara el motiu, malgrat les consultes realitzades a empreses de cerca.

La XMCD neix amb l'objectiu de monitoritzar de manera sistemàtica i automàtica la visibilitat del català en els principals motors de cerca, com ara Google, recopilant dades que permetin identificar aquest fenomen. Mitjançant aquesta monitorització, es poden analitzar les tendències, detectar problemes en el posicionament del català i contribuir a revertir aquesta situació. 

---

### 3. Com funciona la XMCD?

Els sensors desplegats realitzen un procés de monitorització cada 15 minuts entre les 9h i les 22h, aquest procés consisteix en la cerca d'un descriptor al motor de cerca corresponent i obtenint-ne els resultats, simulant així l'ús que podria fer un usuari real. El funcionament general detallat és el següent:

1. El sensor consulta el servidor central per obtenir el descriptor que ha de cercar.
2. Un cop té la informació necessària, inicia el navegador corresponent (actualment, Google Chrome o Firefox).
3. El sensor accedeix a Google i executa la cerca.
4. Quan es carreguen els resultats, el sensor obté les dades dels 10 primers resultats de cerca (títol, descripció, URL i posició).
5. Si no obté 10 resultats a la primera pàgina, continua buscant a les següents pàgines fins a poder agafar els 10 resultats.
6. Finalment, desa la informació obtinguda a la base de dades central.

Cada sensor disposa de credencials individuals i només pot interactuar amb les seves dades. D'aquesta manera també s'assegura la privacitat de les dades reportades al sistema.

---

### 4. Infraestructura dels sensors

Els sensors de la XMCD estan basats en plaques Raspberry Pi 3B+ que executen el sistema operatiu Raspbian basat en Debian 12 (Bookworm). Per al monitoratge intern del rendiment i funcionament dels sensors, s'utilitza el servei Zabbix.

Cada sensor està connectat a la xarxa central mitjançant una VPN xifrada basada en WireGuard, que garanteix una connexió segura amb el servidor central. Els sensors només necessiten connexió elèctrica i accés a la xarxa a través de cablejat, sense accedir a la xarxa privada del col·laborador.

---

### 5. Servidor central

El servidor central és on es desa tota la informació recollida pels sensors. Aquest servidor, gestionat per la Fundació .cat, està connectat amb tots els sensors de la xarxa i gestiona totes les operacions que aquests realitzen, com ara indicar quines cerques han de fer, amb quin cercador o amb quin navegador.

La comunicació entre el servidor central i els sensors es fa a través de la VPN configurada amb WireGuard. La comunicació és bidireccional entre el servidor central i cada sensor, però els sensors no poden comunicar-se entre ells.

##### Fundació .cat
##### Versió 1.0 posada en marxa el 29-04-24
###
