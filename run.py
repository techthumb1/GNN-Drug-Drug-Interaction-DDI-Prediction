import os
import sys
from flask import Flask
from dotenv import load_dotenv

# ─── Setup ────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "backend", "app", "templates"),
    static_folder=os.path.join(BASE_DIR, "backend", "app", "static")
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# ─── Register routes ──────────────────────────────────────────────────────────────
from backend.app.routes import init_routes
init_routes(app)

# ─── Launch ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
