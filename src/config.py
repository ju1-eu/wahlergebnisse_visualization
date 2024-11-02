"""Konfigurationsdatei für die Wahlergebnisse-Visualisierung."""

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class PlotConfig:
    """Plot-Konfiguration."""

    FIGURE_SIZE: Tuple[int, int] = (15, 10)
    DPI: int = 300
    TITLE: str = "US-Wahlergebnisse 2024: Harris vs. Trump"
    XLABEL: str = "Stimmen"

    # Farbschema
    COLORS: Dict[str, str] = field(
        default_factory=lambda: {
            "harris": "#EE9A00",  # orange2
            "trump": "#B22222",  # firebrick
            "slider": "#404040",  # dunkelgrau für Slider
        }
    )

    # Plot-Parameter
    ALPHA: float = 0.8
    BAR_HEIGHT: float = 0.35
    GRID_ALPHA: float = 0.3

    # Slider-Konfiguration
    SLIDER_RANGE: Tuple[float, float] = (0.1, 2.0)
    SLIDER_INIT: float = 1.0
    SLIDER_STEP: float = 0.1


@dataclass
class ExportConfig:
    """Export-Konfiguration."""

    OUTPUT_DIR: str = "output"
    PLOT_FORMATS: Tuple[str, ...] = ("png", "svg", "pdf")
    EXPORT_FORMATS: Tuple[str, ...] = ("csv", "json", "excel", "pickle")


@dataclass
class CacheConfig:
    """Cache-Konfiguration."""

    CACHE_DIR: str = ".cache"
    MAX_CACHE_SIZE: int = 32
    CACHE_EXPIRY: int = 3600  # 1 Stunde in Sekunden
    CACHE_ENABLED: bool = True  # Neues Feld hinzugefügt, standardmäßig aktiviert
