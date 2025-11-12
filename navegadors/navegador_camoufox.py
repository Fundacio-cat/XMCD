from camoufox.sync_api import Camoufox
from navegadors.navegador_base import NavegadorBase
import logging


class CamoufoxNavegador(NavegadorBase):

    def init_navegador(self):
        # Configura el valor de self.navegador com a 3 (Camoufox)
        id_navegador_db = 3
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if not user_agent:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")

        try:
            camoufox_instance = Camoufox(
                headless=False,
                humanize=True,
                locale='ca-ES'
            )

            browser = camoufox_instance.__enter__()
            page = browser.new_page(user_agent=user_agent)
            page.set_viewport_size({'width': self.amplada, 'height': self.altura})
            page.set_default_timeout(max(self.config.temps_espera_cerques * 1000, 45000))
            page.set_default_navigation_timeout(max(self.config.temps_espera_cerques * 1000, 45000))

            self._aplica_mode_stealth(page, user_agent)

            self.camoufox_instance = camoufox_instance
            self.browser = browser
            self.page = page

        except Exception as e:
            self.config.write_log(
                f"Error iniciant el navegador Camoufox: {e}", level=logging.ERROR)
            raise ValueError("Error iniciant el navegador Camoufox")

        return id_navegador_db, browser
    
    def tanca_navegador(self):
        """
        Tanca el navegador Camoufox.
        """
        try:
            if hasattr(self, 'page') and self.page:
                try:
                    self.page.close()
                except Exception:
                    pass
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

    def _aplica_mode_stealth(self, page, user_agent: str) -> None:
        """Injecta JavaScript per ocultar rastres d'automatització bàsics."""
        try:
            user_agent_js = user_agent.replace("\\", "\\\\").replace("'", "\\'")
            script = f"""
                (() => {{
                    const patch = (object, property, value) => {{
                        try {{
                            Object.defineProperty(object, property, {{
                                configurable: true,
                                get: () => value
                            }});
                        }} catch (error) {{
                            console.warn('No s\\'ha pogut sobrescriure', property, error);
                        }}
                    }};

                    patch(navigator, 'webdriver', undefined);
                    patch(navigator, 'userAgent', '{user_agent_js}');
                    patch(navigator, 'languages', ['ca-ES', 'ca', 'es', 'en']);
                    patch(navigator, 'language', 'ca-ES');
                    patch(navigator, 'vendor', '');
                    patch(navigator, 'platform', navigator.platform || 'Win32');
                    patch(navigator, 'hardwareConcurrency', navigator.hardwareConcurrency || 4);
                    patch(navigator, 'deviceMemory', navigator.deviceMemory || 4);
                    patch(navigator, 'maxTouchPoints', navigator.maxTouchPoints || 0);
                    patch(navigator, 'plugins', [1, 2, 3, 4]);

                    if (!window.chrome) {{
                        patch(window, 'chrome', {{ runtime: {{}} }});
                    }}

                    if (navigator.permissions && navigator.permissions.query) {{
                        const originalQuery = navigator.permissions.query.bind(navigator.permissions);
                        navigator.permissions.query = (parameters) => {{
                            if (parameters && parameters.name === 'notifications' && typeof Notification !== 'undefined') {{
                                return Promise.resolve({{ state: Notification.permission }});
                            }}
                            return originalQuery(parameters);
                        }};
                    }}
                }})();
            """
            page.add_init_script(script)
        except Exception as e:
            self.config.write_log(
                f"No s'ha pogut aplicar el mode stealth al Camoufox: {e}", level=logging.WARNING)