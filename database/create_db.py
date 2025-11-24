"""
Database setup script - Creates database and all tables
"""
import mysql.connector
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.schema import CREATE_DATABASE, CREATE_TABLES, INSERT_DEFAULT_USER

load_dotenv()

def create_database():
    """Create the database and all tables"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        cursor = connection.cursor()
        
        print("Creating database...")
        cursor.execute(CREATE_DATABASE)
        print("[OK] Database created")
        
        # Select the database
        database_name = os.getenv('DB_NAME', 'interview_prep_ai')
        cursor.execute(f"USE {database_name}")
        
        print("\nCreating tables...")
        for i, table_sql in enumerate(CREATE_TABLES, 1):
            cursor.execute(table_sql)
            print(f"[OK] Created table {i}/{len(CREATE_TABLES)}")
        
        print("\nInserting default user...")
        cursor.execute(INSERT_DEFAULT_USER)
        connection.commit()
        print("[OK] Default user created")
        
        cursor.close()
        connection.close()
        
        print("\n[OK] Database setup completed successfully!")
        return True
        
    except mysql.connector.Error as err:
        print(f"\n[ERROR] {err}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("Interview Prep AI - Database Setup")
    print("="*50)
    print()
    
    success = create_database()
    
    if success:
        print("\nYou can now run the application with: python main.py")
    else:
        print("\nPlease check your database configuration in .env file")
        sys.exit(1)
