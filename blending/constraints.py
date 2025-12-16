# blending/constraints.py
"""
Structure simple pour stocker les contraintes:
- volume_total (L)
- attr_bounds: dict attribute -> (min, max)
- budget_max (optionnel)
"""
from typing import Dict, Tuple

class Constraints:
    def __init__(self, volume_total: float = 1.0, attr_bounds: Dict[str, Tuple[float, float]] = None, budget_max: float = None):
        self.volume_total = float(volume_total)
        self.attr_bounds = attr_bounds or {}  # ex: {'sucre': (50,200), 'acidite': (3.3,3.9)}
        self.budget_max = float(budget_max) if budget_max is not None else None

    def __repr__(self):
        return f"Constraints(volume={self.volume_total}, attr_bounds={self.attr_bounds}, budget_max={self.budget_max})"
