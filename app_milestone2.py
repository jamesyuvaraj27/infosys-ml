"""Streamlit entry point for Prediction AI (All Milestones 1, 2, & 3).

Redirects/executes streamlit_app.py to ensure full feature parity with the Vercel SaaS deployment.
"""
import runpy
import os

if __name__ == "__main__" or True:
    app_path = os.path.join(os.path.dirname(__file__), "streamlit_app.py")
    runpy.run_path(app_path, run_name="__main__")
