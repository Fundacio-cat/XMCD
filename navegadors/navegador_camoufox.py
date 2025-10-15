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
                # Utilitza l'API de Playwright de Camoufox però adaptat per a ús amb Selenium
                browser = Camoufox(
                    headless=False,
                    humanize={'mouse': True, 'typing': True},  # Afegeix comportament humà
                    locale='ca-ES',  # Català
                    user_agent=user_agent,
                    addons=[]
                )

                # Crea una nova pàgina
                context = browser.new_context(
                    viewport={'width': self.amplada, 'height': self.altura},
                    locale='ca-ES', # Català
                    timezone_id='Europe/Madrid' # Temps local
                )
                page = context.new_page()
                
                # Guarda les referències per utilitzar-les més tard
                self.context = context
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
            if hasattr(self, 'context') and self.context:
                self.context.close()
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

