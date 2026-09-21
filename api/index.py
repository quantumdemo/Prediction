import os
import sys

# Add repository root and contracts path to sys.path for Vercel Serverless environment
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, ".."))
contracts_path = os.path.join(repo_root, "packages", "contracts", "python")

for path in [repo_root, contracts_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from services.ml.app.main import app

# Vercel WSGI/ASGI entry point export
app = app
