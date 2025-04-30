"""
Database initialization script.
Creates all required database tables and initializes with basic data.
"""
import os
import logging
import psycopg2
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_sql_file(connection, cursor, filename):
    """Execute SQL commands from a file."""
    try:
        with open(filename, 'r') as f:
            sql = f.read()
        cursor.execute(sql)
        connection.commit()
        logger.info(f"Successfully executed SQL from {filename}")
    except Exception as e:
        logger.error(f"Error executing SQL from {filename}: {e}")
        connection.rollback()
        raise

def init_db():
    """Initialize the database with schema and initial data."""
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
        cursor = connection.cursor()
        
        # Execute the schema.sql file
        execute_sql_file(connection, cursor, 'schema.sql')
        
        # Close connection
        cursor.close()
        connection.close()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting database initialization...")
    init_db()
    logger.info("Database initialization completed")
