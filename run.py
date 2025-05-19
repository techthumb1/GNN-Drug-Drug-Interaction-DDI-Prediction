import os
import sys
from pathlib import Path
from flask import Flask

# ─── Setup Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))
sys.path.insert(0, str(BASE_DIR / "src"))

# ─── Load environment variables (only for local dev) ───────────────────────────────
if os.environ.get("FLASK_ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

# ─── Create Flask App ──────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=BASE_DIR / "backend" / "app" / "templates",
    static_folder=BASE_DIR / "backend" / "app" / "static"
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# ─── Register Routes ───────────────────────────────────────────────────────────────
try:
    from backend.app.routes import init_routes
    init_routes(app)
except Exception as e:
    app.logger.error(f"Failed to register routes: {e}")
    raise

# ─── Entry Point ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
