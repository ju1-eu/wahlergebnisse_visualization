# US Election Analysis 2024

Ein umfassendes System zur Analyse und Visualisierung der US-Präsidentschaftswahl 2024.

## Features

- Datenvalidierung und -verarbeitung
- Verschiedene Visualisierungen (Swing States, Electoral College, Zeitverlauf)
- Erweiterte statistische Analysen
- Umfangreiche Konfigurationsmöglichkeiten
- Ausführliche Dokumentation

## Projektstruktur

```text
election_analysis/
│
├── src/
│   ├── __init__.py
│   ├── data_validation.py     # DataValidator und ExtendedDataValidator
│   ├── data_processing.py     # DataProcessor und ExtendedDataProcessor
│   ├── visualization.py       # ElectionVisualizer (original script)
│   └── config2.py             # PlotConfig
│
├── data/
│   └── example_data.csv      # Beispieldaten
│
├── output/                   # Ausgabeverzeichnis für Visualisierungen
│   └── .gitkeep
│
├── main2.py                   # Hauptskript
└── requirements.txt
```

## Installation

```bash
# Repository klonen
git clone https://github.com/username/us-election-analysis-2024.git
cd us-election-analysis-2024

# Virtuelle Umgebung erstellen und aktivieren
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Schnellstart

```python
from election_analysis import ElectionVisualizer

# Visualizer initialisieren
visualizer = ElectionVisualizer()

# Visualisierungen erstellen
visualizer.create_swing_states_visualization(data)
visualizer.create_electoral_college_visualization(data)
visualizer.create_national_polls_timeline(dates, harris_polls, trump_polls)
```

## Tests ausführen

```bash
pytest tests/
```

## Lizenz

MIT

## Author

Jan Unger