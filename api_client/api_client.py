from utils.config import Config
import requests
import json

from datetime import datetime


class ApiClient:
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.base_url
        self.headers = {'Accept-Charset': 'UTF-8'}

    def create_resultat(self, cerca_id, posicio, titol, url, descripcio, noticia):
        data = {
            "sensor": self.config.sensor,
            "hora": datetime.now().isoformat(),  # O una data específica en format ISO 8601
            "navegador": "Chrome",
            "cercador": "Google",
            "cercaId": cerca_id,
            "posicio": posicio,
            "titol": titol,
            "url": url,
            "descripcio": descripcio,
            "noticia": noticia
        }
        response = requests.post(f"{self.base_url}/v1/resultats", json=data)
        return response.status_code, response.text

    def obtenir_seguent_cerca(self, sensor):
        url = f"{self.base_url}/v1/seguent_cerca/{sensor}"
        response = requests.get(url)
        if response.status_code == 200:
            # Retorna només el camp 'consulta'
            consulta = response.content.decode('utf-8')
            return json.loads(consulta).get("consulta")
        else:
            return None  # O gestionar l'error com consideris

    def obtenir_user_agent(self, nom_navegador):
        url = f"{self.base_url}/v1/useragent/{nom_navegador}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Retorna el user agent com a text
        else:
            return None  # O gestiona l'error com consideris
