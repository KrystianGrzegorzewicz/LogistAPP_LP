from solver import LinearProductionSolver

profits = [4, 6, 3, 12]

consumption = [
    [1, 2, 1.5, 6],     # środek 1
    [2, 2, 1.5, 4],     # środek 2
]

resources = [90000, 120000]

solver = LinearProductionSolver(
    profits=profits,
    consumption=consumption,
    resources=resources,
)

result = solver.solve()

print("Status:", result["status"])
print("Zysk całkowity:", result["objective"])
print("Plan produkcji:")
for k, v in result["production"].items():
    print(f"  {k} = {v}")

print("\nWykorzystanie zasobów:")
for r in result["resource_usage"]:
    print(
        f"  Zasób {r['resource']}: "
        f"{r['used']:.0f}/{r['limit']} "
        f"({r['usage_pct']:.1f}%)"
    )
