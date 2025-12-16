# blending/utils.py
import csv
import json
from .ingredients import Ingredient

def load_ingredients_from_csv(path):
    """
    CSV attendu: name,cost,max,attr1,attr2,...
    Première ligne: en-têtes (ex: name,cost,max,sucre,acidite)
    Retour: dict name -> Ingredient
    """
    ingredients = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        # headers example: name,cost,max,sucre,acidite
        attr_names = headers[3:]
        for row in reader:
            if not row or row[0].strip() == "":
                continue
            name = row[0].strip()
            cost = float(row[1]) if row[1] else 0.0
            max_qty = float(row[2]) if row[2] else None
            attrs = {}
            for i, a in enumerate(attr_names):
                try:
                    attrs[a] = float(row[3 + i])
                except Exception:
                    attrs[a] = 0.0
            ingredients[name] = Ingredient(name=name, cost=cost, attrs=attrs, max_qty=max_qty)
    return ingredients

def load_constraints_from_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    volume_total = data.get('volume_total', 1.0)
    attr_bounds = data.get('attr_bounds', {})
    budget_max = data.get('budget_max', None)
    return volume_total, attr_bounds, budget_max
