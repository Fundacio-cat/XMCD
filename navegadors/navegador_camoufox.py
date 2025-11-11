from camoufox.sync_api import Camoufox
from navegadors.navegador_base import NavegadorBase
import logging
import re
from typing import Dict


class CamoufoxNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        # Configura el valor de self.navegador com a 3 (Camoufox)
        id_navegador_db = 3
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if user_agent:
            try:
                context_ua = self._obte_context_user_agent(user_agent)

                camoufox_instance = Camoufox(
                    headless=False,
                    humanize=True,
                    locale=context_ua["locale"],
                    timezone=context_ua["timezone"]
                )

                browser = camoufox_instance.__enter__()

                context = browser.new_context(
                    user_agent=user_agent,
                    locale=context_ua["locale"],
                    viewport={'width': self.amplada, 'height': self.altura},
                    timezone_id=context_ua["timezone"],
                    extra_http_headers=self._http_headers(context_ua)
                )

                page = context.new_page()
                self._aplica_mode_stealth(page, context_ua, user_agent)

                self.camoufox_instance = camoufox_instance
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
                try:
                    self.page.close()
                except Exception:
                    pass
            if hasattr(self, 'context') and self.context:
                try:
                    self.context.close()
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

    def _http_headers(self, context_ua: Dict[str, str]) -> Dict[str, str]:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': context_ua["accept_languages"],
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def _aplica_mode_stealth(self, page, context_ua: Dict[str, str], user_agent: str) -> None:
        """Injecta JavaScript per eliminar rastres d'automatització."""
        try:
            user_agent_js = user_agent.replace("\\", "\\\\").replace("'", "\\'")
            platform_js = context_ua["platform"].replace("\\", "\\\\").replace("'", "\\'")
            oscpu_js = context_ua["oscpu"].replace("\\", "\\\\").replace("'", "\\'")
            languages_array = "[" + ", ".join(f"'{lang}'" for lang in context_ua["navigator_languages"]) + "]"

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
                    patch(navigator, 'platform', '{platform_js}');
                    patch(navigator, 'oscpu', '{oscpu_js}');
                    patch(navigator, 'language', '{context_ua["navigator_languages"][0]}');
                    patch(navigator, 'languages', {languages_array});
                    patch(navigator, 'vendor', '{context_ua["vendor"]}');
                    patch(navigator, 'hardwareConcurrency', {context_ua["hardware_concurrency"]});
                    patch(navigator, 'deviceMemory', {context_ua["device_memory"]});
                    patch(navigator, 'maxTouchPoints', {context_ua["max_touch_points"]});
                    patch(navigator, 'plugins', [
                        {{ name: "PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format" }},
                        {{ name: "Widevine Content Decryption Module", filename: "widevinecdm", description: "Enables Widevine licenses" }},
                        {{ name: "Shockwave Flash", filename: "NPSWF32_32_0_0_465.dll", description: "Shockwave Flash 32.0 r0" }}
                    ]);

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

    def _obte_context_user_agent(self, user_agent: str) -> Dict[str, str]:
        """Construeix propietats coherents a partir del user-agent."""
        ua_lower = user_agent.lower()
        context = {
            "platform": "Win32",
            "oscpu": "Windows NT 10.0; Win64; x64",
            "locale": "ca-ES",
            "accept_languages": "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6",
            "navigator_languages": ["ca-ES", "ca", "es", "en"],
            "vendor": "",
            "hardware_concurrency": 8,
            "device_memory": 8,
            "max_touch_points": 0,
            "timezone": "Europe/Madrid"
        }

        if "mac os x" in ua_lower or "macintosh" in ua_lower:
            context.update({
                "platform": "MacIntel",
                "oscpu": "Intel Mac OS X 10_15_7",
                "vendor": "Apple Computer, Inc.",
                "hardware_concurrency": 8,
                "device_memory": 8,
                "max_touch_points": 0,
                "timezone": "Europe/Madrid"
            })
        elif "linux" in ua_lower and "android" not in ua_lower:
            context.update({
                "platform": "Linux x86_64",
                "oscpu": "Linux x86_64",
                "vendor": "",
                "hardware_concurrency": 12,
                "device_memory": 16,
                "max_touch_points": 1,
                "timezone": "Europe/Madrid"
            })
        elif "android" in ua_lower:
            context.update({
                "platform": "Linux armv8l",
                "oscpu": "Linux armv8l",
                "vendor": "Google Inc.",
                "hardware_concurrency": 8,
                "device_memory": 4,
                "max_touch_points": 5,
                "timezone": "Europe/Madrid"
            })

        match = re.search(r"\(([^)]+)\)", user_agent)
        if match:
            context["oscpu"] = match.group(1)

        return context

