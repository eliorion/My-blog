import sys
from pathlib import Path

# Allow 'import linkedin.generate' when pytest runs from inside linkedin/
sys.path.insert(0, str(Path(__file__).parent.parent))
