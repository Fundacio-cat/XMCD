from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from navegadors.navegador_base import NavegadorBase
import os
import logging
import re


class FirefoxNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        # Configura el valor de self.navegador com a 1 (Chrome)
        id_navegador_db = 2
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if user_agent:
            options = Options()
            context_ua = self._obte_context_user_agent(user_agent)
            self._configura_opcions_firefox(options, user_agent, context_ua)

            driver_path = os.path.join(self.config.current_directory, "Controladors", self.config.FIREFOX_DRIVER_PATH)
            service = Service(driver_path)
            try:
                browser = webdriver.Firefox(service=service, options=options)
                browser.set_window_size(self.amplada, self.altura)
                self._habilita_mode_stealth(browser, user_agent, context_ua)
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Firefox: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Firefox")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser

    def _configura_opcions_firefox(self, options: Options, user_agent: str, context_ua: dict) -> None:
        """Aplica preferències per reduir la detecció automàtica."""
        options.set_preference("general.useragent.override", user_agent)
        options.set_preference("intl.accept_languages", context_ua["accept_languages"])
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("toolkit.telemetry.enabled", False)
        options.set_preference("toolkit.telemetry.unified", False)
        options.set_preference("toolkit.telemetry.reportingpolicy.firstRun", False)
        options.set_preference("datareporting.healthreport.uploadEnabled", False)
        options.set_preference("browser.sessionstore.resume_from_crash", False)
        options.set_preference("browser.startup.homepage", "about:blank")
        options.set_preference("general.platform.override", context_ua["platform"])
        options.set_preference("general.oscpu.override", context_ua["oscpu"])
        options.set_preference("general.appversion.override", context_ua["appversion"])
        options.set_preference("network.http.accept.default",
                               "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8")
        options.set_preference("network.http.accept-encoding", "gzip, deflate, br")
        options.set_preference("dom.webnotifications.enabled", True)
        options.set_preference("privacy.trackingprotection.enabled", False)

    def _habilita_mode_stealth(self, browser, user_agent: str, context_ua: dict) -> None:
        """Injecta JavaScript per eliminar rastres de WebDriver i imitar valors humans."""
        user_agent_js = user_agent.replace("\\", "\\\\").replace("'", "\\'")
        platform_js = context_ua["platform"].replace("\\", "\\\\").replace("'", "\\'")
        oscpu_js = context_ua["oscpu"].replace("\\", "\\\\").replace("'", "\\'")
        languages_array = "[" + ", ".join(f"'{lang}'" for lang in context_ua["navigator_languages"]) + "]"
        script = f"""
            (() => {{
                const patch = (object, property, value) => {{
                    try {{
                        Object.defineProperty(object, property, {{
                            get: () => value,
                            configurable: true
                        }});
                    }} catch (error) {{
                        console.warn(`No s'ha pogut sobrescriure ${{property}}:`, error);
                    }}
                }};

                patch(navigator, 'webdriver', undefined);
                patch(navigator, 'userAgent', '{user_agent_js}');
                patch(navigator, 'platform', '{platform_js}');
                patch(navigator, 'oscpu', '{oscpu_js}');
                patch(navigator, 'languages', {languages_array});
                patch(navigator, 'language', '{context_ua["navigator_languages"][0]}');
                patch(navigator, 'vendor', '');
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

        try:
            browser.execute_script(script)
        except Exception as e:
            self.config.write_log(
                f"No s'ha pogut aplicar el mode stealth al Firefox: {e}", level=logging.WARNING)

    def _obte_context_user_agent(self, user_agent: str) -> dict:
        """Construeix propietats coherents amb el user-agent proporcionat."""
        ua_lower = user_agent.lower()
        context = {
            "platform": "Win32",
            "oscpu": "Windows NT 10.0; Win64; x64",
            "appversion": "5.0 (Windows)",
            "accept_languages": "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6",
            "navigator_languages": ["ca-ES", "ca", "es", "en"],
            "hardware_concurrency": 8,
            "device_memory": 8,
            "max_touch_points": 0,
        }

        if "mac os x" in ua_lower or "macintosh" in ua_lower:
            context.update(
                {
                    "platform": "MacIntel",
                    "oscpu": "Intel Mac OS X 10.15",
                    "appversion": "5.0 (Macintosh)",
                    "accept_languages": "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6",
                    "navigator_languages": ["ca-ES", "ca", "es", "en"],
                    "hardware_concurrency": 8,
                    "device_memory": 8,
                    "max_touch_points": 0,
                }
            )
        elif "linux" in ua_lower and "android" not in ua_lower:
            context.update(
                {
                    "platform": "Linux x86_64",
                    "oscpu": "Linux x86_64",
                    "appversion": "5.0 (X11)",
                    "accept_languages": "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6",
                    "navigator_languages": ["ca-ES", "ca", "es", "en"],
                    "hardware_concurrency": 12,
                    "device_memory": 16,
                    "max_touch_points": 1,
                }
            )
        elif "android" in ua_lower:
            context.update(
                {
                    "platform": "Linux armv8l",
                    "oscpu": "Linux armv8l",
                    "appversion": "5.0 (Android)",
                    "accept_languages": "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6",
                    "navigator_languages": ["ca-ES", "ca", "es", "en"],
                    "hardware_concurrency": 8,
                    "device_memory": 4,
                    "max_touch_points": 5,
                }
            )

        match = re.search(r"\(([^)]+)\)", user_agent)
        if match:
            context["oscpu"] = match.group(1)

        return context
