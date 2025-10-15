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
                # Inicialitza Camoufox amb les opcions necessàries
                # Camoufox retorna directament un BrowserContext de Playwright
                browser = Camoufox(
                    headless=False,
                    humanize=True,  # Afegeix comportament humà
                    locale='ca-ES',  # Català
                    user_agent=user_agent
                )
                
                # Crea una nova pàgina directament (Camoufox és un BrowserContext)
                page = browser.new_page()
                
                # Estableix la mida de la finestra
                page.set_viewport_size({'width': self.amplada, 'height': self.altura})
                
                # Guarda la referència a la pàgina per utilitzar-la més tard
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
            if self.browser:
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

