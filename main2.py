#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hauptskript für die Ausführung der Wahlanalyse.

Dieses Skript koordiniert den gesamten Analyseprozess:
1. Laden der Daten
2. Validierung
3. Verarbeitung
4. Visualisierung
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import pandas as pd

from src.data_validation import ExtendedDataValidator, ValidationConfig
from src.data_processing import ExtendedDataProcessor
from src.visualization import ElectionVisualizer
from src.config2 import PlotConfig


class ElectionAnalysis:
    """Hauptklasse für die Wahlanalyse."""

    def __init__(
        self,
        data_path: Path,
        output_dir: Path,
        plot_config: Optional[PlotConfig] = None,
        validation_config: Optional[ValidationConfig] = None,
    ):
        """
        Initialisiert die Wahlanalyse.

        Args:
            data_path: Pfad zur Datendatei
            output_dir: Ausgabeverzeichnis
            plot_config: Optionale Plot-Konfiguration
            validation_config: Optionale Validierungs-Konfiguration
        """
        self.data_path = data_path
        self.output_dir = output_dir
        self.plot_config = plot_config or PlotConfig()
        self.validation_config = validation_config or ValidationConfig()

        self.logger = logging.getLogger(__name__)
        self.df: Optional[pd.DataFrame] = None

        # Verarbeitungskomponenten
        self.validator = ExtendedDataValidator(self.validation_config)
        self.processor = ExtendedDataProcessor()
        self.visualizer = ElectionVisualizer(
            output_dir=str(output_dir), config=self.plot_config
        )

    def setup_logging(self) -> None:
        """Konfiguriert das Logging-System."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.output_dir / "logs" / f"election_analysis_{timestamp}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
        self.logger.info("Logging initialisiert")

    def load_data(self) -> None:
        """Lädt die Wahldaten aus der CSV-Datei."""
        try:
            self.df = pd.read_csv(self.data_path)
            self.logger.info(f"Daten erfolgreich geladen aus: {self.data_path}")
            self.logger.debug(f"Geladene Spalten: {self.df.columns.tolist()}")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Daten: {str(e)}")
            raise

    def validate_data(self) -> bool:
        """
        Validiert die geladenen Daten.

        Returns:
            bool: True wenn Validierung erfolgreich, sonst False
        """
        if self.df is None:
            self.logger.error("Keine Daten zum Validieren geladen")
            return False

        is_valid, errors = self.validator.validate_dataframe_extended(self.df)

        if not is_valid:
            self.logger.error(f"Validierungsfehler: {errors}")
            return False

        self.logger.info("Datenvalidierung erfolgreich")
        return True

    def process_data(self) -> Tuple[Dict, Dict]:
        """
        Verarbeitet die validierten Daten.

        Returns:
            Tuple mit Szenarien und regionalen Ergebnissen
        """
        if self.df is None:
            raise ValueError("Keine Daten zum Verarbeiten geladen")

        # Grundlegende Verarbeitung
        self.df = self.processor.calculate_leads(self.df)
        self.df = self.processor.calculate_percentages(self.df)

        # Erweiterte Analysen
        # probabilities, prob_summary = processor.calculate_winning_probability(df)
        # logger.info(f"Wahrscheinlichkeitsanalyse:\n{prob_summary}")
        scenarios = self.processor.analyze_electoral_scenarios(self.df)
        regional_results = self.processor.regional_analysis(self.df)

        self.logger.info("\nAnalyseergebnisse berechnet")
        return scenarios, regional_results

    def create_visualizations(
        self,
        electoral_data: Dict[str, List],
        timeline_data: Tuple[pd.DatetimeIndex, List[float], List[float]],
    ) -> None:
        """
        Erstellt alle Visualisierungen.

        Args:
            electoral_data: Daten für Electoral College Visualisierung
            timeline_data: Daten für Zeitreihenvisualisierung
        """
        if self.df is None:
            raise ValueError("Keine Daten zum Visualisieren geladen")

        # Swing States Visualisierung
        self.visualizer.create_swing_states_visualization(self.df)
        self.logger.info("Swing States Visualisierung erstellt")

        # Electoral College Visualisierung
        self.visualizer.create_electoral_college_visualization(electoral_data)
        self.logger.info("Electoral College Visualisierung erstellt")

        # Zeitreihen Visualisierung
        dates, harris_polls, trump_polls = timeline_data
        self.visualizer.create_national_polls_timeline(dates, harris_polls, trump_polls)
        self.logger.info("Nationale Umfragen Visualisierung erstellt")

    def run(self) -> None:
        """Führt die komplette Analyse durch."""
        try:
            self.setup_logging()
            self.logger.info("Starte Wahlanalyse...")

            # Verzeichnisse vorbereiten
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Hauptprozess
            self.load_data()

            if not self.validate_data():
                return

            scenarios, regional_results = self.process_data()

            # Beispieldaten für Visualisierungen
            electoral_data = {
                "Kategorie": [
                    "Sichere Stimmen Harris",
                    "Sichere Stimmen Trump",
                    "Umkämpft",
                ],
                "Wahlleute": [225, 170, 143],
            }

            timeline_data = (
                pd.date_range(start="2024-09-01", end="2024-11-02", freq="W"),
                [49.0, 48.8, 48.5, 48.2, 48.0, 48.0, 48.0, 47.9, 48.0],
                [47.0, 47.2, 47.5, 47.8, 48.0, 47.8, 47.9, 47.7, 48.0],
            )

            self.create_visualizations(electoral_data, timeline_data)

            # Ergebnisse loggen
            self.logger.info("\nAnalyseergebnisse:")
            self.logger.info(f"Szenarien: {scenarios}")
            self.logger.info(f"Regionale Analyse: {regional_results}")

            self.logger.info("\nAnalyse erfolgreich abgeschlossen!")

        except Exception as e:
            self.logger.error(f"Fehler bei der Analyse: {str(e)}", exc_info=True)
            raise


def main():
    """Hauptfunktion zum Starten der Analyse."""
    analysis = ElectionAnalysis(
        data_path=Path("./data/example_data.csv"), output_dir=Path("./output")
    )
    analysis.run()


if __name__ == "__main__":
    main()
