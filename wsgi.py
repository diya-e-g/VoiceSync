from app import app
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    app.run(debug=os.environ.get('FLASK_DEBUG', False))