# 811372A-3007 Software Development, Maintenance and Operations 2025

## Project 1: Developer De-duplication

This repository contains data, scripts, and utilities for developer de-duplication
using the Bird heuristic and improved matching rules. The project focuses on
identifying duplicate developer identities from Git repository mining data.

## Project Structure

```
SDMO_Project1/
├── project1devs/          # Developer data and similarity analysis
├── script/                # Python scripts and automation
│   ├── project1developers.py      # Main: mine & deduplicate developers
│   ├── dedupe_utils.py            # Utility functions
│   ├── analyze_patterns.py        # Pattern analysis
│   ├── score_improved_rule.py     # Rule evaluation
│   ├── run_quality_checks.ps1     # Automated quality checks
│   └── summarize_quality.py       # Quality summary generator
├── tests/                 # Test suite (pytest)
├── reports/quality/       # Generated quality reports
└── requirements.txt       # Python dependencies
```

**Key Components:**

- **Data**: Developer pairs with similarity scores and labeled TP/FP annotations
- **Scripts**: Mining, de-duplication (Bird heuristic + improved rules), analysis
- **Quality**: Automated checks (Black, Flake8, Pylint, MyPy, Radon, Bandit)
- **Config**: `.flake8`, `.pylintrc`, `mypy.ini`, `pyproject.toml`, `sonar-project.properties`

## Setup and Installation

The project was developed and tested with Python 3.12 on Windows. It should be
compatible with Python 3.10+.

### Prerequisites

- Python 3.10 or higher
- Git (for cloning the repository)
- PowerShell (for running quality check scripts on Windows)

### Step-by-Step Setup

1. **Clone the repository**:

```bash
git clone <repository-url>
cd SDMO_Project1
```

2. **Create a virtual environment**:

```bash
python -m venv venv312
```

3. **Activate the virtual environment**:

```bash
# On Windows (PowerShell):
venv312\Scripts\activate

# On Windows (Command Prompt):
venv312\Scripts\activate.bat

# On Unix/Mac:
source venv312/bin/activate
```

4. **Upgrade pip** (recommended):

```bash
python -m pip install --upgrade pip
```

5. **Install all dependencies**:

```bash
pip install -r requirements.txt
```

This will install:

- **Core dependencies**: PyDriller, pandas, networkx, scipy, matplotlib, openpyxl, Levenshtein, tenetan
- **Testing tools**: pytest, pytest-cov
- **Quality tools**: black, isort, flake8, pylint, mypy, radon, bandit

## Running the Scripts

**Important**: Ensure your virtual environment is activated before running any scripts.

All main scripts are located in the `script/` directory and should be run from the project root.

### 1. Mine developer data and identify duplicates:

```bash
python script\project1developers.py
```

This script will:

- Mine developer data from the eShopOnContainers repository
- Apply the Bird heuristic for de-duplication
- Generate similarity CSV files in `project1devs/`

### 2. Analyze labeled patterns:

```bash
python script\analyze_patterns.py
```

Analyzes the labeled dataset to identify matching patterns.

### 3. Check label quality:

```bash
python script\check_labels.py
```

Validates the labeled data for consistency.

### 4. Score the improved rule:

```bash
python script\score_improved_rule.py
```

Evaluates the improved de-duplication rule against labeled data.

### 5. Run tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=script --cov-report=html

# Run specific test file
pytest tests\test_utils.py

```

### 6. Run quality checks:

```powershell
# Run all quality tools (from project root)
.\script\run_quality_checks.ps1

# Generate consolidated summary
python script\summarize_quality.py

# View the summary
type reports\quality\summary.md
```

### Quick Start Workflow

```bash
# 1. Activate virtual environment
venv312\Scripts\activate

# 2. Run tests to verify setup
pytest

# 3. Run main analysis
python script\project1developers.py

# 4. Run quality checks
.\script\run_quality_checks.ps1
python script\summarize_quality.py
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

### Running Quality Checks

**Automated (Recommended)**:

```powershell
# Run all quality tools at once
.\script\run_quality_checks.ps1

# Generate consolidated summary
python script\summarize_quality.py
```

This will:

1. Create `reports/quality/` directory in project root
2. Run all quality tools (Black, isort, Flake8, MyPy, Bandit, Radon, Pylint)
3. Save individual reports to `reports/quality/`
4. Generate a summary report

**Individual Tools** (run from project root):

```bash
# Format code with Black
black . --skip-string-normalization

# Sort imports with isort
isort . --filter-files --skip venv312

# Check style with Flake8
flake8 . --exclude=venv312,.venv,__pycache__,reports

# Type check with MyPy
mypy . --ignore-missing-imports

# Security scan with Bandit
bandit -r . -x venv312,.venv,__pycache__,reports

# Complexity analysis with Radon
radon cc . -s -a -e "venv312/*,__pycache__/*,reports/*"
radon mi . -s -e "venv312/*,__pycache__/*,reports/*"

# Lint with Pylint
pylint script/*.py
```
