import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QMessageBox
)
from solver import LinearProductionSolver


class ProductionGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optymalizacja produkcji")
        self.resize(950, 650)

        self.updating = False  # blokada rekurencji

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.init_products_tab()
        self.init_resources_tab()
        self.init_consumption_tab()
        self.init_solution_tab()

    # ================= PRODUCTS =================
    def init_products_tab(self):
        self.products_tab = QWidget()
        layout = QVBoxLayout(self.products_tab)

        self.products_table = QTableWidget(0, 4)
        self.products_table.setHorizontalHeaderLabels(
            ["Nazwa produktu", "Zysk", "Min", "Max"]
        )
        self.products_table.itemChanged.connect(self.on_products_changed)

        layout.addWidget(self.products_table)

        btns = QHBoxLayout()
        add_btn = QPushButton("➕ Dodaj produkt")
        del_btn = QPushButton("❌ Usuń produkt")

        add_btn.clicked.connect(self.add_product)
        del_btn.clicked.connect(self.remove_product)

        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

        self.tabs.addTab(self.products_tab, "Produkty")

    def add_product(self):
        self.updating = True
        row = self.products_table.rowCount()
        self.products_table.insertRow(row)

        defaults = ["Nowy produkt", 0, 0, ""]
        for col, val in enumerate(defaults):
            self.products_table.setItem(row, col, QTableWidgetItem(str(val)))

        self.updating = False
        self.sync_consumption_table()

    def remove_product(self):
        row = self.products_table.currentRow()
        if row >= 0:
            self.products_table.removeRow(row)
            self.sync_consumption_table()

    def on_products_changed(self, item):
        if self.updating:
            return
        if item.column() == 0:  # zmiana nazwy
            self.update_consumption_headers()

    # ================= RESOURCES =================
    def init_resources_tab(self):
        self.resources_tab = QWidget()
        layout = QVBoxLayout(self.resources_tab)

        self.resources_table = QTableWidget(0, 3)
        self.resources_table.setHorizontalHeaderLabels(
            ["Nazwa zasobu", "Limit", "Jednostka"]
        )
        self.resources_table.itemChanged.connect(self.on_resources_changed)

        layout.addWidget(self.resources_table)

        btns = QHBoxLayout()
        add_btn = QPushButton("➕ Dodaj zasób")
        del_btn = QPushButton("❌ Usuń zasób")

        add_btn.clicked.connect(self.add_resource)
        del_btn.clicked.connect(self.remove_resource)

        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

        self.tabs.addTab(self.resources_tab, "Zasoby")

    def add_resource(self):
        self.updating = True
        row = self.resources_table.rowCount()
        self.resources_table.insertRow(row)

        defaults = ["Nowy zasób", 0, ""]
        for col, val in enumerate(defaults):
            self.resources_table.setItem(row, col, QTableWidgetItem(str(val)))

        self.updating = False
        self.sync_consumption_table()

    def remove_resource(self):
        row = self.resources_table.currentRow()
        if row >= 0:
            self.resources_table.removeRow(row)
            self.sync_consumption_table()

    def on_resources_changed(self, item):
        if self.updating:
            return
        if item.column() == 0:
            self.update_consumption_headers()

    # ================= CONSUMPTION =================
    def init_consumption_tab(self):
        self.consumption_tab = QWidget()
        layout = QVBoxLayout(self.consumption_tab)

        layout.addWidget(QLabel("Zużycie zasobów przez produkty"))
        self.consumption_table = QTableWidget(0, 0)
        layout.addWidget(self.consumption_table)

        self.tabs.addTab(self.consumption_tab, "Zużycie")

    def sync_consumption_table(self):
        products = self.get_product_names()
        resources = self.get_resource_names()

        self.consumption_table.setRowCount(len(resources))
        self.consumption_table.setColumnCount(len(products))
        self.consumption_table.setHorizontalHeaderLabels(products)
        self.consumption_table.setVerticalHeaderLabels(resources)

        for r in range(len(resources)):
            for c in range(len(products)):
                if not self.consumption_table.item(r, c):
                    self.consumption_table.setItem(
                        r, c, QTableWidgetItem("0")
                    )

    def update_consumption_headers(self):
        self.consumption_table.setHorizontalHeaderLabels(
            self.get_product_names()
        )
        self.consumption_table.setVerticalHeaderLabels(
            self.get_resource_names()
        )

    # ================= SOLUTION =================
    def init_solution_tab(self):
        self.solution_tab = QWidget()
        layout = QVBoxLayout(self.solution_tab)

        self.solve_btn = QPushButton("▶ OBLICZ")
        self.solve_btn.clicked.connect(self.solve)

        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(
            ["Produkt", "Wielkość produkcji"]
        )

        self.profit_label = QLabel("Łączny zysk: -")

        layout.addWidget(self.solve_btn)
        layout.addWidget(self.result_table)
        layout.addWidget(self.profit_label)

        self.tabs.addTab(self.solution_tab, "Rozwiązanie")

    # ================= SOLVER =================
    def solve(self):
        try:
            products = self.get_product_names()
            resources = self.get_resource_names()

            profits = [
                float(self.products_table.item(r, 1).text())
                for r in range(len(products))
            ]

            min_prod = [
                float(self.products_table.item(r, 2).text() or 0)
                for r in range(len(products))
            ]

            max_prod = [
                float(self.products_table.item(r, 3).text())
                if self.products_table.item(r, 3).text() else None
                for r in range(len(products))
            ]

            limits = [
                float(self.resources_table.item(r, 1).text())
                for r in range(len(resources))
            ]

            consumption = []
            for i in range(len(resources)):
                row = []
                for j in range(len(products)):
                    row.append(
                        float(self.consumption_table.item(i, j).text())
                    )
                consumption.append(row)

            solver = LinearProductionSolver(
                profits=profits,
                consumption=consumption,
                resources=limits,
                min_prod=min_prod,
                max_prod=max_prod,
            )

            result = solver.solve()

            if result["status"] != "Optimal":
                raise ValueError("Brak rozwiązania optymalnego")

            self.result_table.setRowCount(len(products))
            for i, name in enumerate(products):
                self.result_table.setItem(
                    i, 0, QTableWidgetItem(name)
                )
                self.result_table.setItem(
                    i, 1, QTableWidgetItem(
                        f"{result['production'][f'x{i+1}']:.2f}"
                    )
                )

            self.profit_label.setText(
                f"Łączny zysk: {result['objective']:.2f}"
            )

            self.tabs.setCurrentWidget(self.solution_tab)

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    # ================= HELPERS =================
    def get_product_names(self):
        return [
            self.products_table.item(r, 0).text()
            for r in range(self.products_table.rowCount())
        ]

    def get_resource_names(self):
        return [
            self.resources_table.item(r, 0).text()
            for r in range(self.resources_table.rowCount())
        ]


# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductionGUI()
    window.show()
    sys.exit(app.exec())
