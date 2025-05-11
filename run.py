import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from backend.app import create_app

load_dotenv()

app = create_app()

from backend.app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
