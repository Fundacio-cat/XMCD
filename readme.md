# Xarxa de monitoratge del català digital

## Fundació .cat
## Versió 1.0 posada en marxa el 29-04-24


Cada sensor té una password i un usuari personalitzat. 

git clone https://github.com/paufundacio/XMCD.git


### Crontab de cada sensor

```bash
*/15 9-21 * * 1-5 bash /home/catalanet/XMCD/executa_catalanet.bash
0 1 * * * sudo /sbin/shutdown -r # Reinicia a la 1 de la matinada cada dia
```




















