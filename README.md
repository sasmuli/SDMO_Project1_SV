# 811372A-3007 Software Development, Maintenance and Operations 2025

## Project 1: Developer De-duplication

This repository contains data, scripts, and utilities for developer de-duplication
using the Bird heuristic and improved matching rules. The project focuses on
identifying duplicate developer identities from Git repository mining data.

## Contents

### Data Files
- `project1devs/`: Directory with developer data and similarity analysis
  - `devs.csv`: List of developers mined from eShopOnContainersProject
  - `devs_similarity.csv`: Similarity tests for each pair of developers
  - `devs_similarity_t=0.7.csv`: Developer pairs with similarity threshold ≥ 0.7
  - `devs_similarity_t=0.75.csv`: Developer pairs with similarity threshold ≥ 0.75
  - `devs_similarity_t=0.7_labeled.xlsx`: Labeled dataset with TP/FP annotations

### Core Scripts
- `project1developers.py`: Main script demonstrating mining developer information
  and applying the Bird heuristic to identify duplicate developers
- `dedupe_utils.py`: Utility functions for developer de-duplication including:
  - Text normalization and name parsing
  - Surname extraction
  - Email parsing and validation
  - Improved matching rule implementation

### Analysis Scripts
- `analyze_patterns.py`: Analyzes patterns in labeled developer pairs to identify
  matching characteristics
- `check_labels.py`: Validates and inspects labeled data quality
- `score_improved_rule.py`: Evaluates the improved de-duplication rule against
  labeled data
- `summarize_quality.py`: Generates quality metrics summary from static analysis
  reports

### Testing
- `tests/`: Test suite with pytest configuration
  - `test_rule_on_tiny_frame.py`: Unit tests for de-duplication rules
  - `test_utils.py`: Tests for utility functions
  - `conftest.py`: Pytest configuration and fixtures

### Configuration Files
- `requirements.txt`: Python dependencies with pinned versions
- `pyproject.toml`: Black and isort configuration
- `.flake8`: Flake8 linting configuration
- `.pylintrc`: Pylint configuration
- `mypy.ini`: MyPy type checking configuration
- `sonar-project.properties`: SonarQube analysis configuration

## Setup and Installation

The project was developed and tested with Python 3.12 on Windows. It should be
compatible with Python 3.10+.

### Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv venv312

# Activate virtual environment
# On Windows:
venv312\Scripts\activate
# On Unix/Mac:
source venv312/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Scripts

### Mine developer data and identify duplicates:
```bash
python project1developers.py
```

### Analyze labeled patterns:
```bash
python analyze_patterns.py
```

### Score the improved rule:
```bash
python score_improved_rule.py
```

### Run tests:
```bash
pytest
```

## Code Quality

The project uses multiple static analysis tools:
- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Style guide enforcement
- **Pylint**: Code analysis
- **MyPy**: Static type checking
- **Radon**: Complexity metrics
- **Bandit**: Security analysis

Run quality checks via the GitHub Actions workflow or locally using the individual tools.
