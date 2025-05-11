from flask import Flask
from dotenv import load_dotenv
from .routes import init_routes
import os

def create_app():
    load_dotenv()

    base_dir = os.path.dirname(__file__)
    app = Flask(__name__, template_folder=os.path.join(base_dir, "templates"))
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

    init_routes(app)
    return app
