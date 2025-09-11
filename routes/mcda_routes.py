from flask import Blueprint, render_template, flash ,request , session, url_for , redirect 
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from utils.helpers import parse_int, safe_float, calc_roa, build_decision_matrix
import numpy as np
from pymcdm.weights.subjective import AHP
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pymcdm.methods import WSM , VIKOR ,TOPSIS
from pymcdm.methods.partial import PROMETHEE_I
import math




client = MongoClient(MONGO_URI)
db = client[DB_NAME]

mcda_bp = Blueprint("mcda_bp", __name__)

#Selection
@mcda_bp.route("/select", methods=["GET", "POST"])
def select_companies():
    getcontext().prec = 12  # precision for weights

    companies = list(db.companies.find({}))
    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]
    n_criteria = len(criteria_names)

    # Default weight = 1/n_criteria
    default_weight = (Decimal("1") / Decimal(str(n_criteria))).quantize(
        Decimal("0.00000001"), rounding=ROUND_HALF_UP
    )
    weights = [default_weight] * n_criteria

    selected_names = []
    if request.method == "POST":
        selected_names = request.form.getlist("selected_companies")
        weights_input = request.form.getlist("weights")

        if not selected_names or len(selected_names) < 3:
            flash("Please select at least three companies.", "warning")
        elif not weights_input:
            flash("Please enter weights.", "warning")
        else:
            try:
                w_decimal = [Decimal(x).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
                             for x in weights_input]

                tolerance = Decimal("0.00100000")
                total_sum = sum(w_decimal)
                if abs(total_sum - Decimal("1.00000000")) > tolerance:
                    flash("The sum of weights must equal 1.0 (±0.001).", "danger")
                else:
                    # Save to session for methods
                    session["selected_companies"] = selected_names
                    session["weights"] = [float(w) for w in w_decimal]
                    flash("Selection saved! Now you can try different methods.", "success")
                    return redirect(url_for("mcda_bp.wsm"))  # start with WSM
            except Exception:
                flash("Weights must be numeric values.", "danger")

    # Prepare display (same as in WSM)
    companies_display = []
    for c in companies:
        row = {
            "name": c.get("name", "Unknown"),
            "criteria": [
                parse_int(c.get("revenues_million", 0)),
                safe_float(c.get("revenue_percent_change", 0)),
                parse_int(c.get("profits_million", 0)),
                safe_float(c.get("profits_percent_change", 0)),
                parse_int(c.get("assets_million", 0)),
                parse_int(c.get("employees", 0)),
                calc_roa(parse_int(c.get("profits_million", 0)),
                         parse_int(c.get("assets_million", 0)))
            ]
        }
        companies_display.append(row)

    return render_template("select.html",
                           companies=companies_display,
                           criteria_names=criteria_names,
                           selected_names=selected_names,
                           weights=[float(w) for w in weights])

#WSM
@mcda_bp.route("/wsm", methods=["GET", "POST"])
def wsm():
    getcontext().prec = 12

    companies = list(db.companies.find({}))
    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]

    # 🔧 PREJ: selected_names = session.get("selected_names", [])
    # 🔧 ZDAJ: preberi 'selected_companies' (in fallback na 'selected_names' če obstaja)
    selected_names = session.get("selected_companies") or session.get("selected_names", [])

    # uteži iz session; če jih ni, default 1/n
    weights = session.get("weights")
    if not weights:
        n = len(criteria_names)
        default_weight = (Decimal("1") / Decimal(str(n))).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        weights = [float(default_weight)] * n

    results = []
    selected_companies = []

    if selected_names:
        selected_companies = [c for c in companies if c.get("name") in selected_names]

        if selected_companies:
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
        companies=selected_companies,   # pokažemo samo izbrane
        results=results,
        criteria_names=criteria_names,
    )


