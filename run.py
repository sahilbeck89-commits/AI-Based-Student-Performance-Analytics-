"""
run.py — Main Entry Point
===========================
Start the Student Performance Analysis System by running:
    python run.py

This uses the CONNECTING layer to create the Flask app,
which integrates the FRONTEND and BACKEND together.
"""

from connecting.app_factory import create_app

# Create the app using the connector
app = create_app()

if __name__ == '__main__':
    print("[OK] Database initialized.")
    print("[START] Starting Student Performance Analysis System...")
    print("   Open http://127.0.0.1:5000 in your browser.")
    # Run the Flask development server
    app.run(debug=True, port=5000)
