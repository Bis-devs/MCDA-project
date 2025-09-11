from flask import Flask
from flask_cors import CORS
from routes.company_routes import company_bp
from routes.criteria_routes import criteria_bp
from routes.mcda_routes import mcda_bp
from routes.main_routes import main_bp


app = Flask(__name__)
CORS(app)
app.secret_key = "super-secret-key"



# Register blueprints
app.register_blueprint(company_bp)
app.register_blueprint(criteria_bp, url_prefix="/criteria")
app.register_blueprint(mcda_bp, url_prefix="/methods")
app.register_blueprint(main_bp, url_prefix="/")


if __name__ == "__main__":
    app.run(debug=True)
