from AlgorithmImports import *
from datetime import datetime

################################################################################################################################################

class OnDataCustomDataBase(PythonData):
    """
    Classe base per dati personalizzati caricati in OnData (streaming).
    La classe figlia deve definire:
        - data_url o data_path (remote o locale)
        - date_column_name (nome colonna data)
        - date_format (formato data)
        - fields_type_mapping (dict colonna -> funzione conversione)
        - default_type (funzione conversione default, default str)
        - resolution (Resolution.Daily, Hour, Minute)
    """
    headers = None
    default_type = str
    delimiter = ","  # <-- Default, sovrascrivibile nella figlia
    resolution = None  # <-- Deve essere definita nella figlia

    def GetSource(self, config, date, isLive):
        if hasattr(self, 'data_url'):
            return SubscriptionDataSource(self.data_url, SubscriptionTransportMedium.RemoteFile)
        elif hasattr(self, 'data_path'):
            return SubscriptionDataSource(self.data_path, SubscriptionTransportMedium.LocalFile)
        else:
            raise ValueError("Devi definire 'data_url' o 'data_path'")

    def Reader(self, config, line, date, isLiveMode):
        if OnDataCustomDataBase.headers is None:
            OnDataCustomDataBase.headers = line.strip().split(self.delimiter)
            return None

        parts = line.strip().split(self.delimiter)
        data = type(self)()
        data.Symbol = config.Symbol

        try:
            if self.resolution is None:
                raise ValueError("La classe figlia deve definire 'resolution'")

            date_str = parts[OnDataCustomDataBase.headers.index(self.date_column_name)]

            # Controlli sul formato data
            if self.resolution in [Resolution.Hour, Resolution.Minute]:
                if "%H" not in self.date_format and "%M" not in self.date_format:
                    raise ValueError(f"‼ Il formato data '{self.date_format}' non include ore/minuti per risoluzione {self.resolution}")

            dt = datetime.strptime(date_str, self.date_format)

            # Imposta orario standard per Daily
            if self.resolution == Resolution.Daily:
                dt = dt.replace(hour=16, minute=15, second=0)

            data.Time = dt
            data.EndTime = dt

            for i, header in enumerate(OnDataCustomDataBase.headers):
                if header == self.date_column_name:
                    continue
                convert_func = self.fields_type_mapping.get(header, self.default_type)
                setattr(data, header, convert_func(parts[i]))

        except Exception as e:
            raise ValueError(f"‼ Errore nel parsing della riga: {line}\nDettagli: {e}")

        return data



################################################################################################################################################

import json

class InitializeCustomDataBase:
    """
    Classe base per dati statici caricati una volta in Initialize.
    La classe figlia deve definire:
        - data_path o data_url (file locale o remoto)
        - file_type (es. 'json', 'csv', ...)
    """

    data_path = None
    data_url = None
    file_type = "json"  # default
    data = None

    def LoadData(self):
        """
        Carica i dati da file locale o remoto in memoria.
        Supporta JSON (default) o CSV (da estendere).
        """
        if self.data_path:
            source = self.data_path
            local = True
        elif self.data_url:
            source = self.data_url
            local = False
        else:
            raise ValueError("Devi definire 'data_path' o 'data_url'")

        if self.file_type.lower() == "json":
            self._load_json(source, local)
        elif self.file_type.lower() == "csv":
            self._load_csv(source, local)
        else:
            raise NotImplementedError(f"File type '{self.file_type}' non supportato.")

    def _load_json(self, source, local):
        if local:
            with open(source, "r") as f:
                self.data = json.load(f)
        else:
            import requests
            response = requests.get(source)
            response.raise_for_status()
            self.data = response.json()

    def _load_csv(self, source, local):
        import pandas as pd
        if local:
            self.data = pd.read_csv(source)
        else:
            self.data = pd.read_csv(source)

    def GetData(self):
        """
        Ritorna i dati caricati.
        """
        if self.data is None:
            raise RuntimeError("Dati non caricati. Chiama LoadData prima.")
        return self.data