# TOPSIS
@mcda_bp.route("/topsis", methods=["GET"])
def topsis():
    plot_data = None
    getcontext().prec = 12

    companies = list(db.companies.find({}))

    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]

    # Izbor in uteži iz session (isti ključi kot pri Selection/WsM)
    selected_names = session.get("selected_companies") or session.get("selected_names", [])
    weights = session.get("weights")

    # Če uteži manjkajo -> default 1/n
    if not weights:
        n = len(criteria_names)
        default_weight = (Decimal("1") / Decimal(str(n))).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        weights = [float(default_weight)] * n

    results, interpretation = [], []

    # Če ni izbranih podjetij -> prikažemo samo opozorilo v HTML (companies=[])
    if not selected_names:
        return render_template(
            "topsis.html",
            companies=[],
            results=[],
            criteria_names=criteria_names,
            interpretation={},
            plot_data=None
        )

    # Filtriraj izbrane podjetja (originalni Mongo dokumenti)
    selected_docs = [c for c in companies if c.get("name") in selected_names]

    # Pripravi companies_display za prikaz v tabeli (ime + 7 kriterijev)
    companies_display = []
    for comp in selected_docs:
        row, _ = build_decision_matrix([comp])  # shape (1,7)
        companies_display.append({
            "name": comp["name"],
            "criteria": row[0].tolist()
        })

    # Če je vsaj eno podjetje, izvedi TOPSIS
    if selected_docs:
        weights_float = np.array([float(w) for w in weights], dtype=float)
        matrix, criteria_types = build_decision_matrix(selected_docs)

        topsis_method = TOPSIS()
        nmatrix, wmatrix, nis, pis, Dm, Dp, prefs = topsis_method._method(
            matrix, weights_float, criteria_types
        )

        for comp, nrow, wrow, pref in zip(selected_docs, nmatrix, wmatrix, prefs):
            results.append({
                "name": comp["name"],
                "pairs": list(zip(nrow.tolist(), wrow.tolist())),
                "score": round(float(pref), 3)
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        # Interpretacija
        interpretation = {
            "best": results[0]["name"],
            "worst": results[-1]["name"],
            "score_gap": round(results[0]["score"] - results[1]["score"], 3) if len(results) > 1 else None,
            "note": "Scores close to 1 indicate strong performance; scores near 0 indicate weak performance.",
            "percent_scores": [{"name": r["name"], "percent": round(r["score"] * 100, 1)} for r in results],
        }

        if len(results) > 1:
            gap = results[0]["score"] - results[1]["score"]
            if gap < 0.05:
                interpretation["stability"] = "Top 2 companies are very close — ranking may be unstable."
            elif gap > 0.15:
                interpretation["stability"] = "Top company is clearly dominant."
            else:
                interpretation["stability"] = "There is a moderate difference between top 2 companies."

        # Podatki za graf
        plot_data = {
            "labels": [r["name"] for r in results],
            "scores": [round(r["score"], 3) for r in results]
        }

    return render_template(
        "topsis.html",
        companies=companies_display,       # <-- za prikaz (ime + criteria)
        results=results,                   # <-- za rezultate
        criteria_names=criteria_names,
        interpretation=interpretation,
        plot_data=plot_data,
        zip=zip
    )


@mcda_bp.route("/promethee1", methods=["GET"])
def promethee1():

    getcontext().prec = 12

    companies = list(db.companies.find({}))
    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]

    # Izbor & uteži iz session (enako kot pri WSM/TOPSIS)
    selected_names = session.get("selected_companies") or session.get("selected_names", [])
    weights = session.get("weights")

    # Default 1/n, če uteži manjkajo
    if not weights:
        n = len(criteria_names)
        default_weight = (Decimal("1") / Decimal(str(n))).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        weights = [float(default_weight)] * n

    # Če še ni selekcije -> pokažemo prazno stran z opozorilom
    if not selected_names:
        return render_template(
            "promethee1.html",
            companies=[],
            results=[],
            criteria_names=criteria_names,
            interpretation={}
        )

    # Filtriraj izbrane dokumente
    selected_docs = [c for c in companies if c.get("name") in selected_names]
    if not selected_docs:
        return render_template(
            "promethee1.html",
            companies=[],
            results=[],
            criteria_names=criteria_names,
            interpretation={}
        )

    # Pripravi companies_display (ime + 7 kriterijev) za prikaz tabele
    companies_display = []
    for comp in selected_docs:
        row, _ = build_decision_matrix([comp])  # (1,7)
        companies_display.append({
            "name": comp["name"],
            "criteria": row[0].tolist()
        })

    # Izračun PROMETHEE I
    weights_float = np.array([float(w) for w in weights], dtype=float)
    matrix, criteria_types = build_decision_matrix(selected_docs)

    promethee = PROMETHEE_I(preference_function="usual")
    diff_tables, pi_table, (phi_plus, phi_minus) = promethee._method(
        matrix, weights_float, criteria_types
    )

    # results za Φ+, Φ-
    results = []
    for comp, p, m in zip(selected_docs, phi_plus, phi_minus):
        results.append({
            "name": comp["name"],
            "phi_plus": round(float(p), 3),
            "phi_minus": round(float(m), 3),
            "net_flow": round(float(p - m), 3)
        })
    results.sort(key=lambda x: x["net_flow"], reverse=True)

    # step-by-step razlaga
    explained = promethee._method_explained(matrix, weights_float, criteria_types)





    # Interpretacija
    interpretation = {}
    if results:
        interpretation["best"] = results[0]["name"]
        interpretation["worst"] = results[-1]["name"]
        interpretation["note"] = (
            "Φ⁺ (positive) kaže, koliko alternativa nadvlada druge; "
            "Φ⁻ (negative) koliko je nadvladana; net flow = Φ⁺ − Φ⁻."
        )

    return render_template(
        "promethee1.html",
        companies=companies_display,   # za prikaz (ime + kriteriji)
        results=results,               # Φ⁺, Φ⁻, net flow
        criteria_names=criteria_names,
        interpretation=interpretation,
        zip=zip
    )


@mcda_bp.route("/vikor", methods=["GET"])
def vikor():

    getcontext().prec = 12
    companies = list(db.companies.find({}))
    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]

    selected_names = session.get("selected_companies") or session.get("selected_names", [])
    weights = session.get("weights")

    if not weights:
        n = len(criteria_names)
        default_weight = (Decimal("1") / Decimal(str(n))).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        weights = [float(default_weight)] * n

    if not selected_names:
        return render_template("vikor.html",
                               companies=[],
                               results=[],
                               criteria_names=criteria_names,
                               interpretation={})

    selected_docs = [c for c in companies if c.get("name") in selected_names]

    companies_display = []
    for comp in selected_docs:
        row, _ = build_decision_matrix([comp])
        companies_display.append({
            "name": comp["name"],
            "criteria": row[0].tolist()
        })

    weights_float = np.array([float(w) for w in weights], dtype=float)
    matrix, criteria_types = build_decision_matrix(selected_docs)

    # 🔹 Uporabi unpack s 6 vrednostmi
    vikor = VIKOR()
    nmatrix, fminus, fstar, S, R, Q = vikor._method(matrix, weights_float, criteria_types)

    results = []
    for comp, s, r, q in zip(selected_docs, S, R, Q):
        results.append({
            "name": comp["name"],
            "S": round(float(s), 3),
            "R": round(float(r), 3),
            "Q": round(float(q), 3)
        })
    results.sort(key=lambda x: x["Q"])  # manjši Q je boljši

    interpretation = {}
    if results:
        interpretation["best"] = results[0]["name"]
        interpretation["worst"] = results[-1]["name"]
        interpretation["note"] = (
            "Lower Q indicates closer to compromise solution (best trade-off between S and R)."
        )


    plot_labels = []
    plot_scores = []

    for r in results:
        if not math.isnan(r["Q"]):
            plot_labels.append(r["name"])
            plot_scores.append(round(r["Q"], 3))
        else:
            plot_labels.append(r["name"])
            plot_scores.append(None)  # Chart.js bo prazen stolpec

    plot_data = {
        "labels": plot_labels,
        "scores": plot_scores
    }



    return render_template("vikor.html",
                           companies=companies_display,
                           results=results,
                           criteria_names=criteria_names,
                           interpretation=interpretation,
                           zip=zip,
                           plot_data=plot_data)



