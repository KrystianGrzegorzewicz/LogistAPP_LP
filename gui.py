import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from solver import LinearProductionSolver


class ProductionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optymalizacja produkcji")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        # ---- Tabela danych ----
        self.table = QTableWidget(6, 4)
        self.table.setHorizontalHeaderLabels(["W1", "W2", "W3", "W4"])
        self.table.setVerticalHeaderLabels([
            "Zysk",
            "Środek 1",
            "Środek 2",
            "Limit S1",
            "Limit S2",
            "—"
        ])

        default_data = [
            [4, 6, 3, 12],
            [1, 2, 1.5, 6],
            [2, 2, 1.5, 4],
            [90000, 90000, 90000, 90000],
            [120000, 120000, 120000, 120000],
        ]

        for r in range(5):
            for c in range(4):
                self.table.setItem(
                    r, c, QTableWidgetItem(str(default_data[r][c]))
                )

        layout.addWidget(QLabel("Dane wejściowe"))
        layout.addWidget(self.table)

        # ---- Przycisk ----
        self.solve_btn = QPushButton("Oblicz optimum")
        self.solve_btn.clicked.connect(self.solve)
        layout.addWidget(self.solve_btn)

        # ---- Wyniki ----
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

    # -------------------------
    def solve(self):
        try:
            profits = [float(self.table.item(0, j).text()) for j in range(4)]
            consumption = [
                [float(self.table.item(1, j).text()) for j in range(4)],
                [float(self.table.item(2, j).text()) for j in range(4)],
            ]

            resources = [
                float(self.table.item(3, 0).text()),
                float(self.table.item(4, 0).text()),
            ]

            solver = LinearProductionSolver(
                profits=profits,
                consumption=consumption,
                resources=resources,
            )

            result = solver.solve()

            if result["status"] != "Optimal":
                raise ValueError("Brak rozwiązania optymalnego")

            text = f"Zysk całkowity: {result['objective']:.2f} zł\n\n"
            text += "Plan produkcji:\n"
            for k, v in result["production"].items():
                text += f"{k}: {v:.2f}\n"

            self.result_label.setText(text)

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))


# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductionApp()
    window.show()
    sys.exit(app.exec())
