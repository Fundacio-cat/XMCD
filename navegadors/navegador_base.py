from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Tuple, Union
from utils.config import Config


class NavegadorBase(ABC):

    def __init__(self, config: Config):
        """
        Inicialitza les variables de classe i crida a la funció init_navegador, implementada per les classes filles.
        """
        try:
            self.config = config
            self.repository = config.repository
            self.id_navegador_db, self.browser = self.init_navegador()
        except:
            raise ValueError(
                "Error de configuració del navegador. No es troba el repository")

    @abstractmethod
    def init_navegador(self) -> Tuple[int, WebDriver]:
        """
        Inicialitza el navegador.
        """
        pass

    def captura_pantalla(self, nom: str) -> None:
        """
        Realitza una captura de pantalla.

        Args:
        - nom: Nom del fitxer on es guardarà la captura.
        """
        self.browser.save_screenshot(nom)

    def tanca_navegador(self):
        """
        Tanca el navegador.
        """
        self.browser.quit()
