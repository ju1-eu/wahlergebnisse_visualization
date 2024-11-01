"""
Modul zur Visualisierung der Wahlergebnisse.
"""
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Slider
import logging
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
from .config import PlotConfig

logger = logging.getLogger(__name__)

class ElectionVisualizer:
    """
    Erstellt interaktive Visualisierungen der Wahlergebnisse.
    """
    
    def __init__(self, df, config: PlotConfig):
        """
        Initialisiert den Visualizer.
        
        Args:
            df: Pandas DataFrame mit Wahlergebnissen
            config: Plot-Konfiguration
        """
        self.df = df
        self.config = config
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.slider: Optional[Slider] = None
        self.max_votes = max(df['Harris'].max(), df['Trump'].max())
    
    def _setup_style(self):
        """Konfiguriert den Plot-Stil."""
        # Seaborn Style
        sns.set_style("whitegrid", {
            'axes.grid': True,
            'grid.linestyle': '--',
            'grid.alpha': 0.3
        })
        
        # Matplotlib RC Parameter
        plt.rcParams.update({
            'figure.figsize': self.config.FIGURE_SIZE,
            'font.size': 12,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10
        })
    
    def _create_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """Erstellt die Grundfigur."""
        fig, ax = plt.subplots(figsize=self.config.FIGURE_SIZE)
        plt.subplots_adjust(bottom=0.25)  # Platz für Slider
        return fig, ax
    
    def _draw_bars(self, scale: float = 1.0):
        """
        Zeichnet die Balken für beide Kandidaten.
        
        Args:
            scale: Skalierungsfaktor für die Balken
        """
        self.ax.clear()
        y_pos = range(len(self.df))
        
        # Harris Balken
        self.ax.barh(y_pos, 
                    self.df['Harris'] * scale,
                    height=self.config.BAR_HEIGHT,
                    label='Harris',
                    color=self.config.COLORS['harris'],
                    alpha=self.config.ALPHA)
        
        # Trump Balken
        self.ax.barh([y + self.config.BAR_HEIGHT for y in y_pos],
                    self.df['Trump'] * scale,
                    height=self.config.BAR_HEIGHT,
                    label='Trump',
                    color=self.config.COLORS['trump'],
                    alpha=self.config.ALPHA)
                    
        # Differenzmarkierung
        for i, row in self.df.iterrows():
            if row['Harris'] > row['Trump']:
                diff = row['Harris'] - row['Trump']
                self.ax.plot([row['Trump'] * scale, row['Harris'] * scale],
                           [i + self.config.BAR_HEIGHT/2] * 2,
                           color='darkgray',
                           linestyle=':',
                           alpha=0.5,
                           linewidth=1.5)
            elif row['Trump'] > row['Harris']:
                diff = row['Trump'] - row['Harris']
                self.ax.plot([row['Harris'] * scale, row['Trump'] * scale],
                           [i + self.config.BAR_HEIGHT/2] * 2,
                           color='darkgray',
                           linestyle=':',
                           alpha=0.5,
                           linewidth=1.5)
    
    def _add_labels(self, scale: float = 1.0):
        """
        Fügt Beschriftungen zu den Balken hinzu.
        
        Args:
            scale: Skalierungsfaktor für die Position
        """
        for i, row in self.df.iterrows():
            # Harris Werte
            self._add_value_label(
                value=row['Harris'],
                percentage=row['Harris_Percentage'],
                scale=scale,
                y_pos=i,
                color=self.config.COLORS['harris']
            )
            
            # Trump Werte
            self._add_value_label(
                value=row['Trump'],
                percentage=row['Trump_Percentage'],
                scale=scale,
                y_pos=i + self.config.BAR_HEIGHT,
                color=self.config.COLORS['trump']
            )
    
    def _add_value_label(self, value: int, percentage: float, scale: float,
                        y_pos: float, color: str):
        """
        Fügt eine einzelne Wertbeschriftung hinzu.
        
        Args:
            value: Anzahl der Stimmen
            percentage: Prozentualer Anteil
            scale: Skalierungsfaktor
            y_pos: Y-Position
            color: Textfarbe
        """
        self.ax.text(
            value * scale + self.max_votes * 0.01,
            y_pos,
            f'{int(value):,} ({percentage:.1f}%)',
            va='center',
            color=color,
            fontweight='bold',
            fontsize=10
        )
    
    def _configure_axes(self):
        """Konfiguriert die Achsen des Plots."""
        # Y-Achse
        y_pos = range(len(self.df))
        self.ax.set_yticks([y + self.config.BAR_HEIGHT/2 for y in y_pos])
        self.ax.set_yticklabels(self.df['State'])
        
        # Titel und Labels
        self.ax.set_title(self.config.TITLE,
                         fontsize=14,
                         pad=20,
                         fontweight='bold')
        self.ax.set_xlabel(self.config.XLABEL, fontsize=12)
        
        # Legende
        self.ax.legend(
            loc='lower right',
            bbox_to_anchor=(1.0, 1.02),
            ncol=2,
            borderaxespad=0.,
            frameon=True,
            facecolor='white',
            edgecolor='gray'
        )
        
        # Gitter
        self.ax.grid(True,
                    axis='x',
                    linestyle='--',
                    alpha=self.config.GRID_ALPHA)
    
    def _create_slider(self) -> Slider:
        """
        Erstellt und konfiguriert den Slider.
        
        Returns:
            Konfigurierter Slider
        """
        ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
        slider = Slider(
            ax=ax_slider,
            label='Skalierung',
            valmin=self.config.SLIDER_RANGE[0],
            valmax=self.config.SLIDER_RANGE[1],
            valinit=self.config.SLIDER_INIT,
            valstep=self.config.SLIDER_STEP,
            color=self.config.COLORS['slider'],  # Dunkelgrauer Slider
            initcolor='none'
        )
        
        def update(val):
            """Slider Update-Funktion."""
            self._draw_bars(val)
            self._add_labels(val)
            self._configure_axes()
            self.fig.canvas.draw_idle()
        
        slider.on_changed(update)
        return slider
    
    def create_plot(self) -> Tuple[plt.Figure, Slider]:
        """
        Erstellt den interaktiven Plot.
        
        Returns:
            Figure und Slider
        """
        self._setup_style()
        self.fig, self.ax = self._create_figure()
        
        # Initialer Plot
        self._draw_bars()
        self._add_labels()
        self._configure_axes()
        
        # Slider
        self.slider = self._create_slider()
        
        return self.fig, self.slider
    
    def save_plots(self, output_dir: str = 'output/plots'):
        """
        Speichert die Plots in verschiedenen Formaten.
        
        Args:
            output_dir: Ausgabeverzeichnis
        """
        if self.fig is None:
            raise ValueError("Kein Plot zum Speichern vorhanden. "
                           "Rufen Sie zuerst create_plot() auf.")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for fmt in ['png', 'svg', 'pdf']:
            save_path = output_path / f'wahlergebnisse_2024.{fmt}'
            self.fig.savefig(
                save_path,
                bbox_inches='tight',
                dpi=self.config.DPI,
                format=fmt
            )
            logger.info(f"Plot gespeichert als: {save_path}")
    
    def show(self):
        """Zeigt den Plot an."""
        if self.fig is None:
            raise ValueError("Kein Plot zum Anzeigen vorhanden. "
                           "Rufen Sie zuerst create_plot() auf.")
        plt.show()