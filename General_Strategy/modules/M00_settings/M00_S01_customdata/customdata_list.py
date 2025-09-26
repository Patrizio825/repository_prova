from AlgorithmImports import *
from .customdata_base import *
import json
import pandas as pd
from io import StringIO

################################################################################################################################################

class Garch_data(OnDataCustomDataBase):
    data_url = "https://raw.githubusercontent.com/Patrizio825/repository_prova/main/rolling_garch_objects.csv"
    delimiter = ";"
    date_column_name = "Row"
    resolution = Resolution.Daily
    date_format = "%Y-%m-%d"
    default_type = float
    fields_type_mapping = {}

    # Se vuoi, puoi aggiungere fields_type_mapping per specificare qualche campo diverso
    # fields_type_mapping = {
    #     "SomeColumn": int,
    #     "AnotherColumn": str,
    # }

################################################################################################################################################

class Config_data(InitializeCustomDataBase):
    def __init__(self, algorithm, file_extension):
        self.algorithm = algorithm
        self.file_type = file_extension
        self.data_path = f"Project_{algorithm.__class__.__name__}_{algorithm.ProjectId}/config_data/config_data.{file_extension}"
        self.data = None

    def LoadData(self, execution_id):
        key = self.data_path

        if not self.algorithm.ObjectStore.ContainsKey(key):
            raise FileNotFoundError(f"File non trovato nell'ObjectStore: {key}")

        try:
            content = self.algorithm.ObjectStore.Read(key)

            if self.file_type == "json":
                raw_data = json.loads(content)

                if isinstance(raw_data, list):
                    self.data = [entry for entry in raw_data if str(entry.get("execution_id")) == str(execution_id)]
                elif isinstance(raw_data, dict):
                    if str(raw_data.get("execution_id")) == str(execution_id):
                        self.data = raw_data
                    else:
                        self.data = {}
                else:
                    raise ValueError("Formato JSON non supportato. Attesa lista di dizionari.")

            elif self.file_type == "csv":
                df = pd.read_csv(StringIO(content), sep=';')
                df.columns = df.columns.str.strip()
                if "execution_id" not in df.columns:
                    raise ValueError("Il CSV non contiene la colonna 'execution_id'")
                self.data = df[df["execution_id"].astype(str) == str(execution_id)]

            else:
                raise NotImplementedError(f"File type '{self.file_type}' non supportato.")

            # ✅ Logging dei dati filtrati
            self.algorithm.logger.debug(f"Filtraggio per execution_id={execution_id}")

            if self.file_type == "json":
                formatted_json = json.dumps(self.data, indent=2, ensure_ascii=False)
                self.algorithm.logger.debug(f"✅ Dati JSON filtrati:\n{formatted_json}")

            elif self.file_type == "csv":
                self.algorithm.logger.debug(f"✅ Dati CSV filtrati:\n{self.data.to_string(index=False)}")

        except json.JSONDecodeError as e:
            raise ValueError(f"Errore nel parsing JSON: {str(e)}")
        except pd.errors.ParserError as e:
            raise ValueError(f"Errore nel parsing CSV: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Errore generico nel caricamento dati: {str(e)}")

    def GetData(self):
        if self.data is None:
            raise RuntimeError("Dati non caricati. Chiama LoadData prima.")
        return self.data

################################################################################################################################################
