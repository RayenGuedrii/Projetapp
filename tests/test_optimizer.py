# tests/test_optimizer.py
import os
from blending.utils import load_ingredients_from_csv, load_constraints_from_json
from blending.optimizer import optimize_blending
from blending.constraints import Constraints

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ING_CSV = os.path.join(DATA_DIR, "ingredients.csv")
CONS_JSON = os.path.join(DATA_DIR, "constraints.json")

def test_optimize_basic():
    ingredients = load_ingredients_from_csv(ING_CSV)
    volume_total, attr_bounds, budget_max = load_constraints_from_json(CONS_JSON)
    constraints = Constraints(volume_total=volume_total, attr_bounds=attr_bounds, budget_max=budget_max)
    recipe = optimize_blending(ingredients, constraints, solver='auto')
    assert recipe is not None
    assert abs(sum(recipe.x.values()) - constraints.volume_total) < 1e-6
    # sucre between bounds
    total_sucre = sum(ingredients[k].attrs.get('sucre',0.0) * v for k,v in recipe.x.items())
    assert constraints.attr_bounds['sucre'][0] - 1e-6 <= total_sucre <= constraints.attr_bounds['sucre'][1] + 1e-6
