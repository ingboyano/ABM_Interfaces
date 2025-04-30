"""
Dashboard blueprint for displaying the main dashboard and quick actions.
"""
import logging
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard.route('/')
@login_required
def index():
    """Display the main dashboard with quick actions."""
    logger.debug(f"Rendering dashboard for user: {current_user.username}")
    return render_template('dashboard/dashboard.html')

@dashboard.route('/home')
def home():
    """Redirect to the dashboard or login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))
