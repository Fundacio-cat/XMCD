from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from navegadors.navegador_base import NavegadorBase
import os
import logging


class FirefoxNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        # Configura el valor de self.navegador com a 1 (Chrome)
        id_navegador_db = 2
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if user_agent:
            options = Options()
            self._configura_opcions_firefox(options, user_agent)

            driver_path = os.path.join(self.config.current_directory, "Controladors", self.config.FIREFOX_DRIVER_PATH)
            service = Service(driver_path)
            try:
                browser = webdriver.Firefox(service=service, options=options)
                browser.set_window_size(self.amplada, self.altura)
                self._habilita_mode_stealth(browser)
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Firefox: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Firefox")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser

    def _configura_opcions_firefox(self, options: Options, user_agent: str) -> None:
        """Aplica preferències per reduir la detecció automàtica."""
        options.set_preference("general.useragent.override", user_agent)
        options.set_preference("intl.accept_languages", "ca-ES,ca;q=0.9,es;q=0.8,en;q=0.6")
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("toolkit.telemetry.enabled", False)
        options.set_preference("toolkit.telemetry.unified", False)
        options.set_preference("toolkit.telemetry.reportingpolicy.firstRun", False)
        options.set_preference("datareporting.healthreport.uploadEnabled", False)
        options.set_preference("browser.sessionstore.resume_from_crash", False)
        options.set_preference("browser.startup.homepage", "about:blank")
        options.set_preference("general.platform.override", "Linux armv7l")
        options.set_preference("general.oscpu.override", "Linux armv7l")
        options.set_preference("network.http.accept.default",
                               "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8")
        options.set_preference("network.http.accept-encoding", "gzip, deflate, br")
        options.set_preference("dom.webnotifications.enabled", True)

    def _habilita_mode_stealth(self, browser) -> None:
        """Injecta JavaScript per eliminar rastres de WebDriver i imitar valors humans."""
        script = """
            (() => {
                const patch = (object, property, value) => {
                    try {
                        Object.defineProperty(object, property, {
                            get: () => value,
                            configurable: true
                        });
                    } catch (error) {
                        console.warn(`No s'ha pogut sobrescriure ${property}:`, error);
                    }
                };

                const navigatorProto = Object.getPrototypeOf(navigator);
                patch(navigatorProto, 'webdriver', undefined);
                patch(navigatorProto, 'languages', ['ca-ES', 'ca', 'es', 'en']);
                patch(navigatorProto, 'platform', 'Linux armv7l');
                patch(navigatorProto, 'hardwareConcurrency', navigator.hardwareConcurrency || 4);
                patch(navigatorProto, 'deviceMemory', navigator.deviceMemory || 2);
                patch(navigatorProto, 'plugins', [1, 2, 3]);

                if (!window.chrome) {
                    patch(window, 'chrome', { runtime: {} });
                }

                if (navigator.permissions && navigator.permissions.query) {
                    const originalQuery = navigator.permissions.query.bind(navigator.permissions);
                    navigator.permissions.query = (parameters) => {
                        if (parameters && parameters.name === 'notifications' && typeof Notification !== 'undefined') {
                            return Promise.resolve({ state: Notification.permission });
                        }
                        return originalQuery(parameters);
                    };
                }
            })();
        """

        try:
            browser.execute_script(script)
        except Exception as e:
            self.config.write_log(
                f"No s'ha pogut aplicar el mode stealth al Firefox: {e}", level=logging.WARNING)
