"""
Ajoute app/ au sys.path pour que les imports fonctionnent depuis tests/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
