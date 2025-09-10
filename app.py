from flask import Flask, render_template
from flask_cors import CORS
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from routes.company_routes import company_bp

app = Flask(__name__)
CORS(app)

# Povezava z bazo
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Register the blueprint
app.register_blueprint(company_bp, url_prefix="/api/companies")

# 🔹 Glavna stran (frontend)
@app.route("/")
def home():
    return render_template("index.html")   # namesto plain text

if __name__ == "__main__":
    app.run(debug=True)
