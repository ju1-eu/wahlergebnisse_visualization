"""
Modul zum Export der Wahlergebnisse in verschiedene Formate.
"""

import pandas as pd
import json
import pickle
import logging
from pathlib import Path
from typing import List, Dict
from .config import ExportConfig

logger = logging.getLogger(__name__)


class DataExporter:
    """
    Exportiert Wahlergebnisse in verschiedene Dateiformate.
    Unterstützt CSV, JSON, Excel und Pickle.
    """

    def __init__(self, config: ExportConfig):
        """
        Initialisiert den Exporter.

        Args:
            config: Export-Konfiguration
        """
        self.config = config
        self.output_dir = Path(config.OUTPUT_DIR) / "exports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_all(self, df: pd.DataFrame) -> Dict[str, Path]:
        """
        Exportiert Daten in alle unterstützten Formate.

        Args:
            df: Zu exportierende Daten

        Returns:
            Dictionary mit Formaten und Pfaden
        """
        results = {}
        for fmt in self.config.EXPORT_FORMATS:
            try:
                path = self._export_format(df, fmt)
                results[fmt] = path
                logger.info(f"Daten erfolgreich exportiert als {fmt}: {path}")
            except Exception as e:
                logger.error(f"Fehler beim Export als {fmt}: {e}")
        return results

    def export_selected(self, df: pd.DataFrame, formats: List[str]) -> Dict[str, Path]:
        """
        Exportiert Daten in ausgewählte Formate.

        Args:
            df: Zu exportierende Daten
            formats: Liste der gewünschten Formate

        Returns:
            Dictionary mit Formaten und Pfaden
        """
        results = {}
        for fmt in formats:
            if fmt in self.config.EXPORT_FORMATS:
                try:
                    path = self._export_format(df, fmt)
                    results[fmt] = path
                    logger.info(f"Daten erfolgreich exportiert als {fmt}: {path}")
                except Exception as e:
                    logger.error(f"Fehler beim Export als {fmt}: {e}")
            else:
                logger.warning(f"Nicht unterstütztes Format: {fmt}")
        return results

    def _export_format(self, df: pd.DataFrame, format: str) -> Path:
        """
        Exportiert Daten in ein spezifisches Format.

        Args:
            df: Zu exportierende Daten
            format: Gewünschtes Format

        Returns:
            Pfad zur exportierten Datei
        """
        export_funcs = {
            "csv": self._export_csv,
            "json": self._export_json,
            "excel": self._export_excel,
            "pickle": self._export_pickle,
        }

        if format not in export_funcs:
            raise ValueError(f"Nicht unterstütztes Format: {format}")

        return export_funcs[format](df)

    def _export_csv(self, df: pd.DataFrame) -> Path:
        """CSV Export."""
        path = self.output_dir / "wahlergebnisse_2024.csv"
        df.to_csv(path, index=False, encoding="utf-8")
        return path

    def _export_json(self, df: pd.DataFrame) -> Path:
        """JSON Export."""
        path = self.output_dir / "wahlergebnisse_2024.json"

        # Erstelle strukturiertes JSON
        data = {
            "metadata": {
                "total_states": len(df),
                "total_votes": int(df["Total"].sum()),
                "harris_total": int(df["Harris"].sum()),
                "trump_total": int(df["Trump"].sum()),
                "export_date": pd.Timestamp.now().isoformat(),
            },
            "results": df.to_dict(orient="records"),
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path

    def _export_excel(self, df: pd.DataFrame) -> Path:
        """Excel Export mit Formatierung."""
        path = self.output_dir / "wahlergebnisse_2024.xlsx"

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            # Hauptdaten
            df.to_excel(writer, sheet_name="Wahlergebnisse", index=False)

            # Zugriff auf das Arbeitsblatt für Formatierung
            worksheet = writer.sheets["Wahlergebnisse"]

            # Spaltenbreiten anpassen
            worksheet.column_dimensions["A"].width = 20  # State
            for col in worksheet.columns:
                if col[0].column_letter != "A":  # Numerische Spalten
                    worksheet.column_dimensions[col[0].column_letter].width = 15

            # Überschriften formatieren
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)

        return path

    def _export_pickle(self, df: pd.DataFrame) -> Path:
        """Pickle Export."""
        path = self.output_dir / "wahlergebnisse_2024.pkl"

        data = {
            "data": df,
            "metadata": {"creation_time": pd.Timestamp.now(), "version": "1.0.0"},
        }

        with open(path, "wb") as f:
            pickle.dump(data, f)

        return path

    def create_summary(self, df: pd.DataFrame) -> str:
        """
        Erstellt eine Zusammenfassung der Wahlergebnisse.

        Args:
            df: Wahlergebnisse

        Returns:
            Zusammenfassungstext
        """
        summary = [
            "Zusammenfassung der US-Wahlergebnisse 2024",
            "=" * 40,
            f"Anzahl der Bundesstaaten: {len(df)}",
            f"Gesamtstimmen: {df['Total'].sum():,}",
            "",
            "Harris:",
            f"Gesamtstimmen: {df['Harris'].sum():,}",
            f"Durchschnittlicher Anteil: {df['Harris_Percentage'].mean():.1f}%",
            f"Führend in {len(df[df['Harris'] > df['Trump']])} Staaten",
            "",
            "Trump:",
            f"Gesamtstimmen: {df['Trump'].sum():,}",
            f"Durchschnittlicher Anteil: {df['Trump_Percentage'].mean():.1f}%",
            f"Führend in {len(df[df['Trump'] > df['Harris']])} Staaten",
            "",
            "Top 5 knappste Ergebnisse:",
        ]

        # Füge die 5 knappsten Rennen hinzu
        closest_races = df.copy()
        closest_races["Margin"] = (
            closest_races["Harris"] - closest_races["Trump"]
        ).abs()
        closest_races = closest_races.nsmallest(5, "Margin")

        for _, race in closest_races.iterrows():
            margin = race["Margin"]
            leader = "Harris" if race["Harris"] > race["Trump"] else "Trump"
            summary.append(
                f"{race['State']}: {leader} +{margin:,} Stimmen "
                f"({race['Harris_Percentage']:.1f}% vs {race['Trump_Percentage']:.1f}%)"
            )

        return "\n".join(summary)

    def export_summary(self, df: pd.DataFrame) -> Path:
        """
        Exportiert die Zusammenfassung als Textdatei.

        Args:
            df: Wahlergebnisse

        Returns:
            Pfad zur Zusammenfassungsdatei
        """
        summary_path = self.output_dir / "wahlergebnisse_2024_zusammenfassung.txt"
        summary_text = self.create_summary(df)

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        logger.info(f"Zusammenfassung gespeichert: {summary_path}")
        return summary_path
