from flask import Flask, jsonify
from flask_cors import CORS
from .api import bp
from ..logic_playground.api import bp as logic_bp
from ..scalper import bp as scalper_bp
from backend.llm.routes import bp as llm_bp
from backend.strategies.routes import bp as strategies_bp
from ..database import init_db, populate_sample_data
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_db()
    app.register_blueprint(logic_bp)
    app.register_blueprint(scalper_bp)
    app.register_blueprint(llm_bp)
    app.register_blueprint(strategies_bp)
    if os.getenv("CHEROKEE_AUTO_SAMPLE", "1") == "1" and not app.config.get("TESTING"):
        populate_sample_data()
    app.register_blueprint(bp)

    @app.route('/')
    def index():
        """Simple JSON index confirming the API is running."""
        return jsonify({"message": "Cherokee API"})

    return app
