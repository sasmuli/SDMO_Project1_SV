import sys
from pathlib import Path

# Add parent directory to path so tests can import dedupe_utils
sys.path.insert(0, str(Path(__file__).parent.parent))
