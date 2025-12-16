# main.py
import os
from blending.utils import load_ingredients_from_csv, load_constraints_from_json
from blending.constraints import Constraints
from blending.optimizer import optimize_blending



DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ING_CSV = os.path.join(DATA_DIR, "ingredients.csv")
CONS_JSON = os.path.join(DATA_DIR, "constraints.json")

def main():
    print("Chargement des ingrédients...")
    ingredients = load_ingredients_from_csv(ING_CSV)
    print(f"{len(ingredients)} ingrédients chargés.")

    volume_total, attr_bounds, budget_max = load_constraints_from_json(CONS_JSON)
    constraints = Constraints(volume_total=volume_total, attr_bounds=attr_bounds, budget_max=budget_max)
    print("Contraintes :", constraints)

    # Optimisation (auto détecte Gurobi ou PuLP)
    print("Lancement de l'optimisation...")
    recipe = optimize_blending(ingredients, constraints)
    print("Résultat obtenu :")
    print("Coût total :", recipe.objective)
    print("Quantités (L) :")
    for k, v in recipe.x.items():
        print(f"  {k}: {v:.6f} L")
    print("Proportions :")
    for k, v in recipe.proportions().items():
        print(f"  {k}: {v*100:.2f}%")

if __name__ == "__main__":
    main()
