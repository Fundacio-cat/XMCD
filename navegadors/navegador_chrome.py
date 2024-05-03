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
            options.add_argument("--lang=ca")
            driver_path = os.path.join(self.config.current_directory, "Controladors", self.config.CHROME_DRIVER_PATH)
            service = Service(driver_path)
            try:
                browser = webdriver.Chrome(service=service, options=options)
                browser.set_window_size(self.amplada, self.altura)
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Chrome: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Chrome")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser
