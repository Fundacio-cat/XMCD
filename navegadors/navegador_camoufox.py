import json
import logging
import os
import random
import textwrap
import time

from camoufox.sync_api import Camoufox
from navegadors.navegador_base import NavegadorBase


HTTP_HEADERS = {
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

FINGERPRINT_SCRIPT_TEMPLATE = textwrap.dedent("""
    (() => {
        const cfg = __CFG__;

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
        tryDefineProperty(navigator, 'maxTouchPoints', cfg.hasTouch ? Math.max(1, navigator.maxTouchPoints || 1) : 0);

        window.chrome = window.chrome || { runtime: {} };

        if (cfg.viewport) {
            tryDefineProperty(window.screen, 'width', cfg.viewport.width);
            tryDefineProperty(window.screen, 'height', cfg.viewport.height);
            tryDefineProperty(window.screen, 'availWidth', cfg.viewport.width);
            tryDefineProperty(window.screen, 'availHeight', cfg.viewport.height);
        }

        if (cfg.deviceScaleFactor) {
            tryDefineProperty(window.devicePixelRatio ? window : {}, 'devicePixelRatio', cfg.deviceScaleFactor);
        }

        if (cfg.colorScheme) {
            const originalMatchMedia = window.matchMedia;
            window.matchMedia = query => {
                const result = { matches: false, media: query, onchange: null, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent() { return false; } };
                if (query === '(prefers-color-scheme: dark)') {
                    result.matches = cfg.colorScheme === 'dark';
                    return result;
                }
                if (query === '(prefers-color-scheme: light)') {
                    result.matches = cfg.colorScheme === 'light';
                    return result;
                }
                return originalMatchMedia ? originalMatchMedia.call(window, query) : result;
            };
        }

        if (cfg.timezone) {
            try {
                const originalResolved = Intl.DateTimeFormat.prototype.resolvedOptions;
                Intl.DateTimeFormat.prototype.resolvedOptions = function(...args) {
                    const options = originalResolved.apply(this, args);
                    options.timeZone = cfg.timezone;
                    return options;
                };
            } catch (e) {}
        }

        if (cfg.geolocation) {
            try {
                const geo = navigator.geolocation;
                if (geo) {
                    const position = {
                        coords: {
                            latitude: cfg.geolocation.latitude,
                            longitude: cfg.geolocation.longitude,
                            accuracy: cfg.geolocation.accuracy,
                            altitude: null,
                            altitudeAccuracy: null,
                            heading: null,
                            speed: null
                        },
                        timestamp: Date.now()
                    };
                    const success = (callback) => callback && callback(position);
                    const error = (callback) => callback && callback({ code: 1, message: 'Geolocation override' });

                    geo.getCurrentPosition = (onSuccess, onError) => {
                        success(onSuccess);
                        error(onError);
                    };
                    geo.watchPosition = (onSuccess, onError) => {
                        success(onSuccess);
                        error(onError);
                        return Math.floor(Math.random() * 10000);
                    };
                }
            } catch (e) {}
        }

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

HUMAN_SIMULATION_SCRIPT_TEMPLATE = textwrap.dedent("""
    (() => {
        if (window.__camoufoxHumanSimulation) {
            return;
        }
        window.__camoufoxHumanSimulation = true;

        const cfg = __CFG__;
        const rand = (min, max) => Math.random() * (max - min) + min;
        const pick = (array) => array[Math.floor(rand(0, array.length))];

        const schedule = (fn, range) => {
            const [minDelay, maxDelay] = range;
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
            }, cfg.mouseMove);

            schedule(() => {
                const delta = rand(-200, 260);
                window.scrollBy({ top: delta, behavior: 'smooth' });
            }, cfg.scroll);

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
            }, cfg.hover);

            schedule(() => {
                if (document.hasFocus()) {
                    window.blur();
                    setTimeout(() => window.focus(), rand(800, 2600));
                }
            }, cfg.focus);
        }, { once: true });
    })();
""")


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
            timezone = self._tria_timezone()
            geoloc = self._tria_geolocalitzacio()
            color_scheme = self._tria_color_scheme()
            device_scale_factor = self._tria_device_scale_factor(viewport)
            has_touch = self._has_touch(viewport)
            low_resource_mode = self._is_low_resource()
            self.low_resource_mode = low_resource_mode

            if low_resource_mode:
                self.config.write_log(
                    "S'ha detectat un entorn amb pocs recursos. S'utilitzarà una pàgina directa amb scripts optimitzats",
                    level=logging.INFO
                )

                page = browser.new_page(user_agent=user_agent)
                page.set_viewport_size(viewport)
                page.set_default_navigation_timeout(45000)
                page.set_default_timeout(45000)
                page.set_extra_http_headers(self._http_headers())
                page.add_init_script(self._fingerprint_script(timezone, geoloc, color_scheme, has_touch, viewport, device_scale_factor))
                page.add_init_script(self._human_simulation_script(low_resource=True))

                context = None
            else:
                context = browser.new_context(
                    user_agent=user_agent,
                    locale='ca-ES',
                    viewport=viewport,
                    color_scheme=color_scheme,
                    timezone_id=timezone,
                    device_scale_factor=device_scale_factor,
                    geolocation=geoloc,
                    permissions=['geolocation'],
                    has_touch=has_touch
                )

                context.set_extra_http_headers(self._http_headers())
                context.add_init_script(self._fingerprint_script(timezone, geoloc, color_scheme, has_touch, viewport, device_scale_factor))
                context.add_init_script(self._human_simulation_script(low_resource=False))

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
        return HTTP_HEADERS.copy()

    def _fingerprint_script(
        self,
        timezone: str,
        geolocation: dict,
        color_scheme: str,
        has_touch: bool,
        viewport: dict,
        device_scale_factor: float
    ) -> str:
        config = json.dumps({
            'timezone': timezone,
            'geolocation': geolocation,
            'colorScheme': color_scheme,
            'hasTouch': has_touch,
            'viewport': viewport,
            'deviceScaleFactor': device_scale_factor
        })

        return FINGERPRINT_SCRIPT_TEMPLATE.replace('__CFG__', config)

    def _human_simulation_script(self, low_resource: bool) -> str:
        config = {
            'mouseMove': [1800, 5400] if low_resource else [900, 3200],
            'scroll': [4800, 9600] if low_resource else [2200, 5400],
            'hover': [8200, 15000] if low_resource else [3200, 7600],
            'focus': [26000, 42000] if low_resource else [18000, 32000]
        }

        return HUMAN_SIMULATION_SCRIPT_TEMPLATE.replace('__CFG__', json.dumps(config))

    def _is_low_resource(self) -> bool:
        try:
            page_size = os.sysconf('SC_PAGE_SIZE')
            phys_pages = os.sysconf('SC_PHYS_PAGES')
            total_memory = page_size * phys_pages
            # Considerem entorn amb pocs recursos si hi ha <= 2GB de RAM
            return total_memory <= 2 * 1024 * 1024 * 1024
        except (ValueError, AttributeError, OSError):
            return False

