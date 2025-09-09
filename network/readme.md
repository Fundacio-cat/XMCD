# Perfil de Xarxa

Aquest script permet monitoritzar i analitzar l'estat de la xarxa mitjançant pings periòdics a una adreça IP.

## Funcionalitats principals

### Monitoratge de xarxa
- Realitza pings periòdics a una adreça IP o domini configurada
- Guarda els temps de resposta i timestamps en un fitxer JSON
- Permet configurar la durada del monitoratge i l'interval entre pings

### Anàlisi de dades
- Analitza els patrons d'ús de la xarxa per dia de la setmana i hora
- Calcula estadístiques per cada hora:
  - Temps mitjà de resposta
  - Desviació estàndard
  - Nombre de mostres
- Identifica les hores amb més càrrega de trànsit per cada dia

## Configuració

El script permet configurar els següents paràmetres:
- `target`: Adreça IP o domini al qual fer ping (per defecte: "8.8.8.8")
- `interval`: Segons entre pings (per defecte: 300 segons = 5 minuts)
- `duration_minutes`: Durada del monitoratge en minuts (per defecte: 1440 = 24 hores)
- `data_file`: Fitxer on guardar les dades (per defecte: "network_data.json")
- `threshold_percentile`: Percentil per determinar les hores amb més càrrega (per defecte: 75)
- `min_samples_per_hour`: Mínim de mostres necessàries per considerar una hora vàlida

## Ús

1. Executa el script:
```bash
python perfil_xarxa.py
```

2. El script:
   - Inicia el monitoratge segons la configuració
   - Guarda les dades en el fitxer especificat
   - Al finalitzar, mostra:
     - El perfil complet de xarxa amb estadístiques
     - Les hores recomanades per executar el crawler (hores amb menys càrrega)

## Estructura de dades

Les dades es guarden en format JSON amb la següent estructura:
```json
{
  "dia_setmana": {
    "hora": {
      "mean": temps_mitjà,
      "std_dev": desviació_estàndard,
      "samples": nombre_mostres
    },
    "peak_hours": {
      "hours": [hores_amb_més_càrrega],
      "description": "Descripció"
    }
  }
}
```

## Notes
- Les hores de màxima càrrega es determinen analitzant el percentil superior de temps de resposta
- Es requereix un mínim de mostres per hora per considerar les dades vàlides
- El script mostra els resultats en català, incloent els noms dels dies de la setmana


# Comportament

El perfil de xarxa s'inicia un dilluns de la setmana 0.
Un cop finalitzada la setmana 0, el crawler agafa el perfil de xarxa i s'executa amb les hores determinades. 
A partir de la setmana 1, s'executa el crawler amb les hores definides al perfil, i paral·lelament es va realitzant un altre perfil de xarxa.
Quan acaba la setmana 1, s'actualitza el perfil de xarxa amb els resultats obtinguts durant la setmana. 

# Pendent:

Crear un perfil de xarxa del Catalanet de la oficina i estudiar els resultats.
