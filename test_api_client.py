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
        1, 1, "Títol", "https://www.example.com", "Descripció", "true")

    print(f"Status Code: {status_code}, Response: {response_text}")

    # test obtenir_user_agent
    user_agent = client.obtenir_user_agent("Chrome")
    if user_agent:
        print(f"User Agent: {user_agent}")
    else:
        print("No s'ha trobat el user agent o hi ha hagut un error.")
