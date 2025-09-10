from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
companies_collection = db["companies"]

company_bp = Blueprint("company_bp", __name__)

# ➕ Dodaj podjetje
@company_bp.route("/", methods=["POST"])
def add_company():
    data = request.json
    companies_collection.insert_one(data)
    return jsonify({"message": "Company added successfully"}), 201

# 📥 Pridobi podjetja
@company_bp.route("/", methods=["GET"])
def get_companies():
    companies = list(companies_collection.find({}, {"_id": 0}))
    return jsonify(companies), 200
