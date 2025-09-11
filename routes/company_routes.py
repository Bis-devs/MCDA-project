from flask import Blueprint, render_template
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

company_bp = Blueprint("company_bp", __name__, url_prefix="/companies")

@company_bp.route("/test")
def test_companies():
    raw_companies = list(db.companies.find({}, {"_id": 0}))
    return render_template("test_companies.html", companies=raw_companies)
