import json
import os
import logging
import inspect
from dataclasses import dataclass, fields


@dataclass
class Config:
    CHROME_DRIVER_PATH: str
    FIREFOX_DRIVER_PATH: str
    temps_espera_processos: int
    temps_espera_cerques: int
    nombre_de_cerques_per_execucio: int
    fitxer_logs: str
    directori_Imatges: str
    nivell_logging: str
    host: str = None
    port: str = None
    database: str = None
    user: str = None
    password: str = None
    repository = None
    sensor = None
    navegador = None
    cercador = None

    def __post_init__(self):
        self.configure_logging()
        self.current_directory = os.getcwd()  # No funciona al executar-se amb CRON
        # self.current_directory = '/home/catalanet/XMCD'

    def configure_logging(self):
        """Configura el logging amb els paràmetres desitjats."""
        level = getattr(logging, self.nivell_logging.upper(), None)
        if not isinstance(level, int):
            raise ValueError(
                f'Nivell de logging invàlid: {self.nivell_logging}')
        logging.basicConfig(filename=self.fitxer_logs, level=level,
                            format=self.define_format(), encoding='utf-8')

    @staticmethod
    def define_format():
        """Defineix i retorna el format de log desitjat."""
        return "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"

    def write_log(self, message, level=logging.ERROR):
        """
        Escriu un missatge de log amb un determinat nivell.

        Arguments:
        - message (str): El missatge que es vol escriure al log.
        - level (int): El nivell de log (ex: logging.ERROR, logging.INFO, ...). Per defecte és logging.ERROR.
        """
        caller_frame = inspect.currentframe().f_back
        caller_file = caller_frame.f_code.co_filename
        caller_line = caller_frame.f_lineno
        caller_function = caller_frame.f_code.co_name

        detailed_message = f"{message} (Cridat des de {caller_file} línia {caller_line} funció {caller_function})"
        logger = logging.getLogger()
        getattr(logger, logging.getLevelName(level).lower())(detailed_message)

    @classmethod
    def carrega_config(cls, config_json):
        """Carrega la configuració des d'un fitxer JSON."""
        config_path = os.path.join(os.getcwd(), config_json)
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            cls.validate_keys(data)
            return cls(**data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error amb el fitxer '{config_json}': {e}")

    @classmethod
    def validate_keys(cls, data):
        """Valida que totes les claus requerides estiguin presents."""
        required_keys = {field.name for field in fields(cls)}
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            raise ValueError(
                f"Fitxer de configuració incomplet. Falten les següents claus: {', '.join(missing_keys)}")

    def set_repository(self, repository):
        """Estableix el repositori per a la configuració."""
        self.repository = repository

    def set_sensor(self, sensor):
        """Estableix el sensor per a la configuració."""
        self.sensor = sensor

    def set_navegador(self, navegador):
        """Estableix el navegador per a la configuració."""
        self.navegador = navegador

    def set_cercador(self, cercador):
        """Estableix el cercador per a la configuració."""
        self.cercador = cercador
