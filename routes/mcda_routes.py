from flask import Blueprint, render_template, flash ,request , session, url_for , redirect 
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from utils.helpers import build_decision_matrix
import numpy as np
from pymcdm.weights.subjective import AHP

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

mcda_bp = Blueprint("mcda_bp", __name__)


from pymcdm.methods import WSM

@mcda_bp.route("/wsm", methods=["GET", "POST"])
def wsm():
    companies = list(db.companies.find({}))  # all from DB

    # Če je POST → filtriraj samo označene
    selected_names = request.form.getlist("selected_companies")
    if request.method == "POST" and selected_names:
        companies = [c for c in companies if c["name"] in selected_names]

    if not companies:
        flash("Please select at least one company to run WSM.", "warning")
        return render_template("wsm.html", companies=[], results=[], criteria_names=[])

    # Build decision matrix
    matrix, criteria_types = build_decision_matrix(companies)

    # Generate random weights (sum = 1)
    weights = np.random.rand(len(criteria_types))
    weights = weights / np.sum(weights)

    # Run WSM
    wsm_method = WSM()
    nmatrix, wmatrix, prefs = wsm_method._method(matrix, weights, criteria_types)

    results = []
    for i, comp in enumerate(companies):
        pairs = list(zip(nmatrix[i].tolist(), wmatrix[i].tolist()))
        results.append({
            "name": comp["name"],
            "pairs": pairs,
            "score": round(prefs[i], 3)
        })

    criteria_names = [
        "Revenue", "Revenue Growth", "Profit", 
        "Profit Growth", "Assets", "Employees", "ROA"
    ]

    return render_template("wsm.html",
                           companies=companies,
                           results=results,
                           criteria_names=criteria_names,
                           weights=weights,
                           zip=zip)


@mcda_bp.route("/ahp", methods=["GET", "POST"])
def ahp():
    return render_template("ahp.html")





# TOPSIS
@mcda_bp.route("/topsis")
def topsis():
    companies = list(db.companies.find({}, {"_id": 0}))
    decision_matrix, company_names = build_decision_matrix(companies)

    # Example weights and benefit/cost (for now, adjust later)
    weights = [0.15, 0.1, 0.2, 0.1, 0.15, 0.1, 0.2]
    benefit = ["max"] * len(weights)

    scores = topsis_method(np.array(decision_matrix), weights, benefit, graph=False, verbose=False)
    sorted_indices = np.argsort(-scores)
    ranking = [{"company": company_names[i], "score": round(float(scores[i]), 3)} for i in sorted_indices]

    return render_template("topsis.html", ranking=ranking)
