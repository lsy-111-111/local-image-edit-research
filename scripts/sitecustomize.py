from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
root_text = str(ROOT)
while root_text in sys.path:
    sys.path.remove(root_text)
sys.path.insert(0, root_text)
