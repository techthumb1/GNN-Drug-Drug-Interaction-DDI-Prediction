import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5050)
