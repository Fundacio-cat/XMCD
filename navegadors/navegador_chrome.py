from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from repository.repository import Repository
from navegadors.navegador_base import NavegadorBase
from utils.config import Config
import os
import logging


class ChromeNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        # Configura el valor de self.navegador com a 1 (Chrome)
        id_navegador_db = 1
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if user_agent:
            options = Options()
            options.add_argument(f"user-agent={user_agent}")
            # NO FUNCIONA:
            #options.add_argument("--lang=en")
            #options.add_argument("--headless")
            # NO S'HA PROVAT REALMENT
            #options.add_argument("--no-sandbox")
            #options.add_argument("--disable-dev-shm-usage")
            #options.add_argument("--disable-gpu")
            #options.add_argument("--remote-debugging-port=9222")

            # posar driver_path = config.current_directory+"/Controladors/" + config.CHROME_DRIVER_PATH
            driver_path = os.path.join(
                self.config.current_directory, "Controladors", self.config.CHROME_DRIVER_PATH)

            service = Service(driver_path)

            try:
                browser = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Chrome: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Chrome")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser
