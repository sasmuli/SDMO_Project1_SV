
# Run Quality Analysis - SDMO Project 1


Write-Host "=== Running Quality Analysis ==="

# Get project root (parent of script folder)
$projectRoot = Split-Path -Parent $PSScriptRoot
$reportsPath = Join-Path $projectRoot "reports\quality"

# Create reports folder if missing
if (-not (Test-Path $reportsPath)) {
    New-Item -ItemType Directory -Force -Path $reportsPath | Out-Null
    Write-Host "Created reports/quality directory at project root"
}

# 1. Auto-format code using Black
Write-Host "`n Running Black..."
black . --skip-string-normalization > "$reportsPath\black.txt" 2>&1

# 2. Sort imports using isort
Write-Host " Running isort..."
isort . --filter-files --skip venv312 --skip .venv --skip __pycache__ > "$reportsPath\isort.txt" 2>&1

# 3. Run Flake8 for style violations
Write-Host " Running Flake8..."
flake8 . --exclude=venv312,.venv,__pycache__,reports > "$reportsPath\flake8.txt" 2>&1

# 4. Run MyPy for static type checking
Write-Host " Running MyPy..."
mypy . --ignore-missing-imports > "$reportsPath\mypy.txt" 2>&1

# 5. Run Bandit for security scanning
Write-Host " Running Bandit..."
bandit -r . -x venv312,.venv,__pycache__,reports > "$reportsPath\bandit.txt" 2>&1

# 6. Measure complexity using Radon
Write-Host " Running Radon (complexity + maintainability)..."
radon cc . -s -a -e "venv312/*,__pycache__/*,reports/*" > "$reportsPath\radon-cc.txt" 2>&1
radon mi . -s -e "venv312/*,__pycache__/*,reports/*" > "$reportsPath\radon-mi.txt" 2>&1

# 7. Run Pylint for linting and maintainability
Write-Host " Running Pylint..."
$pylintFiles = Get-ChildItem -Recurse -Include *.py | Where-Object { $_.FullName -notmatch "venv312|__pycache__|reports" }
if ($pylintFiles.Count -gt 0) {
    pylint $pylintFiles.FullName > "$reportsPath\pylint.txt" 2>&1
} else {
    Write-Host " No Python files found for Pylint."
}

# 8. Generate summary
Write-Host "`n Creating summary.md..."
$summaryPath = Join-Path $reportsPath "summary.md"
@"
# Quality Analysis Summary
Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Tool Results
- **Black**: Auto-formatting applied (see black.txt)
- **isort**: Imports sorted (see isort.txt)
- **Flake8**: Code style issues logged (see flake8.txt)
- **MyPy**: Static type analysis complete (see mypy.txt)
- **Bandit**: Security scan results in bandit.txt
- **Radon**: Complexity (radon-cc.txt) and maintainability (radon-mi.txt)
- **Pylint**: Detailed linting results (pylint.txt)

Quality analysis complete — reports saved in /reports/quality/
"@ | Out-File -Encoding UTF8 $summaryPath

Write-Host "`n=== Quality Analysis Finished ==="
