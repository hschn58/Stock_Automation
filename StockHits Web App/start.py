import sys
import os

# Ensure the current directory is in the sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

if __name__ == "__main__":
    app.run(debug=False, port=5001)
