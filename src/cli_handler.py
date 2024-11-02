"""
Kommandozeilen-Interface für die Wahlergebnisvisualisierung.
"""

import argparse
import logging
from pathlib import Path
from argparse import Namespace
from datetime import datetime

logger = logging.getLogger(__name__)


class CLIHandler:
    """
    Verarbeitet Kommandozeilenargumente und steuert den Programmablauf.
    """

    def __init__(self):
        """Initialisiert den CLI-Handler."""
        self.parser = self._create_parser()

        # Logging setup
        self._setup_logging()

    def _setup_logging(self):
        """Konfiguriert das Logging-System."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"election_viz_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Erstellt und konfiguriert den ArgumentParser.

        Returns:
            Konfigurierter ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description="Visualisierung der US-Wahlergebnisse 2024",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Beispiele:
  %(prog)s -i wahlergebnisse.txt -o output
  %(prog)s --style dark --export csv json
  %(prog)s --no-cache --format png
            """,
        )

        # Input/Output Optionen
        io_group = parser.add_argument_group("Ein-/Ausgabe Optionen")
        io_group.add_argument(
            "-i",
            "--input",
            default="data/wahl2024-harris-vs-trump.txt",
            help="Pfad zur Eingabedatei (Standard: %(default)s)",
        )
        io_group.add_argument(
            "-o",
            "--output",
            default="output",
            help="Ausgabeverzeichnis (Standard: %(default)s)",
        )

        # Visualisierungsoptionen
        viz_group = parser.add_argument_group("Visualisierungsoptionen")
        viz_group.add_argument(
            "--style",
            choices=["default", "dark", "light"],
            default="default",
            help="Visualisierungsstil (Standard: %(default)s)",
        )
        viz_group.add_argument(
            "--format",
            choices=["png", "svg", "pdf", "all"],
            default="all",
            help="Ausgabeformat für Plots (Standard: %(default)s)",
        )
        viz_group.add_argument(
            "--dpi",
            type=int,
            default=300,
            help="Auflösung für Rasterformate (Standard: %(default)s)",
        )

        # Export-Optionen
        export_group = parser.add_argument_group("Export-Optionen")
        export_group.add_argument(
            "--export",
            choices=["csv", "json", "excel", "pickle", "summary"],
            nargs="+",
            help="Datenexport-Formate",
        )
        export_group.add_argument(
            "--no-interactive",
            action="store_true",
            help="Deaktiviert interaktiven Modus",
        )

        # Cache-Optionen
        cache_group = parser.add_argument_group("Cache-Optionen")
        cache_group.add_argument(
            "--no-cache", action="store_true", help="Deaktiviert Daten-Caching"
        )
        cache_group.add_argument(
            "--clear-cache",
            action="store_true",
            help="Löscht den Cache vor der Ausführung",
        )

        # Entwickleroptionen
        dev_group = parser.add_argument_group("Entwickleroptionen")
        dev_group.add_argument(
            "--debug", action="store_true", help="Aktiviert Debug-Ausgaben"
        )
        dev_group.add_argument(
            "--profile", action="store_true", help="Aktiviert Performance-Profiling"
        )

        return parser

    def parse_args(self) -> Namespace:
        """
        Verarbeitet die Kommandozeilenargumente.

        Returns:
            Namespace mit verarbeiteten Argumenten
        """
        args = self.parser.parse_args()

        # Debug-Modus aktivieren
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug-Modus aktiviert")

        # Argument-Validierung
        self._validate_args(args)

        return args

    def _validate_args(self, args: Namespace):
        """
        Validiert die Kommandozeilenargumente.

        Args:
            args: Zu validierende Argumente
        """
        # Überprüfe Eingabedatei
        input_path = Path(args.input)
        if not input_path.exists():
            self.parser.error(f"Eingabedatei nicht gefunden: {input_path}")

        # Überprüfe Ausgabeverzeichnis
        output_path = Path(args.output)
        if not output_path.parent.exists():
            self.parser.error(
                f"Übergeordnetes Verzeichnis existiert nicht: {output_path.parent}"
            )

        # Überprüfe DPI-Wert
        if args.dpi < 72:
            self.parser.error(f"DPI-Wert muss mindestens 72 sein: {args.dpi}")

        # Cache-Optionen
        if args.no_cache and args.clear_cache:
            self.parser.error(
                "--no-cache und --clear-cache können nicht zusammen verwendet werden"
            )

    def setup_output_dirs(self, args: Namespace):
        """
        Erstellt die benötigten Ausgabeverzeichnisse.

        Args:
            args: Verarbeitete Argumente
        """
        output_base = Path(args.output)

        # Erstelle Hauptverzeichnisse
        dirs = {
            "plots": output_base / "plots",
            "exports": output_base / "exports",
            "cache": output_base / ".cache",
        }

        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Verzeichnis erstellt/überprüft: {dir_path}")

        return dirs

    def handle_cache(self, args: Namespace, cache_dir: Path):
        """
        Verarbeitet Cache-bezogene Argumente.

        Args:
            args: Verarbeitete Argumente
            cache_dir: Cache-Verzeichnis
        """
        if args.clear_cache and cache_dir.exists():
            for file in cache_dir.glob("*"):
                file.unlink()
            logger.info("Cache gelöscht")

        if args.no_cache:
            logger.info("Cache deaktiviert")
