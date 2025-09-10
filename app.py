from flask import Flask, render_template
from flask_cors import CORS
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from routes.company_routes import company_bp
import requests

# 🔹 Ustvari Flask app
app = Flask(__name__)
CORS(app)

# 🔹 Povezava z bazo
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 🔹 Register blueprint
app.register_blueprint(company_bp, url_prefix="/api/companies")


# 👉 Glavna stran
@app.route("/")
def home():
    return render_template("index.html")


# 👉 AHP stran – tukaj boš imela tabelo podjetij
@app.route("/ahp")
def ahp():
    response = requests.get("http://127.0.0.1:5000/api/companies/")
    companies = response.json() if response.status_code == 200 else []
    return render_template("ahp.html", companies=companies)


# 👉 Ostale metode
@app.route("/topsis")
def topsis():
    return render_template("topsis.html")

@app.route("/promethee")
def promethee():
    return render_template("promethee.html")

@app.route("/wsm")
def wsm():
    return render_template("wsm.html")


if __name__ == "__main__":
    app.run(debug=True)
