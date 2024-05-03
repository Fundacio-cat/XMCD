#!/bin/bash
#
# /home/catalanet/XMCD/executa_catalanet.bash
# Llançament de consultes aleatòries
# Versió 0.0.1
#
home_catalanet_monitor=/home/catalanet/XMCD
arxiuregistre=$home_catalanet_monitor/logs/monitor.log
echo "Iniciant el procés catalanet amb logs a $arxiuregistre"

# Calcula un retard aleatori entre 0 i 14 minuts
# 1 execució per hora
retard=$(($RANDOM%(14-1)+1))
#echo "Iniciant el procés després d'un retard de $retard minuts"
sleep ${retard}m

# Executa l'script en un subshell, canvia al directori i executa el comandament,
# redireccionant qualsevol sortida a /dev/null (descarta la sortida)
(cd $home_catalanet_monitor; xvfb-run -a python3 monitor.py) >> /dev/null  2>&1 &

# Registra la data i hora de l'execució
date >> $arxiuregistre 2>&1
