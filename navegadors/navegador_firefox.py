from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from navegadors.navegador_base import NavegadorBase
import os
import logging


class FirefoxNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        # Configura el valor de self.navegador com a 1 (Chrome)
        id_navegador_db = 2
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36.'

        if user_agent:
            options = Options()
            #options.add_argument(f"user-agent={user_agent}")
            options.set_preference('intl.accept_languages', 'ca')
            driver_path = os.path.join(
                self.config.current_directory, "Controladors", self.config.FIREFOX_DRIVER_PATH)
            service = Service(driver_path)
            try:
                browser = webdriver.Firefox(service=service, options=options)
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Firefox: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Firefox")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser
