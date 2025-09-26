from AlgorithmImports import *
from modules import Configurator
from modules.M00_settings.M00_S01_customdata import *

class General_Strategy(QCAlgorithm):

    def Initialize(self):
        self.configurator = Configurator(
                                          self
                                        , logging_enabled = True
                                        , logging_level = "DEBUG"
                                        , execution_id = "1"
        )
        
        # # Esempio di cambio configurazione runtime (ora gestito dal logger)
        # self.logger.set_level("INFO")
        # self.logger.set_enabled(False)

        self.SetStartDate(2024, 1, 1)
        self.SetCash(100000)

        self.printed_garch = False
        self.printed_spx = False

    def OnData(self, data: Slice):
        if self.printed_garch and self.printed_spx:
            return  # Stoppa il print dopo la prima stampa di entrambi

        self.logger.info("=== ESECUZIONE OnData ===")

        for key, info in self.dataentry.securities.items():
            symbol = info.get("symbol")

            if key == "garch_data_customdata_daily_usa" and not self.printed_garch:
                garch = data.get(symbol)
                mu = getattr(garch, 'mu_h1', None) if garch else None
                if garch:
                    self.logger.info(f"{data.Time} | [GARCH DATA] ✅ mu_h1 = {mu}")
                    self.printed_garch = True
                else:
                    self.logger.info(f"{data.Time} | [GARCH DATA] ❌ Nessun dato")

            elif "spx" in key and "indexoption" in key and not self.printed_spx:
                chain = data.OptionChains.get(symbol)
                if chain:
                    self.logger.info(f"{data.Time} | [SPX OPTIONCHAIN] ✅ {len(chain)} contratti")
                    self.printed_spx = True
                else:
                    self.logger.info(f"{data.Time} | [SPX OPTIONCHAIN] ❌ Nessuna OptionChain")
