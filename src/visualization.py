"""
Modul zur Visualisierung der Wahlergebnisse 2024: Harris vs. Trump
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from .config2 import PlotConfig

logger = logging.getLogger(__name__)


class VisualizationError(Exception):
    """Fehler bei der Visualisierung."""

    pass


class ElectionVisualizer:
    """Klasse zur Erstellung von Visualisierungen der US-Wahldaten 2024."""

    def __init__(
        self, output_dir: str = "./output", config: Optional[PlotConfig] = None
    ) -> None:
        """
        Initialisiert den Visualizer.

        Args:
            output_dir: Verzeichnis für die Ausgabedateien
            config: Optionale Konfiguration, verwendet Standard wenn None
        """
        self.output_dir = Path(output_dir)
        self.config = config or PlotConfig()
        self._setup_plotting_style()
        self._ensure_output_dir()

    def _setup_plotting_style(self) -> None:
        """Konfiguriert den globalen Plotting-Stil."""
        try:
            plt.style.use("default")
            plt.rcParams.update(
                {
                    "figure.figsize": self.config.figure_sizes["swing_states"],
                    "font.size": self.config.fonts.SIZES["tick"],
                    "axes.titlesize": self.config.fonts.SIZES["title"],
                    "axes.labelsize": self.config.fonts.SIZES["label"],
                }
            )
        except Exception as e:
            raise VisualizationError(f"Fehler bei Style-Konfiguration: {str(e)}")

    def _ensure_output_dir(self) -> None:
        """Stellt sicher, dass das Ausgabeverzeichnis existiert."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ausgabeverzeichnis bereit: {self.output_dir}")
        except Exception as e:
            raise VisualizationError(
                f"Fehler beim Erstellen des Verzeichnisses: {str(e)}"
            )

    def create_swing_states_visualization(self, df: pd.DataFrame) -> None:
        """
        Erstellt eine Visualisierung der Swing States mit aktuellen Umfragewerten.

        Args:
            df: DataFrame mit den Wahldaten
        """
        try:
            fig, ax = plt.subplots(figsize=self.config.figure_sizes["swing_states"])

            # Balken erstellen
            bars = ax.barh(df["Staat"], df["Führung"])

            # Balken einfärben
            for bar in bars:
                bar.set_color(
                    self.config.colors.REPUBLICAN
                    if bar.get_width() < 0
                    else self.config.colors.DEMOCRATIC
                )

            # Mittellinie und Beschriftungen
            ax.axvline(x=0, color="black", linestyle="-", alpha=0.3)
            ax.set_title(
                "Führung in wichtigen Swing States (Harris vs. Trump)",
                pad=20,
                fontsize=self.config.fonts.SIZES["title"],
                fontweight=self.config.fonts.WEIGHTS["title"],
            )
            ax.set_xlabel(
                "Prozentpunkte Führung\n(+ = Harris führt, - = Trump führt)",
                fontsize=self.config.fonts.SIZES["label"],
                fontweight=self.config.fonts.WEIGHTS["label"],
            )

            # Wahlleute-Annotations
            if self.config.swing_states_settings["show_wahlleute"]:
                for i, row in df.iterrows():
                    align = "left" if row["Führung"] < 0 else "right"
                    offset = self.config.swing_states_settings["annotation_offset"]
                    x_pos = (
                        row["Führung"] - offset
                        if row["Führung"] < 0
                        else row["Führung"] + offset
                    )
                    ax.text(
                        x_pos,
                        i,
                        f"{int(row['Wahlleute'])} Wahlleute",
                        va="center",
                        ha=align,
                        fontsize=self.config.fonts.SIZES["annotation"],
                        fontweight=self.config.fonts.WEIGHTS["annotation"],
                    )

            # Grid
            plt.grid(
                True,
                axis="x",
                alpha=self.config.grid_settings["alpha"],
                linestyle=self.config.grid_settings["style"],
                linewidth=self.config.grid_settings["linewidth"],
            )

            plt.tight_layout()

            # Speichern
            output_path = self.config.get_output_path(
                self.output_dir, "swing_states_analysis", self.config.default_format
            )
            plt.savefig(output_path, dpi=self.config.dpi, bbox_inches="tight")
            plt.close(fig)

            logger.info(f"Swing States Visualisierung erstellt: {output_path}")

        except Exception as e:
            raise VisualizationError(
                f"Fehler bei Swing States Visualisierung: {str(e)}"
            )

    def create_electoral_college_visualization(
        self, electoral_data: Dict[str, List]
    ) -> None:
        """
        Erstellt eine Visualisierung des Electoral College Stands.

        Args:
            electoral_data: Dictionary mit Kategorien und Wahlleuten
        """
        try:
            fig, ax = plt.subplots(figsize=self.config.figure_sizes["electoral"])
            settings = self.config.electoral_college_settings

            # Tortendiagramm erstellen
            wedges, texts, autotexts = ax.pie(
                electoral_data["Wahlleute"],
                labels=[
                    f"{k}\n({v} Wahlleute)"
                    for k, v in zip(
                        electoral_data["Kategorie"], electoral_data["Wahlleute"]
                    )
                ],
                colors=[
                    self.config.colors.DEMOCRATIC,
                    self.config.colors.REPUBLICAN,
                    self.config.colors.NEUTRAL,
                ],
                autopct="%1.1f%%" if settings["show_percentages"] else None,
                startangle=settings["start_angle"],
                explode=settings["explode"],
                shadow=settings["shadow"],
            )

            # Label-Formatierung
            if settings["show_percentages"]:
                for autotext in autotexts:
                    autotext.set_color("white")
                    autotext.set_fontsize(self.config.fonts.SIZES["annotation"])

            title = "Verteilung der Wahlleute im Electoral College"
            if settings["show_total"]:
                title += "\n(270 zum Sieg benötigt)"
            ax.set_title(
                title,
                fontsize=self.config.fonts.SIZES["title"],
                fontweight=self.config.fonts.WEIGHTS["title"],
            )

            # Speichern
            output_path = self.config.get_output_path(
                self.output_dir, "electoral_college", self.config.default_format
            )
            plt.savefig(output_path, dpi=self.config.dpi, bbox_inches="tight")
            plt.close(fig)

            logger.info(f"Electoral College Visualisierung erstellt: {output_path}")

        except Exception as e:
            raise VisualizationError(
                f"Fehler bei Electoral College Visualisierung: {str(e)}"
            )

    def create_national_polls_timeline(
        self,
        dates: pd.DatetimeIndex,
        harris_polls: List[float],
        trump_polls: List[float],
    ) -> None:
        """
        Erstellt eine Visualisierung des nationalen Umfrageverlaufs.

        Args:
            dates: Datumsindizes für die x-Achse
            harris_polls: Liste der Harris-Umfragewerte
            trump_polls: Liste der Trump-Umfragewerte
        """
        try:
            fig, ax = plt.subplots(figsize=self.config.figure_sizes["timeline"])
            settings = self.config.timeline_settings

            # Hauptlinien
            ax.plot(
                dates,
                harris_polls,
                color=self.config.colors.DEMOCRATIC,
                label="Harris",
                marker=settings["marker_style"],
                linewidth=settings["line_width"],
                markersize=settings["marker_size"],
            )
            ax.plot(
                dates,
                trump_polls,
                color=self.config.colors.REPUBLICAN,
                label="Trump",
                marker=settings["marker_style"],
                linewidth=settings["line_width"],
                markersize=settings["marker_size"],
            )

            # 50%-Linie
            ax.axhline(
                y=50,
                color=self.config.grid_settings["color"],
                linestyle=self.config.grid_settings["style"],
                alpha=self.config.grid_settings["alpha"],
            )

            # Beschriftungen
            ax.set_title(
                "Entwicklung der nationalen Umfragewerte",
                fontsize=self.config.fonts.SIZES["title"],
                fontweight=self.config.fonts.WEIGHTS["title"],
            )
            ax.set_xlabel(
                "Datum",
                fontsize=self.config.fonts.SIZES["label"],
                fontweight=self.config.fonts.WEIGHTS["label"],
            )
            ax.set_ylabel(
                "Prozent",
                fontsize=self.config.fonts.SIZES["label"],
                fontweight=self.config.fonts.WEIGHTS["label"],
            )

            if settings["show_grid"]:
                ax.grid(True, alpha=self.config.grid_settings["alpha"])

            ax.legend(
                loc="center left",
                bbox_to_anchor=(1, 0.5),
                fontsize=self.config.fonts.SIZES["annotation"],
            )

            # Achsenformatierung
            ax.set_ylim([45, 52])
            plt.xticks(rotation=settings["rotation"])

            plt.tight_layout()

            # Speichern
            output_path = self.config.get_output_path(
                self.output_dir, "national_polls", self.config.default_format
            )
            plt.savefig(output_path, dpi=self.config.dpi, bbox_inches="tight")
            plt.close(fig)

            logger.info(f"Nationale Umfragen Visualisierung erstellt: {output_path}")

        except Exception as e:
            raise VisualizationError(f"Fehler bei Umfragen-Visualisierung: {str(e)}")

    def save_all_visualizations(
        self,
        df: pd.DataFrame,
        electoral_data: Dict[str, List],
        timeline_data: Tuple[pd.DatetimeIndex, List[float], List[float]],
    ) -> None:
        """
        Erstellt und speichert alle Visualisierungen auf einmal.

        Args:
            df: DataFrame mit Swing-States-Daten
            electoral_data: Dictionary mit Electoral College Daten
            timeline_data: Tuple mit (dates, harris_polls, trump_polls)
        """
        try:
            self.create_swing_states_visualization(df)
            self.create_electoral_college_visualization(electoral_data)
            self.create_national_polls_timeline(*timeline_data)
            logger.info("Alle Visualisierungen erfolgreich erstellt")
        except Exception as e:
            raise VisualizationError(
                f"Fehler beim Erstellen der Visualisierungen: {str(e)}"
            )
