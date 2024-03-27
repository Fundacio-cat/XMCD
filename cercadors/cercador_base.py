from abc import ABC, abstractmethod
from utils.config import Config


class CercadorBase(ABC):
    def __init__(self, config: Config):
        # try except si config o cursor no existeixen
        # generen un error de configuració i no es pot continuar
        try:
            self.config = config
            self.navegador = config.navegador
            self.browser = config.navegador.browser
            self.id_cercador_db = self.inicia_cercador()
        except:
            raise ValueError("Error de configuració del navegador. No es troba el navegador. Potser ha petat abans")

    """
    Crea un cercador a partir de la configuració i el navegador.
    Es crida directament al constructor de la classe cercador.
    dispara un error si no es pot crear el cercador.
    retorna el identificador de cercador de la base de dades.
    """
    @abstractmethod
    def inicia_cercador(self) -> int:
        pass

    @abstractmethod
    def guarda_resultats(self, cerca):
        pass
