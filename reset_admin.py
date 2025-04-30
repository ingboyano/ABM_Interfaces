"""
Script to reset the admin password in the database.
"""
import os
import logging
import psycopg2
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_admin_password():
    """Reset or create admin user with correct password hash."""
    # Get database connection parameters from environment
    db_host = os.environ.get('PGHOST', 'localhost')
    db_port = os.environ.get('PGPORT', '5432')
    db_name = os.environ.get('PGDATABASE', 'vmmanager')
    db_user = os.environ.get('PGUSER', 'postgres')
    db_password = os.environ.get('PGPASSWORD', '')
    
    logger.info(f"Connecting to PostgreSQL at {db_host}:{db_port}/{db_name} as {db_user}")
    
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        connection.autocommit = False
        cursor = connection.cursor()
        
        # Generate password hash using Werkzeug (which is what Flask-Login expects)
        password = 'SvaTecnica1'
        password_hash = generate_password_hash(password)
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()
        
        if admin_exists:
            # Update admin password
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = 'admin'",
                (password_hash,)
            )
            logger.info("Admin password updated successfully")
        else:
            # Create admin user
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                ('admin', 'admin@example.com', password_hash, 'admin')
            )
            logger.info("Admin user created successfully")
        
        connection.commit()
        cursor.close()
        connection.close()
        logger.info("Admin password reset completed successfully")
        
    except Exception as e:
        logger.error(f"Admin password reset failed: {e}")
        if 'connection' in locals():
            connection.rollback()
        raise

if __name__ == "__main__":
    logger.info("Starting admin password reset...")
    reset_admin_password()
    logger.info("Admin password reset completed")