from cercadors.cercador_base import CercadorBase


class BingCercador(CercadorBase):
    def __init__(self, config):
        super().__init__(config)

    def inicia_cercador(self, browser):
        raise NotImplementedError(
            "Método 'inicia_cercador' no implementado para BingCercador")

    def executa_cerca(self, browser, cerca):
        raise NotImplementedError(
            "Método 'executa_cerca' no implementado para BingCercador")

    def guarda_resultats(self, browser, directori_Imatges, navegador, sensor, cerca):
        raise NotImplementedError(
            "Método 'guarda_resultats' no implementado para BingCercador")
