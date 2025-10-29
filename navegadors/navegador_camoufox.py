import logging
import random
import textwrap
import time

from camoufox.sync_api import Camoufox
from navegadors.navegador_base import NavegadorBase


class CamoufoxNavegador(NavegadorBase):

    def init_navegador(self):
        browser = None
        context = None
        camoufox_instance = None

        # Configura el valor de self.navegador com a 3 (Camoufox)
        id_navegador_db = 3
        user_agent = self.repository.cerca_userAgent(id_navegador_db)

        if not user_agent:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")

        try:
            # Inicialitza Camoufox amb configuració bàsica compatible i humanitzada
            camoufox_instance = Camoufox(
                headless=False,
                humanize=True,
                locale='ca-ES'
            )

            # Camoufox utilitza __enter__ per inicialitzar
            # Retorna un Playwright Browser object
            browser = camoufox_instance.__enter__()

            viewport = self._genera_viewport()

            context = browser.new_context(
                user_agent=user_agent,
                locale='ca-ES',
                viewport=viewport,
                color_scheme=self._tria_color_scheme(),
                timezone_id=self._tria_timezone(),
                device_scale_factor=self._tria_device_scale_factor(viewport),
                geolocation=self._tria_geolocalitzacio(),
                permissions=['geolocation'],
                has_touch=self._has_touch(viewport)
            )

            context.set_extra_http_headers(self._http_headers())
            context.add_init_script(self._fingerprint_script())
            context.add_init_script(self._human_simulation_script())

            page = context.new_page()
            page.set_default_navigation_timeout(45000)
            page.set_default_timeout(45000)

            # Guarda les referències per utilitzar-les més tard
            self.camoufox_instance = camoufox_instance
            self.browser_context = context
            self.page = page

            self.config.write_log(
                "Navegador Camoufox inicialitzat amb configuració humanitzada",
                level=logging.DEBUG
            )

        except Exception as e:
            self.config.write_log(
                f"Error iniciant el navegador Camoufox: {e}", level=logging.ERROR)

            if context:
                try:
                    context.close()
                except Exception:
                    pass

            if camoufox_instance:
                try:
                    camoufox_instance.__exit__(type(e), e, None)
                except Exception:
                    pass

            raise ValueError("Error iniciant el navegador Camoufox") from e

        return id_navegador_db, browser
    
    def tanca_navegador(self):
        """
        Tanca el navegador Camoufox.
        """
        try:
            if hasattr(self, 'page') and self.page:
                self.page.close()
            if hasattr(self, 'browser_context') and self.browser_context:
                self.browser_context.close()
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
                self.pausa_humana(0.4, 1.2)
                self.page.screenshot(path=nom, full_page=False)
        except Exception as e:
            self.config.write_log(
                f"Error capturant la pantalla: {e}", level=logging.ERROR)

    def pausa_humana(self, min_segons: float = 0.6, max_segons: float = 1.8) -> None:
        """Fa una pausa aleatòria per simular el temps de reacció humà."""
        if max_segons < min_segons:
            min_segons, max_segons = max_segons, min_segons

        espera = random.uniform(min_segons, max_segons)
        time.sleep(max(0, espera))

    def _genera_viewport(self) -> dict:
        ample = self.amplada + random.randint(-40, 40)
        altura = self.altura + random.randint(-60, 60)
        ample = max(320, min(ample, 2560))
        altura = max(480, min(altura, 1440))
        return {'width': ample, 'height': altura}

    def _tria_device_scale_factor(self, viewport: dict) -> float:
        ample = viewport['width']
        if ample <= 430:
            return round(random.uniform(2.0, 3.0), 2)
        if ample <= 1024:
            return round(random.uniform(1.5, 2.0), 2)
        return round(random.uniform(1.0, 1.3), 2)

    def _has_touch(self, viewport: dict) -> bool:
        ample = viewport['width']
        if ample <= 430:
            return True
        if ample <= 1024:
            return random.random() < 0.6
        return random.random() < 0.15

    def _tria_geolocalitzacio(self) -> dict:
        lat_base, lon_base = 41.3874, 2.1686  # Barcelona
        return {
            'latitude': round(lat_base + random.uniform(-0.2, 0.2), 6),
            'longitude': round(lon_base + random.uniform(-0.2, 0.2), 6),
            'accuracy': random.uniform(25, 120)
        }

    def _tria_timezone(self) -> str:
        return random.choice(['Europe/Madrid', 'Europe/Andorra', 'Europe/Paris'])

    def _tria_color_scheme(self) -> str:
        return random.choices(['light', 'dark'], weights=[0.7, 0.3])[0]

    def _http_headers(self) -> dict:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ca-ES,ca;q=0.9,es;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def _fingerprint_script(self) -> str:
        return textwrap.dedent("""
            (() => {
                const tryDefineProperty = (object, property, value) => {
                    try {
                        Object.defineProperty(object, property, {
                            configurable: true,
                            get: () => value
                        });
                    } catch (e) {}
                };

                tryDefineProperty(navigator, 'webdriver', undefined);
                tryDefineProperty(navigator, 'plugins', [1, 2, 3, 4, 5]);
                tryDefineProperty(navigator, 'languages', ['ca-ES', 'ca', 'es', 'en']);
                tryDefineProperty(navigator, 'language', 'ca-ES');
                tryDefineProperty(navigator, 'platform', 'MacIntel');
                tryDefineProperty(navigator, 'vendor', 'Google Inc.');
                tryDefineProperty(navigator, 'hardwareConcurrency', 8);
                tryDefineProperty(navigator, 'deviceMemory', 8);
                tryDefineProperty(navigator, 'maxTouchPoints', 0);

                window.chrome = window.chrome || { runtime: {} };

                const originalQuery = navigator.permissions && navigator.permissions.query;
                if (originalQuery) {
                    navigator.permissions.query = parameters => (
                        parameters && parameters.name === 'notifications'
                            ? Promise.resolve({ state: Notification.permission })
                            : originalQuery(parameters)
                    );
                }

                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.call(this, parameter);
                };

                if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
                    const originalGetHighEntropyValues = navigator.userAgentData.getHighEntropyValues.bind(navigator.userAgentData);
                    navigator.userAgentData.getHighEntropyValues = async (hints) => {
                        const data = await originalGetHighEntropyValues(hints);
                        if (data.brands) {
                            data.brands = data.brands.filter(entry => !/Not[A-Za-z]+/i.test(entry.brand));
                        }
                        data.platform = 'macOS';
                        return data;
                    };
                }
            })();
        """)

    def _human_simulation_script(self) -> str:
        return textwrap.dedent("""
            (() => {
                if (window.__camoufoxHumanSimulation) {
                    return;
                }
                window.__camoufoxHumanSimulation = true;

                const rand = (min, max) => Math.random() * (max - min) + min;
                const pick = (array) => array[Math.floor(rand(0, array.length))];

                const schedule = (fn, minDelay, maxDelay) => {
                    const run = () => {
                        try {
                            fn();
                        } catch (error) {
                            console.debug('Simulació humana fallida', error);
                        }
                        setTimeout(run, rand(minDelay, maxDelay));
                    };

                    setTimeout(run, rand(minDelay, maxDelay));
                };

                document.addEventListener('DOMContentLoaded', () => {
                    schedule(() => {
                        const event = new MouseEvent('mousemove', {
                            bubbles: true,
                            cancelable: true,
                            clientX: Math.round(rand(10, window.innerWidth - 10)),
                            clientY: Math.round(rand(10, window.innerHeight - 10)),
                            movementX: Math.round(rand(-8, 8)),
                            movementY: Math.round(rand(-8, 8))
                        });
                        document.dispatchEvent(event);
                    }, 900, 3200);

                    schedule(() => {
                        const delta = rand(-200, 260);
                        window.scrollBy({ top: delta, behavior: 'smooth' });
                    }, 2200, 5400);

                    schedule(() => {
                        const interactive = Array.from(document.querySelectorAll('a[href], button, input, textarea, [role="button"], [tabindex]'))
                            .filter(el => el.offsetParent);
                        if (!interactive.length) {
                            return;
                        }
                        const element = pick(interactive);
                        element.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
                        const delay = rand(400, 1600);
                        setTimeout(() => {
                            element.dispatchEvent(new MouseEvent('mouseout', { bubbles: true }));
                        }, delay);
                    }, 3200, 7600);

                    schedule(() => {
                        if (document.hasFocus()) {
                            window.blur();
                            setTimeout(() => window.focus(), rand(800, 2600));
                        }
                    }, 18000, 32000);
                }, { once: true });
            })();
        """)

