# blending_gui.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from blending.utils import load_ingredients_from_csv, load_constraints_from_json
from blending.constraints import Constraints
from blending.optimizer import optimize_blending, Recipe

DATA_DIR = "data"
ING_CSV = f"{DATA_DIR}/ingredients.csv"
CONS_JSON = f"{DATA_DIR}/constraints.json"

# --------- Thread pour exécuter l'optimisation sans bloquer l'UI ---------
class OptimizerThread(QThread):
    result_ready = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, ingredients, constraints):
        super().__init__()
        self.ingredients = ingredients
        self.constraints = constraints

    def run(self):
        try:
            recipe = optimize_blending(self.ingredients, self.constraints, solver='auto')
            self.result_ready.emit(recipe)
        except Exception as e:
            self.error_signal.emit(str(e))

# --------- Fenêtre principale ---------
class BlendingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blending Problem - Cocktail Optimizer")
        self.setGeometry(200, 100, 900, 600)
        self.ingredients = load_ingredients_from_csv(ING_CSV)
        volume_total, attr_bounds, budget_max = load_constraints_from_json(CONS_JSON)
        self.constraints = Constraints(volume_total=volume_total, attr_bounds=attr_bounds, budget_max=budget_max)

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # ---- Table ingrédients ----
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Nom', 'Coût', 'Max', 'Sucre', 'Acidité'])
        self._populate_table()
        layout.addWidget(QLabel("Ingrédients"))
        layout.addWidget(self.table)

        # ---- Contraintes ----
        constr_layout = QHBoxLayout()
        self.volume_input = QLineEdit(str(self.constraints.volume_total))
        self.budget_input = QLineEdit(str(self.constraints.budget_max) if self.constraints.budget_max else "")
        constr_layout.addWidget(QLabel("Volume total (L)"))
        constr_layout.addWidget(self.volume_input)
        constr_layout.addWidget(QLabel("Budget max (€)"))
        constr_layout.addWidget(self.budget_input)
        layout.addWidget(QLabel("Contraintes"))
        layout.addLayout(constr_layout)

        # ---- Bouton lancer optimisation ----
        self.btn_optimize = QPushButton("Lancer optimisation")
        self.btn_optimize.clicked.connect(self.run_optimization)
        layout.addWidget(self.btn_optimize)

        # ---- Résultat ----
        self.result_label = QLabel("Résultats :")
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        # ---- Graphique ----
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def _populate_table(self):
        self.table.setRowCount(len(self.ingredients))
        for i, ing in enumerate(self.ingredients.values()):
            self.table.setItem(i, 0, QTableWidgetItem(ing.name))
            self.table.setItem(i, 1, QTableWidgetItem(str(ing.cost)))
            self.table.setItem(i, 2, QTableWidgetItem(str(ing.max_qty)))
            self.table.setItem(i, 3, QTableWidgetItem(str(ing.attrs.get('sucre',0))))
            self.table.setItem(i, 4, QTableWidgetItem(str(ing.attrs.get('acidite',0))))

    def run_optimization(self):
        # Mettre à jour ingrédients et contraintes depuis l'UI
        try:
            for i, ing in enumerate(self.ingredients.values()):
                ing.cost = float(self.table.item(i,1).text())
                ing.max_qty = float(self.table.item(i,2).text())
                ing.attrs['sucre'] = float(self.table.item(i,3).text())
                ing.attrs['acidite'] = float(self.table.item(i,4).text())
            self.constraints.volume_total = float(self.volume_input.text())
            budget = self.budget_input.text()
            self.constraints.budget_max = float(budget) if budget else None
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur dans les données : {e}")
            return

        # Lancer l'optimisation dans un thread
        self.thread = OptimizerThread(self.ingredients, self.constraints)
        self.thread.result_ready.connect(self.show_result)
        self.thread.error_signal.connect(lambda e: QMessageBox.critical(self, "Erreur Solveur", e))
        self.btn_optimize.setEnabled(False)
        self.thread.finished.connect(lambda: self.btn_optimize.setEnabled(True))
        self.thread.start()

    def show_result(self, recipe: Recipe):
        text = f"Coût total : {recipe.objective:.2f} €\nQuantités (L) :\n"
        for k,v in recipe.x.items():
            text += f"  {k}: {v:.3f}\n"
        text += "Proportions :\n"
        for k,v in recipe.proportions().items():
            text += f"  {k}: {v*100:.2f}%\n"
        self.result_label.setText(text)

        # ---- graphique ----
        self.ax.clear()
        names = list(recipe.x.keys())
        values = list(recipe.proportions().values())
        self.ax.pie(values, labels=names, autopct='%1.1f%%', startangle=140)
        self.ax.set_title("Proportions du cocktail")
        self.canvas.draw()

# --------- Run ---------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlendingApp()
    window.show()
    sys.exit(app.exec_())
