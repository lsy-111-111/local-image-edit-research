from __future__ import annotations

import subprocess
import sys


def test_project_structure_validator_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/validate_project_structure.py"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
