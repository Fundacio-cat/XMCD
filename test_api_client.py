from api_client.api_client import ApiClient
from utils.config import Config

# Exemple d'ús
if __name__ == "__main__":
    config = Config.carrega_config("config_win.json")
    print(f"Base URL: {config.base_url}")
    client = ApiClient(config)
    consulta = client.obtenir_seguent_cerca("jwuuh")
    if consulta:
        print(f"Consulta: {consulta}")
    else:
        print("No s'ha trobat la cerca o hi ha hagut un error.")

    # Reemplaça amb l'URL de la teva API
    status_code, response_text = client.create_resultat(
        "sensr1", "chrome", "Google", 1, 1, "titol", "url", "descripcio", "ca", True)
    print(f"Status Code: {status_code}, Response: {response_text}")
