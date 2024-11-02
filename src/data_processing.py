"""
Modul für die Verarbeitung der Wahldaten.

Bietet Klassen und Funktionen zur Analyse und Verarbeitung von US-Wahldaten,
einschließlich Trend-, Regional- und Wahrscheinlichkeitsanalysen.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np
from scipy.stats import norm
import logging
from datetime import datetime

# Logger Konfiguration
logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Basisklasse für Verarbeitungsfehler."""

    pass


class DataError(ProcessingError):
    """Fehler bei der Datenverarbeitung."""

    pass


class CalculationError(ProcessingError):
    """Fehler bei Berechnungen."""

    pass


@dataclass
class ProcessingConfig:
    """Konfigurationsklasse für Datenverarbeitung."""

    margin_of_error: float = 2.0
    close_race_threshold: float = 1.0
    window_size: int = 7
    rounding_decimals: int = 2
    min_data_points: int = 3
    confidence_level: float = 0.95


class DataProcessor:
    """Basisklasse für Datenverarbeitung."""

    def __init__(self, config: Optional[ProcessingConfig] = None):
        """
        Initialisiert den DataProcessor.

        Args:
            config: Optionale Konfiguration für die Verarbeitung
        """
        self.config = config or ProcessingConfig()
        self.logger = logging.getLogger(__name__)

    def _validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> None:
        """
        Validiert die Eingabedaten.

        Args:
            df: DataFrame zur Validierung
            required_columns: Liste erforderlicher Spalten

        Raises:
            DataError: Bei ungültigen oder fehlenden Daten
        """
        if df is None or df.empty:
            raise DataError("DataFrame ist leer oder None")

        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise DataError(f"Fehlende Spalten: {missing_cols}")

    def calculate_leads(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Berechnet die Führung für jeden Staat.

        Args:
            df: DataFrame mit Wahldaten

        Returns:
            DataFrame mit berechneter Führung

        Raises:
            DataError: Bei Problemen mit den Daten
            CalculationError: Bei Berechnungsfehlern
        """
        try:
            self._validate_data(df, ["Harris", "Trump"])

            result_df = df.copy()
            result_df["Führung"] = (result_df["Harris"] - result_df["Trump"]).round(
                self.config.rounding_decimals
            )

            return result_df

        except Exception as e:
            raise CalculationError(f"Fehler bei Führungsberechnung: {str(e)}")

    def calculate_percentages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Berechnet Prozentanteile für beide Kandidaten.

        Args:
            df: DataFrame mit Wahldaten

        Returns:
            DataFrame mit berechneten Prozentanteilen

        Raises:
            DataError: Bei Problemen mit den Daten
            CalculationError: Bei Berechnungsfehlern
        """
        try:
            self._validate_data(df, ["Harris", "Trump", "Wahlleute"])

            result_df = df.copy()
            total_votes = result_df["Wahlleute"].sum()

            if total_votes == 0:
                raise CalculationError("Gesamtzahl der Wahlleute ist 0")

            for candidate in ["Harris", "Trump"]:
                result_df[f"{candidate}_Anteil"] = (
                    result_df["Wahlleute"]
                    * (result_df[candidate] / 100)
                    / total_votes
                    * 100
                ).round(self.config.rounding_decimals)

            return result_df

        except Exception as e:
            raise CalculationError(f"Fehler bei Prozentberechnung: {str(e)}")


class ExtendedDataProcessor(DataProcessor):
    """Erweiterte Datenverarbeitungsklasse mit zusätzlichen Analysen."""

    REGIONS: Dict[str, List[str]] = {
        "Nordosten": [
            "Maine",
            "New Hampshire",
            "Vermont",
            "Massachusetts",
            "Rhode Island",
            "Connecticut",
            "New York",
            "New Jersey",
            "Pennsylvania",
        ],
        "Mittlerer_Westen": [
            "Ohio",
            "Indiana",
            "Illinois",
            "Michigan",
            "Wisconsin",
            "Minnesota",
            "Iowa",
            "Missouri",
            "North Dakota",
            "South Dakota",
            "Nebraska",
            "Kansas",
        ],
        "Süden": [
            "Delaware",
            "Maryland",
            "Virginia",
            "West Virginia",
            "North Carolina",
            "South Carolina",
            "Georgia",
            "Florida",
            "Kentucky",
            "Tennessee",
            "Alabama",
            "Mississippi",
            "Arkansas",
            "Louisiana",
            "Oklahoma",
            "Texas",
        ],
        "Westen": [
            "Montana",
            "Idaho",
            "Wyoming",
            "Colorado",
            "New Mexico",
            "Arizona",
            "Utah",
            "Nevada",
            "California",
            "Oregon",
            "Washington",
            "Alaska",
            "Hawaii",
        ],
    }

    def calculate_winning_probability(
        self, df: pd.DataFrame, margin_of_error: Optional[float] = None
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Berechnet Gewinnwahrscheinlichkeiten unter Berücksichtigung der Fehlermarge.

        Args:
            df: DataFrame mit Umfragedaten
            margin_of_error: Optionale Fehlermarge in Prozentpunkten

        Returns:
            Tuple aus (DataFrame mit Wahrscheinlichkeiten, Zusammenfassung)

        Raises:
            CalculationError: Bei Berechnungsfehlern
        """
        try:
            margin = margin_of_error or self.config.margin_of_error
            result_df = self.calculate_leads(df)

            # Z-Score Berechnung
            result_df["Z_Score"] = result_df["Führung"] / (margin / 1.96)

            # Gewinnwahrscheinlichkeiten
            result_df["Harris_Gewinnchance"] = (
                norm.cdf(result_df["Z_Score"]) * 100
            ).round(self.config.rounding_decimals)

            result_df["Trump_Gewinnchance"] = (
                100 - result_df["Harris_Gewinnchance"]
            ).round(self.config.rounding_decimals)

            # Gesamtzusammenfassung
            summary = {
                "Harris_Gesamt_Chance": (
                    result_df["Harris_Gewinnchance"] * result_df["Wahlleute"]
                ).sum()
                / result_df["Wahlleute"].sum(),
                "Trump_Gesamt_Chance": (
                    result_df["Trump_Gewinnchance"] * result_df["Wahlleute"]
                ).sum()
                / result_df["Wahlleute"].sum(),
                "Durchschnittliche_Führung": result_df["Führung"].mean(),
                "Median_Führung": result_df["Führung"].median(),
                "Zeitpunkt": datetime.now().isoformat(),
            }

            return result_df, summary

        except Exception as e:
            raise CalculationError(
                f"Fehler bei Wahrscheinlichkeitsberechnung: {str(e)}"
            )

    def analyze_electoral_scenarios(
        self, df: pd.DataFrame
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analysiert verschiedene Electoral College Szenarien.

        Args:
            df: DataFrame mit Wahldaten

        Returns:
            Dictionary mit verschiedenen Szenarien und deren Analysen
        """
        try:
            scenarios = {}

            # Basisszenario
            base_votes = {
                "Harris": df[df["Harris"] > df["Trump"]]["Wahlleute"].sum(),
                "Trump": df[df["Trump"] > df["Harris"]]["Wahlleute"].sum(),
                "Unentschieden": df[df["Harris"] == df["Trump"]]["Wahlleute"].sum(),
            }
            scenarios["Basisszenario"] = {
                "Wahlleute": base_votes,
                "Siegwahrscheinlichkeit": {
                    "Harris": base_votes["Harris"] / 538 * 100,
                    "Trump": base_votes["Trump"] / 538 * 100,
                },
            }

            # Knappe-Staaten-Analyse
            close_states = df[
                abs(df["Harris"] - df["Trump"]) < self.config.close_race_threshold
            ]
            scenarios["Knappe_Staaten"] = {
                "Anzahl": len(close_states),
                "Wahlleute": close_states["Wahlleute"].sum(),
                "Staaten": close_states["Staat"].tolist(),
                "Durchschnittliche_Differenz": abs(
                    close_states["Harris"] - close_states["Trump"]
                ).mean(),
            }

            # Tipping-Point-Analyse
            df_sorted = df.sort_values(by="Führung")
            cumsum = df_sorted["Wahlleute"].cumsum()
            tipping_point_idx = (cumsum >= 270).idxmax()
            scenarios["Tipping_Point"] = {
                "Staat": df_sorted.loc[tipping_point_idx, "Staat"],
                "Führung": df_sorted.loc[tipping_point_idx, "Führung"],
                "Wahlleute": df_sorted.loc[tipping_point_idx, "Wahlleute"],
            }

            return scenarios

        except Exception as e:
            raise CalculationError(f"Fehler bei Szenarioanalyse: {str(e)}")

    def regional_analysis(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Führt eine detaillierte regionale Analyse der Wahlergebnisse durch.

        Args:
            df: DataFrame mit Wahldaten

        Returns:
            Dictionary mit regionalen Analyseergebnissen
        """
        try:
            regional_results = {}

            for region, states in self.REGIONS.items():
                regional_df = df[df["Staat"].isin(states)]

                if regional_df.empty:
                    self.logger.warning(f"Keine Daten für Region {region}")
                    continue

                # Grundlegende Statistiken
                stats = {
                    "Durchschnitt_Harris": regional_df["Harris"].mean(),
                    "Durchschnitt_Trump": regional_df["Trump"].mean(),
                    "Median_Harris": regional_df["Harris"].median(),
                    "Median_Trump": regional_df["Trump"].median(),
                    "Wahlleute_Gesamt": regional_df["Wahlleute"].sum(),
                    "Anzahl_Staaten": len(regional_df),
                    "Führender": (
                        "Harris"
                        if regional_df["Harris"].mean() > regional_df["Trump"].mean()
                        else "Trump"
                    ),
                }

                # Erweiterte Analysen
                stats.update(
                    {
                        "Standardabweichung_Harris": regional_df["Harris"].std(),
                        "Standardabweichung_Trump": regional_df["Trump"].std(),
                        "Max_Führung": regional_df["Führung"].max(),
                        "Min_Führung": regional_df["Führung"].min(),
                        "Knappe_Staaten": len(
                            regional_df[
                                abs(regional_df["Harris"] - regional_df["Trump"])
                                < self.config.close_race_threshold
                            ]
                        ),
                    }
                )

                regional_results[region] = stats

            return regional_results

        except Exception as e:
            raise CalculationError(f"Fehler bei regionaler Analyse: {str(e)}")

    def trending_analysis(
        self, time_series_data: pd.DataFrame, window_size: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Führt eine umfassende Trendanalyse der Umfragedaten durch.

        Args:
            time_series_data: DataFrame mit Zeitreihendaten
            window_size: Optionale Fenstergröße für gleitenden Durchschnitt

        Returns:
            Tuple aus (DataFrame mit Trends, Trendzusammenfassung)
        """
        try:
            df = time_series_data.copy()
            window = window_size or self.config.window_size

            # Gleitende Durchschnitte
            for candidate in ["Harris", "Trump"]:
                df[f"{candidate}_MA"] = (
                    df[candidate]
                    .rolling(window=window, min_periods=self.config.min_data_points)
                    .mean()
                )

                # Trend-Richtung
                df[f"{candidate}_Trend"] = np.where(
                    df[f"{candidate}_MA"] > df[f"{candidate}_MA"].shift(1),
                    "Steigend",
                    "Fallend",
                )

                # Momentum-Berechnung
                df[f"{candidate}_Momentum"] = (
                    df[f"{candidate}_MA"] - df[f"{candidate}_MA"].shift(window)
                ).round(self.config.rounding_decimals)

            # Trendzusammenfassung
            summary = {
                "Harris_Momentum_Gesamt": df["Harris_Momentum"].mean(),
                "Trump_Momentum_Gesamt": df["Trump_Momentum"].mean(),
                "Harris_Positive_Tage": (df["Harris_Trend"] == "Steigend").sum(),
                "Trump_Positive_Tage": (df["Trump_Trend"] == "Steigend").sum(),
                "Letzte_Führung": df["Harris"].iloc[-1] - df["Trump"].iloc[-1],
                "Trend_Zeitraum": f"{df.index[0]} bis {df.index[-1]}",
            }

            return df, summary

        except Exception as e:
            raise CalculationError(f"Fehler bei Trendanalyse: {str(e)}")


def create_processor(
    config: Optional[ProcessingConfig] = None,
) -> ExtendedDataProcessor:
    """Factory-Funktion für einen konfigurierten Processor."""
    return ExtendedDataProcessor(config or ProcessingConfig())
