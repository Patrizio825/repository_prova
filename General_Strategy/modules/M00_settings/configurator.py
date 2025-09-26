from AlgorithmImports import *
from modules.M00_settings.logger import Logger
from modules.M00_settings.dataentry import DataEntry
from modules.M00_settings.executor import Executor

class Configurator:
    def __init__(self, algorithm, logging_enabled=True, logging_level="INFO", execution_id="1"):
        self.algorithm = algorithm
        self.execution_id = execution_id
        self.initialize_all(logging_enabled, logging_level)

    def initialize_all(self, logging_enabled, logging_level):
        # Step 1: Initialize Logger
        logger = self.initialize_logger(logging_enabled, logging_level)
        self.algorithm.logger = logger

        # Step 2: Initialize DataEntry (che carica config e registra securities)
        dataentry = self.initialize_dataentry(logger)
        self.algorithm.dataentry = dataentry
        self.algorithm.config_dict = dataentry.config_data

        # Step 3: Initialize Executor
        executor = self.initialize_executor(logger)
        self.algorithm.executor = executor

        logger.info("✅ Inizializzazione completata.")

    def initialize_logger(self, enabled, level):
        return Logger(
            algorithm=self.algorithm,
            enabled=enabled,
            level=level
        )

    def initialize_dataentry(self, logger):
        logger.info("Inizializzazione DataEntry...")
        try:
            dataentry = DataEntry(self.algorithm, logger, execution_id=self.execution_id)
            logger.info("✅ DataEntry inizializzato correttamente.")
            return dataentry
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione di DataEntry: {e}")
            raise

    def initialize_executor(self, logger):
        logger.info("Inizializzazione Executor...")
        try:
            executor = Executor(self.algorithm, logger)
            logger.info("✅ Executor inizializzato correttamente.")
            return executor
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione di Executor: {e}")
            raise
