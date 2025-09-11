import numpy as np

def parse_int(value_str):
    if value_str is None:
        return 0
    clean_str = str(value_str).replace(',', '').replace('$', '').strip()
    try:
        return int(float(clean_str))
    except ValueError:
        return 0

def safe_float(value, default=0.0):
    """Convert to float safely, handle None and bad strings."""
    if value is None:
        return default
    try:
        return float(str(value).replace('%', '').strip())
    except (ValueError, TypeError):
        return default

def calc_roa(profit, assets):
    if profit and assets and assets > 0:
        return (profit / assets) * 100
    return 0.0

def build_decision_matrix(companies):
    matrix = []
    for comp in companies:
        revenue = parse_int(comp.get("revenues_million", 0))
        revenue_growth = safe_float(comp.get("revenue_percent_change", 0))
        profit = parse_int(comp.get("profits_million", 0))
        profit_growth = safe_float(comp.get("profits_percent_change", 0))
        assets = parse_int(comp.get("assets_million", 0))
        employees = parse_int(comp.get("employees", 0))
        roa = calc_roa(profit, assets)

        row = [revenue, revenue_growth, profit, profit_growth, assets, employees, roa]
        matrix.append(row)

    matrix = np.array(matrix, dtype=float)

    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)

    types = np.array([1, 1, 1, 1, 1, -1, 1])  
    return matrix, types
