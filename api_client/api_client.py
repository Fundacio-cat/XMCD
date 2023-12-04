import requests
import json
from datetime import datetime


class ResultatApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def create_resultat(self, sensor, navegador, cercador, cerca_id, posicio, titol, url, descripcio, llengua, noticia):
        data = {
            "sensor": sensor,
            "hora": datetime.now().isoformat(),  # O una data específica en format ISO 8601
            "navegador": navegador,
            "cercador": cercador,
            "cercaId": cerca_id,
            "posicio": posicio,
            "titol": titol,
            "url": url,
            "descripcio": descripcio,
            "llengua": llengua,
            "noticia": noticia
        }
        response = requests.post(f"{self.base_url}/v1/resultats", json=data)
        return response.status_code, response.text


# Exemple d'ús
if __name__ == "__main__":
    # Reemplaça amb l'URL de la teva API
    client = ResultatApiClient("http://localhost:8080")
    status_code, response_text = client.create_resultat(
        "sensr1", "chrome", "Google", 1, 1, "titol", "url", "descripcio", "ca", True)
    print(f"Status Code: {status_code}, Response: {response_text}")
