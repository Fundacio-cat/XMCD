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
                # Inicialitza Camoufox amb configuració bàsica compatible
                camoufox_instance = Camoufox(
                    headless=False,
                    humanize=True,  # Afegeix comportament humà
                    locale='ca-ES'  # Català
                )
                
                # Camoufox utilitza __enter__ per inicialitzar
                # Retorna un Playwright Browser object
                browser = camoufox_instance.__enter__()
                
                # Crea una nova pàgina amb user_agent personalitzat
                page = browser.new_page(user_agent=user_agent)
                
                # Estableix la mida de la finestra
                page.set_viewport_size({'width': self.amplada, 'height': self.altura})
                
                # Afegeix headers addicionals per semblar més humà
                page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'ca-ES,ca;q=0.9,es;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                })
                
                # Injecta JavaScript per ocultar traces d'automatització
                page.add_init_script("""
                    // Elimina traces de webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Modifica la propietat plugins per semblar més real
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Modifica la propietat languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['ca-ES', 'ca', 'es', 'en'],
                    });
                    
                    // Modifica la propietat platform
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'MacIntel',
                    });
                    
                    // Modifica la propietat hardwareConcurrency
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8,
                    });
                    
                    // Modifica la propietat deviceMemory
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8,
                    });
                    
                    // Elimina traces de Chrome automation
                    window.chrome = {
                        runtime: {},
                    };
                    
                    // Modifica la propietat permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // Modifica la propietat getParameter
                    const getParameter = WebGLRenderingContext.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.';
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris OpenGL Engine';
                        }
                        return getParameter(parameter);
                    };
                """)
                
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

