from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    base_dir = os.path.dirname(__file__)
    app = Flask(__name__, template_folder=os.path.join(base_dir, "templates"))
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

    return app  # ✅ Delay route registration to run.py
