# 🍹 Blending Optimizer: Cocktail Recipe Optimization

An **Operations Research** project that solves a **blending problem** with linear programming: find the cheapest mix of ingredients that respects quality constraints (sugar, acidity, volume, budget).

Comes with a **desktop GUI** (PyQt5) and a command-line mode.

## 📐 The model

**Decision variables:** `x_i` = quantity (L) of ingredient *i*

**Objective:** minimize total cost  `Σ cost_i · x_i`

**Constraints:**
- Total volume: `Σ x_i = V`
- Quality bounds for each attribute *k* (sugar, acidity): `min_k · V ≤ Σ attr_ik · x_i ≤ max_k · V`
- Max quantity per ingredient: `0 ≤ x_i ≤ max_i`
- Optional budget: `Σ cost_i · x_i ≤ B`

## ✨ Features

- Solves with **Gurobi** when available, otherwise falls back to **PuLP** (CBC, free)
- **PyQt5 GUI**: view ingredients, edit constraints, run the optimizer in a background thread, see results as a chart (matplotlib)
- Data-driven: ingredients in CSV, constraints in JSON
- Unit tests with **pytest**

## 📁 Project structure

```
blending/          # Core package: model, constraints, recipe, optimizer
data/              # ingredients.csv, constraints.json
notebooks/         # Exploration notebook
tests/             # pytest tests
main.py            # Command-line entry point
blending_gui.py    # PyQt5 desktop app
```

## 🚀 Getting started

```bash
python -m venv venv
venv\Scripts\activate        # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
```

Run in the terminal:
```bash
python main.py
```

Run the GUI:
```bash
python blending_gui.py
```

Run the tests:
```bash
pytest
```

## 🧪 Customize

Edit `data/ingredients.csv` (name, cost, max quantity, sugar, acidity) and `data/constraints.json` (total volume, attribute bounds, budget) to model your own blending problem.

## 🛠️ Tech

Python · PuLP · Gurobi · PyQt5 · matplotlib · pytest
