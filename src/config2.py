"""
Konfigurationsmodul für die Wahlanalyse.

Dieses Modul stellt Konfigurationsklassen für alle Aspekte der Wahlanalyse bereit,
einschließlich Visualisierung, Datenverarbeitung und Validierung.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional, Any
from pathlib import Path
from datetime import datetime


@dataclass(frozen=True)
class ColorScheme:
    """Farbschemata für verschiedene Visualisierungen."""

    DEMOCRATIC: str = "#0015BC"  # Klassisches Demokraten-Blau
    REPUBLICAN: str = "#FF0000"  # Klassisches Republikaner-Rot
    NEUTRAL: str = "#808080"  # Neutral Grau
    BACKGROUND: str = "#FFFFFF"  # Weißer Hintergrund
    GRID: str = "#E0E0E0"  # Helles Grau für Gitter

    # Zusätzliche Farben für erweiterte Visualisierungen
    STRONG_DEM: str = "#000080"  # Dunkelblau für sichere Demokraten-Staaten
    LEAN_DEM: str = "#6495ED"  # Hellblau für tendenziell Demokraten-Staaten
    STRONG_REP: str = "#8B0000"  # Dunkelrot für sichere Republikaner-Staaten
    LEAN_REP: str = "#FF6B6B"  # Hellrot für tendenziell Republikaner-Staaten
    TOSSUP: str = "#FFD700"  # Gold für Swing States


@dataclass(frozen=True)
class FontConfig:
    """Schriftkonfiguration für Visualisierungen."""

    FAMILY: str = "DejaVu Sans"
    SIZES: Dict[str, int] = field(
        default_factory=lambda: {
            "title": 16,
            "subtitle": 14,
            "label": 12,
            "tick": 10,
            "annotation": 9,
            "small": 8,
        }
    )
    WEIGHTS: Dict[str, str] = field(
        default_factory=lambda: {
            "title": "bold",
            "subtitle": "semibold",
            "label": "normal",
            "annotation": "normal",
        }
    )


@dataclass
class PlotConfig:
    """Zentrale Konfiguration für alle Visualisierungen."""

    # Basis-Einstellungen
    colors: ColorScheme = field(default_factory=ColorScheme)
    fonts: FontConfig = field(default_factory=FontConfig)

    # Plot-Dimensionen
    figure_sizes: Dict[str, Tuple[int, int]] = field(
        default_factory=lambda: {
            "swing_states": (12, 8),
            "electoral": (10, 8),
            "timeline": (12, 6),
            "regional": (14, 8),
            "probability": (10, 6),
        }
    )

    # Ausgabe-Einstellungen
    dpi: int = 300
    output_formats: List[str] = field(default_factory=lambda: ["png", "pdf", "svg"])
    default_format: str = "png"

    # Layout-Einstellungen
    margins: Dict[str, float] = field(
        default_factory=lambda: {"left": 0.1, "right": 0.9, "top": 0.9, "bottom": 0.1}
    )
    spacing: float = 0.35

    # Grid-Einstellungen
    grid_settings: Dict[str, Any] = field(
        default_factory=lambda: {
            "style": "--",
            "alpha": 0.3,
            "color": ColorScheme.GRID,
            "linewidth": 0.5,
        }
    )

    # Spezifische Plot-Einstellungen
    swing_states_settings: Dict[str, Any] = field(
        default_factory=lambda: {
            "show_wahlleute": True,
            "show_percentages": True,
            "annotation_offset": 0.1,
            "bar_height": 0.35,
            "show_confidence": True,
            "confidence_alpha": 0.2,
        }
    )

    electoral_college_settings: Dict[str, Any] = field(
        default_factory=lambda: {
            "start_angle": 90,
            "show_percentages": True,
            "show_total": True,
            "donut_ratio": 0.7,
            "explode": (0.05, 0.05, 0),
            "shadow": True,
        }
    )

    timeline_settings: Dict[str, Any] = field(
        default_factory=lambda: {
            "marker_style": "o",
            "line_width": 2,
            "show_grid": True,
            "rotation": 45,
            "show_confidence": True,
            "confidence_alpha": 0.15,
            "marker_size": 6,
        }
    )

    regional_settings: Dict[str, Any] = field(
        default_factory=lambda: {
            "show_state_names": True,
            "show_electoral_votes": True,
            "colormap_steps": 9,
            "border_color": "#333333",
            "highlight_swing_states": True,
        }
    )

    def __post_init__(self):
        """Validiert die Konfiguration nach der Initialisierung."""
        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validiert die Konfigurationswerte.

        Raises:
            ValueError: Bei ungültigen Konfigurationswerten
        """
        if any(size <= 0 for sizes in self.figure_sizes.values() for size in sizes):
            raise ValueError("Figure sizes müssen positiv sein")

        if self.dpi <= 0:
            raise ValueError("DPI muss positiv sein")

        if not self.output_formats:
            raise ValueError("Mindestens ein Ausgabeformat erforderlich")

    def get_color_map(self, type: str = "diverging") -> Dict[str, str]:
        """
        Erstellt eine Farbpalette für verschiedene Visualisierungstypen.

        Args:
            type: Art der Farbpalette ('diverging', 'sequential', etc.)

        Returns:
            Dictionary mit Farbzuordnungen
        """
        if type == "diverging":
            return {
                "strong_dem": self.colors.STRONG_DEM,
                "lean_dem": self.colors.LEAN_DEM,
                "tossup": self.colors.TOSSUP,
                "lean_rep": self.colors.LEAN_REP,
                "strong_rep": self.colors.STRONG_REP,
            }
        # Weitere Farbpaletten können hier hinzugefügt werden
        return {}

    def get_output_path(
        self, base_dir: Path, name: str, format: Optional[str] = None
    ) -> Path:
        """
        Erstellt einen Ausgabepfad für Visualisierungen.

        Args:
            base_dir: Basis-Verzeichnis
            name: Name der Visualisierung
            format: Optionales Ausgabeformat

        Returns:
            Path-Objekt für die Ausgabedatei
        """
        fmt = format or self.default_format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return base_dir / f"{name}_{timestamp}.{fmt}"


def create_config(**kwargs) -> PlotConfig:
    """
    Factory-Funktion für PlotConfig mit benutzerdefinierten Einstellungen.

    Args:
        **kwargs: Schlüsselwortargumente für die Konfiguration

    Returns:
        Konfiguriertes PlotConfig-Objekt
    """
    return PlotConfig(**kwargs)
