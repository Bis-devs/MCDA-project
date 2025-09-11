from flask import Blueprint, render_template, request, flash

criteria_bp = Blueprint("criteria_bp", __name__)

@criteria_bp.route("/", methods=["GET", "POST"])
def criteria():
    criteria_names = [
        "Revenue", "Revenue Growth", "Profit", 
        "Profit Growth", "Assets", "Employees", "ROA"
    ]

    weights = []
    error = None

    if request.method == "POST":
        try:
            weights = [float(request.form.get(c, 0)) for c in criteria_names]
            total = sum(weights)
            if abs(total - 1.0) > 0.001:
                error = f"⚠️ The sum of weights must be 1. Current: {round(total, 3)}"
            else:
                flash("✅ Weights updated successfully", "success")
        except ValueError:
            error = "⚠️ Enter only numbers."

    return render_template("criteria.html", criteria_names=criteria_names, weights=weights, error=error)
