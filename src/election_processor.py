"""
Modul zur Verarbeitung der Wahlergebnisdaten.
"""

import pandas as pd
import numpy as np  # Hinzugefügt, um die Nutzung von 'np' zu ermöglichen
import re
import logging
import pickle
from pathlib import Path
from typing import Optional, Dict, Any
from .config import CacheConfig

# Logger Setup
logger = logging.getLogger(__name__)


class ElectionDataProcessor:
    """
    Verarbeitet die Wahlergebnisdaten aus der Textdatei.
    Implementiert Caching und Datenvalidierung.
    """

    def __init__(self, input_file: str, cache_config: CacheConfig):
        """
        Initialisiert den Datenprocessor.

        Args:
            input_file: Pfad zur Eingabedatei
            cache_config: Cache-Konfiguration
        """
        self.input_path = Path(input_file)
        self.cache_config = cache_config
        self.cache_dir = Path(cache_config.CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        self._df: Optional[pd.DataFrame] = None

    @property
    def data(self) -> pd.DataFrame:
        """Gibt den verarbeiteten DataFrame zurück."""
        if self._df is None:
            raise ValueError(
                "Daten wurden noch nicht verarbeitet. Rufen Sie zuerst process_data() auf."
            )
        return self._df

    def validate_input(self) -> bool:
        """
        Überprüft die Eingabedatei.

        Returns:
            bool: True wenn die Datei valide ist
        """
        if not self.input_path.exists():
            logger.error(f"Eingabedatei nicht gefunden: {self.input_path}")
            return False

        if self.input_path.stat().st_size == 0:
            logger.error(f"Eingabedatei ist leer: {self.input_path}")
            return False

        return True

    def _get_cache_path(self) -> Path:
        """Erstellt den Cache-Pfad für die Eingabedatei."""
        return self.cache_dir / f"{self.input_path.stem}_cache.pkl"

    def _load_from_cache(self) -> Optional[pd.DataFrame]:
        """
        Versucht, Daten aus dem Cache zu laden.

        Returns:
            Optional[pd.DataFrame]: Gecachte Daten oder None
        """
        cache_path = self._get_cache_path()
        if cache_path.exists():
            try:
                modification_time = cache_path.stat().st_mtime
                if (
                    pd.Timestamp.now().timestamp() - modification_time
                ) < self.cache_config.CACHE_EXPIRY:
                    with open(cache_path, "rb") as f:
                        logger.info(f"Daten aus Cache geladen: {cache_path}")
                        return pickle.load(f)
            except Exception as e:
                logger.warning(f"Fehler beim Laden aus Cache: {e}")
        return None

    def _save_to_cache(self, df: pd.DataFrame):
        """Speichert die verarbeiteten Daten im Cache."""
        try:
            cache_path = self._get_cache_path()
            with open(cache_path, "wb") as f:
                pickle.dump(df, f)
            logger.info(f"Daten im Cache gespeichert: {cache_path}")
        except Exception as e:
            logger.warning(f"Fehler beim Speichern im Cache: {e}")

    def _extract_election_data(self, text: str) -> Dict[str, Any]:
        """
        Extrahiert die Wahlergebnisse aus dem Text.

        Args:
            text: Eingabetext mit Wahlergebnissen

        Returns:
            Dict mit extrahierten Daten
        """
        state_pattern = r"([A-Za-z\s]+):\s+Harris\s+(\d+),\s+Trump\s+(\d+)"
        matches = re.findall(state_pattern, text)

        data = {"State": [], "Harris": [], "Trump": []}

        for match in matches:
            data["State"].append(match[0].strip())
            data["Harris"].append(int(match[1]))
            data["Trump"].append(int(match[2]))

        return data

    def _validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validiert die verarbeiteten Daten.

        Args:
            df: Zu validierende Daten

        Returns:
            bool: True wenn Daten valide sind
        """
        try:
            # Überprüfe Struktur
            required_columns = {"State", "Harris", "Trump"}
            if not all(col in df.columns for col in required_columns):
                logger.error("Fehlende Spalten im DataFrame")
                return False

            # Überprüfe Werte
            if df["Harris"].isna().any() or df["Trump"].isna().any():
                logger.error("NA-Werte in den Stimmdaten gefunden")
                return False

            if (df["Harris"] < 0).any() or (df["Trump"] < 0).any():
                logger.error("Negative Stimmwerte gefunden")
                return False

            # Überprüfe Berechnungen
            df["Total"] = df["Harris"] + df["Trump"]
            if (df["Total"] <= 0).any():
                logger.error("Ungültige Gesamtstimmen gefunden")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler bei der Datenvalidierung: {e}")
            return False

    def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Erweitert die Daten um zusätzliche Berechnungen.

        Args:
            df: Eingabe-DataFrame

        Returns:
            Erweiterter DataFrame
        """
        # Gesamtstimmen
        df["Total"] = df["Harris"] + df["Trump"]

        # Prozentuale Anteile
        df["Harris_Percentage"] = (df["Harris"] / df["Total"] * 100).round(1)
        df["Trump_Percentage"] = (df["Trump"] / df["Total"] * 100).round(1)

        # Führenden Kandidaten
        df["Leading"] = np.where(df["Harris"] > df["Trump"], "Harris", "Trump")

        # Vorsprung in Stimmen
        df["Margin"] = (df["Harris"] - df["Trump"]).abs()

        # Sortierung nach Gesamtstimmen
        df = df.sort_values("Total", ascending=False)

        return df

    def process_data(self) -> pd.DataFrame:
        """
        Hauptmethode zur Datenverarbeitung.

        Returns:
            Verarbeiteter DataFrame
        """
        # Validiere Eingabe
        if not self.validate_input():
            raise ValueError(f"Ungültige Eingabedatei: {self.input_path}")

        # Versuche Cache-Laden
        df = self._load_from_cache()
        if df is not None:
            self._df = df
            return df

        # Verarbeite Daten
        try:
            # Lese Datei
            with open(self.input_path, "r", encoding="utf-8") as file:
                text = file.read()

            # Extrahiere Daten
            data = self._extract_election_data(text)
            df = pd.DataFrame(data)

            # Validiere
            if not self._validate_data(df):
                raise ValueError("Datenvalidierung fehlgeschlagen")

            # Erweitere Daten
            df = self._enrich_data(df)

            # Speichere im Cache
            self._save_to_cache(df)

            self._df = df
            return df

        except Exception as e:
            logger.error(f"Fehler bei der Datenverarbeitung: {e}")
            raise
