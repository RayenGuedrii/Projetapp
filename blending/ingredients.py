# blending/ingredients.py
class Ingredient:
    """
    Représente un ingrédient.
    Attributs usuels : name, cost (€/L), attrs dict (ex: 'sucre', 'acidite', ...)
    """
    def __init__(self, name: str, cost: float, attrs: dict, max_qty: float = None):
        self.name = name
        self.cost = float(cost)
        self.attrs = {k: float(v) for k, v in (attrs.items() if attrs else {})}
        self.max_qty = float(max_qty) if max_qty is not None else None

    def __repr__(self):
        return f"Ingredient({self.name!r}, cost={self.cost}, max={self.max_qty}, attrs={self.attrs})"
