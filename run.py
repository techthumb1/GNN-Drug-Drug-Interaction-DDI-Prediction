import os
import sys
from dotenv import load_dotenv

# Add backend/ and src/ to path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

load_dotenv()

# Import using factory
from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    # Use Render's PORT or fallback to 5050
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=False)
