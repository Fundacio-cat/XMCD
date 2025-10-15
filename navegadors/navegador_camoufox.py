from camoufox.sync_api import Camoufox
from navegadors.navegador_base import NavegadorBase
import logging


class CamoufoxNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        # Configura el valor de self.navegador com a 3 (Camoufox)
        id_navegador_db = 3
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if user_agent:
            try:
                # Inicialitza Camoufox - retorna un context manager
                # Cal utilitzar-lo sense 'with' per mantenir-lo obert
                camoufox_instance = Camoufox(
                    headless=False,
                    humanize=True,  # Afegeix comportament humà
                    locale='ca-ES',  # Català
                    user_agent=user_agent
                )
                
                # Camoufox utilitza __enter__ per inicialitzar
                browser = camoufox_instance.__enter__()
                
                # Ara browser és un BrowserContext i té new_page()
                page = browser.new_page()
                
                # Estableix la mida de la finestra
                page.set_viewport_size({'width': self.amplada, 'height': self.altura})
                
                # Guarda les referències per utilitzar-les més tard
                self.camoufox_instance = camoufox_instance
                self.page = page
                
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Camoufox: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Camoufox")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser
    
    def tanca_navegador(self):
        """
        Tanca el navegador Camoufox.
        """
        try:
            if hasattr(self, 'page') and self.page:
                self.page.close()
            if hasattr(self, 'camoufox_instance') and self.camoufox_instance:
                # Crida __exit__ per tancar correctament el context manager
                self.camoufox_instance.__exit__(None, None, None)
            elif self.browser:
                self.browser.close()
        except Exception as e:
            self.config.write_log(
                f"Error tancant el navegador Camoufox: {e}", level=logging.ERROR)
    
    def captura_pantalla(self, nom: str) -> None:
        """
        Realitza una captura de pantalla amb Camoufox.

        Args:
        - nom: Nom del fitxer on es guardarà la captura.
        """
        try:
            if hasattr(self, 'page') and self.page:
                self.page.screenshot(path=nom, full_page=False)
        except Exception as e:
            self.config.write_log(
                f"Error capturant la pantalla: {e}", level=logging.ERROR)

