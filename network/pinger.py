import subprocess
import time
from datetime import datetime
import json
import os

# =============================================
# CONFIGURACIÓ - PARÀMETRES
# =============================================

CONFIG = {
    'target': "8.8.8.8",        # Adreça a la qual fer ping
    'interval': 60,            # Segons entre pings (5 minuts)
    #'interval': 300,            # Segons entre pings (5 minuts)
    'duration_minutes': 60,   # Durada del monitoratge en minuts (24 hores)
    #'duration_minutes': 1440,   # Durada del monitoratge en minuts (24 hores)
    'data_file': "network_data.json"  # Fitxer on guardar les dades
}

class PingerMonitor:
    """
    Classe per monitoritzar l'estat de la xarxa mitjançant pings.
    Guarda les dades en un fitxer JSON.
    """
    def __init__(self, target=CONFIG['target'], interval=CONFIG['interval'], data_file=CONFIG['data_file']):
        """
        Inicialitza el monitor de xarxa.
        
        Args:
            target (str): Adreça IP o domini al qual fer ping
            interval (int): Segons d'espera entre pings
            data_file (str): Nom del fitxer on guardar les dades
        """
        self.target = target
        self.interval = interval
        self.data_file = data_file
        self.data = self._carregar_dades()

    def _carregar_dades(self):
        """
        Carrega les dades existents del fitxer JSON si existeix.
        Si no existeix, retorna una llista buida.
        """
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []

    def _guardar_dades(self):
        """
        Guarda les dades actuals al fitxer JSON.
        """
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def ping(self):
        """
        Executa un ping a l'adreça objectiu i retorna el temps de resposta.
        
        Returns:
            float: Temps de resposta en mil·lisegons, o None si hi ha error
        """
        try:
            result = subprocess.run(['ping', '-c', '1', self.target], capture_output=True, text=True)
            if result.returncode == 0:
                time_str = result.stdout.split('time=')[-1].split()[0]
                return float(time_str)
            return None
        except Exception as e:
            print(f"Error fent ping: {e}")
            return None

    def monitor(self, duration_days=1):
        """
        Inicia el monitoratge de la xarxa durant el temps especificat.
        
        Args:
            duration_days (int): Nombre de dies a monitoritzar
        """
        # Calculem quan hem d'aturar el monitoratge
        end_time = time.time() + (duration_days * 24 * 60 * 60)
        
        print(f"Iniciant monitoratge de xarxa durant {duration_days} dies...")
        print(f"Fent ping a {self.target} cada {self.interval} segons")
        
        # Bucle principal de monitoratge
        while time.time() < end_time:
            timestamp = datetime.now().isoformat()
            response_time = self.ping()
            
            if response_time is not None:
                # Guardem cada mesura amb la seva data i hora
                data_point = {
                    'timestamp': timestamp,
                    'response_time': response_time
                }
                self.data.append(data_point)
                self._guardar_dades()
                print(f"Ping completat: {response_time}ms")
            
            time.sleep(self.interval)

def main():
    """
    Funció principal que executa el monitoratge.
    """
    monitor = PingerMonitor()
    
    print(f"\nIniciant monitoratge:")
    print(f"- Durada: {CONFIG['duration_minutes']} minuts")
    print(f"- Interval: {CONFIG['interval']} segons")
    print(f"- Objectiu: {CONFIG['target']}")
    
    monitor.monitor(duration_days=CONFIG['duration_minutes']/1440)

if __name__ == "__main__":
    main() 