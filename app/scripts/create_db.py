import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

def create_database_if_not_exists():
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL environment variable is not set.")
        return False

    url = urlparse(db_url)
    db_name = url.path[1:]

    admin_url = db_url.replace(f'/{db_name}', '/postgres')
    
    try:
        conn = psycopg2.connect(admin_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"An error occurred while creating the database: {e}")
        return False

if __name__ == "__main__":
    create_database_if_not_exists()