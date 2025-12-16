# blending/recipe.py
class Recipe:
    """
    Représente une recette produite par l'optimisation.
    x : dict ingredient_name -> quantity (L)
    objective : coût total
    """
    def __init__(self, x: dict = None, objective: float = None, volume: float = None):
        self.x = x or {}
        self.objective = objective
        self.volume = volume

    def proportions(self):
        if not self.x or self.volume in (None, 0):
            return {}
        return {k: v / self.volume for k, v in self.x.items()}

    def __repr__(self):
        return f"Recipe(obj={self.objective}, vol={self.volume}, x={self.x})"
