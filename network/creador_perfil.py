import json
from datetime import datetime
from statistics import mean, stdev

CONFIG = {
    'data_file': "network_data_24h.json"  # Fitxer on guardar les dades
}


class AnalitzadorPerfil:
    """
    Classe per analitzar les dades de ping i crear un perfil de xarxa.
    """
    def __init__(self, data_file=CONFIG['data_file']):
        """
        Inicialitza l'analitzador de perfil.
        
        Args:
            data_file (str): Ruta al fitxer JSON amb les dades de ping
        """
        self.data_file = data_file
        self.data = self._carregar_dades()

    def _carregar_dades(self):
        """
        Carrega les dades del fitxer JSON.
        
        Returns:
            list: Llista de diccionaris amb les dades de ping
        """
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: No s'ha trobat el fitxer {self.data_file}")
            return []
        except json.JSONDecodeError:
            print(f"Error: El fitxer {self.data_file} no té un format JSON vàlid")
            return []

    def identificar_hores_pic(self, perfil, percentil_llindar=75):
        """
        Identifica les hores amb més càrrega de trànsit.
        
        Args:
            perfil (dict): Perfil de xarxa amb estadístiques per hora
            percentil_llindar (int): Percentil per determinar les hores de màxima càrrega
            
        Returns:
            list: Llista d'hores amb més càrrega
        """
        if not perfil:
            return []

        # Obtenim tots els temps mitjans
        temps_mitjans = [(hora, stats['mitjana']) for hora, stats in perfil.items() if isinstance(hora, int)]
        
        # Ordenem per temps de resposta (de més alt a més baix)
        temps_mitjans.sort(key=lambda x: x[1], reverse=True)
        
        # Calculem el nombre d'hores a seleccionar (25% de les hores amb més càrrega)
        num_hores = max(1, int(len(temps_mitjans) * (100 - percentil_llindar) / 100))
        
        # Retornem les hores amb més càrrega
        return [hora for hora, _ in temps_mitjans[:num_hores]]

    def analitzar_perfil(self):
        """
        Analitza les dades recollides i crea un perfil d'ús de la xarxa.
        
        Returns:
            dict: Perfil amb estadístiques per cada hora del dia i hores de màxima càrrega
        """
        if not self.data:
            return None

        # Agrupem les dades per hora del dia
        dades_horaries = {}
        for punt in self.data:
            hora = datetime.fromisoformat(punt['timestamp']).hour
            if hora not in dades_horaries:
                dades_horaries[hora] = []
            dades_horaries[hora].append(punt['response_time'])

        # Calculem estadístiques per cada hora
        perfil = {}
        for hora, temps in dades_horaries.items():
            perfil[hora] = {
                'mitjana': mean(temps),  # Temps mitjà de resposta
                'desviacio': stdev(temps) if len(temps) > 1 else 0,  # Variabilitat
                'mostres': len(temps)  # Nombre de mostres
            }

        # Identifiquem les hores amb més càrrega
        hores_pic = self.identificar_hores_pic(perfil)
        
        # Afegim les hores de màxima càrrega al perfil
        perfil['hores_pic'] = {
            'hores': hores_pic,
            'descripcio': 'Hores amb més càrrega de trànsit (25% superior)'
        }

        return perfil

    def mostrar_perfil(self):
        """
        Guarda el perfil de xarxa en un fitxer de text.
        """
        perfil = self.analitzar_perfil()
        if not perfil:
            print("No hi ha dades per analitzar")
            return

        # Creem el nom del fitxer amb la data actual
        data_actual = datetime.now().strftime("%Y%m%d_%H%M")
        nom_fitxer = f"perfil_xarxa_{data_actual}.txt"

        with open(nom_fitxer, 'w', encoding='utf-8') as f:
            f.write("Perfil de xarxa\n")
            f.write("=" * 50 + "\n")
            
            # Guardem les estadístiques per hora (només les hores numèriques)
            hores = [h for h in perfil.keys() if isinstance(h, int)]
            for hora in hores:
                stats = perfil[hora]
                hora_format = f"{hora:02d}:00"
                f.write(f"\nHora {hora_format}\n")
                f.write(f"  Temps mitjà: {stats['mitjana']:.2f} ms\n")
                f.write(f"  Desviació: {stats['desviacio']:.2f} ms\n")
                f.write(f"  Mostres: {stats['mostres']}\n")

            # Guardem les hores de màxima càrrega
            if 'hores_pic' in perfil:
                f.write("\nHores amb més càrrega:\n")
                for hora in perfil['hores_pic']['hores']:
                    hora_format = f"{hora:02d}:00"
                    f.write(f"- {hora_format}\n")

        print(f"El perfil de xarxa s'ha guardat al fitxer: {nom_fitxer}")

def main():
    analitzador = AnalitzadorPerfil()
    analitzador.mostrar_perfil()

if __name__ == "__main__":
    main() 