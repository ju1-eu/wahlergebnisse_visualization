# setup.py
"""
Setup-Konfiguration für das Wahlergebnisse-Visualisierungsprojekt.
Copyright © Jan Unger 2024
MIT License - Siehe LICENSE Datei für Details
"""

from setuptools import setup, find_packages

# Kernabhängigkeiten
REQUIREMENTS = [
    "pandas",          # Datenverarbeitung
    "matplotlib",      # Basis-Visualisierung
    "seaborn",        # Erweiterte Visualisierung
    "numpy"           # Numerische Berechnungen
]

# Entwicklungsabhängigkeiten
DEV_REQUIREMENTS = [
    "pytest",         # Testing Framework
    "pytest-cov",     # Test Coverage
    "black",          # Code Formatierung
    "flake8",         # Linting
    "mypy"           # Statische Typ-Überprüfung
]

# Lese README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="election_visualization",
    version="1.0.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": DEV_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "election-viz=main:main",
        ],
    },
    author="Jan Unger",
    author_email="[Email]",
    description="Visualisierung der US-Wahlergebnisse 2024",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "visualization",
        "election",
        "data analysis",
        "interactive plotting",
        "political data"
    ],
    python_requires=">=3.11",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ]
)

# requirements.txt
"""
Kernabhängigkeiten für das Wahlergebnisse-Visualisierungsprojekt.
"""

# Kernabhängigkeiten
pandas
matplotlib
seaborn
numpy

# Entwicklungsabhängigkeiten
pytest
pytest-cov
black
flake8
mypy

# dev-requirements.txt
"""
Entwicklungsabhängigkeiten.
Installation: pip install -r dev-requirements.txt
"""
-r requirements.txt

# Dokumentation
sphinx
sphinx-rtd-theme
sphinx-autoapi

# Code-Qualität
pylint
bandit
safety

# Testing
pytest-mock
pytest-asyncio
pytest-xdist

# Typ-Überprüfung
types-setuptools
types-requests