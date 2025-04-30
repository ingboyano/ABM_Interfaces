import os
from app import create_app

app = create_app()

# Add a route for the root path
@app.route('/')
def index():
    """Redirect to dashboard or login page from root URL."""
    from flask_login import current_user
    from flask import redirect, url_for
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
