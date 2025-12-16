# blending/optimizer.py
from .recipe import Recipe
from .constraints import Constraints

# Try to import gurobipy; if absent, we'll use PuLP
try:
    import gurobipy as gp
    from gurobipy import GRB
    _HAS_GUROBI = True
except Exception:
    _HAS_GUROBI = False

try:
    import pulp
    _HAS_PULP = True
except Exception:
    _HAS_PULP = False

def optimize_with_gurobi(ingredients, constraints: Constraints, time_limit=None):
    model = gp.Model("blending")
    model.setParam('OutputFlag', 0)
    if time_limit:
        model.setParam('TimeLimit', time_limit)

    ing_names = list(ingredients.keys())
    x = model.addVars(ing_names, lb=0.0, name="x")

    # Upper bounds
    for i in ing_names:
        if ingredients[i].max_qty is not None:
            x[i].ub = ingredients[i].max_qty

    # Objective: minimize total cost
    model.setObjective(gp.quicksum(ingredients[i].cost * x[i] for i in ing_names), GRB.MINIMIZE)

    # Volume constraint
    model.addConstr(gp.quicksum(x[i] for i in ing_names) == constraints.volume_total, name="volume")

    # Attribute constraints
    for k, (amin, amax) in constraints.attr_bounds.items():
        if amin is not None:
            model.addConstr(gp.quicksum(ingredients[i].attrs.get(k, 0.0) * x[i] for i in ing_names) >= amin * constraints.volume_total,
                            name=f"{k}_min")
        if amax is not None:
            model.addConstr(gp.quicksum(ingredients[i].attrs.get(k, 0.0) * x[i] for i in ing_names) <= amax * constraints.volume_total,
                            name=f"{k}_max")

    # Budget max (optionnel)
    if constraints.budget_max is not None:
        model.addConstr(gp.quicksum(ingredients[i].cost * x[i] for i in ing_names) <= constraints.budget_max, name="budget")

    model.optimize()

    if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
        x_sol = {i: x[i].X for i in ing_names}
        return Recipe(x=x_sol, objective=model.ObjVal, volume=constraints.volume_total)
    else:
        raise RuntimeError(f"Gurobi: modèle non optimal (status {model.Status})")

def optimize_with_pulp(ingredients, constraints: Constraints, time_limit=None):
    if not _HAS_PULP:
        raise RuntimeError("PuLP n'est pas installé.")
    prob = pulp.LpProblem("blending", pulp.LpMinimize)
    ing_names = list(ingredients.keys())
    x = pulp.LpVariable.dicts("x", ing_names, lowBound=0, cat='Continuous')

    # upper bounds
    for i in ing_names:
        if ingredients[i].max_qty is not None:
            prob += x[i] <= ingredients[i].max_qty

    # objective
    prob += pulp.lpSum([ingredients[i].cost * x[i] for i in ing_names])

    # volume
    prob += pulp.lpSum([x[i] for i in ing_names]) == constraints.volume_total

    # attributes
    for k, (amin, amax) in constraints.attr_bounds.items():
        if amin is not None:
            prob += pulp.lpSum([ingredients[i].attrs.get(k, 0.0) * x[i] for i in ing_names]) >= amin * constraints.volume_total
        if amax is not None:
            prob += pulp.lpSum([ingredients[i].attrs.get(k, 0.0) * x[i] for i in ing_names]) <= amax * constraints.volume_total

    # budget
    if constraints.budget_max is not None:
        prob += pulp.lpSum([ingredients[i].cost * x[i] for i in ing_names]) <= constraints.budget_max

    # Solve (PuLP default solver CBC)
    solver = pulp.PULP_CBC_CMD(timeLimit=time_limit) if time_limit else None
    prob.solve(solver)

    status = pulp.LpStatus[prob.status]
    if status in ("Optimal", "Optimal (Integer Feasible)"):
        x_sol = {i: x[i].varValue for i in ing_names}
        obj = pulp.value(prob.objective)
        return Recipe(x=x_sol, objective=obj, volume=constraints.volume_total)
    else:
        raise RuntimeError(f"PuLP: problème non optimal ({status})")

def optimize_blending(ingredients_dict, constraints_obj=None, solver='auto', time_limit=None):
    """
    ingredients_dict : dict name -> Ingredient instance
    constraints_obj : Constraints
    solver : 'auto', 'gurobi', or 'pulp'
    """
    if constraints_obj is None:
        constraints_obj = Constraints()

    if solver == 'auto':
        if _HAS_GUROBI:
            solver_to_use = 'gurobi'
        elif _HAS_PULP:
            solver_to_use = 'pulp'
        else:
            raise RuntimeError("Aucun solveur disponible (Gurobi ou PuLP). Installe PuLP ou configure Gurobi.")
    else:
        solver_to_use = solver

    if solver_to_use == 'gurobi':
        if not _HAS_GUROBI:
            raise RuntimeError("Gurobi non disponible.")
        return optimize_with_gurobi(ingredients_dict, constraints_obj, time_limit=time_limit)
    elif solver_to_use == 'pulp':
        if not _HAS_PULP:
            raise RuntimeError("PuLP non disponible.")
        return optimize_with_pulp(ingredients_dict, constraints_obj, time_limit=time_limit)
    else:
        raise ValueError(f"Solver inconnu: {solver_to_use}")
