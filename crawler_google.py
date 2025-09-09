#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler per Google amb Camoufox i gestió automàtica de Cloudflare
Permet accedir a Google i fer cerques automàtiques
"""

import logging
import asyncio
from typing import List, Dict, Optional
from camoufox import AsyncCamoufox
from camoufox_captcha import solve_captcha
import os
from dotenv import load_dotenv
import csv
from datetime import datetime


# Carregar variables d'entorn
load_dotenv()

# Crear directori de logs si no existeix
if not os.path.exists('logs'):
    os.makedirs('logs')
    print("Directori 'logs' creat")

### Logging ###
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/google.log'),
        logging.StreamHandler()
    ]
)

# Desactivar logs innecessaris
for logger_name in ['WDM', 'selenium', 'urllib3']:
    logging.getLogger(logger_name).disabled = True
logger = logging.getLogger(__name__)

### Crawler ###

class GoogleCrawler:
    """
    Crawler per Google que utilitza Camoufox per superar automàticament Cloudflare
    """
    
    def __init__(self, headless: bool = False, timeout: int = 30):
        """
        Inicialitzar el crawler
        
        Args:
            headless (bool): Si executar el navegador en mode headless
            timeout (int): Temps d'espera màxim per les operacions
        """
        self.browser = None
        self.page = None
        self.timeout = timeout
        self.headless = headless
        self.session_start_time = None

    async def setup_browser(self):
        """Configurar el navegador Camoufox amb protecció anti-detecció"""
        try:
            # Configuració segons la documentació de camoufox-captcha
            self.browser = AsyncCamoufox(
                headless=self.headless,
                geoip=True,
                humanize=True,  # Simular comportament humà
                i_know_what_im_doing=True,
                config={'forceScopeAccess': True},  # Requerit per camoufox-captcha
                disable_coop=True  # Requerit per camoufox-captcha
            )
            
            logger.info("Navegador Camoufox configurat correctament per Google")
            
        except Exception as e:
            logger.error(f"Error configurant el navegador: {e}")
            raise

    async def simulate_human_behavior(self):
        """
        Simula comportament humà realista abans d'accedir a Google
        """
        try:
            import random
                        
            # Simular temps de "pensament" humà
            await asyncio.sleep(random.uniform(1, 2))
            
            # Simular scroll aleatori
            for _ in range(random.randint(2, 4)):
                scroll_amount = random.randint(-300, 300)
                await self.page.evaluate(f"window.scrollBy(0, {scroll_amount});")
                await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # Simular moviments del ratolí
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await self.page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Simular selecció de text
            await self.page.evaluate("""
                var selection = window.getSelection();
                var range = document.createRange();
                var body = document.body;
                range.selectNodeContents(body);
                selection.removeAllRanges();
                selection.addRange(range);
            """)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # Deseleccionar
            await self.page.evaluate("window.getSelection().removeAllRanges();")
            await asyncio.sleep(random.uniform(0.3, 0.5))
            
            logger.info("Comportament humà simulat correctament")
            
        except Exception as e:
            logger.warning(f"Error en simulació de comportament humà: {e}")

    async def search_google(self, query: str):
        """
        Accedeix a Google i fa una cerca
        """
        try:
            # Anar directament a Google
            await self.page.goto("https://www.google.com", timeout=120000)  # 2 minuts
            await asyncio.sleep(2)

            # Simular comportament humà
            await self.simulate_human_behavior()

            # Acceptar cookies si apareix el popup
            try:
                accept_button = await self.page.wait_for_selector('button[aria-label*="Acceptar-ho tot"], button[aria-label*="Aceptar todo"]', timeout=5000)
                if accept_button:
                    await accept_button.click()
                    logger.info("Cookies acceptades")
                    await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"No s'ha trobat el botó d'acceptar cookies: {e}")

            # Buscar la caixa de cerca de Google
            search_input = None
            try:
                # Selector específic pel textarea de cerca de Google
                search_input = await self.page.wait_for_selector('textarea', timeout=5000)
                if search_input:
                    logger.info("Caixa de cerca trobada amb el selector específic")
                else:
                    logger.warning("No s'ha trobat la caixa de cerca de Google") 
                    return False

            except Exception as e:
                logger.error(f"No s'ha trobat la caixa de cerca de Google: {e}")
                return False

            # Fer clic a la caixa de cerca per activar-la
            await search_input.click()
            await asyncio.sleep(1)

            # Escriure la consulta
            await search_input.fill(query)
            await asyncio.sleep(2)
            
            # Enviar la consulta amb Enter
            await search_input.press("Enter")
            logger.info(f"Consulta enviada a Google: {query}")
            
            # Esperar 10 minuts com has demanat
            logger.info("Esperant 10 minuts...")
            await asyncio.sleep(600)  # 10 minuts
            
            logger.info("Cerca completada - 10 minuts han passat")
            return True

        except Exception as e:
            logger.error(f"Error accedint a Google: {e}")
            return False


    async def close(self):
        """
        Tanca el navegador de manera segura
        """
        try:
            if self.browser:
                # AsyncCamoufox es tanca automàticament amb el context manager
                # No cal cridar close() directament
                logger.info("Navegador es tancarà automàticament amb el context manager")
        except Exception as e:
            logger.error(f"Error tancant el navegador: {e}")

async def main():
    crawler = None
    query = "intel·ligència artificial"
    try:
        # Creem l'objecte crawler
        crawler = GoogleCrawler(headless=False)
        
        # Configuram el navegador
        await crawler.setup_browser()
        
        # Crear una nova pàgina dins del context manager
        async with crawler.browser as browser:
            crawler.page = await browser.new_page()
            
            # Esperar un temps realista abans de navegar
            import random
            await asyncio.sleep(random.uniform(1, 3))

            # Processar la consulta a Google
            if await crawler.search_google(query):
                print("✅ Cerca a Google completada amb èxit!")
            else:
                print("❌ Error accedint a Google")
                
    except Exception as e:
        print(f"Error inesperat: {e}")
        logger.error(f"Error inesperat: {e}")
    finally:
        # El navegador es tanca automàticament amb el context manager
        # No cal cridar close() manualment
        if crawler:
            logger.info("Crawler de Google finalitzat - navegador tancat automàticament")

if __name__ == "__main__":
    asyncio.run(main())