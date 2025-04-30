"""
WSGI entry point for Apache mod_wsgi.
"""
import os
import sys

# Add application path to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and create the application
from app import create_app
application = create_app()

if __name__ == "__main__":
    application.run()
