"""US-Wahlergebnisse Visualisierung 2024
------------------------------------
Dieses Skript visualisiert die Wahlergebnisse der US-Wahl 2024 für Harris und Trump.
Es bietet eine interaktive Darstellung mit Skalierungsmöglichkeit und automatischem Export.

Author: Jan Unger
Version: 1.0.1
Last Update: 2024-11-01
"""

import sys
import logging
import cProfile
import pstats
from pathlib import Path
from contextlib import contextmanager
from time import time

from src.cli_handler import CLIHandler
from src.election_processor import ElectionDataProcessor
from src.election_visualizer import ElectionVisualizer
from src.data_exporter import DataExporter
from src.config import PlotConfig, ExportConfig, CacheConfig

logger = logging.getLogger(__name__)


@contextmanager
def timer(description: str):
    """Context Manager für Zeitmessung."""
    start = time()
    yield
    elapsed = time() - start
    logger.debug(f"{description}: {elapsed:.2f} Sekunden")


class ElectionVisualizationApp:
    """Hauptanwendungsklasse."""

    def __init__(self):
        """Initialisiert die Anwendung."""
        self.cli_handler = CLIHandler()
        self.args = None
        self.dirs = None

    def run(self):
        """Führt die Hauptanwendungslogik aus."""
        try:
            # Verarbeite Kommandozeilenargumente
            self.args = self.cli_handler.parse_args()

            # Profiling wenn aktiviert
            if self.args.profile:
                return self._run_with_profiling()
            else:
                return self._run_main()

        except Exception as e:
            logger.error(f"Fehler bei der Ausführung: {e}", exc_info=self.args.debug)
            return 1

    def _run_with_profiling(self):
        """Führt das Programm mit Profiling aus."""
        profiler = cProfile.Profile()
        try:
            profiler.enable()
            result = self._run_main()
            profiler.disable()

            # Speichere Profiling-Ergebnisse
            stats = pstats.Stats(profiler)
            stats.sort_stats("cumulative")

            profile_path = Path(self.args.output) / "profile_stats.txt"
            with open(profile_path, "w") as f:
                stats.stream = f
                stats.print_stats()

            logger.info(f"Profiling-Ergebnisse gespeichert in: {profile_path}")
            return result

        except Exception as e:
            logger.error(f"Fehler beim Profiling: {e}", exc_info=True)
            return 1

    def _run_main(self):
        """Hauptausführungslogik."""
        # Erstelle Verzeichnisse
        self.dirs = self.cli_handler.setup_output_dirs(self.args)

        # Cache-Handling
        self.cli_handler.handle_cache(self.args, self.dirs["cache"])

        # Konfigurationen
        plot_config = PlotConfig()
        export_config = ExportConfig(OUTPUT_DIR=str(self.dirs["exports"]))
        cache_config = CacheConfig(
            CACHE_DIR=str(self.dirs["cache"]),
            CACHE_ENABLED=not self.args.no_cache,  # Jetzt in der CacheConfig-Klasse definiert
        )

        with timer("Gesamtausführung"):
            # Datenverarbeitung
            with timer("Datenverarbeitung"):
                processor = ElectionDataProcessor(self.args.input, cache_config)
                df = processor.process_data()

            # Visualisierung
            with timer("Visualisierung"):
                visualizer = ElectionVisualizer(df, plot_config)
                fig, slider = visualizer.create_plot()

                # Speichere Plots
                if self.args.format != "none":
                    formats = (
                        ["png", "svg", "pdf"]
                        if self.args.format == "all"
                        else [self.args.format]
                    )
                    for fmt in formats:
                        output_path = self.dirs["plots"] / f"wahlergebnisse_2024.{fmt}"
                        fig.savefig(output_path, bbox_inches="tight", dpi=self.args.dpi)
                        logger.info(f"Plot gespeichert als: {output_path}")

            # Datenexport
            if self.args.export:
                with timer("Datenexport"):
                    exporter = DataExporter(export_config)
                    exporter.export_selected(df, self.args.export)

                    if "summary" in self.args.export:
                        summary_path = exporter.export_summary(df)
                        logger.info(f"Zusammenfassung erstellt: {summary_path}")

            # Zeige Plot im interaktiven Modus
            if not self.args.no_interactive:
                visualizer.show()

        return 0


def main():
    """Programmstart."""
    app = ElectionVisualizationApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
