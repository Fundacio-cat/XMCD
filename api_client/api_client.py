from utils.config import Config
import requests
import json

from datetime import datetime


class ElementNoTrobatError(Exception):
    """Excepció per quan un element no es troba."""
    pass


class ErrorDeSollicitudAPI(Exception):
    """Excepció genèrica per errors en la sol·licitud a l'API."""

    def __init__(self, status_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code


class ApiClient:
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.base_url
        self.headers = {'Accept-Charset': 'UTF-8'}

    ##
    # Documentació de la crida
    ##
    # POST /v1/resultats
    # {
    # "sensor": "jwuuh",
    # "hora": "2021-05-02T12:00:00",
    # "navegador": "Chrome",
    # "cercador": "Google",
    # "cercaId": 1,
    # "posicio": 1,
    # "titol": "Títol",
    # "url": "https://www.example.com",
    # "descripcio": "Descripció",
    # "noticia": "true"
    # }
    ##
    # Resultat de la funcion
    # 201 Created
    # Location: http://localhost:8080/v1/resultats/1
    # retorna com a resultat
    # -> (201, "http://localhost:8080/v1/resultats/1")
    # Excepcions
    # 404 Not Found: No sha trobat el el sensor, o bé el cercador, o bé el navegador
    # 400 Bad Request: El format de la petició no és correcte
    # 500 Internal Server Error: Error en el servidor
    ##
    def create_resultat(self, cerca_id, posicio, titol, url, descripcio, noticia) -> (int, str):
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
        try:
            response = requests.post(
                f"{self.base_url}/v1/resultats", json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Manejar errors específics de HTTP
            if response.status_code == 404:
                raise ElementNoTrobatError(
                    f"Element no trobat") from e
            else:
                raise ErrorDeSollicitudAPI(
                    response.status_code, f"Error en la sol·licitud a l'API: {e}") from e
        except requests.RequestException as e:
            # Manejar qualsevol altre tipus d'error en la sol·licitud, com problemes de connexió
            raise ErrorDeSollicitudAPI(-1,
                                       f"Error en la connexió a l'API: {e}") from e

        return response.status_code, response.text

    ##
    # Documentació de la crida
    ##
    # GET /v1/seguent_cerca/{sensor}
    ##
    # retorna com a resultat el camp 'consulta'
    # Excepcions
    # 404 Not Found: No sha trobat el el sensor
    # 500 Internal Server Error: Error en el servidor
    ##
    def obtenir_seguent_cerca(self, sensor) -> str:
        url = f"{self.base_url}/v1/seguent_cerca/{sensor}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Retorna només el camp 'consulta'
                consulta = response.content.decode('utf-8')
                return json.loads(consulta).get("consulta")
            else:
                return None  # O gestionar l'error com consideris
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ElementNoTrobatError(
                    f"Element no trobat") from e
            else:
                raise ErrorDeSollicitudAPI(
                    response.status_code, f"Error en la sol·licitud a l'API: {e}") from e
        except requests.RequestException as e:
            # Manejar qualsevol altre tipus d'error en la sol·licitud, com problemes de connexió
            raise ErrorDeSollicitudAPI(-1,
                                       f"Error en la connexió a l'API: {e}") from e

    def obtenir_user_agent(self, nom_navegador) -> str:
        url = f"{self.base_url}/v1/useragent/{nom_navegador}"
        try:
            response = requests.get(url)
            # Això llençarà una excepció per a codis d'estat 4xx i 5xx
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Manejar errors específics de HTTP
            if response.status_code == 404:
                raise ElementNoTrobatError(
                    f"Element no trobat") from e
            else:
                raise ErrorDeSollicitudAPI(
                    response.status_code, f"Error en la sol·licitud a l'API: {e}") from e
        except requests.RequestException as e:
            # Manejar qualsevol altre tipus d'error en la sol·licitud, com problemes de connexió
            raise ErrorDeSollicitudAPI(-1,
                                       f"Error en la connexió a l'API: {e}") from e

        return response.text