# Results
@mcda_bp.route("/results")
def results():
    criteria_names = [
        "Revenue", "Revenue Growth", "Profit",
        "Profit Growth", "Assets", "Employees", "ROA"
    ]

    # Preberi iz session
    selected_names = session.get("selected_companies") or []
    weights = session.get("weights")

    companies = list(db.companies.find({}))
    selected_companies = [c for c in companies if c.get("name") in selected_names]

    results_data = {}

    if selected_companies and weights:
        try:
            weights_float = np.array([float(w) for w in weights], dtype=float)
            matrix, criteria_types = build_decision_matrix(selected_companies)

            # --- WSM ---
            try:
                wsm_method = WSM()
                _, _, prefs = wsm_method._method(matrix, weights_float, criteria_types)
                wsm_results = [
                    {"name": comp["name"], "score": round(float(pref), 3)}
                    for comp, pref in zip(selected_companies, prefs)
                ]
                wsm_results.sort(key=lambda x: x["score"], reverse=True)
                results_data["WSM"] = wsm_results
            except Exception:
                results_data["WSM"] = []

            # --- TOPSIS ---
            try:
                topsis_method = TOPSIS()
                _, _, _, _, _, _, prefs = topsis_method._method(
                    matrix, weights_float, criteria_types
                )
                topsis_results = [
                    {"name": comp["name"], "score": round(float(pref), 3)}
                    for comp, pref in zip(selected_companies, prefs)
                ]
                topsis_results.sort(key=lambda x: x["score"], reverse=True)
                results_data["TOPSIS"] = topsis_results
            except Exception:
                results_data["TOPSIS"] = []

            # --- PROMETHEE I ---
            try:
                promethee = PROMETHEE_I(preference_function="usual")
                _, _, (phi_plus, phi_minus) = promethee._method(
                    matrix, weights_float, criteria_types
                )
                promethee_results = [
                    {
                        "name": comp["name"],
                        "net_flow": round(float(p - m), 3)
                    }
                    for comp, p, m in zip(selected_companies, phi_plus, phi_minus)
                ]
                promethee_results.sort(key=lambda x: x["net_flow"], reverse=True)
                results_data["PROMETHEE"] = promethee_results
            except Exception:
                results_data["PROMETHEE"] = []

            # --- VIKOR ---
            try:
                vikor = VIKOR()
                _, _, _, S, R, Q = vikor._method(matrix, weights_float, criteria_types)
                vikor_results = [
                    {
                        "name": comp["name"],
                        "Q": round(float(q), 3),
                        "S": round(float(s), 3),
                        "R": round(float(r), 3),
                    }
                    for comp, s, r, q in zip(selected_companies, S, R, Q)
                ]
                vikor_results.sort(key=lambda x: x["Q"])  # manjši Q je boljši
                results_data["VIKOR"] = vikor_results
            except Exception:
                results_data["VIKOR"] = []

        except Exception:
            # če pade že build_decision_matrix
            results_data = {}

    return render_template(
        "results.html",
        criteria_names=criteria_names,
        results_data=results_data,
        selected_companies=selected_companies
    )

@mcda_bp.route("/clear_selection")
def clear_selection():
    session.pop("selected_companies", None)
    session.pop("selected_names", None)
    session.pop("weights", None)
    return redirect(url_for("mcda_bp.select_companies"))