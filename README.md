# Wahlergebnisse Visualisierung 🗳️

[![GitHub license](https://img.shields.io/github/license/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/stargazers)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Interaktive Visualisierung der US-Wahlergebnisse 2024 mit erweiterten Analyse- und Exportfunktionen.

## ✨ Features

- 📊 **Interaktive Visualisierung**
  - Dynamische Balkendiagramme
  - Anpassbare Skalierung
  - Dark/Light Mode Support
  - Echtzeit-Updates

- 📤 **Export-Funktionen**
  - CSV, JSON, Excel Export
  - PDF/SVG/PNG Grafiken
  - Detaillierte Berichte
  - Automatische Zusammenfassungen

- 🖥️ **Benutzerfreundlichkeit**
  - Kommandozeilen-Interface
  - Intuitive Bedienung
  - Umfangreiche Hilfe
  - Fehlerbehandlung

- 🚀 **Technische Features**
  - Effizientes Daten-Caching
  - Multi-Format Support
  - Umfangreiche Test-Suite
  - Modulare Architektur

## 🛠️ Installation

### Voraussetzungen
- Python 3.11 oder höher
- Git

### Schritte

1. **Repository klonen**
   ```bash
   git clone https://github.com/ju1-eu/wahlergebnisse_visualization.git
   cd wahlergebnisse_visualization
   ```

2. **Virtuelle Umgebung einrichten**
   ```bash
   # Unix/macOS
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren**
   ```bash
   # Basis-Installation
   pip install -r requirements.txt

   # Entwicklungs-Installation
   pip install -r dev-requirements.txt

   # Installation mit Entwicklerwerkzeugen
   pip install -e ".[dev]"
   ```

## 📚 Verwendung

### Grundlegende Nutzung
```bash
# Standardausführung
python main.py

# Mit spezifischen Optionen
python main.py --style dark --export csv json

# Hilfe anzeigen
python main.py --help
```

### Erweiterte Optionen
```bash
# Datenexport
python main.py --export csv json excel

# Visualisierungsstil ändern
python main.py --style dark

# Cache verwalten
python main.py --clear-cache
```

## 👩‍💻 Entwicklung

### Code-Qualität

1. **Tests ausführen**
   ```bash
   # Alle Tests
   pytest

   # Mit Coverage-Report
   pytest --cov=src

   # Parallel ausführen
   pytest -n auto
   ```

2. **Code formatieren**
   ```bash
   # Code-Formatierung
   black .

   # Linting
   flake8

   # Typ-Überprüfung
   mypy src/
   ```

### Dokumentation
```bash
# Dokumentation generieren
sphinx-build docs/ docs/_build/
```

## 📊 Beispiel-Output

Die Visualisierung erstellt interaktive Grafiken wie:

- Balkendiagramme der Wahlergebnisse
- Prozentuale Verteilungen
- Vergleichsanalysen
- Trenddarstellungen



## ⭐ Stargazers

[![Stargazers repo roster for @ju1-eu/wahlergebnisse_visualization](https://reporoster.com/stars/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/stargazers)

## 📊 GitHub Stats

[![GitHub issues](https://img.shields.io/github/issues/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/issues)
[![GitHub forks](https://img.shields.io/github/forks/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/network)
[![GitHub stars](https://img.shields.io/github/stars/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/stargazers)
[![GitHub license](https://img.shields.io/github/license/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/blob/main/LICENSE)
[![GitHub contributors](https://img.shields.io/github/contributors/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/graphs/contributors)
[![GitHub last commit](https://img.shields.io/github/last-commit/ju1-eu/wahlergebnisse_visualization)](https://github.com/ju1-eu/wahlergebnisse_visualization/commits/main)

## 🌟 Contributors

Thanks goes to these wonderful people:

<a href="https://github.com/ju1-eu/wahlergebnisse_visualization/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ju1-eu/wahlergebnisse_visualization" />
</a>



## 🤝 Beitragen

Beiträge sind willkommen! Bitte beachten Sie:

1. Fork des Repositories von [ju1-eu/wahlergebnisse_visualization](https://github.com/ju1-eu/wahlergebnisse_visualization)
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📝 Lizenz

MIT Lizenz

© Jan Unger 2024

Diese Software/Arbeit darf unter folgenden Bedingungen genutzt, kopiert, verändert und verteilt werden:

1. **Nutzung**: Diese Lizenz erlaubt es jedem, diese Software/Arbeit kostenlos zu nutzen, unter Beachtung der unten aufgeführten Bedingungen.

2. **Veränderung und Weiterverbreitung**: Änderungen an dieser Software/Arbeit sind zulässig. Diese Veränderungen dürfen unter denselben Bedingungen wie das Original weiterverbreitet werden.

3. **Urheberrechtshinweis**: Alle Kopien oder Verteilungen der Software/Arbeit müssen einen Urheberrechtshinweis wie folgt enthalten:  
   © Jan Unger 2024. Alle Rechte vorbehalten.

4. **Keine Haftung**: Der Lizenzgeber übernimmt keine Haftung für Schäden, die aus der Nutzung der Software/Arbeit entstehen.

5. **Begrenzung der Nutzung**: Die Nutzung dieser Software/Arbeit ist nur zu legalen Zwecken gestattet. Jeglicher Missbrauch ist untersagt.

## 📞 Kontakt

- **Author**: Jan Unger
- **GitHub**: [@ju1-eu](https://github.com/ju1-eu)
- **Projekte**: [GitHub Repositories](https://github.com/ju1-eu?tab=repositories)

## 🙏 Danksagung

Besonderer Dank gilt:

- Allen Mitwirkenden und Contributors
- Der Open-Source-Community
- Den Entwicklern der verwendeten Bibliotheken:
  - [pandas](https://pandas.pydata.org/)
  - [matplotlib](https://matplotlib.org/)
  - [seaborn](https://seaborn.pydata.org/)
  - [numpy](https://numpy.org/)