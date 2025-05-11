import os
import sys
from dotenv import load_dotenv

# Add backend/ and src/ to path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

load_dotenv()

# Import the Flask app from backend
from backend.app import app

if __name__ == "__main__":
    # Bind to 0.0.0.0 and respect $PORT from Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=False)
