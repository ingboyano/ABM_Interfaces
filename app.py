import os
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

def create_app():
    """Application factory function that creates and configures the Flask app."""
    app = Flask(__name__)
    
    # Configure secret key from environment variable
    app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
    
    # Configure proxy fix for proper URL generation
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure database connection
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/vmmanager"
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    # Import User model for loader function
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from blueprints.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from blueprints.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    
    from blueprints.vms import vms as vms_blueprint
    app.register_blueprint(vms_blueprint)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Add template context processors
    @app.context_processor
    def utility_processor():
        return {
            'now': datetime.now
        }
    
    return app
