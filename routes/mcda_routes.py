from flask import Blueprint, render_template, flash ,request , session, url_for , redirect 
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from utils.helpers import build_decision_matrix
import numpy as np
from pymcdm.weights.subjective import AHP
from pymcdm.methods import TOPSIS
from decimal import Decimal, ROUND_HALF_UP, getcontext


client = MongoClient(MONGO_URI)
db = client[DB_NAME]

mcda_bp = Blueprint("mcda_bp", __name__)


from pymcdm.methods import WSM

@mcda_bp.route("/wsm", methods=["GET", "POST"])
def wsm():
    getcontext().prec = 12  # enough precision for 8 decimals

    companies = list(db.companies.find({}))

    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]
    n_criteria = len(criteria_names)

    selected_names = request.form.getlist("selected_companies")

    # Default weight = exact 1/7 with 8 decimal places
    default_weight = (Decimal("1") / Decimal(str(n_criteria))).quantize(
        Decimal("0.00000001"), rounding=ROUND_HALF_UP
    )
    weights = [default_weight] * n_criteria  # keep as Decimal for validation

    # Read manual weights if provided
    weights_input = request.form.getlist("weights")
    weights_ok = True

    if request.method == "POST" and weights_input:
        try:
            w_decimal = [Decimal(x).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
                         for x in weights_input]

            if len(w_decimal) != n_criteria:
                flash(f"Expected {n_criteria} weights, got {len(w_decimal)}.", "danger")
                weights_ok = False
            else:
                # Allow very small tolerance
                tolerance = Decimal("0.00100000")  # accept up to ±0.001
                total_sum = sum(w_decimal)

                if abs(total_sum - Decimal("1.00000000")) > tolerance:
                    flash("The sum of weights must be exactly 1.00000000.", "danger")
                    weights_ok = False
                else:
                    weights = w_decimal
        except Exception:
            flash("Weights must be numeric values.", "danger")
            weights_ok = False

    results = []
    if request.method == "POST" and selected_names and weights_ok:
        selected_companies = [c for c in companies if c.get("name") in selected_names]
        if not selected_companies:
            flash("Please select at least one company.", "warning")
        else:
            # Convert Decimals to floats for numpy
            weights_float = np.array([float(w) for w in weights], dtype=float)

            matrix, criteria_types = build_decision_matrix(selected_companies)
            wsm_method = WSM()
            nmatrix, wmatrix, prefs = wsm_method._method(matrix, weights_float, criteria_types)

            for comp, nrow, wrow, pref in zip(selected_companies, nmatrix, wmatrix, prefs):
                results.append({
                    "name": comp["name"],
                    "pairs": list(zip(nrow.tolist(), wrow.tolist())),
                    "score": round(float(pref), 3)
                })

    return render_template(
        "wsm.html",
        companies=companies,
        results=results,
        criteria_names=criteria_names,
        selected_names=selected_names,
        weights=[float(w) for w in weights],  # convert to float for display
        zip=zip
    )





@mcda_bp.route("/ahp", methods=["GET", "POST"])
def ahp():
    return render_template("ahp.html")




# TOPSIS
@mcda_bp.route("/topsis", methods=["GET", "POST"])
def topsis():
    plot_data = None
    getcontext().prec = 12
    companies = list(db.companies.find({}))

    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]
    n_criteria = len(criteria_names)

    selected_names = request.form.getlist("selected_companies")

    # Default weights = 1/n_criteria (rounded to 3 decimals for display)
    default_weight = (Decimal("1") / Decimal(str(n_criteria))).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    )
    weights = [default_weight] * n_criteria

    # Read manual weights
    weights_input = request.form.getlist("weights")
    weights_ok = True
    if request.method == "POST" and weights_input:
        try:
            w_decimal = [Decimal(x).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
                         for x in weights_input]
            if len(w_decimal) != n_criteria:
                flash(f"Expected {n_criteria} weights, got {len(w_decimal)}.", "danger")
                weights_ok = False
            else:
                tolerance = Decimal("0.00100000")
                total_sum = sum(w_decimal)
                if abs(total_sum - Decimal("1.00000000")) > tolerance:
                    flash("The sum of weights must be exactly 1.00000000.", "danger")
                    weights_ok = False
                else:
                    weights = w_decimal
        except Exception:
            flash("Weights must be numeric values.", "danger")
            weights_ok = False

    # Prepare companies with criteria for display
    companies_display = []
    for comp in companies:
        matrix_row, _ = build_decision_matrix([comp])
        companies_display.append({
            "name": comp["name"],
            "criteria": matrix_row[0].tolist()
        })

    results, interpretation = [], {}
    if request.method == "POST" and selected_names and weights_ok:
        selected_companies = [c for c in companies if c.get("name") in selected_names]
        if not selected_companies:
            flash("Please select at least one company.", "warning")
        else:
            weights_float = np.array([float(w) for w in weights], dtype=float)
            matrix, criteria_types = build_decision_matrix(selected_companies)

            # Run TOPSIS
            topsis_method = TOPSIS()
            nmatrix, wmatrix, nis, pis, Dm, Dp, prefs = topsis_method._method(
                matrix, weights_float, criteria_types
            )

            for comp, nrow, wrow, pref in zip(selected_companies, nmatrix, wmatrix, prefs):
                results.append({
                    "name": comp["name"],
                    "pairs": list(zip(nrow.tolist(), wrow.tolist())),
                    "score": round(float(pref), 3)
                })

            results.sort(key=lambda x: x["score"], reverse=True)

            # Simple interpretation
            interpretation["best"] = results[0]["name"]
            interpretation["worst"] = results[-1]["name"]
            interpretation["score_gap"] = round(results[0]["score"] - results[1]["score"], 3) \
                if len(results) > 1 else None
            interpretation["note"] = (
                "Scores close to 1 indicate strong performance; scores near 0 indicate weak performance."
            )

            

            results.sort(key=lambda x: x["score"], reverse=True)

            interpretation["best"] = results[0]["name"]
            interpretation["worst"] = results[-1]["name"]
            interpretation["score_gap"] = round(results[0]["score"] - results[1]["score"], 3) \
                if len(results) > 1 else None
            interpretation["note"] = (
                "Scores close to 1 indicate strong performance; scores near 0 indicate weak performance."
            )

            # 🔹 New additions
            # Percent closeness (0–100%)
            interpretation["percent_scores"] = [
                {"name": r["name"], "percent": round(r["score"] * 100, 1)}
                for r in results
            ]

            # Ranking stability note
            if len(results) > 1:
                gap = results[0]["score"] - results[1]["score"]
                if gap < 0.05:
                    interpretation["stability"] = "Top 2 companies are very close — ranking may be unstable."
                elif gap > 0.15:
                    interpretation["stability"] = "Top company is clearly dominant."
                else:
                    interpretation["stability"] = "There is a moderate difference between top 2 companies."

                    # Data for plotting (company names + scores)
            if results:
                plot_data = {
                "labels": [r["name"] for r in results],
                "scores": [round(r["score"], 3) for r in results]
                            }


    return render_template(
    "topsis.html",
    companies=companies_display,
    results=results,
    criteria_names=criteria_names,
    selected_names=selected_names,
    weights=[float(w) for w in weights],
    interpretation=interpretation,
    plot_data=plot_data,   
    zip=zip
)


