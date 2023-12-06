from api_client.api_client import ApiClient, ElementNoTrobatError, ErrorDeSollicitudAPI
from utils.config import Config

# Exemple d'ús
if __name__ == "__main__":
    config = Config.carrega_config("config_win.json")
    print(f"Base URL: {config.base_url}")
    client = ApiClient(config)
    try:
        consulta = client.obtenir_seguent_cerca("jwuuh")
        if consulta:
            print(f"Consulta: {consulta}")
        else:
            print("No s'ha trobat la cerca o hi ha hagut un error.")
    except ElementNoTrobatError as e:
        print(f"ElementNoTrobatError: {e}")
    except ErrorDeSollicitudAPI as e:
        print(f"ErrorDeSollicitudAPI: {e}")
    except Exception as e:
        print(f"Error: {e}")

    try:
        # Reemplaça amb l'URL de la teva API
        status_code, response_text = client.create_resultat(
            1, 1, "Títol", "https://www.example.com", "Descripció", "true")
        print(f"Status Code: {status_code}, Response: {response_text}")
    except ElementNoTrobatError as e:
        print(f"ElementNoTrobatError: {e}")
    except ErrorDeSollicitudAPI as e:
        print(f"ErrorDeSollicitudAPI: {e}")
    except Exception as e:
        print(f"Error: {e}")

    try:
       # test obtenir_user_agent
        user_agent = client.obtenir_user_agent("Chrome")
        if user_agent:
            print(f"User Agent: {user_agent}")
        else:
            print("No s'ha trobat el user agent o hi ha hagut un error.")
    except ElementNoTrobatError as e:
        print(f"ElementNoTrobatError: {e}")
    except ErrorDeSollicitudAPI as e:
        print(f"ErrorDeSollicitudAPI: {e}")
    except Exception as e:
        print(f"Error: {e}")

    # test obtenir_user_agent
    try:
        user_agent = client.obtenir_user_agent("navegador_inextistent")
    except ElementNoTrobatError as e:
        print(f"Error: {e}")
    except ErrorDeSollicitudAPI as e:
        print(f"Error: {e}")
    else:
        print(f"User Agent: {user_agent}")
