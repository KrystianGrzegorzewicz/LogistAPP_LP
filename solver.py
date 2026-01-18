from pulp import (
    LpProblem,
    LpVariable,
    LpMaximize,
    lpSum,
    LpStatus,
    value,
)


class LinearProductionSolver:
    def __init__(
        self,
        profits: list[float],
        consumption: list[list[float]],
        resources: list[float],
        min_prod: list[float] | None = None,
        max_prod: list[float] | None = None,
        integer: bool = False,
    ):
        """
        profits[j]      = c_j
        consumption[i][j] = a_ij
        resources[i]    = b_i
        min_prod[j]     = d_j
        max_prod[j]     = m_j
        """

        self.n = len(profits)        # liczba wyrobów
        self.k = len(resources)      # liczba ograniczeń

        self.profits = profits
        self.consumption = consumption
        self.resources = resources
        self.min_prod = min_prod
        self.max_prod = max_prod
        self.integer = integer

        self.model = None
        self.variables = []

    # ------------------------------
    def build_model(self):
        self.model = LpProblem("Production_Optimization", LpMaximize)

        # Zmienne decyzyjne
        var_type = "Integer" if self.integer else "Continuous"

        self.variables = [
            LpVariable(
                f"x{j+1}",
                lowBound=self.min_prod[j] if self.min_prod else 0,
                upBound=self.max_prod[j] if self.max_prod else None,
                cat=var_type,
            )
            for j in range(self.n)
        ]

        # Funkcja celu
        self.model += lpSum(
            self.profits[j] * self.variables[j]
            for j in range(self.n)
        ), "Total_Profit"

        # Ograniczenia zasobów
        for i in range(self.k):
            self.model += (
                lpSum(
                    self.consumption[i][j] * self.variables[j]
                    for j in range(self.n)
                )
                <= self.resources[i],
                f"Resource_{i+1}",
            )

    # ------------------------------
    def solve(self):
        if self.model is None:
            self.build_model()

        status = self.model.solve()

        return {
            "status": LpStatus[status],
            "objective": value(self.model.objective),
            "production": {
                f"x{j+1}": value(self.variables[j])
                for j in range(self.n)
            },
            "resource_usage": self._resource_usage(),
        }

    # ------------------------------
    def _resource_usage(self):
        usage = []
        for i in range(self.k):
            used = sum(
                self.consumption[i][j] * value(self.variables[j])
                for j in range(self.n)
            )
            usage.append({
                "resource": i + 1,
                "used": used,
                "limit": self.resources[i],
                "usage_pct": 100 * used / self.resources[i],
            })
        return usage
