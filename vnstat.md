# Monitorització de la xarxa amb vnStat a Mac

## 1. Instal·lar vnStat

```sh
brew install vnstat # Mac
sudo apt-get install vnstat # Debian
```

---

## 2. Identificar la interfície de xarxa amb IP

Executa:
```sh
ifconfig
```

---

## 3. Iniciar el servei vnStat

**Mac**:
```sh
brew services start vnstat # Mac
brew services list # Comprova

sudo systemctl start vnstat # Debian
sudo systemctl status vnstat # Comprova
```

---

## 4. Afegir la interfície (si cal)

```sh
sudo vnstat --add -i NOM_INTERFICIE
```

Substitueix `NOM_INTERFICIE` pel nom correcte (ex: `eth0`).

---

## 5. Consultar estadístiques d'una interfície concreta

- **Resum general:**
```sh
vnstat -i eth0
```

- **Ús per hores:**
```sh
vnstat -i eth0 -h
```

- **Ús per dies:**
```sh
vnstat -i eth0 -d
```

- **Ús en temps real:**
```sh
vnstat -i eth0 -l
```

- **Llistat de totes les interfícies monitoritzades:**
```sh
vnstat --iflist
```

---

## 6. Notes i consells

- El servei `vnstatd` (daemon) és qui crea i manté la base de dades. Si no està actiu, no es recullen dades.
- Si la interfície no apareix, assegura't que està activa i que el servei funciona.
- Pots deixar el servei funcionant i consultar les estadístiques quan vulguis.

---

## 7. Accés a la base de dades

### Ubicació de la base de dades
```sh
sqlite3 /var/lib/vnstat/vnstat.sql
```

### Comandes bàsiques de SQLite3
- `.tables` - Mostra les taules disponibles
- `.schema NOM_TAULA` - Mostra l'estructura d'una taula
- `.headers on` - Mostra els noms de les columnes
- `.mode column` - Formata la sortida en columnes
- `.quit` - Surt de sqlite3
- `.help` - Mostra l'ajuda

### Consultes útils

**Veure les interfícies monitoritzades:**
```sql
SELECT * FROM info;
```

**Veure les dades per hores:**
```sql
SELECT * FROM hour ORDER BY date DESC LIMIT 24;
```

**Veure les dades per dies:**
```sql
SELECT * FROM day ORDER BY date DESC LIMIT 7;
```

**Veure el trànsit total per dia (en MB):**
```sql
SELECT date, rx/1024/1024 as rx_mb, tx/1024/1024 as tx_mb 
FROM day 
ORDER BY date DESC;
```

**Veure les hores amb més trànsit:**
```sql
SELECT date, hour, rx/1024/1024 as rx_mb, tx/1024/1024 as tx_mb 
FROM hour 
ORDER BY (rx + tx) DESC 
LIMIT 10;
```

---

Fitxer de configuració:

```sh
nano /opt/homebrew/etc/vnstat.conf # Mac
nano /etc/vnstat.conf # Debian
```