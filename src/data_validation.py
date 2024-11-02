"""
Modul für die Validierung der Wahldaten.

Dieses Modul stellt Klassen zur Validierung von US-Wahldaten bereit.
Es prüft die Datenintegrität, Staatennamen und Prozentverteilungen.
"""

from typing import List, Tuple, Set, Dict, Optional
import pandas as pd
import logging
from dataclasses import dataclass

# Logger-Konfiguration
logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """Konfigurationsklasse für Validierungsparameter."""

    min_percentage: float = 0.0
    max_percentage: float = 100.0
    total_electoral_votes: int = 536
    percentage_sum_min: float = 94.0
    percentage_sum_max: float = 100.0
    required_columns: Set[str] = frozenset({"Staat", "Harris", "Trump", "Wahlleute"})


class DataValidator:
    """Basisklasse für Datenvalidierung."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        """Initialisiert den Validator mit optionaler Konfiguration."""
        self.config = config or ValidationConfig()

    def validate_percentages(self, values: List[float]) -> Tuple[bool, List[float]]:
        """
        Überprüft, ob alle Werte im gültigen Prozentbereich liegen.

        Args:
            values: Liste von Prozentwerten

        Returns:
            Tuple aus (ist_valid, ungültige_werte)
        """
        invalid_values = [
            x
            for x in values
            if not self.config.min_percentage <= x <= self.config.max_percentage
        ]
        is_valid = len(invalid_values) == 0
        if not is_valid:
            logger.error(f"Ungültige Prozentwerte gefunden: {invalid_values}")
        return is_valid, invalid_values

    def validate_electoral_votes(self, votes: List[int]) -> Tuple[bool, int]:
        """
        Überprüft die Korrektheit der Wahlleute-Summe.

        Args:
            votes: Liste der Wahlleute-Zahlen

        Returns:
            Tuple aus (ist_valid, aktuelle_summe)
        """
        total_votes = sum(votes)
        is_valid = total_votes == self.config.total_electoral_votes
        if not is_valid:
            logger.error(
                f"Ungültige Gesamtzahl der Wahlleute: {total_votes} "
                f"(sollte {self.config.total_electoral_votes} sein)"
            )
        return is_valid, total_votes

    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, str]]:
        """
        Validiert das gesamte DataFrame auf Korrektheit.

        Args:
            df: pandas DataFrame mit Wahldaten

        Returns:
            Tuple aus (ist_valid, fehlermeldungen)
        """
        validation_results = {}

        # Debug-Ausgabe
        logger.info(f"Verfügbare Spalten: {df.columns.tolist()}")

        # Spaltenprüfung
        missing_columns = self.config.required_columns - set(df.columns)
        if missing_columns:
            msg = f"Fehlende Spalten: {missing_columns}"
            logger.error(msg)
            validation_results["missing_columns"] = msg
            return False, validation_results

        try:
            # Prozentprüfung
            harris_valid, harris_invalid = self.validate_percentages(df["Harris"])
            trump_valid, trump_invalid = self.validate_percentages(df["Trump"])

            if not (harris_valid and trump_valid):
                validation_results["invalid_percentages"] = {
                    "Harris": harris_invalid,
                    "Trump": trump_invalid,
                }

            # Wahlleute-Prüfung
            votes_valid, total_votes = self.validate_electoral_votes(df["Wahlleute"])
            if not votes_valid:
                validation_results["invalid_votes"] = total_votes

            return len(validation_results) == 0, validation_results

        except Exception as e:
            logger.error(f"Validierungsfehler: {str(e)}")
            validation_results["error"] = str(e)
            return False, validation_results


class ExtendedDataValidator(DataValidator):
    """Erweiterte Validierungsklasse mit zusätzlichen Prüfungen."""

    VALID_STATES: Set[str] = {
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
        "District of Columbia",
    }

    def validate_state_names(self, states: List[str]) -> Tuple[bool, Set[str]]:
        """
        Überprüft die Gültigkeit der Staatennamen.

        Args:
            states: Liste der zu prüfenden Staatennamen

        Returns:
            Tuple aus (ist_valid, ungültige_staaten)
        """
        invalid_states = set(states) - self.VALID_STATES
        is_valid = len(invalid_states) == 0
        if not is_valid:
            logger.error(f"Ungültige Staatennamen gefunden: {invalid_states}")
        return is_valid, invalid_states

    def validate_sum_to_hundred(
        self, row: pd.Series, tolerance: float = 6.0
    ) -> Tuple[bool, float]:
        """
        Überprüft, ob die Prozentsummen plausibel sind.

        Args:
            row: Eine Zeile aus dem DataFrame
            tolerance: Erlaubte Abweichung von 100% (für sonstige Kandidaten)

        Returns:
            Tuple aus (ist_valid, summe)
        """
        total = row["Harris"] + row["Trump"]
        is_valid = (
            self.config.percentage_sum_min <= total <= self.config.percentage_sum_max
        )
        return is_valid, total

    def validate_dataframe_extended(
        self, df: pd.DataFrame
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Erweiterte Validierung mit detailliertem Fehlerbericht.

        Args:
            df: pandas DataFrame mit Wahldaten

        Returns:
            Tuple aus (ist_valid, fehlermeldungen)
        """
        errors = {}

        # Basis-Validierung
        base_valid, base_errors = self.validate_dataframe(df)
        if not base_valid:
            errors["base_validation"] = base_errors

        # Staatennamen-Validierung
        states_valid, invalid_states = self.validate_state_names(df["Staat"].tolist())
        if not states_valid:
            errors["invalid_states"] = list(invalid_states)

        # Prozentsummen-Validierung
        invalid_sums = []
        for idx, row in df.iterrows():
            is_valid, total = self.validate_sum_to_hundred(row)
            if not is_valid:
                invalid_sums.append(
                    {
                        "state": row["Staat"],
                        "total": total,
                        "harris": row["Harris"],
                        "trump": row["Trump"],
                    }
                )

        if invalid_sums:
            errors["invalid_sums"] = invalid_sums

        return len(errors) == 0, errors


def create_validator(
    config: Optional[ValidationConfig] = None,
) -> ExtendedDataValidator:
    """Factory-Funktion für einen konfigurierten Validator."""
    return ExtendedDataValidator(config or ValidationConfig())
