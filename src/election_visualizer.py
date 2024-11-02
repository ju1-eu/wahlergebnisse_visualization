"""
Modul zur Visualisierung der Wahlergebnisse 2024: Harris vs. Trump
"""

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Slider
import logging
from pathlib import Path
from typing import Tuple, Optional
from .config import PlotConfig

logger = logging.getLogger(__name__)


class ElectionVisualizer:
    def __init__(self, df, config: PlotConfig):
        """
        Initialisiert den Visualizer.
        """
        self.df = df
        self.config = config
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.slider: Optional[Slider] = None
        self.max_votes = max(df["Harris"].max(), df["Trump"].max())

        # Status-Zusammenfassung berechnen
        self.total_states = len(df)
        self.harris_wins = sum(df["Harris"] > df["Trump"])
        self.trump_wins = sum(df["Trump"] > df["Harris"])

    def _setup_style(self):
        """Konfiguriert den Plot-Stil."""
        sns.set_style(
            "whitegrid",
            {
                "axes.grid": True,
                "grid.linestyle": "--",
                "grid.alpha": 0.5,
            },
        )

        plt.rcParams.update(
            {
                "figure.figsize": self.config.FIGURE_SIZE,
                "font.size": 10,
                "axes.labelsize": 12,
                "axes.titlesize": 14,
                "xtick.labelsize": 10,
                "ytick.labelsize": 10,
            }
        )

    def _create_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """Erstellt die Grundfigur mit zusätzlichem Platz für Zusammenfassung."""
        fig, ax = plt.subplots(figsize=self.config.FIGURE_SIZE)
        plt.subplots_adjust(bottom=0.25, top=0.85)  # Mehr Platz oben für Summary
        return fig, ax

    def _draw_bars(self, scale: float = 1.0):
        """Zeichnet die Balken mit verbesserter Farbgebung."""
        self.ax.clear()
        y_pos = range(len(self.df))

        harris_color = "#0051A5"  # Demokratisches Blau
        trump_color = "#FF2827"  # Republikanisches Rot

        # Harris Balken
        self.ax.barh(
            y_pos,
            self.df["Harris"] * scale,
            height=self.config.BAR_HEIGHT,
            label="Harris",
            color=harris_color,
            alpha=0.9,  # Erhöhte Deckkraft
        )

        # Trump Balken
        self.ax.barh(
            [y + self.config.BAR_HEIGHT for y in y_pos],
            self.df["Trump"] * scale,
            height=self.config.BAR_HEIGHT,
            label="Trump",
            color=trump_color,
            alpha=0.9,
        )

        # Differenzmarkierung
        for i, row in self.df.iterrows():
            if row["Harris"] > row["Trump"]:
                self._draw_difference_line(
                    row["Trump"] * scale,
                    row["Harris"] * scale,
                    i + self.config.BAR_HEIGHT / 2,
                )
            elif row["Trump"] > row["Harris"]:
                self._draw_difference_line(
                    row["Harris"] * scale,
                    row["Trump"] * scale,
                    i + self.config.BAR_HEIGHT / 2,
                )

    def _draw_difference_line(self, start: float, end: float, y_pos: float):
        """Zeichnet Differenzlinie."""
        self.ax.plot(
            [start, end],
            [y_pos] * 2,
            color="darkgray",
            linestyle=":",
            alpha=0.7,
            linewidth=1.5,
        )

    def _add_labels(self, scale: float = 1.0):
        """Fügt Beschriftungen im ersten Drittel der Balken hinzu."""
        for i, row in self.df.iterrows():
            # Harris Werte
            self._add_value_label(
                value=row["Harris"],
                percentage=row["Harris_Percentage"],
                scale=scale,
                y_pos=i,
                is_winner=row["Harris"] > row["Trump"],
            )

            # Trump Werte
            self._add_value_label(
                value=row["Trump"],
                percentage=row["Trump_Percentage"],
                scale=scale,
                y_pos=i + self.config.BAR_HEIGHT,
                is_winner=row["Trump"] > row["Harris"],
            )

    def _add_value_label(
        self, value: int, percentage: float, scale: float, y_pos: float, is_winner: bool
    ):
        """
        Fügt eine einzelne Wertbeschriftung hinzu.
        """
        # Position bei 10% der Balkenlänge
        x_pos = value * scale * 0.1

        label_text = f"{int(value):,} ({percentage:.1f}%)"
        if is_winner:
            label_text += " ✓"  # Siegerkennzeichnung

        self.ax.text(
            x_pos,
            y_pos,
            label_text,
            va="center",
            color="black",
            fontweight="bold" if is_winner else "normal",
            fontsize=9,
        )

    def _add_summary(self):
        """Fügt Zusammenfassungstext über dem Plot hinzu."""
        summary_template = (
            "Ausgezählte Staaten: {total} von 50 + D.C.\n"
            "Harris (D): {h_wins} Staaten ({h_pct:.1f}%) | "
            "Trump (R): {t_wins} Staaten ({t_pct:.1f}%)"
        )

        h_pct = self.harris_wins / self.total_states * 100
        t_pct = self.trump_wins / self.total_states * 100

        summary_text = summary_template.format(
            total=self.total_states,
            h_wins=self.harris_wins,
            h_pct=h_pct,
            t_wins=self.trump_wins,
            t_pct=t_pct,
        )

        plt.figtext(
            0.5,
            0.92,
            summary_text,
            ha="center",
            fontsize=10,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray"),
            multialignment="center",
        )

    def _configure_axes(self):
        """Konfiguriert die Achsen des Plots."""
        y_pos = range(len(self.df))
        self.ax.set_yticks([y + self.config.BAR_HEIGHT / 2 for y in y_pos])
        self.ax.set_yticklabels(self.df["State"])

        self.ax.set_title(
            "US-Wahlergebnisse 2024: Harris vs. Trump\n",
            fontsize=14,
            pad=20,
            fontweight="bold",
        )
        self.ax.set_xlabel("Stimmen", fontsize=12)

        self.ax.legend(
            loc="lower right",
            bbox_to_anchor=(1.0, 1.02),
            ncol=2,
            borderaxespad=0.0,
            frameon=True,
            facecolor="white",
            edgecolor="gray",
        )

        self.ax.grid(
            True,
            axis="x",
            linestyle="--",
            linewidth=0.7,
            alpha=0.7,
        )

    def create_plot(self) -> Tuple[plt.Figure, Optional[Slider]]:
        """Erstellt den interaktiven Plot mit Slider."""
        try:
            self._setup_style()
            self.fig, self.ax = self._create_figure()

            self._draw_bars()
            self._add_labels()
            self._configure_axes()
            self._add_summary()

            slider_ax = plt.axes([0.1, 0.1, 0.65, 0.03])
            self.slider = Slider(
                slider_ax,
                "Skalierung",
                valmin=0.1,
                valmax=2.0,
                valinit=1.0,
                valstep=0.1,
            )

            def update(val):
                self._draw_bars(val)
                self._add_labels(val)
                self._configure_axes()
                self._add_summary()
                self.fig.canvas.draw_idle()

            self.slider.on_changed(update)

            return self.fig, self.slider

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Plots: {str(e)}", exc_info=True)
            raise

    def show(self):
        """Zeigt den Plot an."""
        try:
            if self.fig is None:
                raise ValueError("Plot wurde noch nicht erstellt.")
            plt.show()
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen des Plots: {str(e)}", exc_info=True)
            raise

    def save(self, filepath: Path, **kwargs):
        """Speichert den Plot."""
        try:
            if self.fig is None:
                raise ValueError("Plot wurde noch nicht erstellt.")

            self.fig.savefig(filepath, bbox_inches="tight", **kwargs)
            logger.info(f"Plot gespeichert: {filepath}")

        except Exception as e:
            logger.error(f"Fehler beim Speichern: {str(e)}", exc_info=True)
            raise
