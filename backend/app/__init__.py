from flask import Flask
from dotenv import load_dotenv
from .routes import init_routes  # ✅ Handles everything
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

    init_routes(app)  # ✅ All routes get registered here
    return app
