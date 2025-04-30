"""
Authentication blueprint for handling user login, logout and registration.
"""
import os
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from urllib.parse import urlparse

from app import db
from models import User
from forms import LoginForm

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password', 'danger')
            logger.warning(f"Failed login attempt for user: {form.username.data}")
            return render_template('auth/login.html', form=form)
        
        # Log in the user
        login_user(user, remember=form.remember.data)
        logger.info(f"User {user.username} logged in successfully")
        flash(f'Welcome, {user.username}!', 'success')
        
        # Redirect to the requested page or dashboard
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    username = current_user.username
    logout_user()
    logger.info(f"User {username} logged out")
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
