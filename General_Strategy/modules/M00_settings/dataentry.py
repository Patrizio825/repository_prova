from AlgorithmImports import *
from .M00_S01_customdata import *
import json

class DataEntry:
    def __init__(self, algorithm, logger, execution_id="1"):
        self.algorithm = algorithm
        self.logger = logger
        self.config_data = None
        self.securities = {}

        # Carica config e registra securities subito all'inizializzazione
        self.config_data = self._load_config_data(execution_id)
        self.add_securities()

    def _load_config_data(self, execution_id):
        """Carica i dati di configurazione JSON dall'ObjectStore"""
        self.logger.info("Caricamento dati di configurazione JSON...")

        try:
            config_data = Config_data(self.algorithm, file_extension="json")
            config_data.LoadData(execution_id)
            data = config_data.GetData()

            if not data:
                msg = f"⚠ Nessun dato di configurazione trovato per execution_id {execution_id}"
                self.logger.error(f"‼ {msg}")
                raise ValueError(msg)

            self.logger.info("✅ Dati JSON caricati con successo")
            self.logger.info(json.dumps(data, indent=2, ensure_ascii=False))
            return data

        except FileNotFoundError as e:
            self.logger.warning(f"⚠ File config JSON non trovato: {e}")
            return []
        except Exception as e:
            self.logger.error(f"‼ Errore durante il caricamento config JSON: {e}")
            raise

    def add_securities(self):
        """Registra tutte le security definite nella configurazione"""
        if self.config_data is None:
            raise RuntimeError("Config data non caricato. Chiamare load_config_data prima.")

        self.logger.info("Registrazione delle security in corso...")

        for execution in self.config_data:
            for strategy_group in execution.get("strategy_groups", []):
                for strategy in strategy_group.get("strategies", []):
                    for security in strategy.get("security", []):
                        
                        ticker          = str(security["ticker"])
                        security_type   = str(security["security_type"])
                        resolution      = str(security["resolution"])
                        market          = str(security.get("market", "USA"))
                        # Chiave basata solo sul ticker e attributi standardizzati
                        key = (ticker, security_type, resolution, market)
                        self.get_security(key, security)

        self.logger.info("✅ Registrazione security completata.")

    def get_security(self, key, security):
        """Converte, valida e registra la singola security"""
        for row in self.securities.values():
            if row["key"] == key:
                security["ticker"]          = row["ticker"]
                security["security_type"]   = row["security_type"]
                security["resolution"]      = row["resolution"]
                security["market"]          = row["market"]
                security["symbol"]          = row["symbol"]
                security["security_object"] = row["security_object"]
                return

        ticker, security_type, resolution, market = key

        # Validazione e conversione Security_Type

        if security_type == "CustomData":
            custom_class = getattr(customdata_list, ticker, None)
            if custom_class is None:
                raise ValueError(f"‼ Classe CustomData non trovata per ticker: {ticker}")
            security_type = custom_class
        else:
            try:
                security_type = getattr(SecurityType, security_type)
            except AttributeError:
                raise ValueError(f"‼ SecurityType non valido: {security_type}")

        # Validazione e conversione resolution
        try:
            resolution = getattr(Resolution, resolution)
        except AttributeError:
            raise ValueError(f"‼ Resolution non valida: {resolution}")

        # Validazione e conversione market
        try:
            market = getattr(Market, market)
        except AttributeError:
            raise ValueError(f"‼ Market non valido: {market}")

        # Aggiunta security in base al tipo
        if issubclass(security_type, OnDataCustomDataBase):
            security_object = self.algorithm.AddData(security_type, ticker, resolution)
        elif security_type == SecurityType.Option:
            security_object = self.algorithm.AddOption(ticker, resolution, market)
        elif security_type == SecurityType.IndexOption:
            security_object = self.algorithm.AddIndexOption(ticker, resolution, market)
        else:
            raise ValueError(f"‼ SecurityType non mappato: {security_type}")

        self.logger.info(f"✅ Security aggiunta:  [{ticker}, {security_type}, {resolution}, {market}]")

        # Salva riferimento nel dizionario originale
        security["ticker"] = ticker
        security["security_type"] = security_type
        security["resolution"] = resolution
        security["market"] = market
        security["symbol"] = security_object.Symbol
        security["security_object"] = security_object

        num = "_".join(str(part).lower() for part in key)

        self.securities[num] = {
            "key": key,
            "ticker": ticker,
            "security_type": security_type,
            "resolution": resolution,
            "market": market,
            "security_object": security_object,
            "symbol": security_object.Symbol
        }
