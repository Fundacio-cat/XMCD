from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from navegadors.navegador_base import NavegadorBase
import os
import logging
import re


class ChromeNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        # Configura el valor de self.navegador com a 1 (Chrome)
        id_navegador_db = 1
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if user_agent:
            options = Options()
            self._configura_opcions_chrome(options, user_agent)
            driver_path = os.path.join(self.config.current_directory, "Controladors", self.config.CHROME_DRIVER_PATH)
            service = Service(driver_path)
            try:
                browser = webdriver.Chrome(service=service, options=options)
                browser.set_window_size(self.amplada, self.altura)
                self._habilita_mode_stealth(browser, user_agent)
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Chrome: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Chrome")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser

    def _configura_opcions_chrome(self, options: Options, user_agent: str) -> None:
        """Configura opcions per reduir la detecció automàtica."""
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--lang=ca-ES")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-first-run")
        options.add_argument("--ignore-certificate-errors")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "intl.accept_languages": "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6",
            },
        )

    def _habilita_mode_stealth(self, browser, user_agent: str) -> None:
        """Injecta configuracions per emular un navegador real."""
        context_ua = self._obte_context_user_agent(user_agent)
        try:
            browser.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {
                    "userAgent": user_agent,
                    "acceptLanguage": "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6",
                    "platform": context_ua["platform"],
                },
            )
        except Exception as e:
            self.config.write_log(
                f"No s'ha pogut aplicar l'override del user-agent pel mode stealth: {e}",
                level=logging.WARNING,
            )

        user_agent_js = user_agent.replace("\\", "\\\\").replace("'", "\\'")
        oscpu_js = context_ua["oscpu"].replace("\\", "\\\\").replace("'", "\\'")
        platform_js = context_ua["platform"].replace("\\", "\\\\").replace("'", "\\'")
        script = f"""
            (() => {{
                const patch = (object, property, value) => {{
                    try {{
                        Object.defineProperty(object, property, {{
                            configurable: true,
                            get: () => value
                        }});
                    }} catch (error) {{
                        console.warn("No s'ha pogut sobrescriure", property, error);
                    }}
                }};

                patch(navigator, 'webdriver', undefined);
                patch(navigator, 'userAgent', '{user_agent_js}');
                patch(navigator, 'platform', '{platform_js}');
                patch(navigator, 'oscpu', '{oscpu_js}');
                patch(navigator, 'languages', ['ca-ES', 'ca', 'es', 'en']);
                patch(navigator, 'hardwareConcurrency', {context_ua["hardware_concurrency"]});
                patch(navigator, 'deviceMemory', {context_ua["device_memory"]});
                patch(navigator, 'plugins', [
                    {{ name: "Chrome PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format" }},
                    {{ name: "Chromium PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format" }},
                    {{ name: "Microsoft Edge PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format" }}
                ]);

                if (!window.chrome) {{
                    patch(window, 'chrome', {{ runtime: {{}} }});
                }}

                const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
                if (originalQuery) {{
                    window.navigator.permissions.query = (parameters) => (
                        parameters && parameters.name === 'notifications'
                            ? Promise.resolve({{ state: Notification.permission }})
                            : originalQuery(parameters)
                    );
                }}
            }})();
        """
        try:
            browser.execute_script(script)
        except Exception as e:
            self.config.write_log(
                f"No s'ha pogut aplicar el JavaScript de stealth al Chrome: {e}",
                level=logging.WARNING,
            )

    def _obte_context_user_agent(self, user_agent: str) -> dict:
        """Deduïx propietats de la plataforma a partir del user-agent."""
        ua_lower = user_agent.lower()
        context = {
            "platform": "Win32",
            "oscpu": "Windows NT 10.0; Win64; x64",
            "hardware_concurrency": 8,
            "device_memory": 8,
        }

        if "mac os x" in ua_lower or "macintosh" in ua_lower:
            context.update(
                {
                    "platform": "MacIntel",
                    "oscpu": "Intel Mac OS X 10_15_7",
                    "hardware_concurrency": 8,
                    "device_memory": 8,
                }
            )
        elif "linux" in ua_lower:
            context.update(
                {
                    "platform": "Linux x86_64",
                    "oscpu": "Linux x86_64",
                    "hardware_concurrency": 12,
                    "device_memory": 16,
                }
            )
        elif "android" in ua_lower:
            context.update(
                {
                    "platform": "Linux armv8l",
                    "oscpu": "Linux armv8l",
                    "hardware_concurrency": 8,
                    "device_memory": 4,
                }
            )

        match = re.search(r"\(([^)]+)\)", user_agent)
        if match:
            context["oscpu"] = match.group(1)

        return context
