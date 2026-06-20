"""
Connecting — App Factory
=========================
Integration layer that wires Frontend ↔ Backend ↔ Blockchain.

Responsibilities:
  1. Point Flask at FRONTEND templates and static files
  2. Register BACKEND page + API blueprints
  3. Register BLOCKCHAIN identity blueprint (url_prefix=/blockchain)
  4. Configure session management
  5. Initialise the SQLite database
"""

import os
import sys
from flask import Flask

# ── Make sure the project root is on the Python path ──────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import init_db
from backend.routes import page_routes, api_routes
from backend.csv_upload_route import csv_bp


def create_app():
    """
    App Factory — creates and returns the configured Flask application.

    Integration logic
    -----------------
    template_folder  → frontend/templates/
    static_folder    → frontend/static/
    Blueprints       → page_routes, api_routes, blockchain_routes
    Database         → SQLite initialised via init_db()
    """

    # ── Paths ──────────────────────────────────────────────────────────────
    frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')
    template_dir = os.path.join(frontend_dir, 'templates')
    static_dir   = os.path.join(frontend_dir, 'static')

    # ── Create app ─────────────────────────────────────────────────────────
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )

    # ── Config ─────────────────────────────────────────────────────────────
    app.secret_key = 'student_performance_secret_key_2026'

    # ── Register blueprints ────────────────────────────────────────────────
    app.register_blueprint(page_routes)          # /, /login, /dashboard …
    app.register_blueprint(api_routes)           # /api/…
    app.register_blueprint(csv_bp)               # /api/upload-csv

    # ── Initialise database ────────────────────────────────────────────────
    init_db()

    return app
