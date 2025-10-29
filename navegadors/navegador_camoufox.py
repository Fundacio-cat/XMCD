from camoufox.sync_api import Camoufox
from navegadors.navegador_base import NavegadorBase
import logging
import threading
import random
import time


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
                    
                    // Segueix la posició del ratolí per poder simular millor el comportament humà
                    window.mouseX = window.innerWidth / 2;
                    window.mouseY = window.innerHeight / 2;
                    
                    document.addEventListener('mousemove', function(e) {
                        window.mouseX = e.clientX;
                        window.mouseY = e.clientY;
                    }, true);
                    
                    // Simula moviments ocasionals del ratolí fins i tot quan no hi ha interacció
                    // (com si l'usuari estigués present però no interactuant activament)
                    setInterval(function() {
                        if (Math.random() < 0.1) { // 10% de probabilitat cada segon
                            window.mouseX += (Math.random() - 0.5) * 2;
                            window.mouseY += (Math.random() - 0.5) * 2;
                            window.mouseX = Math.max(0, Math.min(window.innerWidth, window.mouseX));
                            window.mouseY = Math.max(0, Math.min(window.innerHeight, window.mouseY));
                        }
                    }, 1000);
                """)
                
                # Guarda les referències per utilitzar-les més tard
                self.camoufox_instance = camoufox_instance
                self.page = page
                
                # Inicialitza el sistema de comportament humà continu
                self.human_behavior_active = True
                self.human_thread = None
                self._inicia_comportament_huma()
                
            except Exception as e:
                self.config.write_log(
                    f"Error iniciant el navegador Camoufox: {e}", level=logging.ERROR)
                raise ValueError("Error iniciant el navegador Camoufox")
        else:
            self.config.write_log(
                "No hi ha user agent disponible.", level=logging.ERROR)
            raise ValueError("No hi ha user agent disponible.")
        return id_navegador_db, browser
    
    def _inicia_comportament_huma(self):
        """
        Inicia el thread que simula comportament humà continu.
        """
        if hasattr(self, 'page') and self.page:
            self.human_thread = threading.Thread(
                target=self._comportament_huma_continu,
                daemon=True
            )
            self.human_thread.start()
            self.config.write_log(
                "Comportament humà continu iniciat", level=logging.INFO)
    
    def _comportament_huma_continu(self):
        """
        Thread en segon pla que simula activitat humana constant.
        """
        while self.human_behavior_active:
            try:
                if hasattr(self, 'page') and self.page:
                    # Decideix quina acció fer segons probabilitats naturals
                    accio = random.choices(
                        ['moviment_ratoli', 'scroll', 'pausa_lectura', 'micro_moviment'],
                        weights=[30, 25, 30, 15],
                        k=1
                    )[0]
                    
                    if accio == 'moviment_ratoli':
                        self._simula_moviment_ratoli_aleatori()
                    elif accio == 'scroll':
                        self._simula_scroll_natural()
                    elif accio == 'pausa_lectura':
                        self._simula_pausa_lectura()
                    elif accio == 'micro_moviment':
                        self._simula_micro_moviment_ratoli()
                    
                    # Espera un temps aleatori entre accions (2-8 segons)
                    time.sleep(random.uniform(2.0, 8.0))
                else:
                    time.sleep(1)
            except Exception as e:
                # Si hi ha errors, espera una mica i continua
                self.config.write_log(
                    f"Error en comportament humà continu: {e}", 
                    level=logging.WARNING)
                time.sleep(5)
    
    def _simula_moviment_ratoli_aleatori(self):
        """
        Simula un moviment natural del ratolí per la pantalla.
        """
        try:
            viewport = self.page.viewport_size
            if not viewport:
                return
            
            # Posició actual (o posició aleatòria si no la podem obtenir)
            x_actual = random.randint(100, viewport['width'] - 100)
            y_actual = random.randint(100, viewport['height'] - 100)
            
            # Posició objectiu
            x_objectiu = random.randint(50, viewport['width'] - 50)
            y_objectiu = random.randint(50, viewport['height'] - 50)
            
            # Mou el ratolí en una trajectòria natural (bezier-like)
            num_punts = random.randint(3, 7)
            for i in range(num_punts):
                # Interpolació cúbica per una trajectòria més natural
                t = i / (num_punts - 1) if num_punts > 1 else 0
                # Aplica una corba suau (bezier simplificat)
                t_smooth = t * t * (3 - 2 * t)
                
                x = x_actual + (x_objectiu - x_actual) * t_smooth
                y = y_actual + (y_objectiu - y_actual) * t_smooth
                
                # Afegeix una petita variació aleatòria per semblar més humà
                x += random.randint(-5, 5)
                y += random.randint(-5, 5)
                
                self.page.mouse.move(x, y)
                
                # Actualitza la posició al JavaScript per mantenir la sincronització
                self.page.evaluate(f"""
                    () => {{
                        window.mouseX = {x};
                        window.mouseY = {y};
                    }}
                """)
                
                time.sleep(random.uniform(0.01, 0.03))
                
        except Exception as e:
            pass  # Ignora errors silenciosament
    
    def _simula_scroll_natural(self):
        """
        Simula un scroll natural de la pàgina.
        """
        try:
            # Decideix si fer scroll amunt o avall
            direccio = random.choice(['down', 'up'])
            
            # Quantitat de scroll (petita per semblar natural)
            quantitat = random.randint(50, 300)
            
            if direccio == 'down':
                self.page.mouse.wheel(0, quantitat)
            else:
                self.page.mouse.wheel(0, -quantitat)
            
            # Pausa després del scroll per simular lectura
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            pass
    
    def _simula_pausa_lectura(self):
        """
        Simula una pausa com si l'usuari estigués llegint.
        """
        try:
            # Pausa més llarga (3-8 segons) que simula lectura
            pausa = random.uniform(3.0, 8.0)
            
            # Durant la pausa, pot fer micro-moviments ocasionals
            if random.random() < 0.3:  # 30% de probabilitat
                time.sleep(pausa * 0.5)
                self._simula_micro_moviment_ratoli()
                time.sleep(pausa * 0.5)
            else:
                time.sleep(pausa)
                
        except Exception as e:
            pass
    
    def _simula_micro_moviment_ratoli(self):
        """
        Simula petits moviments del ratolí (com tremor natural o ajustaments mínims).
        """
        try:
            viewport = self.page.viewport_size
            if not viewport:
                return
            
            # Obtenim la posició actual del ratolí des del JavaScript injectat
            posicio_actual = self.page.evaluate("""
                () => {
                    return { 
                        x: window.mouseX || window.innerWidth / 2, 
                        y: window.mouseY || window.innerHeight / 2 
                    };
                }
            """)
            
            x = posicio_actual.get('x', viewport['width'] / 2)
            y = posicio_actual.get('y', viewport['height'] / 2)
            
            # Petits moviments aleatoris (1-15 píxels) per simular micro-moviments naturals
            x_nou = x + random.randint(-15, 15)
            y_nou = y + random.randint(-15, 15)
            
            # Limita dins del viewport
            x_nou = max(10, min(viewport['width'] - 10, x_nou))
            y_nou = max(10, min(viewport['height'] - 10, y_nou))
            
            # Mou el ratolí amb velocitat variable (poc passos = moviment més ràpid i natural)
            self.page.mouse.move(x_nou, y_nou, steps=random.randint(1, 3))
            
            # Actualitza la posició al JavaScript per mantenir la sincronització
            self.page.evaluate(f"""
                () => {{
                    window.mouseX = {x_nou};
                    window.mouseY = {y_nou};
                }}
            """)
            
            time.sleep(random.uniform(0.1, 0.3))
            
        except Exception as e:
            pass
    
    def _simula_moviment_ratoli_a_element(self, element):
        """
        Simula un moviment natural del ratolí cap a un element específic.
        
        Args:
        - element: Element Playwright cap al qual moure el ratolí
        """
        try:
            # Obté la posició de l'element
            box = element.bounding_box()
            if box:
                x_centre = box['x'] + box['width'] / 2
                y_centre = box['y'] + box['height'] / 2
                
                # Mou el ratolí a prop de l'element amb trajectòria natural
                # Comença una mica abans i acosta gradualment
                x_inici = x_centre + random.randint(-100, 100)
                y_inici = y_centre + random.randint(-100, 100)
                
                # Moviment intermedi
                self.page.mouse.move(x_inici, y_inici)
                self.page.evaluate(f"""
                    () => {{
                        window.mouseX = {x_inici};
                        window.mouseY = {y_inici};
                    }}
                """)
                time.sleep(random.uniform(0.1, 0.3))
                
                # Moviment final cap a l'element
                x_final = x_centre + random.randint(-5, 5)
                y_final = y_centre + random.randint(-5, 5)
                self.page.mouse.move(x_final, y_final, steps=random.randint(5, 10))
                self.page.evaluate(f"""
                    () => {{
                        window.mouseX = {x_final};
                        window.mouseY = {y_final};
                    }}
                """)
                time.sleep(random.uniform(0.2, 0.4))
                
        except Exception as e:
            pass
    
    def tanca_navegador(self):
        """
        Tanca el navegador Camoufox i atura el comportament humà.
        """
        try:
            # Atura el thread de comportament humà
            if hasattr(self, 'human_behavior_active'):
                self.human_behavior_active = False
            
            # Espera que el thread s'aturi (màxim 2 segons)
            if hasattr(self, 'human_thread') and self.human_thread:
                self.human_thread.join(timeout=2.0)
            
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

