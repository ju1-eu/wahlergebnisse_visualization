"""
Dokumentation für das US Election Analysis System

Setup und Installation:
----------------------
1. Virtuelle Umgebung erstellen:
   python -m venv venv
   source venv/bin/activate  # Unix
   venv\Scripts\activate     # Windows

2. Abhängigkeiten installieren:
   pip install -r requirements.txt

3. Konfiguration anpassen:
   - config.py enthält alle anpassbaren Parameter
   - logging.conf für Logger-Einstellungen
   - .env für Umgebungsvariablen

Verwendung:
----------
Basis-Verwendung:
```python
from election_analysis import ElectionVisualizer, DataProcessor, PlotConfig

# Konfiguration erstellen
config = PlotConfig()

# Visualizer initialisieren
visualizer = ElectionVisualizer(config=config)

# Daten verarbeiten und visualisieren
visualizer.create_swing_states_visualization(data)
```

Erweiterte Funktionen:
```python
# Regionale Analyse
processor = ExtendedDataProcessor()
regional_results = processor.regional_analysis(data)

# Wahrscheinlichkeitsberechnung
probabilities = processor.calculate_winning_probability(data)
```

Best Practices:
-------------
1. Datenvalidierung:
   - Immer ExtendedDataValidator für umfassende Prüfungen verwenden
   - Fehlerberichte loggen und behandeln
   - Plausibilitätsprüfungen durchführen

2. Fehlerbehandlung:
   - Spezifische Exceptions verwenden
   - Aussagekräftige Fehlermeldungen
   - Logging auf verschiedenen Levels

3. Performance:
   - Große Datensätze in Chunks verarbeiten
   - DataFrame-Operationen optimieren
   - Caching für wiederholte Berechnungen

4. Testing:
   - Unit-Tests für alle Kernfunktionen
   - Integration-Tests für Workflows
   - Performance-Tests für große Datensätze

5. Code-Struktur:
   - Klare Trennung von Daten, Logik und Visualisierung
   - Dependency Injection für bessere Testbarkeit
   - Wiederverwendbare Komponenten

Beispiel-Workflows:
-----------------
1. Basis-Analyse:
```python
def basic_analysis(data_path: str, output_dir: str):
    # Konfiguration
    config = PlotConfig()
    
    # Daten laden und validieren
    data = pd.read_csv(data_path)
    validator = ExtendedDataValidator()
    is_valid, errors = validator.validate_dataframe_extended(data)
    
    if not is_valid:
        logger.error(f"Validierungsfehler: {errors}")
        return
    
    # Verarbeitung
    processor = ExtendedDataProcessor()
    processed_data = processor.calculate_leads(data)
    
    # Visualisierung
    visualizer = ElectionVisualizer(output_dir=output_dir, config=config)
    visualizer.create_all_visualizations(processed_data)
```

2. Erweiterte Analyse:
```python
def advanced_analysis(data_path: str, output_dir: str):
    # Basis-Setup
    config = PlotConfig()
    processor = ExtendedDataProcessor()
    visualizer = ElectionVisualizer(output_dir=output_dir, config=config)
    
    # Daten laden und aufbereiten
    data = pd.read_csv(data_path)
    processed_data = processor.calculate_leads(data)
    
    # Erweiterte Analysen
    probabilities = processor.calculate_winning_probability(processed_data)
    regional_analysis = processor.regional_analysis(processed_data)
    scenarios = processor.analyze_electoral_scenarios(processed_data)
    
    # Visualisierungen erstellen
    visualizer.create_probability_plot(probabilities)
    visualizer.create_regional_analysis_plot(regional_analysis)
    visualizer.create_scenario_analysis_plot(scenarios)
    
    return {
        "probabilities": probabilities,
        "regional_analysis": regional_analysis,
        "scenarios": scenarios
    }
```

Logging und Monitoring:
---------------------
```python
def setup_monitoring():
    # Logging-Konfiguration
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'election_analysis.log',
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    })
```

Performance-Optimierung:
----------------------
```python
def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Optimiert ein DataFrame für bessere Performance."""
    # Datentypen optimieren
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
    
    # Kategorische Daten optimieren
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:  # Weniger als 50% unique Werte
            df[col] = df[col].astype('category')
    
    return df
```
"""