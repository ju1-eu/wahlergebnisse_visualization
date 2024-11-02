import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_data():
    """Erzeugt Testdaten."""
    return pd.DataFrame(
        {
            "Staat": ["Arizona", "Georgia", "Michigan"],
            "Harris": [46.8, 47.3, 47.6],
            "Trump": [48.2, 48.2, 47.0],
            "Wahlleute": [11, 16, 15],
        }
    )


@pytest.fixture
def config():
    """Erzeugt Test-Konfiguration."""
    return PlotConfig()


class TestDataValidation:
    """Tests für die Datenvalidierung."""

    def test_percentage_validation(self, sample_data):
        validator = DataValidator()
        assert validator.validate_percentages(sample_data["Harris"])
        assert validator.validate_percentages(sample_data["Trump"])

    def test_electoral_votes(self):
        validator = DataValidator()
        assert validator.validate_electoral_votes([269, 269])
        assert not validator.validate_electoral_votes([270, 270])


class TestDataProcessing:
    """Tests für die Datenverarbeitung."""

    def test_calculate_leads(self, sample_data):
        processor = DataProcessor()
        processed_data = processor.calculate_leads(sample_data)
        assert "Führung" in processed_data.columns
        assert all(
            processed_data["Führung"]
            == processed_data["Harris"] - processed_data["Trump"]
        )

    def test_winning_probability(self, sample_data):
        processor = ExtendedDataProcessor()
        probabilities = processor.calculate_winning_probability(sample_data)
        assert all(0 <= prob <= 100 for prob in probabilities["Harris_Gewinnchance"])
        assert all(0 <= prob <= 100 for prob in probabilities["Trump_Gewinnchance"])


class TestVisualization:
    """Tests für die Visualisierungen."""

    def test_swing_states_plot(self, sample_data, config, tmp_path):
        visualizer = ElectionVisualizer(output_dir=str(tmp_path), config=config)
        visualizer.create_swing_states_visualization(sample_data)
        assert (tmp_path / f"swing_states_analysis.{config.output_format}").exists()

    def test_electoral_college_plot(self, config, tmp_path):
        electoral_data = {
            "Kategorie": ["Harris", "Trump", "Umkämpft"],
            "Wahlleute": [225, 170, 143],
        }
        visualizer = ElectionVisualizer(output_dir=str(tmp_path), config=config)
        visualizer.create_electoral_college_visualization(electoral_data)
        assert (tmp_path / f"electoral_college.{config.output_format}").exists()


def test_integration(sample_data, config, tmp_path):
    """Integrationstests für den gesamten Prozess."""
    try:
        # Datenvalidierung
        validator = ExtendedDataValidator()
        is_valid, errors = validator.validate_dataframe_extended(sample_data)
        assert is_valid, f"Validierungsfehler: {errors}"

        # Datenverarbeitung
        processor = ExtendedDataProcessor()
        processed_data = processor.calculate_leads(sample_data)
        probabilities = processor.calculate_winning_probability(processed_data)
        regional_analysis = processor.regional_analysis(processed_data)

        # Visualisierung
        visualizer = ElectionVisualizer(output_dir=str(tmp_path), config=config)
        visualizer.create_swing_states_visualization(processed_data)

        # Überprüfung der Ausgaben
        assert (tmp_path / f"swing_states_analysis.{config.output_format}").exists()
        assert all(0 <= p <= 100 for p in probabilities["Harris_Gewinnchance"])
        assert isinstance(regional_analysis, dict)

    except Exception as e:
        pytest.fail(f"Integrationstests fehlgeschlagen: {str(e)}")
